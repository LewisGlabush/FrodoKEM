from typing import Callable
from sage.all import log, sqrt, pi, RR, ZZ, load, cached_function  # type: ignore
load("lwe-estimator/estimator.py") # primal_usvp and dual_scale are used from here


from frodo import frodo_params
from cost_models import svp_models, reduction_algs
from lattice_estimator.estimator import LWE, Simulator
from lattice_estimator.estimator.nd import DiscreteGaussian
from lattice_estimator.estimator.lwe_parameters import LWEParameters


def lattice_estimator(name:str, q:int, n:int, m:int, sigma:float, reduction_model:Callable, analysis_type:str, verbose:bool=True):
    secret_distr = DiscreteGaussian(sigma, 0)
    params = LWEParameters(n=n, q=q, Xs=secret_distr, Xe=secret_distr, m=m, tag=f"{name} ct")
    if analysis_type == "beyond":
        deny_list = ("arora-gb", "bkw", "bdd_hybrid", "bdd_mitm_hybrid", "dual", "dual_hybrid")
        shape = Simulator.CN11
    elif analysis_type == "core":
        deny_list = (
                    # "usvp", "bdd",
                     "arora-gb", "bkw", "bdd_hybrid", "bdd_mitm_hybrid",
                    #  "dual",        # this should be a basic dual. it calls DualHybrid internally, but with no guessing/mitm happening (ie basic dual)
                    #  "dual_hybrid"  # matzov, does not call DualHybrid, I think fft is possible but not used (k_fft=0 is passed)
                                    # no [INDOCRYPT:EspJouKha20], would call DualHybrid; numbers are very similar (but larger than) matzov. using fft=True almost matches them. using mitm=True gives nonesense results, very large
                                    # mitm or no mitm?  is mitm = [IEEE:CHHS19]? is matzov doing mitm?
                     )
        shape = Simulator.GSA
    else:
        raise ValueError("`analysis_type` can be `\"core\"` or `\"beyond\"`")

    estimate = LWE.estimate(
        params,
        red_cost_model=reduction_model,
        red_shape_model=shape,
        deny_list=deny_list,
        catch_exceptions=False,
        verbose=verbose
    )

    rv = OrderedDict()
    if "usvp" in estimate:
        rv["uSVP cost"] = log(estimate["usvp"]["rop"], 2)
        rv["uSVP beta"] = estimate["usvp"]["beta"]
        rv["uSVP dim"] = estimate["usvp"]["d"]
    if "bdd" in estimate:
        rv["BDD cost"] = log(estimate["bdd"]["rop"], 2)
        rv["BDD red beta"] = estimate["bdd"]["beta"]
        rv["BDD svp beta"] = estimate["bdd"]["eta"]
        rv["BDD dim"] = estimate["bdd"]["d"]
    if "dual" in estimate:
        rv["Dual cost"] = log(estimate["dual"]["rop"], 2)
        rv["Dual vecs (?)"] = log(estimate["dual"]["mem"], 2)
        rv["Dual beta"] = estimate["dual"]["beta"]
        rv["Dual dim"] = estimate["dual"]["d"]
    if "dual_hybrid" in estimate:
        # estimator is using MATZOV as dual_hybrid
        rv["Dual hyb cost"] = log(estimate["dual_hybrid"]["rop"], 2)
        rv["Dual guess (?)"] = log(estimate["dual_hybrid"]["guess"], 2)
        rv["Dual N (?)"] = log(estimate["dual_hybrid"]["N"], 2)
        rv["Dual d/s indices (?)"] = estimate["dual_hybrid"]["zeta"]
        rv["Dual fft indices (?)"] = estimate["dual_hybrid"]["t"]
        rv["Dual red beta"] = estimate["dual_hybrid"]["beta"]
        rv["Dual sieve beta"] = estimate["dual_hybrid"]["beta_"]
        rv["Dual LWE samples"] = estimate["dual_hybrid"]["m"]
    return rv


def lwe_estimator(name:str, q:int, n:int, m:int, sigma:float, reduction_model:Callable):
    """
        Following the "Estimate all the schemes" methodology.
    """
    load("lwe-estimator/estimator.py") # primal_usvp and dual_scale are used from here
    secret_distribution = "normal"
    success_probability = 0.99
    alpha = sqrt(2*pi)*sigma/RR(q)
    reduction_cost_model = reduction_model
    return primal_usvp(  # type: ignore
        n, alpha, q, secret_distribution=secret_distribution, m=m, success_probability=success_probability, reduction_cost_model=reduction_cost_model
    )


from pprint import pprint
from tabulate import tabulate  # type: ignore
from typing import Tuple
import itertools
import parallelism
from collections import OrderedDict


def estimate_attack(estimate_params:Tuple, verbose=False):
    params, svp_model_name, reduction_alg_name, analysis_type = estimate_params
    name, q, n, bar_n, sigma = params
    m = n + bar_n
    reduction_model = reduction_algs[reduction_alg_name](svp_models[svp_model_name], svp_model_name)
    if verbose:
        lwe_estimator_estimate = lwe_estimator(name, q, n, m, sigma, reduction_model)
        print(f"LWE estimator (GSA-intersect {reduction_model.__name__}):", lwe_estimator_estimate)
    estimates = lattice_estimator(name, q, n, m, sigma, reduction_model, analysis_type, verbose=verbose)
    rv = OrderedDict()
    rv["Params"] = name
    rv["SVP model"] = svp_model_name
    rv["Reduction"] = reduction_alg_name
    for (k, v) in estimates.items():
        rv[k] = v
    if analysis_type == "core":
        # add other attacks to rv
        pass
    return rv


def beyond_core_svp():
    data = []
    data_lock = parallelism.Lock()
    beyond_core_analysis = list(itertools.product(
        frodo_params,
        ["c-lsf-sieve", "2d-ram-sieve", "parallel-approx-enum"],
        ["bkz", "pbkz"],
        ["beyond"]
    ))
    total_params = len(beyond_core_analysis)
    for rv in parallelism.eval(estimate_attack, beyond_core_analysis, total=total_params, use_tqdm=True, parallel=True):
        data_lock.acquire()
        try:
            data.append(rv)
        finally:
            data_lock.release()
    table = tabulate(data, headers = "keys", tablefmt="latex")
    print("\nBeyond Core SVP\n")
    print(table)


def core_svp():
    data = []
    data_lock = parallelism.Lock()
    core_analysis = list(itertools.product(
        frodo_params,
        [
            "q-rand-walk-sieve",
            "q-grover-sieve",
            "c-lsf-sieve"
        ],
        ["core"],
        ["core"]
    ))
    total_params = len(core_analysis)
    for rv in parallelism.eval(estimate_attack, core_analysis, total=total_params, use_tqdm=True, parallel=True):
        data_lock.acquire()
        try:
            data.append(rv)
        finally:
            data_lock.release()
    table = tabulate(data, headers = "keys", tablefmt="latex")
    print("\nCore SVP\n")
    print(table)


if __name__ == "__main__":
    core_svp()
    beyond_core_svp()

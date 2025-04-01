from sage.all import ZZ, RR, log  # type: ignore
from sage.all import cached_function  # type: ignore
from lattice_estimator.estimator.reduction import ReductionCost, Kyber


@cached_function
def QSieveRandomWalk(beta):
    # https://eprint.iacr.org/2021/570
    _beta = beta - Kyber.d4f(beta)
    return _beta * ZZ(2)**RR(0.257*_beta)


@cached_function
def QSieveGrover(beta):
    # https://research.tue.nl/files/14673128/20160216_Laarhoven.pdf
    _beta = beta - Kyber.d4f(beta)
    return _beta * ZZ(2)**RR(0.265*_beta)


@cached_function
def CSieveLSF(beta):
    # BDGL16 https://eprint.iacr.org/2015/1128
    _beta = beta - Kyber.d4f(beta)
    return _beta * ZZ(2)**RR(0.292*_beta)


@cached_function
def CSieve2DRAM(beta):
    # table 4 of [Jaques24] https://cic.iacr.org/p/1/3/6
    _beta = beta - Kyber.d4f(beta)
    return _beta * ZZ(2)**RR(0.3113*_beta)


@cached_function
def CParallelABLR21(beta):
    # this below returns the simulated wall-time for one approx SVP call
    # including requried preprocessing for asymptotically optimal enumeration.
    # being wall-time, we don't include the _beta factor used for sieving.
    # to account for parallelisation, we estimate the memory used by sieving,
    # and estimate the amount of CPUs that a machine equivalent to the one used
    # for sieving would run under a constant cpu : memory : wire ratio assumption [Jaques24]
    # assuming an nVidia GeForce RTX 4090 architecture
    log_runtime = RR(0.1250 * beta * log(beta, 2) - 0.654 * beta + 25.84 + log(64, 2))
    log_sieving_mem = RR(0.2075 * beta + log(beta, 2))
    log_mem_to_cpu_ratio = 28.3
    log_cpu = log_sieving_mem - log_mem_to_cpu_ratio
    cost = ZZ(2) ** (log_runtime - log_cpu)
    return cost


svp_models = {
    "q-rand-walk-sieve": QSieveRandomWalk,
    "q-grover-sieve": QSieveGrover,
    "c-lsf-sieve": CSieveLSF,
    "2d-ram-sieve": CSieve2DRAM,
    "parallel-approx-enum": CParallelABLR21
}


class CoreSieve(ReductionCost):
    """
        NOTE: we ignore memory
    """
    short_vectors = ReductionCost._short_vectors_sieve # TODO: this or Kyber's? this gives cheaper attacks
    # short_vectors = Kyber.short_vectors

    d4f = lambda self, beta: Kyber.d4f(beta)

    def __init__(self, svp_model, svp_model_name="?"):
        self.__name__ = f"core-{svp_model_name}"
        self.svp_model = svp_model
    
    def __call__(self, beta, d, B=None):
        return self.svp_model(beta)


class BKZModel(ReductionCost):
    short_vectors = ReductionCost._short_vectors_sieve # TODO: this or Kyber's? this gives cheaper attacks
    # short_vectors = Kyber.short_vectors

    d4f = lambda self, beta: Kyber.d4f(beta)

    def __init__(self, svp_model, svp_model_name="?", tours=8):
        self.__name__ = f"bkz-{svp_model_name}"
        self.svp_model = svp_model
        self.tours = tours
    
    def __call__(self, beta, d, B=None):
        # we conservatively ignore the last beta indices
        if d == beta:
            svp_calls_per_tour = 1
        else:
            svp_calls_per_tour = d - beta
        one_tour = svp_calls_per_tour * self.svp_model(beta)
        return self.tours * one_tour


class PBKZModel(ReductionCost):
    short_vectors = ReductionCost._short_vectors_sieve # TODO: this or Kyber's? this gives cheaper attacks
    # short_vectors = Kyber.short_vectors

    def __init__(self, svp_model, svp_model_name="?"):
        self.__name__ = f"pbkz-{svp_model_name}"
        self.svp_model = svp_model
    def __call__(self, beta, d, B=None):
        # we conservatively ignore the last beta indices on each BKZ tour
        return sum(
            (1 if d == _beta else d - _beta) * self.svp_model(_beta)
            for _beta in range(60, beta+1)
        )

reduction_algs = {
    'core': CoreSieve,
    'bkz': BKZModel,
    'pbkz': PBKZModel
}

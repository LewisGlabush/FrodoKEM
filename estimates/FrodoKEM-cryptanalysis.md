# Instructions

Dependencies:
- sagemath
- tqdm and tabulate python modules
- various estimators (see below)

To install the estimators, run `bash fetch_estimators.sh`
Install the python modules inside sage with `sage -pip install tqdm tabulate`
Then you can run `sage cross-estimates.py`

# Literature
- 2023-1892: asymptotic of hybrid primal attacks (low relevance) (DJB)
  
  Complains that Frodo didn't cite Howgrave-Graham's paper. I don't understand what the conclusions are. 

- 2024-592: formal aysmptotics for required block size (mid relevance) (DJB)
  
  No idea what this means for estimates.

- 2025-266: memory-efficient BKW (if sample-efficient too, highly relevant)

  "By leveraging the
  exponential growth of size-c subsets, it significantly reduces the number of initial
  samples needed, thereby lowering memory usage."

  Thm.1 needs N samples N >= q^((b + c\log_q c + 1)/(c-1)), where c >= 2, 1 <= b <= n

- 2024-713: asymptotics of G6K (mid relevant in current beyond core model)
- 2024-787: solving LWE using diophantine approximations (?)
- 2024-1681: a new LLL variant (not relevant)
- 2022-1343: new strategies for two-step mode LWE solving (relevant)
- 2024-601: provable reduction of NTRU lattices
- 2021-152: hybrid dual attacks (low relevance)
- 2021-557: dual attacks for CVP
- 2022-656: a "quantum augmented" dual attack
- 2022-1330: hybrid dual and meet-lwe attack (low relevance)
- 2022-1403: dual attack with hints (low relevance)
- 2022-1404: hints for improving primal dual and bkw (low relevance)
- 2023-1547: "estimation of key enumeration" with applications to LWE

And then the dual / MATZOV debate
- Matzov report (high relevance, disputed)
- 2023-1850: trying to fix heuristics in dual-sieve attacks
- 2019-1231: a refined analysis of using the Fourier transform for the distinguishing step
- enhancing the dual attack against MLWE (yay, no structure here)
- 2022-1750: faster dual attacks using coding theory
- 2023-1238: on the independence heuristic in the dual attack
- 2023-1508: provable dual attacks
- 2024-1791: discrete gaussian sampling for bkz-reduced basis ("significantly improve the complexity of the 2023-1508 attack")

# New beyond Core-SVP estimates

- [x] classical sieve exponent: 292, Jaques24
- [x] d4f
- [ ] repeats SVP:
  - [x] bkz,
  - [x] pbkz,
  -  [ ] (two-step https://github.com/Summwer/lwe-estimator-with-pnjbkz/tree/main). note, the two-step codebase is a mess. if max block size is predictable, then can underesitmate two-step by assuming one tour of max block size BKZ + une enum at the end
- [ ] variance over beta with CN11
- [x] no gates (kyber needed them)
- [x] no dual, controversial
- [x] area-times? then compare with 2020+ enum?
  - note: bkw and dual return "mem", but these are some number of vectors stored for distinguishing also, in the case of dual hybrid, they are anyway an upper bound
  - [x] suggestion: for beyond, it's not about storing multiple vectors, it's about the sieve's mem consumption. just figure that out, and return the memory for a single sieve after computing the total runtime of the attack. can compare this to enum, maybe
    - [x] 2-sieves: 0.292 + 0.2075/2 is what BDGL16 would naively suggest as wire_area-time cost. however bdgl16 was not optimised to reduce wire_are-time cost (hwich by assumption 1 is processor_area-time too) so instead we use [Jaq24] instead. hence we report 0.292 for RAM, 0.3113 (or higher) for 2D-mem costs.
    - [x] how does it compare to enumeration? how many CPUs match [Jaq24]'s architecture for sieving? well, for concrete numbres he uses an nVidia GPU, does a bits / tensor cores estimates (24GB/576 cores = 41.7 MB/core = 2**28.3 bits/core) and assumes asymptotically memory / cpus is constant, hence may as well use this one. then we take the memory to be beta * 2^0.2075 beta, and use the constant for gettin the number of cores.
- [ ] maybe reproduce old numbers with the new estimator?

# Core-SVP estimates

Do Core:
- [ ] All points in beyond, plus:
- [x] plain dual (code is there, point below about _short_vectors_sieve still needs to be addressed)
- [-] matzov
  - note: this is both an attack and (in the estimator) a cost model for sieving
  - [x] the cost model is a variant of the Kyber gate-count cost model. For a core-sieve estimate, it can be replaced with 0.292, as it does always produce higher numbers
  - [x] the way the estimator is written, dual_hybrid is defaulted to matzov.
  - [x] calling non-matzov needs manual intervention.
  - [-] what dual hybrids do we want to consider? mitm? does matzov include mitm? see comments on cross-estimates.py
    - looks like matzov as implemented uses no fft and no mitm. it gives smallest costs. not sure about how to enable fft, unclear from code
- [-] ReductionCost._short_vectors_sieve, do we want this or Kyber.short_vectors?
  - this should have different values for enum, or maybe we just ignore enum and leave this by default
  - Kyber's looks buggy, and gives larger costs anyway; will discuss with lattice-estimator maintainers
- [x] Quantum sieves: via Grover 0.265, via quantum random walks 0.257 (new quantum https://eprint.iacr.org/2021/570.pdf)
- [ ] provable dual (?)  -- check: these should only cost more than MATZOV, so unnecessary
- [ ] Quantum enumeration lower bounds?
- [ ] Enum lower bounds? The values in sieving are kinda lower-bound-ish.
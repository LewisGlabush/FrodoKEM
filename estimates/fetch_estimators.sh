
# lattice estimator
rm -rf lattice_estimator || true
git clone https://github.com/malb/lattice-estimator lattice_estimator
(
    cd lattice_estimator;
    git checkout 787c05a0eacc2c74bc834a6bb86262e2e90f54ab;
    git apply ../lattice-estimator.patch;
    touch __init__.py
)

# LWE estimator
rm -rf lwe-estimator || true
git clone https://bitbucket.org/malb/lwe-estimator lwe-estimator
(
    cd lwe-estimator;
    git checkout c50ab18d53ae05321f61f701eb809b1bc675c816
)

# leaky estimator, NIST branch
rm -rf leaky-LWE-Estimator-NIST-round3 || true
git clone https://github.com/lducas/leaky-LWE-Estimator leaky-LWE-Estimator-NIST-round3
(
    cd leaky-LWE-Estimator-NIST-round3;
    git checkout NIST-round3
)

# usvp-simulation
rm -rf usvp_simulation || true
git clone https://github.com/fvirdia/usvp-simulation usvp_simulation
(
    cd usvp_simulation;
    git checkout 333416dc30ce26bc6031f026090efae5f218c773
)

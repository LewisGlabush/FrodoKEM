# All matrices are defined over Z_q

# Attacking the long-term secret key:
# LWE instance = (A, B), S, E
# A is n x n, uniform
# S is n x \bar{n}, sampled close to round(N(0, sigma^2))
# E is n x \bar{n}, sampled close to round(N(0, sigma^2))
# breaking a single column breaks Decision LWE, so we can ignore \bar{n}

# Attacking the ephemeral secret in a ciphertext
# LWE instance = ([A|B]^T, [C1|C2]^T), S'^T, [E'|E'']^T
# [A|B]^T = (n + \bar{n}) x n
# S'^T is n x \bar{m}, sampled close to round(N(0, sigma^2))
# [E'|E'']^T is (n + \bar{n}) x \bar{m} sampled close to round(N(0, sigma^2))
# breaking a single column breaks Decision LWE, so we can ignore \bar{m}


frodo_params = [
    # name, q, n, bar_n, sigma
    ("Frodo-640", 32768, 640, 8, 2.8),
    ("Frodo-967", 65536, 967, 8, 2.3),
    ("Frodo-1344", 65536, 1344, 8, 1.4),
]

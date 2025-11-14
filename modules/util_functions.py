import numpy as np
from itertools import combinations

def subsets_of_size_k(n, k):
    """Returns all subsets of {1, 2, ..., n} of size k."""
    s = list(range(1, n+1))  # Generate candidates {1, 2, ..., n}
    return [set(comb) for comb in combinations(s, k)]

def subsets_of_size_interval(n, min_k, max_k):
    """Returns all subsets of {1, 2, ..., n} with size in [min_k, max_k]."""
    s = list(range(1, n+1))  # Generate candidates {1, 2, ..., n}
    return [set(comb) for r in range(min_k, max_k+1) for comb in combinations(s, r)]

def compare_intersections(W, W_prime, votes):
    """
    Returns binary array where element i = 1 if vote i strictly prefers W_prime over W.
    Preference is based on intersection size: |vote_i ∩ W_prime| > |vote_i ∩ W|.
    """
    L = []
    for A_i in votes:
        # Voter utility is intersection size with committee
        if len(A_i.intersection(W_prime)) > len(A_i.intersection(W)):
            L.append(1)  # Strict preference for W_prime
        else:
            L.append(0)  # Weak preference for W or indifferent
    return np.array(L)

def all_experiments_up_to_m(M, min_M = 2, min_k = 2):
    """Generate all (m, k) combinations where min_M <= m <= M, and min_k ≤ k < m."""
    experiment_list = []
    for m in range(min_M, M+1):
        for k in range(min_k, m):  # k must be at least min_k and less than m
            experiment_list.append({"m": m, "k": k})
    return experiment_list
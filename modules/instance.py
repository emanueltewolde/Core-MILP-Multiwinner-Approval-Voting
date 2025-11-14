import numpy as np
from modules.util_functions import subsets_of_size_k, compare_intersections, subsets_of_size_interval

class inst():
    """
    Represents an approval-based multi-winner voting instance.
    
    In approval-based multi-winner voting:
    - There are m candidates {1, 2, ..., m}
    - Voters submit approval ballots (subsets of candidates they approve)
    - A committee of size k is selected from the m candidates
    - Each voter's utility for committee W is |S ∩ W| where S is their approval set
    
    This class generates all possible:
    - Approval votes (subsets of candidates)
    - Committees (k-sized subsets of candidates) 
    - Deviations (alternative committees voters might prefer)
    - Preference relationships between committees and deviations
    """
    def __init__(self, m, k, exclude_subsets=False, min_dev_size=None, max_dev_size=None, min_vote_size=None, max_vote_size=None):
        """
        Initialize an approval-based multi-winner voting instance.
        
        Args:
            m (int): Number of candidates {1, 2, ..., m}
            k (int): Size of committee to be selected
            exclude_subsets (bool): If True, exclude deviations W' ⊆ W (subset deviations)
                                  This is important because subset deviations are trivially unprofitable
            min_dev_size (int): Minimum size of deviation committees to consider
            max_dev_size (int): Maximum size of deviation committees to consider  
            min_vote_size (int): Minimum size of approval votes to consider
            max_vote_size (int): Maximum size of approval votes to consider
        """
        self.m = m  # Number of candidates in the election
        self.k = k  # Target committee size
        
        # If True, excludes trivial subset deviations W' ⊆ W which are never profitable
        self.exclude_subsets = exclude_subsets

        # Set bounds on deviation committee sizes (default: consider all sizes 1 to k)
        if min_dev_size is None:
            self.min_dev_size = 1
        else:
            self.min_dev_size = min_dev_size
            
        if max_dev_size is None:
            self.max_dev_size = k
        else:
            self.max_dev_size = max_dev_size
            
        # Set bounds on approval vote sizes (default: consider all sizes 0 to m)
        if min_vote_size is None:
            self.min_vote_size = 0
        else:
            self.min_vote_size = min_vote_size
            
        if max_vote_size is None:
            self.max_vote_size = m
        else:
            self.max_vote_size = max_vote_size

    
    def generate_powersets(self):
        """
        Generate all relevant combinatorial objects for the approval-based multi-winner voting instance.
        
        Creates:
        - votes: All possible approval ballots (subsets of candidates within size bounds)
        - committees: All possible k-sized committees  
        - deviations: All possible alternative committees within size bounds
        - valid_devs: For each committee, which deviations are strategically relevant
        
        The valid_devs structure excludes subset deviations W' ⊆ W if exclude_subsets=True,
        since such deviations never improve voter utility (|S ∩ W'| ≤ |S ∩ W| for all votes S).
        """
        # Generate all possible approval votes within specified size bounds
        self.votes = subsets_of_size_interval(n=self.m, min_k=self.min_vote_size, max_k=self.max_vote_size)
        self.num_votes = len(self.votes)

        # Generate all possible k-sized committees
        self.committees = subsets_of_size_k(self.m, self.k)
        self.num_comms = len(self.committees)
        
        # Generate all possible deviation committees within specified size bounds
        self.deviations = subsets_of_size_interval(n=self.m, min_k=self.min_dev_size, max_k=self.max_dev_size)
        self.num_devs = len(self.deviations)

        # For each committee W, determine which deviations W' are strategically relevant
        self.valid_devs = [[] for _ in range(self.num_comms)]
        for i in range(self.num_comms):
            for j in range(self.num_devs):
                # Exclude subset deviations W' ⊆ W if requested (they're never profitable)
                if not (self.exclude_subsets and self.deviations[j].issubset(self.committees[i])):
                    self.valid_devs[i].append(j)

    def generate_improver_matrix(self):
        """
        Generate the preference matrix M[i,j,f] indicating strict preferences.
        
        M[i,j,f] = 1 if vote at index f strictly prefers deviation at index j over committee at index i
        M[i,j,f] = 0 otherwise
        
        In approval-based multi-winner voting, vote S strictly prefers committee W' over W if:
        |S ∩ W'| > |S ∩ W|
        
        This matrix is crucial for computing deviation incentives in the optimization models.
        """
        # Initialize 3D preference matrix: committees × deviations × votes
        M = np.zeros((self.num_comms, self.num_devs, self.num_votes))
        
        for i in range(self.num_comms):
            for j in range(self.num_devs):
                W = self.committees[i]    # Current committee
                Wp = self.deviations[j]   # Potential deviation committee
                # Compare utility |S ∩ W'| vs |S ∩ W| for all votes S
                M[i,j] = compare_intersections(W, Wp, self.votes)        

        self.impr = M  # Store as "improver" matrix
        
    
    def priceability_voter_indices(self, i, f):
        """
        Returns the indices of committees T that satisfy the priceability condition.
        
        Finds committees T such that:
        - |T| = |vote ∩ committee| + 1 (exactly one more candidate than current utility)
        - T ⊆ vote (T is subset of the original vote)
        - (vote ∩ committee) ⊆ T (T contains all currently satisfied candidates)
        
        Args:
            i: Committee index
            f: Vote index
            
        Returns:
            List of committee indices satisfying the priceability conditions
        """
        output = []
        vote = self.votes[f]           # The voter's approval set
        committee = self.committees[i] # The current committee
        
        for f1 in range(self.num_votes):
            # Check if vote f1 satisfies the three conditions above
            if (len(self.votes[f1]) == len(vote.intersection(committee)) + 1 and 
                self.votes[f1].issubset(vote) and 
                (self.votes[f].intersection(committee)).issubset(self.votes[f1])):
                output.append(f1)

        return output
    
    def priceability_voter_candidate_indices(self, i, c, f):
        """
        Returns indices of committees T that satisfy priceability condition AND contain candidate c+1.
        
        Finds committees T such that:
        - c+1 ∈ T (committee contains the specific candidate)
        - |T| = |vote ∩ committee| + 1 (exactly one more candidate than current utility)
        - T ⊆ vote (T is subset of the original vote)
        - (vote ∩ committee) ⊆ T (T contains all currently satisfied candidates)
        
        Args:
            i: Committee index
            c: Candidate index (0-based, so candidate is c+1)
            f: Vote index
            
        Returns:
            List of committee indices satisfying priceability conditions for candidate c+1
        """
        output = []
        vote = self.votes[f]           # The voter's approval set
        committee = self.committees[i] # The current committee
        
        for f1 in range(self.num_votes):
            # Check if vote f1 contains candidate c+1 AND satisfies priceability conditions
            if (c+1 in self.votes[f1] and 
                len(self.votes[f1]) == len(vote.intersection(committee)) + 1 and 
                self.votes[f1].issubset(vote) and 
                (self.votes[f].intersection(committee)).issubset(self.votes[f1])):
                output.append(f1)

        return output

    def lindahl_voter_indices(self, i, f):
        """
        Returns indices of committees T that improve utility under Lindahl pricing conditions.
        
        Finds committees T such that:
        - |T| > |vote ∩ committee| (more candidates than current utility)
        - T ⊆ vote (T is subset of the original vote)
        
        Note: We only check subsets of the original vote because if any subset T ⊆ vote
        is overpriced, then any set T' ⊄ vote would also be overpriced (since the voter
        doesn't approve candidates in T' \ vote).
        
        Args:
            i: Committee index
            f: Vote index
            
        Returns:
            List of committee indices that improve utility under Lindahl conditions
        """
        output = []
        vote = self.votes[f]           # The voter's approval set
        committee = self.committees[i] # The current committee
        voter_utility = len(vote.intersection(committee))  # Current utility |vote ∩ committee|
        
        for f1 in range(self.num_votes):
            # Check if vote f1 improves utility and is subset of original vote
            if len(self.votes[f1]) > voter_utility and self.votes[f1].issubset(vote):
                output.append(f1)

        return output
    
    def lindahl_voter_candidate_indices(self, i, c, f):
        """
        Returns indices of committees T that improve utility under Lindahl pricing AND contain candidate c+1.
        
        Finds committees T such that:
        - c+1 ∈ T (committee contains the specific candidate)
        - |T| > |vote ∩ committee| (more candidates than current utility)
        - T ⊆ vote (T is subset of the original vote)
        
        Same reasoning as lindahl_voter_indices - we only check subsets since
        any non-subset would also be overpriced.
        
        Args:
            i: Committee index
            c: Candidate index (0-based, so candidate is c+1)
            f: Vote index
            
        Returns:
            List of committee indices that improve utility under Lindahl conditions for candidate c+1
        """
        output = []
        vote = self.votes[f]           # The voter's approval set
        committee = self.committees[i] # The current committee
        voter_utility = len(vote.intersection(committee))  # Current utility |vote ∩ committee|
        
        for f1 in range(self.num_votes):
            # Check if vote f1 improves utility, contains candidate c+1, and is subset of original vote
            if (len(self.votes[f1]) > voter_utility and 
                c+1 in self.votes[f1] and 
                self.votes[f1].issubset(vote)):
                output.append(f1)

        return output
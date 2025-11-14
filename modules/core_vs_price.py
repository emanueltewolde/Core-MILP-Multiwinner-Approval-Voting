import gurobipy as gp
from gurobipy import GRB
import os

class core_vs_price():
    """
    Optimization model described in Section 6 and in the appendix of the accompanying paper submission comparing core concepts against pricing axioms in approval-based multi-winner voting.
    
    This class implements a program with quadratic constraints that finds the minimum core deviation incentive for (wlog) the first committee while ensuring it is not (Lindahl) priceable via its dual.
    
    Key variables:
    - x[f]: Proportion of voters with vote profile f
    - t[c]: Dual variable for the (Lindahl) priceabilty axiom for candidate at index c + 1
    - g[f,f1]: Dual probabilities for the (Lindahl) priceabilty axiom for vote and committee pair at indices f and f1
    - v: Objective value representing minimum core deviation incentive for the first committee 
    
    The model minimizes v subject to constraints ensuring priceability
    """
    def __init__(self, instance, droop=False, lindahl=True):
        quota = instance.k
        if droop:
            quota+=1
        self.instance=instance
        
        self.model = gp.Model("Core")
            

        # x[f] = proportion of voters with vote profile f
        x = self.model.addVars(self.instance.num_votes, vtype=GRB.CONTINUOUS, lb=0, ub=1, name="x")
        self.model.addConstr(gp.quicksum(x[i] for i in range(self.instance.num_votes)) == 1, "simplex constraint")

        # t[c] = dual variable for candidate c+1 in the pricing mechanism
        t = self.model.addVars(self.instance.m, vtype=GRB.CONTINUOUS, lb=0, name="t")
        # g[f,f1] = dual probability variables for pricing constraint satisfaction
        g = self.model.addVars(self.instance.num_votes, self.instance.num_votes, vtype=GRB.CONTINUOUS, lb=0, name="g")
        # v = minimum core deviation incentive for the first committee
        v = self.model.addVar(name="v", vtype=GRB.CONTINUOUS, lb=-2, ub=2)

        # Focus on committee at index 1 (without loss of generality)
        i = 1

        # Ensure v is at least the deviation incentive for all valid deviations from committee i
        for j in self.instance.valid_devs[i]:
            deviation_incentive = gp.quicksum(self.instance.impr[i,j,f]*x[f] for f in range(self.instance.num_votes)) - len(self.instance.deviations[j])/quota
            self.model.addConstr(v >= deviation_incentive, "minmax constraint")

        # sum of t's cannot exceed committee size
        self.model.addConstr(gp.quicksum(t[c] for c in range(self.instance.m)) <= self.instance.k, name="dual constraint")
        
        # g's form a joint probability distribution
        if lindahl:
            # Lindahl: sum over all valid utility improvements must equal 1
            self.model.addConstr(gp.quicksum(g[f,f1] for f in range(self.instance.num_votes) for f1 in self.instance.lindahl_voter_indices(i, f)) == 1)
        else:
            # Priceability: sum over all valid priceability improvements must equal 1
            self.model.addConstr(gp.quicksum(g[f,f1] for f in range(self.instance.num_votes) for f1 in self.instance.priceability_voter_indices(i, f)) == 1)
        
        # Dual constraints for each vote and candidate
        for f in range(self.instance.num_votes):
            for c in range(self.instance.m):
                # Only apply constraint if voter f approves candidate c+1
                if c+1 in self.instance.votes[f]:
                    if lindahl:
                        self.model.addConstr(t[c]*x[f] - gp.quicksum(g[f,f1] for f1 in self.instance.lindahl_voter_candidate_indices(i, c, f)) >= 0)
                    else:
                        self.model.addConstr(t[c]*x[f] - gp.quicksum(g[f,f1] for f1 in self.instance.priceability_voter_candidate_indices(i, c, f)) >= 0)

        self.model.setObjective(v, GRB.MINIMIZE)

        self.model.update()   
        
    def var_no_check(self):
        """Print the size of the optimization model (number of variables and constraints)."""
        print(f"Number of variables  : {self.model.NumVars}")
        print(f"Number of constraints: {self.model.NumConstrs}")

    def solve(self, path="saved_objects/milp/unnamed"):
        """
        Solve the core vs pricing optimization model and save results.
        
        Creates directory structure and files:
        - {path}.log: Gurobi solver log
        - {path}/proofs_and_solutions/{basename}_proof.lp: LP formulation
        - {path}/proofs_and_solutions/{basename}_solutions.txt: Solution details
        
        Args:
            path: Base path for saving results
        """
        base_name = os.path.basename(path)
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)  
        
        # Set up solver logging
        self.model.setParam('LogFile', path + '.log')

        # Create subdirectory for proofs and solutions
        proofandsols_dir = os.path.join(directory, 'proofs_and_solutions')
        os.makedirs(proofandsols_dir, exist_ok=True)
        
        # Write LP formulation to file
        proof_path = os.path.join(proofandsols_dir, f'{base_name}_proof.lp')
        self.model.write(proof_path)

        # Set path for solution output
        self.solution_path = os.path.join(proofandsols_dir, f'{base_name}_solutions.txt')

        # Solve the optimization problem
        self.model.optimize()

    def get_assignments(self, path="runs/core_vs_price"):
        """
        Extract and save the optimal solution assignments to a text file.
        
        Saves:
        - Optimal objective value (minimum core deviation incentive)
        - Vote distribution x[f] for all votes with positive probability
        
        Args:
            path: Base path (unused, solution path set in solve())
        """
        if self.model.status != GRB.OPTIMAL:
            print("*" * 50)
            print("Cannot save optimal variable assignments because the model hasn't been solved to optimality yet!")
            print("*" * 50)
            return

        full_path = self.solution_path
        print(f"Saving optimal solution assignments written to {full_path}")
        
        if not os.path.exists(full_path):
            with open(full_path, 'w') as file:
                file.write('\n')

        with open(full_path, 'a') as sol_file:
            sol_file.write("\n")
            sol_file.write("\n")
            sol_file.write("--------------------------------------\n")
            sol_file.write("--------------------------------------\n")
            sol_file.write("--------------------------------------\n")
            sol_file.write("\n")
            
            # Write the optimal objective value (minimum core deviation incentive)
            sol_file.write(f"The optimal objective value is: {round(self.model.objVal,5)}\n")
            
            # Extract and write vote distribution
            x = [None for _ in range(self.instance.num_votes)]
            for i in range(self.instance.num_votes):
                varname = "x[" + str(i) + "]"
                assigned_val = round(self.model.getVarByName(varname).X, 5)
                x[i] = assigned_val
                # Only report votes with non-negligible probability
                if assigned_val > 1e-5:
                    vote = self.instance.votes[i]
                    sol_file.write(f"{assigned_val*100} percentage of the votes are {vote}.\n")
            sol_file.write("\n")
            sol_file.write("\n")          
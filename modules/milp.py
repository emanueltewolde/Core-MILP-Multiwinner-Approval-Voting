import gurobipy as gp
from gurobipy import GRB
import numpy as np
import os

class milp():
    """
    Mixed Integer Linear Programming formulation for finding the core in approval-based multi-winner voting.
    
    This class implements the MILP model described in Section 3 of the accompanying paper submission that finds the worst-case value of the sizewise-least core across all possible vote distributions. The core exists if and only if the optimal objective value is < 0 for Hare quota or ≤ 0 for Droop quota.
    
    Key variables:
    - x[f]: Proportion of voters with vote profile f
    - y[i,j]: Binary variable indicating if deviation j is chosen as worst-case for committee i
    - v: Objective value representing value of the sizewise-least core
    
    The model maximizes v subject to constraints ensuring v represents the M under some vote distribution.
    """
    def __init__(self, instance, initial_vars=False, droop=False):
        self.instance = instance
        self.model = gp.Model("Core")

        # Set quota for deviation cost calculation
        self.droop = droop
        self.quota = self.instance.k
        if self.droop:
            self.quota += 1  # Droop quota = k+1

        # x[f] = proportion of voters with vote profile f (sums to 1)
        x = self.model.addVars(self.instance.num_votes, vtype=GRB.CONTINUOUS, lb=0, ub=1, name="x")
        self.model.addConstr(gp.quicksum(x[i] for i in range(self.instance.num_votes)) == 1, "simplex constraint")
        
        # y[i,j] = 1 if deviation j is selected as worst-case for committee i
        y = self.model.addVars(self.instance.num_comms, self.instance.num_devs, vtype=GRB.BINARY, name="y")
        for i in range(self.instance.num_comms):
            # Each committee must select at least one deviation as worst-case
            self.model.addConstr(gp.quicksum(y[i,j] for j in self.instance.valid_devs[i]) >= 1, "y-constraint")

        # v = maximum deviation incentive across all committees and vote distributions
        v = self.model.addVar(name="v", vtype=GRB.CONTINUOUS, lb=-2, ub=2)

        # Big-M constraints: v ≤ deviation_incentive[i,j] + M*(1 - y[i,j])
        for i in range(self.instance.num_comms):
            for j in self.instance.valid_devs[i]:
                deviation_incentive = gp.quicksum(self.instance.impr[i,j,f]*x[f] for f in range(self.instance.num_votes)) - len(self.instance.deviations[j])/self.quota
                # When y[i,j]=1: v ≤ deviation_incentive; When y[i,j]=0: constraint inactive (+ 3)
                self.model.addConstr(v <= deviation_incentive + 3 - 3*y[i,j], "minmax constraint")

        # Maximize worst-case value of the sizewise-least core
        self.model.setObjective(v, GRB.MAXIMIZE)

        # Provide warm start values to achieve theoretical lower bound if requested
        if initial_vars:
            # Set initial objective based on quota type
            if self.droop:
                v.Start = 0 
            else:
                v.Start = -1/(self.instance.k*(self.instance.k+1))
            
            # Initialize vote distribution: equal weight on singleton votes {1}, {2}, ..., {k+1}
            x_initial_vars = {i: 0 for i in range(self.instance.num_votes)}
            for i in range(1, self.instance.k+2):
                x_initial_vars[i] = 1/(self.instance.k+1)
            for index, var in x.items():
                var.Start = x_initial_vars[index]

            # Initialize deviation selection: for each committee, choose singleton deviation
            y_initial_vars = {(i,j): 0 for i in range(self.instance.num_comms) for j in range(self.instance.num_devs)}

            for i in range(self.instance.num_comms):
                # Find first candidate in {1,...,k+1} not in committee i
                no_rep = 1
                while no_rep in self.instance.committees[i]:
                    no_rep += 1
                if no_rep > self.instance.k+1:
                    raise Exception("Something's up with the initial values")
                # Set y[i,j] = 1 for deviation j = {no_rep}
                dev = (self.instance.deviations).index({no_rep})
                y_initial_vars[(i,dev)] = 1
            for index, var in y.items():
                var.Start = y_initial_vars[index]
        
        self.model.update()   


    def var_no_check(self):
        """Print the size of the optimization model (number of variables and constraints)."""
        print(f"Number of variables  : {self.model.NumVars}")
        print(f"Number of constraints: {self.model.NumConstrs}")


    def solve(self, path="runs/milp/unnamed"):
        """
        Solve the MILP model and save results to specified path.
        
        Creates directory structure and files:
        - {path}.log: Gurobi solver log
        - {path}/proofs_and_solutions/{basename}_proof.lp: LP formulation
        - {path}/proofs_and_solutions/{basename}_solutions.txt: Solution details
        
        Args:
            path: Base path for saving results
        """
        # self.model.setParam('Threads', 8)  # Uncomment to use multiple threads

        base_name = os.path.basename(path)
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)  
        
        # Set up solver logging
        self.model.setParam('LogFile', path + '.log')

        # Create subdirectory for proofs and solutions
        proofandsols_dir = os.path.join(directory, 'proofs_and_solutions')
        os.makedirs(proofandsols_dir, exist_ok=True)
        
        # Write Branch and Bound LP proofs to file
        proof_path = os.path.join(proofandsols_dir, f'{base_name}_proof.lp')
        self.model.write(proof_path)

        # Set path for solution output
        self.solution_path = os.path.join(proofandsols_dir, f'{base_name}_solutions.txt')

        # Solve the optimization problem
        self.model.optimize()

    def get_assignments(self, path="runs/milp/unnamed"):
        """
        Extract and save the optimal solution assignments to a text file.
        
        Saves:
        - Optimal objective value (maximum deviation incentive)
        - Vote distribution x[f] for all votes with positive probability
        - For each committee, which deviations were selected as worst-case and their incentives
        
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
                file.write('')

        with open(full_path, 'a') as sol_file:
            # Write the optimal objective value (maximum deviation incentive)
            sol_file.write(f"The optimal objective value is: {self.model.objVal}\n")
            
            # Extract and write vote distribution
            x = [None for _ in range(self.instance.num_votes)]
            for i in range(self.instance.num_votes):
                varname = "x[" + str(i) + "]"
                assigned_val = self.model.getVarByName(varname).X
                x[i] = assigned_val
                # Only report votes with non-negligible probability
                if assigned_val > 1e-8:
                    vote = self.instance.votes[i]
                    sol_file.write(f"{assigned_val*100} percentage of the votes are {vote}.\n")
            sol_file.write("\n")
            sol_file.write("\n")                

            # For each committee, report which deviations were selected as worst-case
            for i in range(self.instance.num_comms):
                devs = []
                incentives = []
                for j in self.instance.valid_devs[i]:
                    varname = "y[" + str(i) + "," + str(j) + "]"
                    assigned_val = self.model.getVarByName(varname).X
                    rounded = np.round(assigned_val, decimals=4)
                    
                    # Verify binary variable is actually binary
                    if rounded != 0 and rounded != 1:
                        raise Exception(f"Binary variable {varname} has been assigned to nonbinary value {assigned_val}.")
                    elif rounded == 1:
                        # This deviation was selected as worst-case for this committee
                        devs.append(self.instance.deviations[j])
                        # Calculate the actual deviation incentive
                        incentive = sum(self.instance.impr[i,j,f]*x[f] for f in range(self.instance.num_votes)) - len(self.instance.deviations[j])/self.quota
                        incentives.append(incentive)

                comm = self.instance.committees[i]
                text = f"For committee {comm}, the voters would like to deviate to any of the following subcommittees: "
                for f in range(len(devs)):
                    text += f"{devs[f]} with deviation incentives {incentives[f]}, "
                text += "\n"
                sol_file.write(text)
            
            sol_file.write("\n")
            sol_file.write("\n")
            sol_file.write("--------------------------------------\n")
            sol_file.write("--------------------------------------\n")
            sol_file.write("--------------------------------------\n")
            sol_file.write("\n")
            

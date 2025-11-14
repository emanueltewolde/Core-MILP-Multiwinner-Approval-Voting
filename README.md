# Approval-Based Multi-Winner Voting: Core Analysis

This repository contains code for analyzing core concepts in approval-based multi-winner voting systems, comparing different quota systems (Droop vs. Hare) and priceability axioms (Lindahl vs. priceability). 

It implements the theoretical framework described in the associated AAAI 2026 paper:

"**[On the Edge of Core (Non-)emptiness: An Automated Reasoning Approach to Approval-based Multi-winner Voting](http://arxiv.org/)**" by *Ratip Emin Berker\*, Emanuel Tewolde\*, Vincent Conitzer, Mingyu Guo, Marijn Heule, and Lirong Xia*. (\*equal contribution)

**Citation:**

```bibTeX
@inproceedings{Berker2026edge,
    author = {Ratip Emin Berker, Emanuel Tewolde, Vincent Conitzer, Mingyu Guo, Marijn Heule, and Lirong Xia,
    title = "On the Edge of Core (Non-)emptiness: An Automated Reasoning Approach to Approval-based Multi-winner Voting",
    year = "2026",
    booktitle = "AAAI",
}
```

## Setup

### Prerequisites

- **Conda** (Anaconda or Miniconda)
- **Gurobi Optimizer** with a valid license
  - Academic licenses are free and available at [gurobi.com](https://www.gurobi.com/academia/academic-program-and-licenses/)
  - The license must be activated on your system before running experiments

### Creating the Environment

1. Create a new conda environment with Python 3.10.13:
```bash
conda create --name abc_voting python=3.10.13
```

2. Activate the environment:
```bash
conda activate abc_voting
```

3. Install the required packages:
```bash
pip install numpy==1.26.4
pip install gurobipy==11.0.3
```

### Verifying Gurobi Installation

Test that Gurobi is properly installed and licensed:
```
python -c "import gurobipy as gp; model = gp.Model(); print('Gurobi is working!')"
```

## Running Experiments

### Quick Start

Run all experiments with default settings:
```bash
python main.py
```

This will execute all combinations of:
- **Quota systems**: Hare quota (k) vs. Droop quota (k+1)
- **Priceability axioms**: Lindahl priceability vs. priceability axiom
- **Problem types**: MILP (worst-case core analysis) vs. core-vs-priceability comparison

### Experiment Types

1. **MILP Experiments** (`milp_up_to_m`):
   - Find the worst-case value of the sizewise-least core
   - Determines if the core exists (objective < 0 for Hare, or <= 0 for Droop)

2. **Core vs. Priceability Experiments** (`core_vs_price_up_to_m`):
   - Find minimum core deviation incentive while satisfying priceability axioms
   - Compare core stability under different priceability axioms


## Code Structure

### Core Modules

- **`modules/instance.py`**: Defines voting instances with candidates, committees, and voter preferences
- **`modules/milp.py`**: Mixed Integer Linear Programming formulation for core analysis
- **`modules/core_vs_price.py`**: Optimization comparing core concepts against priceability axioms
- **`modules/util_functions.py`**: Utility functions for combinatorial generation and preference comparison
- **`main.py`**: Main experiment runner

### Key Concepts

- **Voting Instance**: m candidates, committee size k, approval ballots
- **Core**: Set of stable outcomes where no coalition wants to deviate
- **Quotas**: 
  - Hare quota: k (more permissive)
  - Droop quota: k+1 (more restrictive)
- **priceability axioms**:
  - Lindahl priceability: Based on Lindahl equilibrium (more restrictive)
  - Priceability (more permissive)

## Results

### Output Structure

Experiments create the following directory structure:

```
runs/
├── milp_with_hare/
│   └── m3k2/
│       ├── m3k2.log                    # Solver log
│       └── proofs_and_solutions/
│           ├── m3k2_proof.lp           # LP formulation
│           └── m3k2_solutions.txt      # Optimal solutions
├── milp_with_droop/
├── harecore_vs_lindahl/
├── harecore_vs_priceability/
├── droopcore_vs_lindahl/
└── droopcore_vs_priceability/
```

### Result Files

- **`.log`**: Gurobi solver output and statistics
- **`_proof.lp`**: Mathematical formulation in LP format
- **`_solutions.txt`**: Optimal objective values, vote distributions, and deviation incentives

### Example Results

For comparison, the `example_runs/` directory contains the examples of how these results will look like, for the simple instances of up to m=3. The structure mirrors the `runs/` directory.

## Interpreting Results

### MILP Results

- **Objective Value**: Maximum deviation incentive across all committees
- **Core Existence**: 
  - Core exists if objective < 0 (Hare) or <= 0 (Droop)
  - Positive values indicate core non-existence

### Core vs. Priceability Results

- **Objective Value**: Minimum core deviation incentive under priceability constraints
- **Vote Distribution**: Optimal voter preference profile
- **Counterexample existence**: 
  - Core stable committee that is not priceable exists if objective < 0 (Hare) or <= 0 (Droop)
  - Positive values indicate no counterexample exists

## Technical Notes

- Subset deviations are excluded as they're never profitable
- The code uses 1-based indexing for candidates {1, 2, ..., m}

## Thank you

...for your interest in our work! Feel free to post a github issue if you have any questions.

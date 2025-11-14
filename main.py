#%%
from modules.instance import inst
from modules.milp import milp
from modules.core_vs_price import core_vs_price
from modules.util_functions import all_experiments_up_to_m

def milp_up_to_m(m, make_quota_droop):
    """Run MILP experiments for all (m,k) combinations up to m candidates."""
    iterator = all_experiments_up_to_m(m, min_k=1)
    quota = "droop" if make_quota_droop else "hare"

    for iter in iterator:
        m = iter["m"]
        k = iter["k"]
        save_path = 'runs/milp_with_{}/m{}k{}'.format(quota, m, k)
        print("Saving files at ", save_path)

        # Create approval-based multi-winner voting instance
        if k == 1:
            abc = inst(m, k)
        else:
            # wlog exclude subset deviations, limit deviation size to k-1
            abc = inst(m, k, exclude_subsets=True, max_dev_size=k-1)
        abc.generate_powersets()
        abc.generate_improver_matrix()

        # Solve MILP to find worst-case value of the sizewise-least core
        solver = milp(abc, initial_vars=True, droop=make_quota_droop)
        solver.solve(save_path)
        solver.get_assignments(save_path)

def core_vs_price_up_to_m(m, make_quota_droop, make_price_lindahl):
    """Run core vs pricing experiments for all (m,k) combinations up to m candidates."""
    iterator = all_experiments_up_to_m(m, min_k=1)
    quota = "droop" if make_quota_droop else "hare"
    price = "lindahl" if make_price_lindahl else "priceability"

    for iter in iterator:
        m = iter["m"]
        k = iter["k"]
        save_path = 'runs/{}core_vs_{}/m{}k{}'.format(quota, price, m, k)
        print("Saving files at ", save_path)

        # Create approval-based multi-winner voting instance: exclude subset deviations, allow full-size deviations
        abc = inst(m, k, exclude_subsets=True, max_dev_size=k)
        abc.generate_powersets()
        abc.generate_improver_matrix()

        # Solve core vs pricing to find minimum core deviation incentive while satisfying pricing axioms
        solver = core_vs_price(abc, droop=make_quota_droop, lindahl=make_price_lindahl)
        solver.solve(save_path)
        solver.get_assignments(save_path)


if __name__ == "__main__":
    # Run all experiments for m candidates with different quota and pricing combinations

    #####################################################################################################
    ################################# COMMENT OUT THE ONES YOU DO NOT WANT TO RUN ################################
    #####################################################################################################
    
    # MILP experiments: find worst-case value of the sizewise-least core

    milp_up_to_m(m=7, make_quota_droop=False)  # Hare quota
    # milp_up_to_m(m=7, make_quota_droop=True)   # Droop quota


    # Core vs pricing experiments: find minimum core deviation incentives while satisfying pricing axioms

    # core_vs_price_up_to_m(m=5, make_quota_droop=False, make_price_lindahl=False)  # Hare + priceability
    # core_vs_price_up_to_m(m=4, make_quota_droop=False, make_price_lindahl=True)   # Hare + Lindahl
    # core_vs_price_up_to_m(m=6, make_quota_droop=True, make_price_lindahl=False)   # Droop + priceability
    # core_vs_price_up_to_m(m=5, make_quota_droop=True, make_price_lindahl=True)    # Droop + Lindahl
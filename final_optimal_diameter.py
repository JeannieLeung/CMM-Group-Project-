

import numpy as np

# Import existing functions: 
import numpy as np
#start code with creating new branch again 
from Power.power_and_cp_root_finding import expected_power_MW

from ODE_group.ODE_code import solve_tip_for_DV
from Blade_cost_Regression.blade_size_cost import deterministic_blade_cost

RHO_AIR = 1.225    # not used here but common constant if you extend
DELTA_MAX_FRAC = 0.05   # 5% tip-deflection limit
D_CAP = 130.0           # practical cap (transport/tower clearance)

#  Wind speeds for WhiteLee Wind Farm
velocityDict: dict = {
    "light": 1.9,           # light wind speed in m/s, 44.66% of the time
    "gentle": 4.7,          # gentle wind speed in m/s, 18.99% of the time
    "moderate": 6.75,       # moderate wind speed in m/s, 16.7% of the time
    "fresh": 9.4,           # fresh wind speed in m/s, 9.5% of the time
    "strong": 12.3,         # strong wind speed in m/s, 1.34% of the time
    "near_gale": 15.6,      # near gale wind speed in m/s, 0.15% of the time
    "strong_gale": 22.6     # strong gale wind speed in m/s, 0.006% of the time

}
   

def cost_gbp(D: float) -> float:
    return float(deterministic_blade_cost(D/2)["TotalCost_£"])

def worstcase_tip_deflection(D: float) -> float:
    """Use the worst (highest) wind bin to check structural feasibility."""
    V = max(b[1] for b in WIND_BINS)
    R = D/2
    omega = lambda_opt * V / R
    return float(solve_tip_for_DV(D, V, omega))   # returns y_tip in metres

def is_structurally_feasible(D: float) -> bool:
    y = worstcase_tip_deflection(D)
    L = D/2
    return (y <= DELTA_MAX_FRAC * L) and (D <= D_CAP)

def optimise_diameter(D_min=80.0, D_max=130.0, step=0.5):
    grid = np.arange(D_min, D_max + 1e-9, step)
    feasible = [D for D in grid if is_structurally_feasible(D)]
    if not feasible:
        raise RuntimeError("No feasible diameters satisfy deflection/cap limits.")

    results = []
    for D in feasible:
        power = float(expected_power_MW(D))           # MW
        cost  = cost_gbp(D)                           # £
        score = power / cost                          # MW per £
        results.append((D, score, power, cost))

    # pick best MW per £
    D_opt, score, power, cost = max(results, key=lambda t: t[1])
    return {
        "D_opt_m": D_opt,
        "objective_MW_per_GBP": score,
        "expected_power_MW": power,
        "cost_GBP": cost,
        "feasible_count": len(feasible)
    }

if __name__ == "__main__":
    out = optimise_diameter()
    print(f"[Integrated optimum] D = {out['D_opt_m']:.1f} m | "
          f"Score: {out['objective_MW_per_GBP']:.3e} MW/£ | "
          f"E[P]={out['expected_power_MW']:.2f} MW | Cost=£{out['cost_GBP']:,.0f} | "
          f"Feasible grid points={out['feasible_count']}")

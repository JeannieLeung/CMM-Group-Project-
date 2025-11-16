import numpy as np

# Import existing functions:
from Power.power_and_cp_root_finding import (
    expected_power_MW,
    compute_lambda_optimal,
    Omega_r,  # only if you need it elsewhere
)
from ODE_group.ODE_code import solve_tip_for_DV
from Blade_cost_Regression.blade_size_cost import deterministic_blade_cost

RHO_AIR = 1.225
DELTA_MAX_FRAC = 0.05
D_CAP = 130.0

velocityDict = {
    "light": 1.9,
    "gentle": 4.7,
    "moderate": 6.75,
    "fresh": 9.4,
    "strong": 12.3,
    "near_gale": 15.6,
    "strong_gale": 22.6,
}

# tie it to your module’s wind API if you want a single source
WIND_BINS = list(velocityDict.items())

# one-time compute; safe because it's a function now
lambda_opt = compute_lambda_optimal()



def cost_gbp(D: float) -> float:
    per_blade = float(deterministic_blade_cost(D/2)["TotalCost_£"])
    return 3.0 * per_blade

def worstcase_tip_deflection(D: float) -> float:
    V = max(velocityDict.values())   # use the max wind speed
    R = D / 2
    omega = lambda_opt * V / R
    return float(solve_tip_for_DV(D, V, omega))

def is_structurally_feasible(D: float) -> bool:
    y = worstcase_tip_deflection(D)
    L = D / 2
    return (y <= DELTA_MAX_FRAC * L) and (D <= D_CAP)

def optimise_diameter(D_min=80.0, D_max=130.0, step=0.5, V_power=6.0):
    grid = np.arange(D_min, D_max + 1e-9, step)
    feasible = [D for D in grid if is_structurally_feasible(D)]
    if not feasible:
        raise RuntimeError("No feasible diameters satisfy deflection/cap limits.")

    results = []
    for D in feasible:
        power = float(expected_power_MW(D, V_power))  # use API from power module
        cost = cost_gbp(D)
        score = power / cost
        results.append((D, score, power, cost))

    D_opt, score, power, cost = max(results, key=lambda t: t[1])
    return {
        "D_opt_m": D_opt,
        "objective_MW_per_GBP": score,
        "expected_power_MW": power,
        "cost_GBP": cost,
        "feasible_count": len(feasible),
    }

if __name__ == "__main__":
    
    out = optimise_diameter()
    print(
        f"[Integrated optimum] D = {out['D_opt_m']:.1f} m | "
        f"Score: {out['objective_MW_per_GBP']:.3e} MW/£ | "
        f"E[P]={out['expected_power_MW']:.2f} MW | Cost=£{out['cost_GBP']:,.0f} | "
        f"Feasible grid points={out['feasible_count']}"
    )

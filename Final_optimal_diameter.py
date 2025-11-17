# === Integrated Safety + Cost + Power Optimiser ===

import numpy as np

from ODE_group.ODE_code import WIND_VELOCITIES, solve_tip_for_DV
from Blade_cost_Regression.blade_size_cost import deterministic_blade_cost
from Power.power_and_cp_root_finding import (
    compute_lambda_optimal,
    expected_power_MW,
)


# PARAMETERS
DELTA_MAX_FRAC = 0.1                    # allowable tip deflection = 10% of blade length
D_CAP = 130                             # maximum manufacturable diameter
LAMBDA_OPT = compute_lambda_optimal()


# STRUCTURAL CHECK
def worstcase_tip_deflection(D: float) -> float:
    V = max(WIND_VELOCITIES.values())   # 22.6 m/s (strong gale)
    R = D / 2.0
    omega = LAMBDA_OPT * V / R          # rotational speed based on λ_opt
    return solve_tip_for_DV(D, V, omega)

def is_structurally_feasible(D: float) -> bool:
    y_tip = worstcase_tip_deflection(D)
    L = D / 2.0
    return (y_tip <= DELTA_MAX_FRAC * L) and (D <= D_CAP)

def get_safe_diameters(D_min=40, D_max=D_CAP, step=0.5):
    grid = np.arange(D_min, D_max + 1e-9, step)
    safe = [D for D in grid if is_structurally_feasible(D)]
    return np.array(safe)


# COST MODEL
def blade_cost_gbp(D):
    L = D / 2.0
    per_blade = deterministic_blade_cost(L)["TotalCost_£"]
    return 3.0 * per_blade  # 3 blades per turbine


# OPTIMISATION
def optimise_over_safe_diameters(V_power=6.0):
    safe_D = get_safe_diameters()
    if safe_D.size == 0:
        raise RuntimeError("No structurally safe diameters!")

    results = []
    for D in safe_D:
        power = float(expected_power_MW(D, V_power))  
        cost  = float(blade_cost_gbp(D))              
        score = power / cost                          
        results.append((D, score, power, cost))

    D_opt, best_score, best_power, best_cost = max(results, key=lambda t: t[1])

    return {
        "D_opt_m": D_opt,
        "objective_MW_per_GBP": best_score,
        "expected_power_MW": best_power,
        "cost_GBP": best_cost,
        "safe_diameters": safe_D,
    }


# MAIN EXECUTION
if __name__ == "__main__":
    out = optimise_over_safe_diameters(V_power=6.0)
    print(
        f"Optimal D (within safety) = {out['D_opt_m']:.1f} m\n"
        f"Power  = {out['expected_power_MW']:.2f} MW\n"
        f"Cost   = £{out['cost_GBP']:,.0f}\n"
        f"Score  = {out['objective_MW_per_GBP']:.3e} MW/£"
    )

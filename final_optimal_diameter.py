#new code 
#Get the safe diameters 
import numpy as np
from ODE_code import ySG_array, blade_lengths  # ySG at strongest wind, and the matching diameters

DELTA_MAX_FRAC = 0.1  # e.g. tip deflection <= 10% of blade length

def get_safe_diameters():
    safe_D = []
    for D, y_tip in zip(blade_lengths, ySG_array):
        L = D / 2.0                  # blade length
        limit = DELTA_MAX_FRAC * L    # max allowed deflection
        if y_tip <= limit:
            safe_D.append(D)
    return np.array(safe_D)

# evaluate power and cost on the safe set
from Power.power_and_cp_root_finding import expected_power_MW
from Blade_cost_Regression.blade_size_cost import deterministic_blade_cost

def blade_cost_gbp(D):
    """Total blade cost for one turbine at diameter D."""
    L = D / 2.0
    per_blade = deterministic_blade_cost(L)["TotalCost_£"]
    return 3.0 * per_blade  # 3 blades


#Combine optimisation 
def optimise_over_safe_diameters(V_power=6.0):
    safe_D = get_safe_diameters()
    if safe_D.size == 0:
        raise RuntimeError("No structurally safe diameters!")

    results = []
    for D in safe_D:
        power = float(expected_power_MW(D, V_power))   # MW at chosen wind speed
        cost  = float(blade_cost_gbp(D))               # £
        score = power / cost                           # MW per £
        results.append((D, score, power, cost))

    # pick the diameter with best score
    D_opt, best_score, best_power, best_cost = max(results, key=lambda t: t[1])

    return {
        "D_opt_m": D_opt,
        "objective_MW_per_GBP": best_score,
        "expected_power_MW": best_power,
        "cost_GBP": best_cost,
        "safe_diameters": safe_D,
    }


if __name__ == "__main__":
    out = optimise_over_safe_diameters(V_power=6.0)
    print(
        f"Optimal D (within safety) = {out['D_opt_m']:.1f} m\n"
        f"Power = {out['expected_power_MW']:.2f} MW\n"
        f"Cost  = £{out['cost_GBP']:,.0f}\n"
        f"Score = {out['objective_MW_per_GBP']:.3e} MW/£"
    )

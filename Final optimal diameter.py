import numpy as np

# --- imports from your teammates' modules (now snake_case) ---
from power_and_cp_root_finding import lambda_optimal, calculate_Cp   # you can also import expected_power_MW if it exists
from ODE_code import solve_tip_for_DV
from Blade_cost_Regression.blade_size_cost import deterministic_blade_cost

RHO_AIR = 1.225
DELTA_MAX_FRAC = 0.05
D_CAP = 130.0

# Wind bins with frequencies (use these instead of velocityDict for aggregation)
WIND_BINS = [
    ("light",       1.9,   0.4466),
    ("gentle",      4.7,   0.1899),
    ("moderate",    6.75,  0.1670),
    ("fresh",       9.4,   0.0950),
    ("strong",      12.3,  0.0134),
    ("near_gale",   15.6,  0.0015),
    ("strong_gale", 22.6,  0.00006),
]

def expected_power_MW(D: float) -> float:
    """Wind-frequency weighted power at diameter D, running at lambda_opt."""
    R = D / 2.0
    P = 0.0
    for _, V, p in WIND_BINS:
        omega = lambda_optimal * V / R                   # run at aero optimum
        Cp = calculate_Cp(lambda_optimal, omega, V)      # your BEM Cp
        P_k = 0.5 * RHO_AIR * np.pi * R**2 * Cp * V**3
        P += p * P_k
    return P / 1e6  # MW

def cost_gbp(D: float) -> float:
    return float(deterministic_blade_cost(D/2)["TotalCost_£"])

def worstcase_tip_deflection(D: float) -> float:
    """Check deflection at the highest wind bin."""
    V = max(b[1] for b in WIND_BINS)
    R = D/2
    omega = lambda_optimal * V / R
    return float(solve_tip_for_DV(D, V, omega))   # metres

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
        power = float(expected_power_MW(D))   # MW
        cost  = cost_gbp(D)                   # £
        score = power / cost                  # MW per £
        results.append((D, score, power, cost))
    D_opt, score, power, cost = max(results, key=lambda t: t[1])
    return {"D_opt_m": D_opt, "objective_MW_per_GBP": score,
            "expected_power_MW": power, "cost_GBP": cost,
            "feasible_count": len(feasible)}

if __name__ == "__main__":
    out = optimise_diameter()
    print(f"[Integrated optimum] D = {out['D_opt_m']:.1f} m | "
          f"Score: {out['objective_MW_per_GBP']:.3e} MW/£ | "
          f"E[P]={out['expected_power_MW']:.2f} MW | Cost=£{out['cost_GBP']:,.0f} | "
          f"Feasible grid points={out['feasible_count']}")

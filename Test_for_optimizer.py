from Power.power_and_cp_root_finding import (
    compute_lambda_optimal,
    expected_power_MW,
)

# 1. TEST LAMBDA OPTIMAL
print("=== Test: compute_lambda_optimal() ===")
lam = compute_lambda_optimal()
print(f"Optimal λ = {lam:.4f}")

# 2. TEST POWER FOR A RANGE OF DIAMETERS
print("\n=== Test: expected_power_MW(D) ===")
for D in [50, 80, 100, 120]:
    P = expected_power_MW(D, V_site=6.0)
    print(f"D = {D:>3} m → P = {P:.3f} MW")

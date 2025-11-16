from ODE_code import ySG_array
from ODE_code import blade_lengths
from ODE_code import I

safety_factor = 1.35 #industry  standard, this can be changed depending on varying companies policies

#safety pass --> safety rule, deflection should not exceed 1/10 of the blade length divided by a safety factor
# safety factor accounts for material stress limits, ensures the turbine can handle longer exposure to loads:
for diameter, y_tip in zip(blade_lengths, ySG_array):
    if y_tip < (0.1 * diameter)/safety_factor:
        print(f"Diameter {diameter:.1f} m → SAFE")
    else:
        print(f"Diameter {diameter:.1f} m → UNSAFE")


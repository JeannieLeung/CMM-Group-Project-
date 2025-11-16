from ODE_code import ySG_array
from ODE_code import blade_lengths
from ODE_code import I


uts: int = 1000 #ultimate tensile strength of glass fibre reinforced polymer with carbon fibres
safety_factor = 2

#safety pass 1 --> safety rule, deflection should not exceed 1/10 of the blade length:
for diameter, y_tip in zip(blade_lengths, ySG_array):
    if y_tip < (0.1 * diameter)/safety_factor:
        print(f"Diameter {diameter:.1f} m → SAFE")
    else:
        print(f"Diameter {diameter:.1f} m → UNSAFE")

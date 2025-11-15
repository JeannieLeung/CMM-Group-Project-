import numpy as np
from math import hypot
from scipy.integrate import solve_bvp

#  Wind speeds for WhiteLee Wind Farm, to be changed as needed
velocityDict: dict = {
    "light": 1.9,           # light wind speed in m/s, 44.66% of the time
    "gentle": 4.7,          # gentle wind speed in m/s, 18.99% of the time
    "moderate": 6.75,       # moderate wind speed in m/s, 16.7% of the time
    "fresh": 9.4,           # fresh wind speed in m/s, 9.5% of the time
    "strong": 12.3,         # strong wind speed in m/s, 1.34% of the time
    "near_gale": 15.6,      # near gale wind speed in m/s, 0.15% of the time
    "strong_gale": 22.6     # strong gale wind speed in m/s, 0.006% of the time
}

drag_force_results: list[list[float]] = []
rot_force_results: list[list[float]] = []
deflection_results: list[list[float]] = []

#define other input variables
E: int = 40e9  # Young's modulus for glass fibre reinforced polymer
cd: float = 1.28  # Drag coefficient for a flat plate perpendicular to flow
density_air: float = 1.225  # Density of air in kg/m^3
tsr: int = 6.0
density_blade: int = 1550 # Density of glass fibre reinforced polymer with carbon fibre in kg/m^3
gravity: float = 9.81
width: int=2
height: int=1
I: float = (height*width**3)/12

# Define list fo blade lengths to be tested, realistic range based on model chosen
# Turbine blade diameters from 80m to 140m in 1m increments, while being represented by radii
#TODO Upper bound for blade length chosen based on optimal rotor radius given by power calculation "CMM3 Group Project Power and Cp Root Finding doc" 
#TODO TOM WRITE THIS IN THE README PLEASE!!
blade_lengths = np.arange(40.0, 70.0, 0.5)  
    
# Function to compute drag forces for all diameters at a given wind speed
def drag_load(blade_lengths: list, wind_speed: float, cd: float=1.28, density_air:float =1.225) -> list:
    drag_load_list = []  # Initialize an empty list to store drag forces
    for i in blade_lengths:
        dl = 0.5 * cd * density_air * height * (wind_speed** 2)
        drag_load_list.append(dl)
    return drag_load_list

#function to compute rotational drag force
def rot_load(blade_lengths, wind_speed, cd, density_air, width):
    rot_load_list = []
    for i in blade_lengths:
        rot_speed = tsr * wind_speed / i
        ar = 0.5* (rot_speed**2) * density_air * cd * width 
        rot_load_list.append(ar)
        
    return rot_load_list
        
def grav_load(blade_lengths, density_blade, gravity, width):
    grav_load_list = []
    for i in blade_lengths:
        b = density_blade * gravity * width * height
        grav_load_list.append(b)
    return grav_load_list

def solve_tip_deflection_for_length(L: float, a_r: float, b_const: float, rl_const: float) -> float:
    """
    Solve two BVPs on [0, L] with cantilever BCs:
      y(0)=y'(0)=0, y''(L)=y'''(L)=0
    1) EI*y'''' = a_r x^2 + b_const
    2) EI*y'''' = rl_const
    Return hypot(y1(L), y2(L)).
    """
    def make_solver(rhs_func):
        # y1=y, y2=y', y3=y'', y4=y'''
        def ode(x, Y):
            d1 = Y[1]
            d2 = Y[2]
            d3 = Y[3]
            d4 = rhs_func(x)/(E*I)
            return np.vstack((d1,d2,d3,d4))
        def bc(Ya, Yb):
            return np.array([Ya[0], Ya[1], Yb[2], Yb[3]])
        x = np.linspace(0.0, L, 10)
        Y0 = np.zeros((4, x.size))
        sol = solve_bvp(ode, bc, x, Y0, max_nodes=10000)
        if sol.status != 0:
            x = np.linspace(0.0, L, 50)
            Y0 = np.zeros((4, x.size))
            sol = solve_bvp(ode, bc, x, Y0, max_nodes=10000)
        return sol.sol(np.array([L]))[0,0]
    rhs1 = lambda x: a_r*(x**2) + b_const
    rhs2 = lambda x, r=rl_const: np.full_like(x, r, dtype=float)
    y1L = make_solver(rhs1)
    y2L = make_solver(rhs2)
    return hypot(y1L, y2L)

# Paste wind speeds and run ODE
wind_keys = ["light","gentle","moderate","fresh","strong","near_gale","strong_gale"]
deflection_results = []

for key in wind_keys:
    V = velocityDict[key]
    drag_list = drag_load(blade_lengths, V, cd, density_air)            # rl (wind) [N/m]
    grav_list = grav_load(blade_lengths, density_blade, gravity, width) # b (gravity) [N/m]
    ar_list   = rot_load(blade_lengths, V, cd, density_air, width)      # a_r [N/m^3]

    y_for_this_wind = []
    for L, a_r, b, rl in zip(blade_lengths, ar_list, grav_list, drag_list):
        b_const  = float(b)    # gravity only in (a)
        rl_const = float(rl)        # wind only in (b)
        y_tip = solve_tip_deflection_for_length(float(L), float(a_r), b_const, rl_const)
        y_for_this_wind.append(y_tip)

    deflection_results.append(y_for_this_wind)


# Print in format
print("# Results (BVP): deflection vs. blade length")
for i, vals in zip(blade_lengths, zip(*deflection_results)):
    yL, yG, yM, yF, yS, yNG, ySG = vals
    print(f"Diameter: {i:.1f} m, yL: {yL:.3g} m, yG: {yG:.3g} m, yM: {yM:.3g} m, "
          f"yF: {yF:.3g} m, yS: {yS:.3g} m, yNG: {yNG:.3g} m, ySG: {ySG:.3g} m")
    
#prepare necessary data for final calculation of allowable diameter    
ySG_array = np.array(deflection_results[-1])
print(ySG_array)

import numpy as np
import warnings
from math import hypot
from scipy.integrate import solve_bvp


#  Wind speeds for WhiteLee Wind Farm, to be changed as needed
WIND_VELOCITIES: dict = {
    "light": 1.9,           # light wind speed in m/s, 44.66% of the time
    "gentle": 4.7,          # gentle wind speed in m/s, 18.99% of the time
    "moderate": 6.75,       # moderate wind speed in m/s, 16.7% of the time
    "fresh": 9.4,           # fresh wind speed in m/s, 9.5% of the time
    "strong": 12.3,         # strong wind speed in m/s, 1.34% of the time
    "near_gale": 15.6,      # near gale wind speed in m/s, 0.15% of the time
    "strong_gale": 22.6     # strong gale wind speed in m/s, 0.006% of the time
}


#define other input variables
BLADE_YOUNGS_MODULUS: int = 45e9  # Young's modulus for glass fibre reinforced polymer with carbon fibre 
BLADE_DRAG_COEF: float = 0.4  # Drag coefficient for an inefficient aerofoil perpendicular to flow NEED TO ADDRESS IN REPORT
AIR_DENSITY: float = 1.225  # Density of air in kg/m^3
TIP_SPEED_RATIO: int = 6.0 # estimate based off of Siemens website IMPORTANT TO PUT IN REPORT
BLADE_MASS_PER_LENGTH: int = 410 # kg/m, estimate based off of Siemens website IMPORTANT TO PUT IN REPORT
GRAVITY: float = 9.81
BLADE_WIDTH: int = 2.5
BLADE_HEIGHT: int = 0.8
I_BEND_ACROSS_HEIGHT = (BLADE_WIDTH * BLADE_HEIGHT ** 3) / 12   # load acts over height (vertical)
I_BEND_ACROSS_WIDTH  = (BLADE_HEIGHT * BLADE_WIDTH ** 3) / 12   # load acts over width  (lateral)

#TODO: CHANGE THE ROT SPEED TO BE A FUNCTION OF TIP SPEED RATIO AND WIND SPEED, FOR NOW THIS WILL SUFFICE



    
def drag_load(blade_lengths: list, wind_speed: float) -> list:
    """
    Load due to wind drag acting transversely onto the blade
    """
    return [0.5 * BLADE_DRAG_COEF * AIR_DENSITY * BLADE_HEIGHT * (wind_speed ** 2)] * len(blade_lengths)


def grav_load(blade_lengths: list) -> list:
    """
    Load due to weight of the blade uniformly distrubuted
    """
    return [BLADE_MASS_PER_LENGTH * GRAVITY] * len(blade_lengths)


def rot_load(blade_lengths: list, wind_speed: float) -> list:
    """
    Load due to rotation of the blade causing drag, parallel to the gravitational force
    """

    rot_load_list = [0.0] * len(blade_lengths)
    for i, length in enumerate(blade_lengths):
        rot_speed = TIP_SPEED_RATIO * wind_speed / length
        ar = 0.5 * (rot_speed ** 2) * AIR_DENSITY * BLADE_DRAG_COEF * BLADE_WIDTH 
        rot_load_list[i] = ar
        
    return rot_load_list
        

#TODO WIDTH AND HEIGHT ARE ARBITRARY GUESSES FOR NOW

def analytic_tip_deflections(L: float, a_r: float, b_const: float, rl_const: float):
    """
    Analytical solutions for the differential equations:

    y-direction (gravity + rotational drag):
    y_y(L) = (13/180) * a_r * L^6 / (E I_y) + b_const * L^4 / (8 E I_y)

    x-direction (wind drag, uniform):
    y_x(L) = rl_const * L^4 / (8 E I_x)
    """
    EI_y = BLADE_YOUNGS_MODULUS * I_BEND_ACROSS_HEIGHT
    EI_x = BLADE_YOUNGS_MODULUS * I_BEND_ACROSS_WIDTH

    y_y = ((13.0 / 180.0) * a_r * L ** 6 / EI_y) + (b_const * L ** 4 / (8.0 * EI_y))
    y_x = rl_const * L ** 4 / (8.0 * EI_x)

    return y_y, y_x


def _sanity_check_tip_deflection(
    L: float,
    a_r: float,
    b_const: float,
    rl_const: float,
    y1_num: float,
    y2_num: float,
    rtol: float = 1e-3,
    atol: float = 1e-6,
) -> None:
    
    """
    Sanity checks:
    1) Input validity (positive length, finite loads).
    2) BVP numerical result vs. analytic closed-form for the same loads.
    3) Small-deflection assumption (|y_tip| / L << 1).
    """

    if L <= 0.0:
        raise ValueError(f"Blade length L must be positive; got L={L!r}")

    for name, val in [("a_r", a_r), ("b_const", b_const), ("rl_const", rl_const)]:
        if not np.isfinite(val):
            raise ValueError(f"Non-finite value for {name}: {val!r}")

    # Tip deflections for comparison
    y1_ana, y2_ana = analytic_tip_deflections(L, a_r, b_const, rl_const)

    if not np.all(np.isfinite([y1_num, y2_num, y1_ana, y2_ana])):
        raise FloatingPointError(
            "Non-finite tip deflection encountered (NaN or inf) in BVP or "
            "analytic comparison."
        )

    # Compare numerical BVP against analytic solution
    if not np.isclose(y1_num, y1_ana, rtol=rtol, atol=atol):
        diff = abs(y1_num - y1_ana)
        rel = diff / (abs(y1_ana) + atol)
        warnings.warn(
            f"y-direction BVP tip deflection deviates from analytic solution by "
            f"{diff:.3e} m (relative {rel:.3e}).",
            RuntimeWarning,
        )

    if not np.isclose(y2_num, y2_ana, rtol=rtol, atol=atol):
        diff = abs(y2_num - y2_ana)
        rel = diff / (abs(y2_ana) + atol)
        warnings.warn(
            f"x-direction BVP tip deflection deviates from analytic solution by "
            f"{diff:.3e} m (relative {rel:.3e}).",
            RuntimeWarning,
        )

    # Check small-deflection regime
    y_tot = hypot(y1_num, y2_num)
    if L > 0.0:
        rel_defl = y_tot / L
        if rel_defl > 0.1:
            warnings.warn(
                "Large deflection detected: |y_tip|/L = "
                f"{rel_defl:.2f}. Small-deflection Euler-Bernoulli theory may "
                "not be strictly valid here.",
                RuntimeWarning,
            )


def solve_tip_deflection_for_length(L: float, a_r: float, b_const: float, rl_const: float) -> float:
    """
    Solve two BVPs on [0, L] with cantilever BCs:
      y(0)=y'(0)=0, y''(L)=y'''(L)=0
    1) EI*y'''' = a_r x^2 + b_const
    2) EI*y'''' = rl_const
    Return hypot(y1(L), y2(L)).
    """
    def make_solver(rhs_func, EI):
        # y1=y, y2=y', y3=y'', y4=y'''

        def ordinary_differntial_equation(x, Y):
            d1 = Y[1]                                                       # y1' = y2
            d2 = Y[2]                                                       # y2' = y3
            d3 = Y[3]                                                       # y3' = y4
            d4 = rhs_func(x) / (EI)                                         # y4' = y'''' = w(x)/EI
            return np.vstack((d1, d2, d3, d4))

        def boundary_conditions(Ya, Yb):
            """
            Ya = Y at x=0  = [y(0), y'(0)]
            Yb = Y at x=L  = [y''(L), y'''(L)]
            """
            return np.array([Ya[0], Ya[1], Yb[2], Yb[3]])

        # Using a reasonable guess for the starting point, solve for BVP
        x = np.linspace(0.0, L, 10)
        Y0 = np.zeros((4, x.size))
        sol = solve_bvp(ordinary_differntial_equation, boundary_conditions, x, Y0, max_nodes=10000)

        if sol.status != 0:             # Checking in case solver did not converge
            x = np.linspace(0.0, L, 50)
            Y0 = np.zeros((4, x.size))
            sol = solve_bvp(ordinary_differntial_equation, boundary_conditions, x, Y0, max_nodes=10000)
        
        if sol.status != 0:
            raise RuntimeError(
                f"BVP solver failed to converge for L={L}, EI={EI}. "
                f"Status: {sol.status}, message: {sol.message}"
            )

        if not np.all(np.isfinite(sol.y)):
            raise FloatingPointError(
                "Non-finite values in BVP solution array (NaN or inf)."
            )

        return sol.sol(np.array([L]))[0,0]
    
    # Load distribution for ODE in y-direction due to rotational drag and weight
    rhs1 = lambda x: a_r * (x ** 2) + b_const
    # Load distribution for ODE in x-direction due to wind
    rhs2 = lambda x, r=rl_const: np.full_like(x, r, dtype=float)

    EI_y = BLADE_YOUNGS_MODULUS * I_BEND_ACROSS_HEIGHT
    EI_x = BLADE_YOUNGS_MODULUS * I_BEND_ACROSS_WIDTH

    # Apply solver to functions
    y1L = make_solver(rhs1, EI_y)
    y2L = make_solver(rhs2, EI_x)

    _sanity_check_tip_deflection(L, a_r, b_const, rl_const, y1L, y2L)

    return hypot(y1L, y2L)


def results():
    # Paste wind buns and run ODE
    wind_keys = ["light","gentle","moderate","fresh","strong","near_gale","strong_gale"]
    deflection_results = []

    # Define list for blade lengths to be tested, realistic range based on model chosen
    blade_lengths = np.arange(40.0, 80.0, 0.5)  # Turbine blade diameters from 80m to 160m in 1m increments, while being represented by radii

    # For each wind case compute the corresponding load
    for key in wind_keys:
        vel = WIND_VELOCITIES[key]
        drag_list = drag_load(blade_lengths, vel)            # rl (wind) [N/m]
        grav_list = grav_load(blade_lengths)                 # b (gravity) [N/m]
        ar_list   = rot_load(blade_lengths, vel)             # a_r [N/m^3]

        # Solve ODE for each beam length for every blade length and store in deflection_results
        y_for_this_wind = []
        for L, a_r, b, rl in zip(blade_lengths, ar_list, grav_list, drag_list):
            b_const  = float(b)         # gravity only in (a)
            rl_const = float(rl)        # wind only in (b)
            y_tip = solve_tip_deflection_for_length(float(L), float(a_r), b_const, rl_const)
            y_for_this_wind.append(y_tip)

        deflection_results.append(y_for_this_wind)

    data_by_wind = {k: v for k, v in zip(wind_keys, deflection_results)}

    print("# Results (BVP): deflection vs. blade length")
    for i, vals in zip(blade_lengths, zip(*deflection_results)):
       yL, yG, yM, yF, yS, yNG, ySG = vals
       print(f"Diameter: {2*i:.1f} m, yL: {yL:.3g} m, yG: {yG:.3g} m, yM: {yM:.3g} m, "
             f"yF: {yF:.3g} m, yS: {yS:.3g} m, yNG: {yNG:.3g} m, ySG: {ySG:.3g} m")
       
    return data_by_wind, blade_lengths


if __name__ == "__main__": 
    data_by_wind, blade_lengths = results()

    ySG_array = np.array(data_by_wind["strong_gale"])

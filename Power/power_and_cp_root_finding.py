import math 
import numpy as np 
import matplotlib.pyplot as plt 

#Code added to be used in optimizer code 
V_wind = 6.0  # default site wind speed (m/s) – safe for imports


def compute_lambda_optimal():
    lambda_guess = 8.5
    ERROR_TOLERANCE = 1e-6
    MAX_ITER = 20
    return newton(g_lambda, dg_dlambda, lambda_guess, ERROR_TOLERANCE, MAX_ITER)

def expected_power_MW(D, V=V_wind):
    R = D / 2.0
    lam = (Omega_r * R) / V
    Cp = calculate_Cp(lam, Omega_r, V)
    RHO_AIR = 1.225
    P = 0.5 * RHO_AIR * math.pi * (R**2) * Cp * (V**3)
    return P / 1_000_000.0

"""
I am finding the root of a function g(lambda)=0 using the newton raphson technique 
Also calculating the relative error between iterations such that the loop will stop when the gap between iterations is small enough to be approximated as the root. This is defined by the equation ((xn-xnold)/xn) the theory behind this equation is that as the newton raphson equation convergs towards the root, the 'bracket' between the two guesses gets smaller. 
this small error calculation means that once the bracket between guesses is sufficiently small the code will have found the root. this prevents excessive iterations finding an exact root.

Parameters
f : the function of lambda derived from the primary power equation for wind turbones: P = 1/2 * air density * pi * Radius of blade^2 * Cp * air velocity^3
Df : The derivative of f described above 
x0 : my initial guess for lambda 
rleative_error_tolerance : The cirteria for loop termination - once the relative error between guesses is below this value the code will stop running.
max_iter : a pre determined number of maximum iterations - I have had to select a number of 50 iterations to prevent an infinite loop. (not sure if i need this only probably need one or the other)

"""


#Implemementning Newton raphson method 
def newton(f, Df, x0, relative_error_tolerance, max_iter):
    
    #initial root guess for tts ratio based on reseach - range is 6 to 9.5, this section will also store the previous guess to input into a formula to calculate the relative error 
    xn_old = x0
    
    #loop for a maximum number of iterations
    for n in range(1, max_iter + 1):
        
        #Evaluating f(x0) and f'(x0) at the previous guess value 
        fxn_old = f(xn_old)
        Dfxn_old = Df(xn_old)
        
        #preventing my code crashing with a zero error 
        if Dfxn_old == 0:
            print('Zero derivative - No solution found')
            return None 
        
          #Using newton raphson formula to calculate the new guess 
        xn = xn_old - (fxn_old / Dfxn_old)
    
    #calculating stoping criteria based on Approximate relative error, there are two formulae here using if and else, the first deals with most cases and the  second deals with the case in which xn is exactly zero 
        if xn != 0: 
         error = abs((xn - xn_old) / xn)
        else:
         error = abs(xn - xn_old)
        
        print(f" Iteration {n}: x = {xn:.8f}, Relative error = {error:.2e}") #this print uses f string placeholders to print the output values based on the calculations
   
    #If the error is within the acceptable tolerance, the solution has been found
        if error < relative_error_tolerance:
         
            print(f" Relative error is less than error tolerance after {n} iterations -> solution found ") #maybe over the top adding an f string to present how many iterations it took to converge 
         
            return xn
    
    #Updating the old guess to continue the loop if the error has not been reached 
        xn_old = xn
    
    #secondary criteria - maximum number of iterations. If the set limit is reached wihtout a root being found the code will terminate and report failure 
    print(f"Maximum iterations {max_iter} exceeded, no solution found.")
    return None 

""" 
The code from lines 65 to 168 models the behavior of a wind turbine of radius 20.5m, this was ok for me to do as unlike the other sections of the report I am solely modelling the power output and power coefficient of the wind turrbine NOT its strength or lifetime which means using a 20.5m model values will still maintain accuracy when used to calculate values for wind turbines with longer blades 
To calculate the Power Coefficient (Cp) accurately, a BEM simulation was the only feesable option. I couldn't get a model which ran to 50m diameter however the behavior of the models is identical from radius of 20 to radius of 50 
The data below is copied directly from 'the fundamental text on wind turbine design' I have chosen to model the blades behavior using BEM theory because while it does face limitations in higher radii (r>=60m) which require correction models, more accurate methods such as computational fluid dynamics are too 'compuationally expensive' which means even if i could code that 
my mac cant run computatioonal fluid dynamics. 
There were two interesting areas in this section that required extensive research - the glauert correction for 'high axial induction' using only the simple BEM theory model gave outputs that would be initially acceptable but in comparing them to experimental values from the real world they were found to be quite inaccurate, especially in terms of power generation. 
The second was the axial induction factor, the code for this made up a significant portion of this section
"""
def get_airfoil_data(alpha_deg):
    """
    Model of airfoil data (Cl and Cd).
    """
    alpha_rad = math.radians(alpha_deg)
    if abs(alpha_deg) < 10:
        Cl = 2 * math.pi * alpha_rad
    else:
        Cl = 0 # Simplified stall in case the 'angle of attack' of the blade is over 10 degrees. angle of attack is the angle that the blade edge makes with the wind.
    Cd = 0.015
    return Cl, Cd

def calculate_Cp(lambda_value, omega_r, v_wind):
    blade_data = [
        {"r": 4.5, "twist": 20.0, "chord": 1.63}, {"r": 6.5, "twist": 13.0, "chord": 1.540},
        {"r": 8.5, "twist": 7.45, "chord": 1.420}, {"r": 10.5, "twist": 4.85, "chord": 1.294},
        {"r": 12.5, "twist": 3.15, "chord": 1.163}, {"r": 14.5, "twist": 2.02, "chord": 1.026},
        {"r": 16.5, "twist": 0.77, "chord": 0.881}, {"r": 18.5, "twist": 0.14, "chord": 0.705},
        {"r": 20.3, "twist": 0.02, "chord": 0.265} 
    ]
    R_total = 20.5
    B_num = 3
    RHO_AIR = 1.225
    total_torque = 0.0

    for i in range(len(blade_data) - 1):
        elem = blade_data[i]
        r = elem["r"]; chord = elem["chord"]
        dr = blade_data[i+1]["r"] - r
        a = 0.0; a_prime = 0.0

        for _ in range(100):
            if (1 + a_prime) * omega_r * r == 0: continue
            phi_rad = math.atan(((1 - a) * v_wind) / ((1 + a_prime) * omega_r * r))
            if phi_rad < 0: phi_rad += math.pi
            alpha_deg = math.degrees(phi_rad) - elem["twist"]
            Cl, Cd = get_airfoil_data(alpha_deg)
            Cn = Cl * math.cos(phi_rad) + Cd * math.sin(phi_rad)
            Ct = Cl * math.sin(phi_rad) - Cd * math.cos(phi_rad)
            sigma = (B_num * chord) / (2 * math.pi * r)
            f = (B_num / 2) * (R_total - r) / (r * math.sin(max(phi_rad, 0.001))) # Avoid sin(0)
            F = (2 / math.pi) * math.acos(math.exp(-min(f, 35)))
            
            #Using the Glauert correction for high a values 
            a_c = 0.2
            
            K_denom = (sigma * Cn)
            if K_denom == 0: K_denom = 1e-6 # Avoid division by zero *do not remove* code wont work
            K = (4 * F * math.sin(phi_rad)**2) / K_denom
            
            a_new_unreliable = 1 / (K + 1) if K != -1 else 0.5
            
            if a_new_unreliable <= a_c:
                 a_new = a_new_unreliable
            else:
                # Calculate the term inside the square root
                sqrt_term_content = (K*(1 - 2*a_c) + 2)**2 + 4*(K*a_c**2 - 1)
                
               # Safety net to prevent math error - if value is negative falls back on the previous simpler equation
                if sqrt_term_content < 0:
                    a_new = a_new_unreliable 
                else:
                    sqrt_term = math.sqrt(sqrt_term_content)
                    a_new = 0.5 * (2 + K*(1 - 2*a_c) - sqrt_term)
                
            a = 0.7 * a + 0.3 * a_new
            
            Ct_denom = (sigma * Ct)
            if Ct_denom == 0: Ct_denom = 1e-6
            denom = (4 * F * math.sin(phi_rad) * math.cos(phi_rad) / Ct_denom) - 1
            
            if denom == 0:
                a_prime_new = 0.0
            else:
                a_prime_new = 1 / denom

            # check for convergence using 'a' and 'a_prime'
            if abs(a - a_new) < 1e-5 and abs(a_prime - a_prime_new) < 1e-5:
                break
            
            # updating a_prime for each loop that its used 
            a_prime = 0.7 * a_prime + 0.3 * a_prime_new
        
        V_rel_sq = ((1-a)*v_wind)**2 + ((1+a_prime)*omega_r*r)**2
        p_T = 0.5 * RHO_AIR * V_rel_sq * chord * Ct
        total_torque += B_num * p_T * r * dr
    
    Area = math.pi * R_total**2
    P_avail = 0.5 * RHO_AIR * Area * v_wind**3
    return total_torque * omega_r / P_avail if P_avail > 0 else 0.0

""" 
Instead of using a really complex method for deriving my expressions for the functions G and G' I am using the mathematical formula for the derivative of a function - how much it changes over a step which is usually time 
This is essentially like changing distance to distance over time and then to acceleration 
"""

#Defining input constants such as step size, rotational speed and the radius used in the BEM model - NB this radius is not the optimal radius it is the model radius used to find cp 
step_size = 1e-5 # Middle ground testing step sizes for functions 
Radius = 20.5
Omega_r = 10.0 * (2 * math.pi /60) #I am using 10 rpm here as that is within the optimal range for an industrial wind turbine in lower wind speeds. 
    
def g_lambda(lambda_value):
    """ 
    this is the origignal function derived from the equation for power from a wind turbine
    """
    
    h = step_size
    
    #Adjusting v wind from a constant to a dynamic value 
    V_mid = (Omega_r * Radius)/lambda_value 
    V_high = (Omega_r * Radius)/(lambda_value + h)
    V_low = (Omega_r * Radius)/(lambda_value - h) 
    
    #the BEM theory model needs to be called now three times in order for the derivative to be found accurately 
    Cp_mid = calculate_Cp(lambda_value, Omega_r, V_mid)
    Cp_high = calculate_Cp(lambda_value + h, Omega_r, V_high)
    Cp_low = calculate_Cp(lambda_value - h, Omega_r, V_low)
    
    #Calculating the first derivative numerically 
    dCp_dlambda = (Cp_high - Cp_low) / (2 * h )
    
    #calculation step for g
    g = 2 * Cp_mid + lambda_value * dCp_dlambda
    return g 

def dg_dlambda(lambda_value):
    h = step_size
    
    V_mid = (Omega_r * Radius)/(lambda_value) 
    V_high = (Omega_r * Radius)/(lambda_value + h)
    V_low = (Omega_r * Radius)/(lambda_value - h) 
    
    Cp_mid = calculate_Cp(lambda_value, Omega_r, V_mid)
    Cp_high = calculate_Cp(lambda_value + h, Omega_r, V_high)
    Cp_low = calculate_Cp(lambda_value - h, Omega_r, V_low)
    
 
    #we need dCp/dlambda here aswell 
    dCp_dlambda = (Cp_high - Cp_low) / (2 * h)
    
    #doing the same for second derivative 
    d2Cp_dlambda2 = (Cp_high - 2 * Cp_mid + Cp_low) / (h**2)
    
    #Numerically calculating g'(lambda) - the derivative of g(lambda)
    dg_dlambda = 3 * dCp_dlambda + lambda_value * d2Cp_dlambda2
    return dg_dlambda

""" 
This is the final section - collating the inputs from all of the previous code to put through the newton raphson solver and to print the results for power generation and for power coefficient

"""
if __name__ == "__main__":
    
    # Design constants 
    # these calculations will use the annual average wind speed of our land based wind farm, but the BEM (blade element momentim model) theory needs to use dynamic wind values 
    V_wind = 6.0
    
    # the rotational velocity of wind turbine is set globally (across the whole code) to 10rpm which is around 1 rad/s since this is in the normal range of large wind turbines and a lower rotational velocity lowers 
    # wear on the gears, bearings etc inside of the wind turbine generator, this lengthens its life and reduces the ferquency of required visits to maintain it 
    print("Wind Turbine Power and Cp Optimization using Newton Raphson and BEM Theory")
    print(f"Annual Site Wind Speed Average: {V_wind} m/s")
    print(f"Design Rotational Speed: {Omega_r:.3f} rad/s (10 RPM)")

    # Setting constants for the newton raphson to run
    lambda_guess = 8.5   # Initial guess for the optimal tip to speed ratio 
    ERROR_TOLERANCE = 1e-6 #Calculated acceptable error - not relative error tolerance from earlier as that is a stopping term which changes as the iterations progress, this is a number for the value accuracy which I want the code to meet 
    MAX_ITER = 20      #arbitrary number just in case the relative error tolerance section didnt do its job, if i was using bisection i would use the relevant equation to calculate the number of itersations that it should take 

    # running newton raphson solver using all the setup from above 
    # Pass the numerical functions to the solver
    lambda_optimal = newton(g_lambda, dg_dlambda, lambda_guess, ERROR_TOLERANCE, MAX_ITER)
                               
                              

    # Final calculations and findings 
    if lambda_optimal is not None:
        # Calculate final radius based on the annual average wind speed for the turbine site 
        R_optimal = (lambda_optimal * V_wind) / Omega_r
        D_optimal = 2 * R_optimal
        
        # Calculate the Cp at the optimal lambda using the model's physics
        # We must use the V_wind that CORRESPONDS to lambda_optimal for the 20.5m model
        V_wind_for_optimal_Cp = (Omega_r * Radius) / lambda_optimal 
        Cp_at_optimal = calculate_Cp(lambda_optimal, Omega_r, V_wind_for_optimal_Cp)
        
        print("Optimization successs")
        print(f"Optimal Tip-Speed Ratio: {lambda_optimal:.4f}")
        print(f"Max Power Coefficient at this TTS: {Cp_at_optimal:.4f}")
        print(f"Optimal Rotor Radius: {R_optimal:.2f} m")
        print(f"Optimal Rotor Diameter: {D_optimal:.2f} m")
    else:
        print("\nOptimization failed. Could not find a solution.")


"""
Creating a plot of the results (Power against radius, Cp vs Lambda) as long as the root has been found
"""

#First plot: Power generated against radius
#radius range is from 10m to 65m
radius_range = np.linspace(10, 65, 50) # 50 points from 10m to 65m
power_values = []
RHO_AIR = 1.225 #air density at sea level 
        
print("Calculating Power-Radius plot ")
for R in radius_range:
    # Final values for Lambda are calculated using the standard formula 
    Lambda_final = (Omega_r * R) / V_wind
    
    
    # Avoid division by zero if Lambda_final is 0
    V_wind_for_model = 0.0
    if Lambda_final > 1e-6:
        V_wind_for_model = (Omega_r * Radius) / Lambda_final # 'Radius' is 20.5
    
    # Get the Cp for this tip-speed ratio (Lambda_final)
    Cp = calculate_Cp(Lambda_final, Omega_r, V_wind_for_model)

   #Calculating power for the wind turbine at the given avrage wind velocity, and the found coefficient of performance value 
    power = 0.5 * RHO_AIR * math.pi * (R**2) * Cp * (V_wind**3)
    power_values.append(power / 1_000) # Convert power to Kilowatts 
            
plt.figure(2)        
plt.plot(radius_range, power_values, 'g-', label='Estimated Power')
plt.axvline(x=R_optimal, color='r', linestyle='--', label=f'Optimal Radius is ({R_optimal:.2f} m)')
plt.title(f'Power vs Blade Radius at wind speed {V_wind} m/s')
plt.xlabel('Blade Radius (m)')
plt.ylabel('Power (kW)')
plt.grid(True)
plt.legend()
plt.savefig('Power_vs_Radius.png')
print("Saved 'Power_vs_Radius.png'")

if lambda_optimal is not None:
    print("Plotting Cp vs Lambda & Power vs radius")
    
    #second plot - Cp vs lambda - I am actually modelling this using values from a paper (cited in report) which has a corresponding graph of power vs radius and cp vs lambda which allows me to check the shape of the graphs against those in the text cited. 
    #the graph in the text 'the aerodynamics of wind turbines' is attached in the report, this plot will allow us to check the final values against those found by other researchers
    #value range
    Lambda_values = np.linspace(1,15,50)  
    Cp_values = []
    
    for Lambda in Lambda_values:
        V_wind_dynamic = (Omega_r * Radius) / Lambda
        Cp = calculate_Cp(Lambda, Omega_r, V_wind_dynamic)
        Cp_values.append(Cp)
        
        
    plt.figure(1)
    plt.plot(Lambda_values, Cp_values, 'b-', label='Cp (BEM Model)')
    plt.axvline(x=lambda_optimal, color='r', linestyle='--', label=f'Optimal Lambda ({lambda_optimal:.2f})')
    plt.title('Power Coefficient (Cp) vs Tip-Speed Ratio (Lambda)')
    plt.xlabel('Tip-Speed Ratio (Lambda)')
    plt.ylabel('Power Coefficient (Cp)')
    plt.grid(True)
    plt.legend()
    plt.savefig('Cp_vs_Lambda.png')
    print("Saved 'Cp_vs_Lambda.png'")
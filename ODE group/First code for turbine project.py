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
deflection_results: list[list[float]] = []

#define other input variables
E: int = 210e9  # Young's modulus for steel 
cd: float = 1.28  # Drag coefficient for a flat plate perpendicular to flow
density_air: float = 1.225  # Density of air in kg/m^3

# Define list fo blade lengths to be tested, realistic range based on model chosen
blade_lengths = list(range(50, 120, 1))  # Turbine blade diameters from 20m to 100m in 1m increments
    
# Function to compute drag forces for all diameters at a given wind speed
def drag_force(blade_lengths: list, wind_speed: float, cd: float=1.28, density_air:float =1.225, width: int=1) -> list:
    drag_force_list = []  # Initialize an empty list to store drag forces
    for i in blade_lengths:
        area = i * width
        f = 0.5 * cd * density_air * area * wind_speed ** 2
        drag_force_list.append(f)
    return drag_force_list

# Function to compute deflectiion for all diameters at a given wind speed
def deflection(blade_lengths, wind_force, E = 210e9, width = 1, height = 2):
    tip_deflection = [] 
    for i, w in zip(blade_lengths, wind_force):
        I = (width * height ** 3) / 12  # Moment of inertia for a rectangular cross-section
        ''' 
        This is found from ODE of bending beam with distributed load
        d^2y/dx^2 * EI = (w*(L-x)^2/2)
        dy/dx * EI = (w*(L-x)^3/6) + C1
        y * EI = (w*(L-x)^4/24) + C1*x + C2
        Applying boundary conditions at x = L (y=0, dy/dx=0) to solve for C1 and C2
        C1 = 0, C2 = 0
        '''
        y = (w * i ** 4 ) / (8 * E * I)
        tip_deflection.append(y)
    return tip_deflection

# Compute forces for min, avg, and max wind speeds
for i in velocityDict:
    drag_force_results.append(drag_force(blade_lengths, velocityDict[i]))
    deflection_results.append(deflection(blade_lengths, drag_force_results[-1]))

#Print formatted results
for i, yL, yG, yM, yF, yS, yNG, ySG in zip(blade_lengths, deflection_results[0], deflection_results[1], deflection_results[2], deflection_results[3], deflection_results[4], deflection_results[5], deflection_results[6]):
    print(f"Diameter: {i} m, yL: {yL:.3g} m, yG: {yG:.3g} m, yM: {yM:.3g} m, yF: {yF:.3g} m, yS: {yS:.3g} m, yNG: {yNG:.3g} m, ySG: {ySG:.3g} m")
    

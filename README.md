# Optimising Wind Turbine Rotor Diameter Against Structural Deflection

## Table of Contents
- [Overview](#overview)
- [Project Objectives](#project-objectives)
- [Background](#background)
- [Methodology](#methodology)
- [Tools & Technologies](#tools--technologies)
- [Results](#results)
- [How to Run](#how-to-run)
- [Contributors](#contributors)

---

## Overview

In the UK, the largest onshore windfarm is Whitelee Windfarms located on Eaglesham Moor, with a current number of 215 turbines generating up to 539 megawatts of electricity, enough to power over 350,000 homes. Considering cost of the turbine and their lifespan, quality design would optimize the kW/year the turbine produces with minimal cost, aiming to produce profit within 2-5 years, theoretically, this can be done by increasing its diameter. However, being located in Eaglesham Moor, turbines are subject to strong gales of up to 46.5-54.8MPH especially during winter, and this leads to potential problems of strain of the turbine blades causing fatigue failure over time, which could shorten a turbines lifespan, or cause increased expenses for maintenance. 

This project aims to solve the question **for a Gamesa 2.3 93 wind turbine operating in Whitelee Wind Farm, what is the optimised diameter of the turbine blades, producing max power whilst considering material cost and tip deflection?** 

---

## Project Objectives
- Identify relationship between cost of turbine and blade lengths
- Predict tip deflection using ordinary differential equations for different wind speeds
- Identify optimal lengths of blades within safe limits, maximising power output and minimising cost
- Produce visualisations and documented findings.

---

## Background
A Gamesa wind turbine has three blades, with swept diameters ranging from 50-135m in length. If we isolate our problem, when wind hits our blade at a certain wind speed, the force against the wind turbine’s blades will be drag force. Assuming the wind directly hits the blade in its perpendicular form, this can be modelled as a linearly increasing distributed load across the entire blade. As the blade rotates from this wind speed, we then have a rotational force acting on the blade. Both rotational force and drag force are the primary causes of strain in our scenario. Hence this program aims to model these loads on the blade to find the deflection, and identify when lengths are within a safe limit.

## Methodology
First we identified the inputs that will be used to run this program. This can be adjusted depending on different industry needs. For Whitelee Wind Farms we have used the following inputs:
  - Range of wind speeds from given location (Eaglesham)  
  - Air density   
  - Material --> glass fibre reinforced polymer with carbon fibre
  - Range of lengths of the turbine blade (40-70m) 
  - Max deflection allowed, safety factor = 1.5 (for reasonable result checking)
Then we made some assumptions and simplified the turbine model, finding appropriate governing equations that would be used for solving this problem. The key simplifications we made were, treating the turbine blades as having a **rectangular shape**, instead of an airfoil. This choice allows us to apply beam theory to computing the behavior of the blade, which is a computationally light and efficient method, well suited for optimization of practical procedures. **Euler Bernouilli Beam Theory** was used to compute the beam deflection, with **fluid drag force** equations and **rotational drag force** equations being used as the load on the beam. Another assumption we made was that the **wind will only be hitting the blades directly**, as this would produce the greatest deflection, which is the goal. 

Then we employed reasonable numerical methods to go about solving this problem which are given in greater depth in tools and technologies section. Finally once output data for deflections, optimal power output and cost graphs were generated, a combined performance-to-cost metric was used to optimise diameter. This diameter represents the best balance between aerodynamic performance, structural reliability, and manufacturing cost. 


## Tools and Technologies
**ODE SECTION**
Three distributed loads were modelled, each defined so that their computed values align elementwise with the blade
length array. Wind drag load (drag_load/rl): a uniform transverse load derived from drag coefficient, air density, and 
wind velocity. A list with the same length as the blade-length array is generated, so each blade length receives its own value. Gravity load (grav_load/b): a uniform downward load based on mass-per-unit-length and gravity, again returned as an array matching the blade-length index. Rotational aerodynamic load (rot_load/ar): a length-dependent load computed using a rotation speed derived from the chosen tip-speed ratio and wind velocity. Because it depends on 
each blade radius, a unique value is produced for every entry in the blade-length array. 
Then the solver factory (solve_tip_deflection_for_length) is defined. Inside the solver factory, the fourth-order beam 
equation is rewritten as a system of four first-order equations representing the deflection, the slope, the curvature, and the rate of change of curvature (y’, y’’, y’’’, y’’’’). This allows solve_bvp to integrate the problem. The cantilever boundary conditions are encoded as a four-value vector: zero deflection and zero slope at the root, and zero curvature and zero shear at the tip. Returning these four results together lets the solver enforce all conditions at once and keeps the method general for any load distribution. After this we define the ODEs and pump the blade length list into it in the results section. Additionally, the solver includes a built-in adaptive fallback: if the first attempt fails to converge, the routine regenerates a finer mesh and retries before raising an error. A dedicated verification function (_sanity_check_tip_deflection) then checks numerical stability, compares each BVP result with the analytic solution, and ensures the small-deflection assumptions remain valid. For each blade length, the solver is applied twice—once for bending in the plane of gravity and rotation, and once for bending due to wind drag—before combining both components into a final tip deflection.

**ROOT FINDING SECTION**
The Root finding method chosen was Newton Raphson. Through research it was found that the functions  
associated with this topic – Cp and Power – required complex inputs and their graphs could be quite erratic and the 
full calculations to model and run the wind turbine would be slow. Therefore bracketing methods (false position and 
Linear Bisection) with a ‘guaranteed convergence’ were attractive to me but due to the possible long run times and the 
trial and error nature of figuring out new code from research they were unsuitable. Open root finding methods were 
found to be the key as they are quicker and more robust; my choices were between Inverse quadratic interpolation and 
Newton Raphson, the former relies heavily on the initial three guesses and since the BEM model can output extremely 
similar values of Cp at different values of tip to speed ratio there was a stronger possibility of errors and a lot more troubleshooting. Ultimately I chose Newton Raphson due to its robustness,  relative simplicity and ease of working.

**REGRESSION SECTION**
Polynomial regression is a regression technique that models the relationship between the independent variable (in this 
case blade length), and the dependent variable (total cost) as an nth-degree polynomial. It allows fitting of non-linear relationships, which in the real world, is more appropriate than a simple linear model. Initially a .csv was created, this contained data related to the cost of producing a blade of differing lengths. Blade geometry and volume scaling, glass vs carbon fractions, structural strengthening for relevant blade sizes, material cost, mold, and tooling cost, additional-piece mold for larger blades, handling cost, jigs and QA cost, tooling amortization and total blade cost were used to estimate the cost of each blade. Subsequently, a 2nd order polynomial regression was created with the help of the sklearn library. Conclusively, the two py’s output a blade cost.csv and a polynomial regression fitted to the .csv data. 

## Results
This code should output the following. 
  - Power generated at different blade diameters  
  - Deflection produced at different blade lengths and corresponding wind speed 
  - Blade lengths vs cost graph 
  - Safe/Not safe check for each length tested 
  - A recommended best optimised diameter for chosen system

The design analysis combined aerodynamic modelling, cost estimation, and structural safety checks to determine a 
balanced optimal turbine diameter. Although the BEM aerodynamic model predicted maximum power at 124.58 m, 
both the deflection model and cost model showed that such a size is not suitable for onshore use. After applying the 
deflection limit and considering the cost–performance trade-off, the final chosen diameter was 90.5 m (45.25 m blade).

## How to Run
First, the user must define the inputs they will be using based on the real world simulation. This code requires a user input the following:

For the cost graph
- range of blade lengths to be trialled
- material of the turbine blade (cost per unit volume)

For the deflection calculation
- wind speeds in the area chosen
- range of blade lengths to be trialled
- material of the turbine blade (elastic modulus)
- guessed dimensions of the turbine blade 
- safety factor for deflections to determine safe or unsafe blade lengths

In each section of the code, these inputs can be adjusted and included as variables. From there, the code can simply be run and expected data will be outputed, a list of deflections for corresponding blade lengths and wind speeds for ODE section, and graphs for regression and root finding section.  


## Contributors
JeannieLeung - Jeannie Leung
UOEATP - Alex Patton
Magnus-Heidenreich - Magnus Heidenreich
pwei818 - Peggie Wei
TomChadEDIN - Tom Chad
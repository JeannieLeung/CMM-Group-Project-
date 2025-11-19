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

This projects investigates **for a Gamesa 2.3 93 wind turbine operating in Whitelee Wind Farm, what is the optimised diameter of the turbine blades, producing max power whilst considering material cost and tip deflection?** 

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



## Tools 

## Results

## How to Run

## Contributors

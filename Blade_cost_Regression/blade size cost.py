import numpy as np
import pandas as pd

# Parameters
diameters = np.arange(50, 136, 1)   # 50–135 m
num_blades = 3
production_volume_turbines = 50
blades_total_produced = production_volume_turbines * num_blades

# Material cost (£/m³)
C_glass = 1500.0    # £/m³ (slightly cheaper)
C_carbon = 12000.0  # £/m³ (reduced for realistic scaling)

# Initial model
def blade_volume(L):
    # Reduced scaling factor to match realistic volumes (hundreds of m³)
    return 12.0 * (L / 50.0)**2.4

# Initial carbon fraction
def base_carbon_fraction(L):
    if L <= 25:
        return 0.10
    elif L >= 70:
        return 0.40
    else:
        return 0.10 + (L - 25) * (0.30 / (70 - 25))

# Structural adjustment for larger blades
def structural_strengthening(L):
    extra_carbon = 0.0
    volume_mult = 1.0
    if L > 60:
        extra_carbon += 0.005 * (L - 60) / 10.0  
        volume_mult += 0.0015 * (L - 60)
    return volume_mult, extra_carbon

# Tooling cost model (scaled down)
def tooling_cost_components(L,
                            base_mould_cost=150_000.0,
                            mould_size_growth_factor=0.0003,
                            two_piece_threshold=60.0,
                            two_piece_multiplier=2.0,
                            handling_base_per_blade=3_000.0,
                            handling_growth_per_m=40.0,
                            dedicated_jig_base=30_000.0,
                            qa_rig_base=15_000.0):
    mould_factor = 1.0 + mould_size_growth_factor * (L - 50.0)**2
    mould_cost = base_mould_cost * mould_factor
    if L >= two_piece_threshold:
        mould_cost *= two_piece_multiplier

    handling_cost_per_blade = handling_base_per_blade + handling_growth_per_m * (L - 50.0)
    additional_fixed = dedicated_jig_base + qa_rig_base
    tooling_fixed_design_cost = mould_cost + additional_fixed

    return tooling_fixed_design_cost, handling_cost_per_blade

def amortized_tooling_per_blade(L, production_volume_blades=blades_total_produced):
    tooling_fixed, handling_per_blade = tooling_cost_components(L)
    amortized_fixed_per_blade = tooling_fixed / max(1, production_volume_blades)
    per_blade_tooling = amortized_fixed_per_blade + handling_per_blade
    return per_blade_tooling

# Support complexity multiplier
def support_multiplier(L, base=1.0, growth=0.004):
    return base + growth * L

# Cost model function
def deterministic_blade_cost(L, production_blades=blades_total_produced):
    V_base = blade_volume(L)
    volume_mult, extra_c = structural_strengthening(L)
    V = V_base * volume_mult

    f_carbon_base = base_carbon_fraction(L)
    f_carbon = min(max(f_carbon_base + extra_c, 0.0), 1.0)

    C_mat = f_carbon * C_carbon + (1 - f_carbon) * C_glass

    sup_mult = support_multiplier(L)

    material_structural_cost = V * C_mat * sup_mult
    tooling_amort_per_blade = amortized_tooling_per_blade(L, production_volume_blades=production_blades)
    total_cost = material_structural_cost + tooling_amort_per_blade

    return {
        "Diameter_m": 2 * L,
        "BladeLength_m": L,
        "Volume_m3": V,
        "CarbonFraction": f_carbon,
        "MaterialCostPer_m3_£": C_mat,
        "MaterialStructuralCost_£": material_structural_cost,
        "ToolingAmortPerBlade_£": tooling_amort_per_blade,
        "TotalCost_£": total_cost
    }

# Table 
def compute_table(diameters):
    data = []
    for D in diameters:
        L = D / 2.0
        data.append(deterministic_blade_cost(L))
    df = pd.DataFrame(data)
    return df

# Main 
if __name__ == "__main__":
    df = compute_table(diameters)
    pd.options.display.float_format = "{:,.0f}".format
    print(df.head(8))
    print(df.tail(8))
    df.to_csv("blade_costs.csv", index=False)
    print("Saved blade_costs.csv")

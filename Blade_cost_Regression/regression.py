import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Load CSV
df = pd.read_csv(r"C:\Users\Alexander Patton\OneDrive - University of Edinburgh\YR 3\Professional issues\CMM-Group-Project-\Blade_cost_Regression\blade_costs.csv")

# (X) and (y) variables
X = df["BladeLength_m"].values.reshape(-1, 1)
y = df["TotalCost_£"].values

# Polynomial regression 
degree = 2
poly = PolynomialFeatures(degree=degree)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)

# R²
y_pred = model.predict(X_poly)
r2 = r2_score(y, y_pred)

# Regression equation
coeffs = model.coef_
intercept = model.intercept_

terms = [f"{coeffs[i]:.3e}*x^{i}" if i > 0 else f"{intercept:.3e}" for i in range(len(coeffs))]
equation = " + ".join(terms)
print("\nPolynomial Regression Equation (degree = {}):".format(degree))
print("y =", equation)
print(f"\nR² = {r2:.4f}")

# Plot
plt.figure(figsize=(8,6))
plt.scatter(X, y, color="blue", label="Data")
x_plot = np.linspace(X.min(), X.max(), 300).reshape(-1,1)
y_plot = model.predict(poly.transform(x_plot))
plt.plot(x_plot, y_plot, color="red", linewidth=2, label="Polynomial Fit")
plt.xlabel("Blade Length (m)")
plt.ylabel("Total Cost (£)")
plt.title(f"Polynomial Regression (degree = {degree})\nR² = {r2:.4f}")
plt.legend()
plt.grid(True)
plt.show()

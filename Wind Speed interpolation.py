#importing modules
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate 
import math
import random

mph = [6.3, 8.6, 6.5, 5.9, 5.6, 6.1, 5.4, 5.5, 5.2, 6.6, 5.8, 7]
mph_max = [14.4, 16.8, 14.1, 13.6, 12.6, 13, 12, 12.6, 12.3, 13.8, 13.3, 15]
mps = [i/2.237 for i in mph]
mps_max = [j/2.237 for j in mph_max]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

x = np.arange(len(months))
y = np.array(mps)
y_2 = np.array(mps_max)
interpolate = scipy.interpolate.splrep(x,y,k=3)
x_new = np.linspace(0, len(months)-1, 31)
z = scipy.interpolate.splev(x_new,interpolate)
interpolate_max = scipy.interpolate.splrep(x,y_2,k=3)
z_2 = scipy.interpolate.splev(x_new,interpolate_max)
y_min = 0
y_max = max(mps_max) + 1

plt.scatter(x,y, label = 'average wind - given')
plt.plot(x_new,z, label = 'average wind - interpolated')
plt.scatter(x, y_2, label = 'max wind - given')
plt.plot(x_new, z_2, label = 'max speed - interpolated')
plt.legend()
plt.title('Annual Wind Forecast at Whitelee Wind Farm')
plt.xticks(ticks=x, labels=months)
plt.xlabel('Month')  
plt.yticks(np.arange(y_min, y_max, 1))
plt.ylabel('Wind Speed (m/s)')
plt.grid(True)
plt.savefig('Wind Interpolation Annual')

interpolated_average = np.array(z)
interpolated_max = np.array(z_2)
print(interpolated_average)
print(interpolated_max)
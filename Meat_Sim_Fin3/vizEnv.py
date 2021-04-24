from pyMCDS import pyMCDS
import numpy as np
import matplotlib.pyplot as plt
 
# load data
mcds = pyMCDS('output00000500.xml', './')
 
# Set our z plane and get our substrate values along it
z_val = 0.00
plane_oxy = mcds.get_concentrations('oxygen', z_slice=z_val)
 
# Get the 2D mesh for contour plotting
xx = mcds.get_mesh()[0]
yy = mcds.get_mesh()[1]
print(len(xx))
 
# We want to be able to control the number of contour levels so we
# need to do a little set up
num_levels = 21
min_conc = plane_oxy.min()
max_conc = plane_oxy.max()
my_levels = np.linspace(min_conc, max_conc, num_levels)

# set up the figure area and add data layers
ax = plt.subplot()
fig = ax.figure
cs = ax.contourf(xx[:,:,0], yy[:,:,0], plane_oxy, levels=my_levels)
ax.contour(xx[:,:,0], yy[:,:,0], plane_oxy, color='black', levels = my_levels,linewidths=0.5)
 
# Now we need to add our color bar
cbar1 = fig.colorbar(cs, shrink=0.75)
cbar1.set_label('mmHg')
 
# Let's put the time in to make these look nice
ax.set_aspect('equal')
ax.set_xlabel('x (micron)')
ax.set_ylabel('y (micron)')
ax.set_title('oxygen (mmHg) at t = {:.1f} {:s}, z = {:.2f} {:s}'.format(mcds.get_time(),mcds.data['metadata']['time_units'],z_val,mcds.data['metadata']['spatial_units']))
plt.show()
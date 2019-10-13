import os
import geopandas
import numpy as np
import copy
import math
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import scipy.interpolate

###############################
# Inputs

# Number points in meshgrid
Nmesh = 300

# Maximum travel time (min)
tmax = 130

# Colormap
colormap = 'rainbow'

# Plot data points
pltpoints = True

# Coastline data
coastdata = os.path.join(os.getcwd(),'data','coastline',
                     'zealand_amager.shp')

###############################
# Main script

# Data path
dpath = os.path.join(os.getcwd(),'data')

# Load coastlines
print('Loading coastline data ...')
longlatcoasts = geopandas.read_file(coastdata)

# Import travel data
fname = 'traveldata.csv'
print("Loading '" + fname +  "' ...")
traveldata = np.loadtxt(os.path.join(dpath,fname),delimiter=',')
x = traveldata[:,1]
y = traveldata[:,0]
z = traveldata[:,2]

# Limits for latitudes and longitudes
latlim = [min(y), max(y)]
longlim = [min(x), max(x)]

# Make meshgrid
lats = np.linspace(latlim[0],latlim[1],Nmesh)
longs = np.linspace(longlim[0],longlim[1],Nmesh)
longmesh, latmesh = np.meshgrid(longs, lats)

# Interpolate travel data
print("Interpolating data ...")
rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
Z = rbf(longmesh, latmesh)

# Loop through points to find cut coastlines
print("Cropping overlay ...")
for ii in range(len(longs)):
    for jj in range(len(lats)):
        point = Point(longs[ii], lats[jj])

        # Check if any polygon contains point
        contains = 0
        for ll in range(len(longlatcoasts)):
            contains ^= longlatcoasts.iloc[ll][3].contains(point)

        # Fill with nan if point is outside
        if not contains:
             Z[jj,ii] = np.nan

# Transparency in colormap (nan values)
transp_cmap = copy.copy(plt.cm.get_cmap(colormap))
transp_cmap.set_bad(alpha=0)

# Maximum level
#maxlvl = int(math.ceil(np.nanmax(z) / 10.0)) * 10 + 10

# Plot
print("Plotting overlay ...")
fig = plt.figure()
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
plt.contourf(longmesh,latmesh,Z,levels=np.arange(0,tmax,10),
             cmap=transp_cmap)
plt.xlim(longlim)
plt.ylim(latlim)
fig.set_size_inches(Nmesh/100,Nmesh/100)
 
# Save plot to file
print("Saving overlay ...")
plt.savefig(os.path.join(dpath,'overlay.png'), dpi=1000,transparent=True,
            bbox_inches=0,pad_inches=0)
plt.close()

# Plot data points
print('Plotting data points')
if pltpoints:
    plt.figure()
    plt.contourf(longmesh,latmesh,Z,levels=np.arange(0,tmax,10),
             cmap=transp_cmap)
    cbar =plt.colorbar()
    cbar.ax.set_ylabel('Travel time (min)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.xlim(longlim)
    plt.ylim(latlim)
    plt.scatter(x, y,s=0.5,marker='.',color='k')
    plt.savefig(os.path.join(dpath,'datapoints.pdf'))
    plt.show()
print("Done!")

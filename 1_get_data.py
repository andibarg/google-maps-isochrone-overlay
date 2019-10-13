import os
import geopandas
import numpy as np
import googlemaps
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from datetime import datetime
import time
import re

###############################
# Inputs

# Destination coordinates (lat, long)
destination = (55.6783,12.5864)

# Grid corners coordinates (lat, long)
corner1 = (55.86484,12.0726363)
corner2 = (55.550041,12.6874933)

# Grid resolution (lat, long)
resolution = (0.0025, 0.005)

# Arrival time (yyyy, m, d, h, m)
arrivaldate = datetime(2019, 10, 21, 9, 0)

# Travel mode ('bicycling', 'driving', 'transit', 'walking')
travelmode = "transit"

# Time delay between queries (s)
dt = 0.1

# Text file with google maps API key
apipath = 'apikey.txt'

# Coastline data
coastdata = os.path.join(os.getcwd(),'data','coastline',
                     'zealand_amager.shp')

###############################
# Functions

# Convert time string to minutes
def timestr2int(timestr):
    # Find and convert hours
    hours = re.findall('\d+ hour', timestr)
    if len(hours) == 0:
        hours = 0
    else:
        hours = int(hours[0][:-5])
        
    # Find and convert minutes
    mins = re.findall('\d+ min', timestr)
    if len(mins) == 0:
        mins = 0
    else:
        mins = int(mins[0][:-4])

    # Total time in min
    return hours*60 + mins

###############################
# Main script

# Data path
dpath = os.path.join(os.getcwd(),'data')

# Load coastlines
print('Loading coastline data ...')
longlatcoasts = geopandas.read_file(coastdata)

# Load API key
with open(apipath) as f:
    api_key = f.readline()
    f.close

# Googlemaps sign in
gmaps = googlemaps.Client(key=api_key)

# Create data file
fname = 'traveldata.csv'
np.savetxt(os.path.join(dpath,fname),[],header='lat,long,time(min)')

# Grid coordinates
lats = np.arange(corner1[0],corner2[0],
                 np.sign(corner2[0]-corner1[0])*resolution[0])
longs = np.arange(corner1[1],corner2[1],
                 np.sign(corner2[1]-corner1[1])*resolution[1])

# Loop
print('Collecting data. Press ctrl+c to stop...')
for ii, long in enumerate(longs):
    for jj, lat in enumerate(lats):
        # Print progress
        print('%i/%i' %(ii*len(lats)+jj,len(lats)*len(longs)))
        
        # Check if any polygon contains origin
        point = Point(long, lat)
        contains = 0
        for ll in range(len(longlatcoasts)):
            contains ^= longlatcoasts.iloc[ll][3].contains(point)
        if not contains:
            continue

        # Query google maps
        direction_result = gmaps.directions('%.6f,%.6f' %(lat,long),
                                    '%.6f,%.6f' %(destination[0],destination[1]),
                                    mode=travelmode,
                                    arrival_time=arrivaldate)

        # Pause
        time.sleep(dt)

        if len(direction_result) == 0:
            continue

        # Extract travel time
        timestr = direction_result[0]['legs'][0]['duration']['text']
        T = timestr2int(timestr)

        # Append row to file
        with open(os.path.join(dpath,fname),'a') as fd:
            fd.write('%.6f,%.6f,%i\n'%(lat,long,T))

print('Done!')

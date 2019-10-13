import os
import numpy as np

###############################
# Inputs

# Map title
title = 'overlayongmap'

# Zoom level
zoom = 10

# Opacity of map
opacity = 0.5

# Text file with google maps API key
apipath = 'apikey.txt'

###############################
# Main script

# Data path
dpath = os.path.join(os.getcwd(),'data')

# Import travel data
fname = 'traveldata.csv'
print("Loading '" + fname +  "' ...")
traveldata = np.loadtxt(os.path.join(dpath,fname),delimiter=',')
x = traveldata[:,1]
y = traveldata[:,0]
z = traveldata[:,2]

# Set center and bounds
center = (np.mean(y), np.mean(x))
bounds_dict = {
          'north': max(y),
          'south': min(y),
          'east': max(x),
          'west': min(x)
        }

# Limits for latitudes and longitudes
latlim = [min(y), max(y)]
longlim = [min(x), max(x)]

# Load API key
if apipath:
    with open(apipath) as f:
        apikey = f.readline()
        f.close
else:
    apikey=None

# Path to over lay image
overlay_path = 'overlay.png'

#####
# The following code is partly copied from the 'gmplot' package:
# https://github.com/vgm64/gmplot

# Create html file
print("Writing html file ...")
f = open(os.path.join(dpath,'overlayongmap.html'), 'w')
f.write('<html>\n')

# Write header
f.write('<head>\n')
f.write(
    '<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
f.write(
    '<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>\n')
f.write('<title>%s</title>\n' % title)
if apikey:
    f.write('<script type="text/javascript" src="https://maps.googleapis.com/maps/api/'+
            'js?libraries=visualization&sensor=true_or_false&key=%s"></script>\n' % apikey )
else:
    f.write('<script type="text/javascript" src="https://maps.googleapis.com/maps/api/'+
            'js?libraries=visualization&sensor=true_or_false"></script>\n' )
f.write('<script type="text/javascript">\n')
f.write('\tfunction initialize() {\n')

# Write Map
f.write('\t\tvar centerlatlng = new google.maps.LatLng(%f, %f);\n' %
        (center[0], center[1]))
f.write('\t\tvar myOptions = {\n')
f.write('\t\t\tzoom: %d,\n' % zoom)
f.write('\t\t\tcenter: centerlatlng,\n')
f.write('\t\t\tmapTypeId: google.maps.MapTypeId.ROADMAP\n')
f.write('\t\t};\n')
f.write(
    '\t\tvar map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);\n')
f.write('\n')

# Write ground overlay
bounds_string = 'var imageBounds = {'
bounds_string += "north:  %.4f,\n" % bounds_dict['north']
bounds_string += "south:  %.4f,\n" % bounds_dict['south']
bounds_string += "east:  %.4f,\n" % bounds_dict['east']
bounds_string += "west:  %.4f};\n" % bounds_dict['west']

# Set boundaries
f.write(bounds_string)
f.write('var groundOverlay;' + '\n')
f.write('groundOverlay = new google.maps.GroundOverlay(' + '\n')
f.write('\n')
f.write("'" + overlay_path + "'," + '\n')
f.write('imageBounds, {opacity: %f});' %opacity + '\n')
f.write('groundOverlay.setMap(map);' + '\n')

# Finish up
f.write('\t}\n')
f.write('</script>\n')
f.write('</head>\n')
f.write(
    '<body style="margin:0px; padding:0px;" onload="initialize()">\n')
f.write(
    '\t<div id="map_canvas" style="width: 100%; height: 100%;"></div>\n')
f.write('</body>\n')
f.write('</html>\n')
f.close()

print("Done!")

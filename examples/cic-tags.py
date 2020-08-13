import sys
import time
import arena

arena.init("oz.andrew.cmu.edu", "realm", "cic-tags")

# Draw origin cube
rotation = (0.0, 0.0, 0.0, 0.0)
scale = (0.15, 0.02, 0.15)
color = (255, 0, 0)
location = (0, 0, 0)
objName = 'originCube'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

# Draw April tag locations
# location = (1.079, 0.789, 0.071)
# rotation = (0.0, 0.0, 0.0, 0.0)
# scale = (0.15, 0.15, 0.02)
# color = (0, 255, 0)
# arena.Object(location=location, rotation=rotation, scale=scale, color=color)

location = (-0.005500, 0.002750, -0.002000)
rotation = (-0.710485, -0.008524, 0.012173, 0.703555)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagA'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-20.191750, 1.403500, 3.938750)
rotation = (-0.005390, 0.758753, -0.005104, 0.651336)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagB'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-3.767750, 1.534000, 1.625250)
rotation = (0.003748, -0.998965, -0.000873, 0.045319)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagC'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (4.124250, 1.487250, -5.553500)
rotation = (0.999917, 0.002296, -0.012655, 0.000044)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagD'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-5.225000, 4.475750, -6.038750)
rotation = (0.658342, -0.000186, -0.752719, 0.000018)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagE'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-20.186250, 5.746750, 4.056000)
rotation = (0.000458, 0.755081, 0.004921, 0.655613)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagF'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-3.074750, 5.578250, 7.672750)
rotation = (-0.001083, -0.999979, 0.000962, 0.006395)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagG'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (3.596750, 5.615500, -5.547750)
rotation = (0.004928, 0.014041, -0.006135, 0.999870)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagH'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-2.371000, 5.494500, -13.388500)
rotation = (-0.001692, 0.708911, -0.004435, 0.705282)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagI'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (4.122000, 5.204500, 5.359000)
rotation = (0.000018, -0.003861, -0.999977, 0.005548)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagJ'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (1.382000, 5.278250, 13.796250)
rotation = (0.003899, 0.992195, 0.000470, 0.124637)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagK'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (4.833750, 9.835500, -5.551250)
rotation = (0.000964, -0.001278, -0.000611, 0.999999)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagL'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-6.628392, 9.819152, -7.048774)
rotation = (0.001128, 0.737325, 0.000576, 0.675537)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagM'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-3.960250, 10.030750, 1.674500)
rotation = (-0.003218, -0.998090, -0.002082, 0.061650)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagN'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-20.171250, 10.002500, 4.225500)
rotation = (-0.005580, 0.751748, 0.003681, 0.659417)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagO'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-6.569750, 9.584500, 5.383000)
rotation = (0.008366, -0.997227, -0.001253, 0.073939)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagP'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-29.257500, 9.833000, 5.143250)
rotation = (0.018251, 0.755837, 0.015634, 0.654318)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagQ'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-13.738250, 9.860750, 6.136500)
rotation = (-0.005237, 0.758151, 0.001397, 0.652056)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagR'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-19.759750, 10.081500, 8.857250)
rotation = (-0.001817, 0.758261, -0.003394, 0.651939)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagS'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

location = (-16.933750, 8.415750, 7.829250)
rotation = (0.707398, 0.049648, -0.034485, 0.704226)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
objName = 'tagT'
arena.Object(objName=objName, location=location,
             rotation=rotation, scale=scale, color=color)

print("View scene at URL: https://xr.andrew.cmu.edu/?scene=cic-tags")
print("Note, tags set with persist so open browser before running.")

arena.handle_events()

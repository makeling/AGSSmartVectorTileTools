# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-11-29
# Update Time :
# Change Log  :
##      1.
##      2.
##      3.

import time
import arcpy
import math

def express_arcpy_error():
    severity = arcpy.GetMaxSeverity()
    if severity == 2:
        # If the tool returned an error
        arcpy.AddError("Error occurred \n{0}".format(arcpy.GetMessages(2)))
    elif severity == 1:
        # If the tool returned no errors, but returned a warning
        arcpy.AddWarning("Warning raised \n{0}".format(arcpy.GetMessages(1)))
    else:
        # If the tool did not return an error or a warning
        arcpy.AddMessage(arcpy.GetMessages())

# Description: Loop layers and calculate lod for every feature in the layer.
def calculate_lods_for_feature(in_layers, fieldName):
    try:
        startTime = time.time()
        timeStampName = time.strftime('%Y_%m_%d %H:%M:%S', time.localtime(time.time()))
        arcpy.AddMessage("Start compute lods at: {0}".format(timeStampName))

        for layer in in_layers:
            arcpy.AddMessage("Calculating lod for layer : {0}.".format(layer))
            add_field(layer, fieldName, 9)
            cursor = arcpy.da.UpdateCursor(layer, ['SHAPE@', 'OID@', fieldName])
            lyr_path = layer.dataSource

            desc = arcpy.Describe(lyr_path)
            extent = desc.extent
            arcpy.AddMessage("Original dataset extent:" + str(desc.extent))
            ext_wm = extent.projectAs(arcpy.SpatialReference(102100))
            arcpy.AddMessage("New WebMercator extent:" + str(ext_wm))
            start_level, start_compute_resolution = confirm_level(ext_wm)


            if desc.shapeType == "Polygon":
                baselength, basearea = get_length_area_from_pixel(96, 295828764)
                lod_area = basearea / math.pow(4, start_level - 1)
                arcpy.AddMessage("start lod area: " + str(lod_area))
                for row in cursor:
                    lod = calculate_lod_for_polygon(row[0], baselength, lod_area,start_level)
                    row[2] = lod
                    cursor.updateRow(row)
            elif desc.shapeType == "Point":
                count = get_count(layer)
                arcpy.AddMessage("Total Points:" + str(count))
                if count < 200000:
                    arcpy.AddMessage("Input point sets too small for optimized, skip!")
                    continue
                else:
                    n = math.ceil(math.log(count / (512 * 512 / 16), 4))
                    arcpy.AddMessage("n:" + str(n))
                    for row in cursor:
                        oid = row[1]
                        lod = calculate_lod_for_point(oid,start_level,n)
                        row[2] = lod
                        cursor.updateRow(row)
            elif desc.shapeType == 'Polyline':
                baselength = get_length_from_pixel(96, 295828764)
                lod_length = baselength / math.pow(2, start_level - 1)
                for row in cursor:
                    lod = calculate_lod_for_polyline(row[0],lod_length,start_level)
                    row[2] = lod
                    cursor.updateRow(row)

        endTime = time.time()
        print("Compute finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        arcpy.AddMessage("Compute finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        print("\n")
        arcpy.AddMessage("\n")
    except arcpy.ExecuteError:
        express_arcpy_error()

# Description: Compute the total records for a featureclass
def get_count(layer):
    fields = ['SHAPE@']
    count = 0
    with arcpy.da.SearchCursor(layer, fields) as cursor:
        for row in cursor:
            count += 1

    return count

# Description: get the start level based on layer extent
def confirm_level(extent):
    width = extent.width
    height = extent.height
    arcpy.AddMessage("width:"+str(width) +"     height:"+ str(height))

    length = max(width, height)
    base_resolution = 78271.516964011724
    base_tile_resolution = base_resolution * 512

    for level in range(21):
        start_compute_resolution = base_tile_resolution

        if length >= base_tile_resolution:
            arcpy.AddMessage("level:" + str(level))
            arcpy.AddMessage("base tile resolution:" + str(base_tile_resolution))
            return level, start_compute_resolution
        else:
            base_tile_resolution /= 2

# Description: Add a new field with name lod to a table
def add_field(inFeatures,fieldName,fieldPrecision):
    try:
        startTime = time.time()
        timeStampName = time.strftime('%Y_%m_%d %H:%M:%S', time.localtime(time.time()))
        print("start add new field for: ", inFeatures, " at: ", timeStampName)
        arcpy.AddMessage("start add new field for: {0} at: {1}".format(str(inFeatures), str(timeStampName)))

        # Execute AddField for new field
        arcpy.AddField_management(inFeatures, fieldName, "Text", fieldPrecision,
                                  field_alias=fieldName, field_is_nullable="NULLABLE")

        endTime = time.time()
        print(inFeatures, "Add field:", fieldName, "finished, elapsed: ", str(endTime - startTime) + '  Seconds.eter..')
        arcpy.AddMessage(
            "Add field: {0} finished, elapsed: {1}  Seconds.eter..".format(fieldName, str(endTime - startTime)))
        print("\n")
        arcpy.AddMessage("\n")

    except arcpy.ExecuteError:
        express_arcpy_error()

# Description: Compute get area and length per pixel based on dpi and scale
def get_length_area_from_pixel(dpi,scale):
    pixel = 1 / dpi * 0.025
    length = scale * pixel
    area = length * length
    return length,area

# Description: Compute get length per pixel based on dpi and scale
def get_length_from_pixel(dpi,scale):
    pixel = 1 / dpi * 0.025
    length = scale * pixel
    return length

# Description: Calculate lod for every polygon
def calculate_lod_for_polygon(feature,baselength, basearea, start_level):
    try:
        if feature:
            area = feature.getArea("GEODESIC", "SQUAREMETERS")
            # length = feature.getLength("GEODESIC", "METERS")
            lod = start_level

            for i in range(20):
                # arcpy.AddMessage(str(i) + ":" + str(basearea) + "___"+str(area))
                # arcpy.AddMessage(str(i) + ":" + str(baselength) + "___" + str(length))
                if area >= basearea :
                    return str(lod)
                else:
                    lod += 1
                    basearea /= 4
                    baselength /= 2

            return str(lod)
        else:
            print(type(feature))
            return "19"
    except arcpy.ExecuteError:
        express_arcpy_error()

# Description: Calculate lod for every point
def calculate_lod_for_point(id, start_level, n):
    try:
        for i in range(n):
            if id % math.pow(4, n - i) == 0:
                return start_level
            else:
                start_level += 1
        return start_level
    except arcpy.ExecuteError:
        express_arcpy_error()

# Description: Calculate lod for every polyline
def calculate_lod_for_polyline(feature,baselength, start_level):
    try:
        if feature:
            length = feature.getLength("GEODESIC", "METERS")
            lod = start_level

            for i in range(20):
                # arcpy.AddMessage(str(i) + ":" + str(basearea) + "___"+str(area))
                # arcpy.AddMessage(str(i) + ":" + str(baselength) + "___" + str(length))
                if length >= baselength:
                    return lod
                else:
                    lod += 1
                    baselength /= 2

            return lod
        else:
            print(type(feature))

    except arcpy.ExecuteError:
        express_arcpy_error()

def execute():
    in_map = arcpy.GetParameter(0)
    arcpy.AddMessage("Input map : {0}.".format(in_map))
    in_layers = arcpy.GetParameter(1)

    field_name = "lod"

    calculate_lods_for_feature(in_layers, field_name)

# execute()











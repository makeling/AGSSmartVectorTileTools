# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-12-5
# Update Time : 2018-12-13
# Change Log  :
##      1.
##      2.
##      3.

import time
import arcpy

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

def dissolve_polygon(inMap,inFeatures):
    try:
        fields = arcpy.ListFields(inFeatures)
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        homeFolder = aprx.homeFolder
        in_map = aprx.listMaps(inMap)[0]
        lyr = in_map.listLayers(inFeatures)[0]
        ds_path = lyr.dataSource

        arcpy.AddMessage(ds_path)

        if ds_path.split(".")[1] == 'shp':
            outFeatures = ds_path.split(".")[0] + "_background"
        else:
            outFeatures = ds_path + "_background"

        arcpy.AddMessage("Out Feature path:" + outFeatures)

        for field in fields:
            if field.type == "OID":
                field_name = field.name
                # arcpy.AddMessage(field_name)
                arcpy.Dissolve_management(in_features=lyr,
                                          out_feature_class=outFeatures,
                                          dissolve_field=field_name)

                bg_lyr = in_map.addDataFromPath(outFeatures)

                if bg_lyr != None:
                    arcpy.AddMessage("move background layer:")
                    arcpy.AddMessage("bg layer: " + str(bg_lyr.name))
                    arcpy.AddMessage("main layer:" + str(lyr.name))
                    in_map.moveLayer(bg_lyr,lyr, 'BEFORE')

        aprx.save()
    except arcpy.ExecuteError:
        express_arcpy_error()


def batch_dissolve_layer(inMap, inLayers):
    try:
        startTime = time.time()
        timeStampName = time.strftime('%Y_%m_%d %H:%M:%S', time.localtime(time.time()))
        print("Start dissolve Task at: {0}".format(timeStampName))
        arcpy.AddMessage("Start dissolve Task at: {0}".format(timeStampName))

        for layer in inLayers:
            arcpy.AddMessage("Input Layer : {0}.".format(layer))
            desc = arcpy.da.Describe(layer)

            if desc['shapeType'] == "Polygon":
                dissolve_polygon(inMap, layer.name)
            else:
                arcpy.AddMessage("Input Layer type is not polygon, skip.")

        endTime = time.time()
        print("Compute finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        arcpy.AddMessage("Dissolve finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        print("\n")
        arcpy.AddMessage("\n")
    except arcpy.ExecuteError:
        express_arcpy_error()


def execute():
    in_map = arcpy.GetParameterAsText(0)
    arcpy.AddMessage(in_map)
    arcpy.AddMessage("Input map : {0}.".format(in_map))
    # in_layer = arcpy.GetParameterAsText(1)
    # arcpy.AddMessage("Input Layer : {0}.".format(in_layer))

    in_layers = arcpy.GetParameter(1)

    batch_dissolve_layer(in_map, in_layers)


# execute()
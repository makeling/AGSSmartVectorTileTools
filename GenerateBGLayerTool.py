# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-12-21
# Update Time :
# Change Log  :
##      1.
##      2.
##      3.

import arcpy
import GenerateBGLayer

def execute():
    in_map = arcpy.GetParameterAsText(0)
    arcpy.AddMessage(in_map)
    arcpy.AddMessage("Input map : {0}.".format(in_map))

    in_layers = arcpy.GetParameter(1)

    GenerateBGLayer.batch_dissolve_layer(in_map, in_layers)


execute()
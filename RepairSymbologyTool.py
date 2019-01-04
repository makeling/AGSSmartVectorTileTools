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
import RepairLayerSymbology


def execute():
    in_map = arcpy.GetParameterAsText(0)
    arcpy.AddMessage("Input map : {0}.".format(in_map))
    in_layers = arcpy.GetParameter(1)
    save_a_copy = arcpy.GetParameterAsText(2)
    arcpy.AddMessage("Save a copy:" + save_a_copy)
    RepairLayerSymbology.batch_repairs(in_map,in_layers,save_a_copy)

execute()
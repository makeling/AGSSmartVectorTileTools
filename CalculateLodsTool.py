# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-12-20
# Update Time :
# Change Log  :
##      1.
##      2.
##      3.


import arcpy
import CalculateLods

def execute():
    in_map = arcpy.GetParameter(0)
    arcpy.AddMessage("Input map : {0}.".format(in_map))
    in_layers = arcpy.GetParameter(1)

    field_name = "lod"

    CalculateLods.calculate_lods_for_feature(in_layers, field_name)

execute()


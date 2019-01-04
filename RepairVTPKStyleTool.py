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
import RepairVTPKStyles

def execute():
    in_vtpk = arcpy.GetParameterAsText(0)
    arcpy.AddMessage("Input vtpk path: {0}.".format(in_vtpk))
    RepairVTPKStyles.batch_repairs(in_vtpk)

execute()





# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-12-6
# Update Time : 2018-12-13
#               2019-03-19
# Change Log  :
##      1. update layer definition value: lyr.definitionQuery = field_name + ' < 100000'
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

def update_simple_renderer(sym, original_main_renderer):
    try:
        symbol = original_main_renderer.symbol
        sym.updateRenderer('UniqueValueRenderer')
        main_renderer = sym.renderer

        fields = ['lod']
        main_renderer.fields = fields
        for g in main_renderer.groups:
            for item in g.items:
                for value in item.values:
                    # arcpy.AddMessage(value[0])
                    item.symbol = symbol
        # if 'lod' not in fields:
        #     fields = ['lod']
        #     main_renderer.fields = fields
        #     for g in main_renderer.groups:
        #         for item in g.items:
        #             for value in item.values:
        #                 # arcpy.AddMessage(value[0])
        #                 item.symbol = symbol
        return symbol
    except arcpy.ExecuteError:
        express_arcpy_error()

def update_unique_value_renderer(main_renderer):
    try:
        # setup symbol template
        num = 0
        groups = main_renderer.groups
        symbol_template = {}

        for group in groups:
            for item in group.items:
                symbol_template[item.label] = item.symbol
                for value in item.values:
                    num += 1
                    # arcpy.AddMessage(value)
        arcpy.AddMessage("generate symbol template finished, total values:" + str(num))

        fields = [i.lower() for i in main_renderer.fields]

        if 'lod' not in fields:
            fields0 = main_renderer.fields
            fields0.append('lod')
            main_renderer.fields = fields0
            for g in main_renderer.groups:
                for item in g.items:
                    for value in item.values:
                        key = value[0]
                        # arcpy.AddMessage(value[0])
                        item.symbol = symbol_template[key]
    except arcpy.ExecuteError:
        express_arcpy_error()

def update_background_renderer(inMap,bgLayer,symbol):
    try:
        # repair the symbol color of  background layer equal to the outline color of the main layer.
        arcpy.AddMessage("Repairing the symbology of bg layer: {0}".format(bgLayer))
        bg_color = symbol.outlineColor

        arcpy.AddMessage("background color = " + str(bg_color))
        bg_lyr = inMap.listLayers(bgLayer)[0]

        # arcpy.AddMessage(bg_lyr)

        bg_sym = bg_lyr.symbology
        bg_sym.renderer.symbol.color = bg_color
        bg_sym.renderer.symbol.outlineColor = bg_color

        bg_lyr.symbology = bg_sym
        arcpy.AddMessage("Repaired successfully for layer: {0}".format(bgLayer))
    except arcpy.ExecuteError:
        express_arcpy_error()

def repair_symbology_general(inMap, inLayer):
    try:
        lyr = inMap.listLayers(inLayer)[0]
        ds_path = lyr.dataSource
        fields = arcpy.ListFields(ds_path)
        for field in fields:
            if field.type == "OID":
                field_name = field.name
                lyr.definitionQuery = field_name + ' < 100000'

        sym = lyr.symbology
        main_renderer = sym.renderer

        arcpy.AddMessage("Repairing the symbology of layer: {0}".format(lyr))

        # repair the renderer of main layer add lod field.
        if main_renderer.type == 'SimpleRenderer':
            update_simple_renderer(sym, main_renderer)
        elif main_renderer.type == 'UniqueValueRenderer':
            update_unique_value_renderer(main_renderer)
        lyr.symbology = sym
        lyr.definitionQuery = ''
        arcpy.AddMessage("Repaired successfully for layer: {0}".format(lyr))
    except arcpy.ExecuteError:
        express_arcpy_error()

def repair_polygon_symbology(inMap, inLayer):
    try:
        lyr = inMap.listLayers(inLayer)[0]

        ds_path = lyr.dataSource

        fields = arcpy.ListFields(ds_path)
        for field in fields:
            if field.type == "OID":
                field_name = field.name
                lyr.definitionQuery = field_name + ' < 100000'

        if ds_path.split(".")[1] == 'shp':
            bgLayer = ds_path.split(".")[0] + "_background"
        else:
            bgLayer = ds_path + "_background"
            bgLayer_name = bgLayer.split("\\").pop()
            arcpy.AddMessage("background layer name: " + str(bgLayer_name))

        sym = lyr.symbology
        main_renderer = sym.renderer

        arcpy.AddMessage("Repairing the symbology of layer: {0}".format(lyr))

        # repair the renderer of main layer add lod field.
        if main_renderer.type == 'SimpleRenderer':
            symbol = update_simple_renderer(sym,main_renderer)
        elif main_renderer.type == 'UniqueValueRenderer':
            symbol = main_renderer.groups[0].items[0].symbol
            update_unique_value_renderer(main_renderer)

        lyr.symbology = sym
        lyr.definitionQuery = ''
        arcpy.AddMessage("Repaired successfully for layer: {0}".format(lyr))
        update_background_renderer(inMap,bgLayer_name,symbol)

    except arcpy.ExecuteError:
        express_arcpy_error()

def batch_repairs(inMap, inLayers,saveACopy):
    try:
        startTime = time.time()
        timeName = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        timeStampName = time.strftime('%Y_%m_%d %H:%M:%S', time.localtime(time.time()))
        print("Start Repair Symbology at: {0}".format(timeStampName))
        arcpy.AddMessage("Start Repair Symbology at: {0}".format(timeStampName))

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx_path = aprx.filePath
        in_map = aprx.listMaps(inMap)[0]

        for layer in inLayers:
            inLayer = layer.name
            arcpy.AddMessage("Input Layer : {0}.".format(inLayer))
            desc = arcpy.da.Describe(layer)
            layer_type = desc['shapeType']
            arcpy.AddMessage("Input Layer Shape Type: {0}.".format(layer_type))
            if layer_type == "Polygon":
                repair_polygon_symbology(in_map, inLayer)
            else:
                repair_symbology_general(in_map, inLayer)

        if saveACopy.lower() == 'true':
            aprx_path_copy = aprx_path[:-5] + "_" + timeName + ".aprx"
            aprx.saveACopy(aprx_path_copy)
            arcpy.AddMessage("save s copy aprx:" + aprx_path_copy)
        else:
            aprx.save()

        endTime = time.time()
        print("Repair Symbology finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        arcpy.AddMessage("Repair Symbology finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        print("\n")
        arcpy.AddMessage("\n")
    except arcpy.ExecuteError:
        express_arcpy_error()

def execute():
    in_map = arcpy.GetParameterAsText(0)
    arcpy.AddMessage("Input map : {0}.".format(in_map))
    in_layers = arcpy.GetParameter(1)
    save_a_copy = arcpy.GetParameterAsText(2)
    arcpy.AddMessage("Save a copy:" + save_a_copy)

    batch_repairs(in_map,in_layers,save_a_copy)


# execute()
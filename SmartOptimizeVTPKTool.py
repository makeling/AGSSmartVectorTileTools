# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-12-14
# Update Time :
# Change Log  :
##      1.
##      2.
##      3.

import os,time
import arcpy
import CalculateLods
import GenerateBGLayer
import RepairLayerSymbology
import RepairVTPKStyles

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

def copy_aprx(SaveACopy):
    if SaveACopy == 'true':
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx_path = aprx.filePath
        arcpy.AddMessage("Current aprx path:" + aprx_path)
        aprx_path_copy = aprx_path[:-5] + "_copy.aprx"
        aprx.saveACopy(aprx_path_copy)
        arcpy.AddMessage("Save a copy for your original project:" + aprx_path_copy)
        arcpy.AddMessage("==================================")

# Automatically finding xml file and allowing user to choose origin index polygon
def get_tile_scheme(in_map):
    try:
        arcpy.AddMessage("# Starting finding existing XML file ...")
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map = aprx.listMaps(in_map)[0]
        # getting xml file
        map_sr = map.defaultCamera.getExtent().spatialReference
        map_sr_name = map_sr.name
        map_sr_wkid = map_sr.factoryCode
        vtpk_xml_name = "VTTS_"+str(map_sr_wkid)+"_"+map_sr_name+".xml"
        local_path = os.path.join(os.path.expanduser("~"), "AppData\Local\ESRI\Geoprocessing")
        vtpk_xml_path = os.path.join(local_path,vtpk_xml_name)
        arcpy.AddMessage("# Bingo! " + vtpk_xml_path + " has been found!")
        tile_scheme = vtpk_xml_path
        # getting service type
        if map_sr_wkid == 3857:
            service_type = "ONLINE"
        else:
            service_type = "EXISTING"
        # building index polygons
        common_aux_paras = [tile_scheme, service_type]
        return common_aux_paras
    except:
        express_arcpy_error()

def generate_vtpk(in_map,outVtpk):
    try:
        startTime = time.time()
        timeStampName = time.strftime('%Y_%m_%d %H:%M:%S', time.localtime(time.time()))
        arcpy.AddMessage("Start generate vtpk at: {0}".format(timeStampName))
        common_aux_paras = get_tile_scheme(in_map)

        tile_scheme = common_aux_paras[0]
        arcpy.AddMessage(tile_scheme)
        service_type = common_aux_paras[1]

        arcpy.management.CreateVectorTilePackage(in_map=in_map,
                                                 output_file=outVtpk,
                                                 service_type=service_type,
                                                 tiling_scheme=tile_scheme,
                                                 tile_structure="INDEXED",
                                                 min_cached_scale="",
                                                 max_cached_scale="",
                                                 index_polygons="",
                                                 summary=None,
                                                 tags=None)

        endTime = time.time()
        arcpy.AddMessage("Genterate vtpk finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))
        print("\n")
        arcpy.AddMessage("\n")

    except arcpy.ExecuteError:
        express_arcpy_error()

def execute_workflow(in_map, in_layers, field_name, save_a_copy, out_vtpk):
    arcpy.AddMessage("==================================")
    copy_aprx(save_a_copy)

    arcpy.AddMessage("step 1: Calculate Lods for Layers.")
    CalculateLods.calculate_lods_for_feature(in_layers,field_name)

    arcpy.AddMessage("==================================")
    arcpy.AddMessage("step 2: Generate background for Polygon Layers.")
    GenerateBGLayer.batch_dissolve_layer(in_map, in_layers)

    arcpy.AddMessage("==================================")
    arcpy.AddMessage("step 3: Repaired Layers Symbology based on ArcPro.")
    RepairLayerSymbology.batch_repairs(in_map, in_layers, 'false')

    arcpy.AddMessage("==================================")
    arcpy.AddMessage("step 4: Generate VTPK.")
    generate_vtpk(in_map, out_vtpk)

    arcpy.AddMessage("==================================")
    arcpy.AddMessage("step 5: Repair VTPK Style _ repaired minzoom.")
    RepairVTPKStyles.batch_repairs(out_vtpk)

def initialize_params():
    in_map = arcpy.GetParameter(0)
    arcpy.AddMessage("Input map : {0}.".format(in_map))

    in_layers = arcpy.GetParameter(1)

    save_a_copy = arcpy.GetParameterAsText(2)
    arcpy.AddMessage("Save a copy:" + save_a_copy)

    out_vtpk = arcpy.GetParameterAsText(3)
    arcpy.AddMessage("Out VTPK Path:" + out_vtpk)

    field_name = "lod"

    return in_map, in_layers, field_name, save_a_copy, out_vtpk

in_map, in_layers, field_name, save_a_copy, out_vtpk = initialize_params()

execute_workflow(in_map, in_layers, field_name, save_a_copy, out_vtpk)



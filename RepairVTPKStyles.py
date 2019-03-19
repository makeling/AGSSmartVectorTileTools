# -*- coding: utf-8 -*-
# !/usr/bin/python
__author__ = 'ma_keling'
# Version     : 1.0.0
# Start Time  : 2018-12-13
# Update Time : 2019-3-19
# Change Log  :
##      1. repair lod value:lod = id_array.pop().split(',').pop().strip()
##      2.
##      3.

import arcpy
import os,time,json
import  zipfile

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

def updateLayerSchema(updateJson, layerName, strokeWidth):
    j = updateJson
    layers = j['layers']
    new_layers = []

    for layer in layers:
        id = layer['id']
        layer_name= id.split('/')[0]
        fields = id.split('/')[1]

        if layer_name == layerName and fields != '<all other values>':
            lod = fields.split(',')[0]
            print(layerName, ', ', lod)

            #update layer
            layer['id'] = id + '/1'
            layer['minzoom'] = int(lod) - 1
            stroke_color = layer["paint"]["fill-outline-color"]
            fill_color = layer["paint"]["fill-color"]
            layer["paint"] = {"fill-color":fill_color}

            print("strokecolor", stroke_color)
            print(layer["paint"])
            new_layers.append(layer)

            newLayer = {}

            newLayer['id'] = id + '/0'
            newLayer['type'] = 'line'
            newLayer['source'] = layer['source']
            newLayer['source-layer'] = layer['source-layer']
            newLayer['filter'] = layer['filter']
            newLayer['minzoom'] = int(lod) - 1
            newLayer['layout']={"line-cap":"round", "line-json":"round"}
            newLayer['paint']={'line-color':stroke_color, 'line-width':strokeWidth}

            new_layers.append(newLayer)

        else:
            new_layers.append(layer)

    j['layers'] = new_layers

    return j

def updateZoomLinux(vtpk,root):
    arcpy.AddMessage("Reading Style file: root.json")
    czip = zipfile.ZipFile(vtpk, 'a')
    for f in czip.namelist():
        if f == 'p12/resources/styles/root.json':
            # root = czip.read(f).decode('utf-8')
            root_json = json.loads(root)
            layers = root_json['layers']

            for layer in layers:
                id = layer['id']
                id_array = id.split('/')
                layer_name = id_array[0]
                lod = ""

                if len(id_array) == 3:
                    lod = id_array[len(id_array) - 2].split(',').pop().strip()
                elif len(id_array) == 2:
                    lod = id_array.pop().split(',').pop().strip()

                if lod != "":
                    if lod.isdigit():
                        arcpy.AddMessage("Repaired minzoom param for layer:{0}".format(id))
                        # update layer
                        layer['minzoom'] = int(lod)

            root_json['layers'] = layers

            # content = json.dumps(root_json, ensure_ascii=False)
            content = json.dumps(root_json, ensure_ascii=False)

            # with czip.open(f, mode='w') as myfile:
            #     myfile.write("ttt".encode(encoding="utf-8"))
            # czip.writestr(f, content, compress_type=zipfile.ZIP_STORED)

    czip.close()

def updateZoomWin(vtpk,root):
    arcpy.AddMessage("Reading Style file: root.json")
    czip = zipfile.ZipFile(vtpk,mode='r')
    new_vtpk = vtpk + ".zip"
    nzip = zipfile.ZipFile(new_vtpk,mode='w')
    for f in czip.namelist():
        if f == 'p12/resources/styles/root.json':
            # root = czip.read(f).decode('utf-8')
            root_json = json.loads(root)
            layers = root_json['layers']

            for layer in layers:
                id = layer['id']
                id_array = id.split('/')
                layer_name = id_array[0]
                lod = ""

                if len(id_array) == 3:
                    lod = id_array[len(id_array) - 2].split(',').pop().strip()
                elif len(id_array) == 2:
                    lod = id_array.pop().split(',').pop().strip()

                if lod != "":
                    if lod.isdigit():
                        arcpy.AddMessage("Repaired minzoom param for layer:{0}".format(id))
                        # update layer
                        layer['minzoom'] = int(lod) - 1

            root_json['layers'] = layers

            # content = json.dumps(root_json, ensure_ascii=False)
            content = json.dumps(root_json, ensure_ascii=False)

            nzip.writestr(f, content, compress_type=zipfile.ZIP_STORED)

            # with nzip.open(f, mode='w') as myfile:
            #     myfile.write(content.encode(encoding="utf-8"))
        else:
            nzip.writestr(f,czip.read(f),compress_type=zipfile.ZIP_STORED)

    czip.close()
    nzip.close()

    vtpk_mid = vtpk+".del"
    os.rename(vtpk,vtpk+".del")
    os.rename(new_vtpk,vtpk)
    os.remove(vtpk_mid)



def zip_read(vtpk):
    czip = zipfile.ZipFile(vtpk, 'r')
    root_original = ""

    for f in czip.namelist():
        # print(f)
        if f == 'p12/resources/styles/root.json':
            root_original = czip.read(f).decode('utf-8')
            # root_json = json.loads(root_original)
            # layers = root_json['layers']
            #
            # for layer in layers:
            #     print(layer)

    czip.close()
    return root_original

def batch_repairs(in_vtpk):
    startTime = time.time()

    timeStampName = time.strftime('%Y_%m_%d %H:%M:%S', time.localtime(time.time()))

    print("Start Repair VTPK at: {0}".format(timeStampName))

    arcpy.AddMessage("Start Repair VTPK at: {0}".format(timeStampName))

    root = zip_read(in_vtpk)

    updateZoomWin(in_vtpk, root)

    endTime = time.time()

    print("Repair VTPK finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))

    arcpy.AddMessage("Repair VTPK finished, elapsed: {0} Seconds.eter..".format(str(endTime - startTime)))

    print("\n")

    arcpy.AddMessage("\n")

def execute():
    in_vtpk = arcpy.GetParameterAsText(0)

    arcpy.AddMessage("Input vtpk path: {0}.".format(in_vtpk))

    # in_vtpk = r"C:\Users\Administrator\Documents\ArcGIS\Projects\spatialAnalysis\vtpks\smart04.vtpk"

    batch_repairs(in_vtpk)

# execute()





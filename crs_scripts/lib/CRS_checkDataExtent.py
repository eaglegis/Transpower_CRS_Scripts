#################################################
###     CRS_checkDataExtent.py                ###
### go through feature class in crs.gdb       ###
### delete the features outside nz boundary   ###
### Eagle Technology 2018                     ###
#################################################
# methods
# 1. set arcpy.env.extent(), and then use CopyFeatures followed by GetCount - this is good if not too many features are copied
# 2. create a rectangle geometry and then use it as the select_features in Select Layer By Location, followed by Get Count

import arcpy, os
import etgLib

sr = arcpy.SpatialReference(2193)

args = []
def crs_check_data_extent(args):
    # script parameters
    gdb = args[0]
    extentString = args[1]
    itemsToCheck = args[2]
    log = args[3]

    # workspace
    arcpy.env.workspace = gdb

    # script name
    script_name = os.path.basename(__file__)
    
    # variables
    err_message = None

    etgLib.log_info(log, 'calling {}'.format(script_name), True)
    try:
        
        extentValues = extentString.split(',')

        if len(extentValues) != 4:
            err_message = "missing pamaremter in extent config"
            return err_message
            
        xMin = int(extentValues[0])
        yMin = int(extentValues[1])
        xMax = int(extentValues[2])
        yMax = int(extentValues[3])

        
        extent = arcpy.Extent(xMin,yMin,xMax,yMax)
        extentArray = arcpy.Array(i for i in (extent.lowerLeft,  
                                            extent.lowerRight,  
                                            extent.upperRight,  
                                            extent.upperLeft,  
                                            extent.lowerLeft))
        # create a extent polygon
        extentPolygon = arcpy.Polygon(extentArray, sr)  

        # go through feature class in crs gdb, delete feature which is out of the nz bound
        fcs = arcpy.ListFeatureClasses()

        if len(itemsToCheck) > 0:
            fcs = list(set(fcs).intersection(set(itemsToCheck)))

        for fc in fcs:
            name = arcpy.Describe(fc).name
            etgLib.log_info(log, 'checking {0}...'.format(name))

            # Make a layer and select features which within the extent polygon
            lyr = 'lyr_{}'.format(name)
            etgLib.delete_layer(lyr)
            
            arcpy.MakeFeatureLayer_management(fc, lyr)
            count = int(arcpy.GetCount_management(lyr)[0])            
           
            arcpy.SelectLayerByLocation_management(lyr, "INTERSECT", extentPolygon, "", "NEW_SELECTION", "NOT_INVERT")
            arcpy.SelectLayerByLocation_management(lyr, "", "","","SWITCH_SELECTION")

            count = int(arcpy.GetCount_management(lyr)[0]) 
            # delete features outside nz bound
            if count > 0:
                etgLib.log_info(log, 'deleting features in {0}: {1}'.format(name,count))                
                arcpy.DeleteFeatures_management(lyr)
        
    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)

    return err_message      

# if __name__ == '__main__':
#     main(args)



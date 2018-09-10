#####################################
###     CRS1_repairCRSdata.py     ###
### Python script to list all CRS ###
###  data and repair polygon data ###
### Karen Chadwick  November 2016 ###
### modified by Eagle 2018        ### 
#####################################

### Import modules
import arcpy, os
import etgLib
import datetime, time

args = []
def print_list(lst, log):
    for itm in lst:
        etgLib.log_info(log, itm)

def crs1_repair_crs_data(args):
    # script name
    script_name = os.path.basename(__file__)

    # script parameters
    gdb = args[0]    
    log = args[1]

    # Set environment
    arcpy.env.workspace = gdb
    
    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)

    # start time
    starttime = datetime.datetime.now()

    # variables
    err_message = None
    fc_cadastre = 'CADASTRE'
    fld_cadastre = 'F_issues'
    fc_ownerfixed = 'OWNER_FIXED'
    fc_plan ='PLAN'
    fc_parcelplan = 'PARCEL_PLAN'

    try:
              
        ## Delete any extraneous data
        etgLib.log_info(log, 'Delete any extraneous data',True)
        etgLib.delete_layer(fc_ownerfixed)

        # list all the feature classes
        pointfcl = []
        linefcl = []
        polyfcl = [] 
        tbll = []           

        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:                
            desc = arcpy.Describe(fc)
            if desc.shapeType == 'Point':
                pointfcl.append(fc)
            elif desc.shapeType == 'Polyline':
                linefcl.append(fc)
            elif desc.shapeType == 'Polygon':
                polyfcl.append(fc)
            else:
                pass
        
        etgLib.log_info(log, 'Point feature classes:',True)
        print_list(pointfcl,log)
        etgLib.log_info(log, 'Polyline feature classes:',True)
        print_list(linefcl, log)
        etgLib.log_info(log, 'Polygon feature classes:',True)
        print_list(polyfcl, log)

        etgLib.log_info(log, 'tables:',True)
        tbll = arcpy.ListTables()
        print_list(tbll, log)
                    
        # add field to CADASTRE
        if etgLib.field_exist(fc_cadastre, fld_cadastre) == False:
            etgLib.log_info(log, 'adding field [{0}] in {1}'.format(fld_cadastre,fc_cadastre))
            arcpy.AddField_management(fc_cadastre,fld_cadastre,"TEXT","","",250)

        # Repair polygon geometry
        etgLib.log_info(log,'Repairing polygon geometries...')
        for polyfc in polyfcl:                
            preCount = arcpy.GetCount_management(polyfc).getOutput(0)
            arcpy.RepairGeometry_management(polyfc)
            postCount = arcpy.GetCount_management(polyfc).getOutput(0)
            etgLib.log_info(log,'{0}: features pre-repair {1} - post-repair {2}'.format(polyfc, preCount, postCount))
            
        # Rename PLAN to PARCEL_PLAN
        if arcpy.Exists(fc_plan):
            arcpy.Rename_management(fc_plan,fc_parcelplan)
            etgLib.log_info(log,'Renamed {0} to {1}'.format(fc_plan,fc_parcelplan))
        else:               
            etgLib.log_info(log,'ERROR: feature class {} not found'.format(fc_plan))

        etgLib.log_process_time(log,starttime)

        # ### Note that number of features pre- and post-repair should be emailed to Technical Specialist
        # print('***NOTE: next step/s = email pre- and post-repair feature counts to Technical Specialist...')

    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)

    return err_message      

######################################
###     CRS2_emptyNDCSTGsde.py     ###
###  Python script to remove data  ###
###      from NDCSTG database      ###
### Karen Chadwick   November 2016 ###
### modified by Eagle 2018         ### 
######################################

### Import modules
import arcpy
import datetime, time
import os   

starttime = datetime.datetime.now()

# Assign values
itemsToKeep = ["NZC_STG.MapData.CRS_AuditTable","NZC_STG.MapData.CRS_SpatialTablesToUpdate",
               "NZC_STG.MapData.CRS_TablesToUpdate","NZC_STG.MapData.DATA_LOAD_DATE",
               "NZC_STG.MapData.tp_parcel_address_vw","NZC_STG.MapData.tp_parcel_title_owner_vw",
               "NZC_STG.MapData.tp_parcel_title_vw","NZC_STG.MapData.tp_title_address_vw",
               "NZC_STG.MapData.tp_title_owner_address_vw","NZC_STG.MapData.vwRecordCounts"]
# # testing on stg.gdb
# itemsToKeep = ["PARCEL_LABEL","TP_PROPERTY","TP_PROPERTY_LINK"]               
# variables
args = []
err_message = None
log_messages = []


def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def crs2_empty_stage_sde(args):
    # script name
    script_name = os.path.basename(__file__)

    # script parameters
    sde = args[0]  
    # log = args[1]

    # Set environment
    arcpy.env.workspace = sde
      
    # log function
    log_msg ('calling {}'.format(script_name))

    # variables
    err_message = None

    try:
        # clear workspce cache
        arcpy.ClearWorkspaceCache_management()
       
        # Find all feature classes and delete a subset
        fcl = arcpy.ListFeatureClasses()
        log_msg('Deleting subset of feature classes:')
        
        for fc in fcl:
            log_msg(fc)
            if fc in itemsToKeep:
                log_msg('Kept:{}'.format(fc))
            else:
                try:
                    arcpy.Delete_management(fc)
                    log_msg('Deleted: {}'.format(fc))
                except:
                    # print('***ERROR*** while deleting {} - delete manually!!!').format(fc)
                    err_message = 'ERROR: deleting {}\n'.format(fc)

        
        # Find all tables and delete a subset
        tbll = arcpy.ListTables()
        log_msg('Deleting subset of feature tables:')
        for tbl in tbll:
            if tbl in itemsToKeep:
                log_msg('Kept:{}'.format(tbl))
            else:
                try:
                    arcpy.Delete_management(tbl)
                    log_msg('Deleted: {}'.format(tbl))
                except:                    
                    if err_message != None:
                        err_message = err_message + 'ERROR: deleting {}\n'.format(tbl)
                    else:
                        err_message = 'ERROR: deleting {}\n'.format(tbl)

        log_msg( "Process time: %s \n" % str(datetime.datetime.now()-starttime))

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    return err_message, log_messages
    

############################################
### CRS10_prodSPREPORTandSPOWNrefresh.py ###
###   Python script to refresh data in   ###
###    production SPREPORT  and SPOWN    ###
###  Karen Chadwick          March 2017  ###
############################################

########################################################################
########################################################################
########################################################################
##### *IMPORTANT* SINCE THIS SCRIPT REFRESHES DATA IN A PRODUCTION #####
##### DATABASE, IT SHOULD BE RUN OUTSIDE OF REGULAR BUSINESS HOURS #####
########################################################################
########################################################################
########################################################################

### Import modules
import arcpy,os,datetime
import etgLib 

starttime = datetime.datetime.now()

# script name
script_name = os.path.basename(__file__)

args = []

# ################################################################################
# ###################### Only edit items between here -------------------> #######
# prepSPREPORTpath = r"Database Connections\pp_Dataloader@SPREPORT@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### preprod SPREPORT SDE path
# prodSPREPORTpath = r"Database Connections\p_dataloader@SPREPORT@SQLPRD-SPATIAL.transpower.co.nz.sde"  ### production SPREPORT SDE path
# prepSPOWNpath = r"Database Connections\pp_Dataloader@SPOWN@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### preprod SPOWN SDE path
# prodSPOWNpath = r"Database Connections\p_dataloader@SPOWN@SQLPRD-SPATIAL.transpower.co.nz.sde"  ### production SPOWN SDE path
# ###################### <--------------------------------------- and here #######
# ################################################################################

# Set environment
arcpy.env.overwriteOutput = True

# Assign values
spreportFClist = ["SPREPORT.MAPDATA.SITE_Parcel","SPREPORT.MAPDATA.SPAN_Parcel","SPREPORT.MAPDATA.STRUCTURE_Parcel",
                  "SPREPORT.MAPDATA.SECTION_Parcel"]
spownFClist = ["SPOWN.MAPDATA.Connect_Property"]

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

def crs10_prod_db_refresh (args):
    # parameters
    prepSPREPORTpath = args[0]
    prodSPREPORTpath = args[1]
    prepSPOWNpath = args[2]
    prodSPOWNpath = args[3]      
    log = args[4]

    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)

    # variables
    err_message = None

    try:
        ##### Truncate data in production SDEs and then append from preprod
        ### SPREPORT
        for fc in spreportFClist:
            # Assign locations
            inFC = os.path.join(prepSPREPORTpath,fc)
            prodFC = os.path.join(prodSPREPORTpath,fc)
            # Count input number of records
            infcRowCount = arcpy.GetCount_management(inFC).getOutput(0)
            etgLib.log_info(log, 'INPUT {0}: {1} records'.format(inFC,infcRowCount))            
            # Truncate
            arcpy.TruncateTable_management(prodFC)
            # Append
            arcpy.Append_management(inFC,prodFC,"NO_TEST")
            # Count number of records in prod
            prodfcRowCount = arcpy.GetCount_management(prodFC).getOutput(0)
            etgLib.log_info(log, 'PRODUCTION {0}: {1} records'.format(prodFC,prodfcRowCount))
            
        ### SPOWN
        for fc in spownFClist:
            # Assign locations
            inFC = os.path.join(prepSPOWNpath,fc)
            prodFC = os.path.join(prodSPOWNpath,fc)
            # Count input number of records
            infcRowCount = arcpy.GetCount_management(inFC).getOutput(0)
            etgLib.log_info(log, 'INPUT {0}: {1} records'.format(inFC,infcRowCount))         
            
            # Truncate
            arcpy.TruncateTable_management(prodFC)
            fieldMap = "TP_PROPERTY_LINK_PROPERTY_ID \"TP_PROPERTY_LINK_PROPERTY_ID\" true false false 8 Double 0 0 ,First,#," + inFC + ",PROPERTY_ID,-1,-1;OBJECTID_1 \"OBJECTID_1\" true false false 4 Long 0 0 ,First,#;PROPERTY_ID \"PROPERTY_ID\" true false false 8 Double 0 0 ,First,#," + inFC + ",PROPERTY_ID,-1,-1;PARCEL_ID \"PARCEL_ID\" true false false 8 Double 0 0 ,First,#," + inFC + ",PROPERTY_ID,-1,-1;COUNT_PARCEL_ID \"COUNT_PARCEL_ID\" true true false 2 Short 0 0 ,First,#," + inFC + ",COUNT_PARCEL_ID,-1,-1;SHAPE_STArea__ \"SHAPE_STArea__\" true false true 8 Double 0 0 ,First,#;SHAPE_STLength__ \"SHAPE_STLength__\" true false true 8 Double 0 0 ,First,#;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#;SHAPE_Area \"SHAPE_Area\" false true true 8 Double 0 0 ,First,#"
            # Append
            arcpy.Append_management(inFC,prodFC,"NO_TEST", fieldMap)
            # Count number of records in prod
            prodfcRowCount = arcpy.GetCount_management(prodFC).getOutput(0)            
            etgLib.log_info(log, 'PRODUCTION {0}: {1} records'.format(prodFC,prodfcRowCount))
                            
        etgLib.log_process_time(log,starttime)  

    except Exception as e:
        print ("ERROR: {}".format(e))
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
        
    return err_message

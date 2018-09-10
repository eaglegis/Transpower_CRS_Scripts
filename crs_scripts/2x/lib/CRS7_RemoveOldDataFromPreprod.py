############################################
###   CRS7_RemoveOldDataFromPreprod.py   ###
### Python script to remove all old data ###
###        from preprod NZCONTEXT        ###
###  Karen Chadwick            May 2017  ###
############################################

### Import modules
import arcpy,os,datetime
import etgLib 

starttime = datetime.datetime.now()

# script name
script_name = os.path.basename(__file__)

args = []

def crs7_remove_old_data_from_preprod(args):

    # parameters
    preprodPath = args[0]
    preprodPrefix = args[1]   
    log = args[2]

    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)

    # variables
    err_message = None


    try:
        ##### Find and delete any old data (*_o) from previous month's processing
        # Get lists of tables and FCs
        etgLib.log_info(log, 'Getting lists of tables and FCs from {} ...'.format(preprodPath))
        arcpy.env.workspace = preprodPath
        
        fcl = arcpy.ListFeatureClasses()
        tbll = arcpy.ListTables()

        # Work through list of feature classes       
        etgLib.log_info(log, '==> Checking preprod FCs for old data...',True)
        for fc in fcl:        
            ppfcname = fc[len(preprodPrefix):]
            # if fc.endswith("_o") or fc.endswith("_oo"):
            if ppfcname.endswith("_o") or ppfcname.endswith("_oo"):                               
                etgLib.log_info(log, 'Removing: {} ...'.format(fc))
                if arcpy.Exists(fc):
                    arcpy.Delete_management(fc)
            
        # Work through list of tables
        etgLib.log_info(log, '==> Checking preprod tables for old data...',True)
        for tbl in tbll:        
            pptblname = tbl[len(preprodPrefix):]
            # if tbl.endswith("_o") or tbl.endswith("_oo"): 
            if pptblname.endswith("_o") or pptblname.endswith("_oo"):                                
                etgLib.log_info(log, 'Removing: {} ...'.format(tbl))
                if arcpy.Exists(tbl):
                    arcpy.Delete_management(tbl)            

        etgLib.log_process_time(log,starttime)  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message
 

############################################
###   CRS7_RemoveOldDataFromPreprod.py   ###
### Python script to remove all old data ###
###        from preprod NZCONTEXT        ###
###  Karen Chadwick            May 2017  ###
############################################

### Import modules
import arcpy,os,datetime

starttime = datetime.datetime.now()

# script name
script_name = os.path.basename(__file__)

# variables
args = []
err_message = None
log_messages = []

def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def crs7_remove_old_data_from_preprod(args):

    # parameters
    preprodPath = args[0]
    preprodPrefix = args[1]   
    # log = args[2]

    # log function
    log_msg ('calling {}'.format(script_name))

    # variables
    err_message = None

    try:
        ##### Find and delete any old data (*_o) from previous month's processing
        # Get lists of tables and FCs
        log_msg ( 'Getting lists of tables and FCs from {} ...'.format(preprodPath))
        arcpy.env.workspace = preprodPath
        
        fcl = arcpy.ListFeatureClasses()
        tbll = arcpy.ListTables()

        # Work through list of feature classes       
        log_msg ('==> Checking preprod FCs for old data...')
        for fc in fcl:        
            ppfcname = fc[len(preprodPrefix):]
            # if fc.endswith("_o") or fc.endswith("_oo"):
            if ppfcname.endswith("_o") or ppfcname.endswith("_oo"):                               
                log_msg ( 'Removing: {} ...'.format(fc))
                if arcpy.Exists(fc):
                    arcpy.Delete_management(fc)
            
        # Work through list of tables
        log_msg ('==> Checking preprod tables for old data...')
        for tbl in tbll:        
            pptblname = tbl[len(preprodPrefix):]
            # if tbl.endswith("_o") or tbl.endswith("_oo"): 
            if pptblname.endswith("_o") or pptblname.endswith("_oo"):                                
                log_msg ( 'Removing: {} ...'.format(tbl))
                if arcpy.Exists(tbl):
                    arcpy.Delete_management(tbl)            

        log_msg ( "Process time: %s \n" % str(datetime.datetime.now()-starttime)) 

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message, log_messages
 

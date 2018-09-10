#######################################
###    CRS4_copyTablesToNZCSTG.py   ###
###   Python script to copy tables  ###
###        to NDCSTG database       ###
### Karen Chadwick    November 2016 ###
### modified by Eagle 2018          ###
#######################################
####################################################
# Loosely based on copy_supply_tables_to_NZCSTG.py #
####################################################

### Import modules
import arcpy
import datetime
import os  

starttime = datetime.datetime.now()

# variables
args = []
err_message = None
log_messages = []


def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def crs4_copy_tbls_stage(args):
    # script name
    script_name = os.path.basename(__file__)

    # script parameters
    sdePath = args[0]  
    gdbPath = args[1]
    sdePrefix = args[2]
   
    # Set environment
    arcpy.env.workspace = gdbPath
    arcpy.env.overwriteOutput = True
    arcpy.env.configkeyword= "GEOMETRY"

    # log function
    log_msg ('calling {}'.format(script_name))

    # variables
    err_message = None    
    # excludeList = ["INSTRUMENT"]
    excludeList = []

    try:
    
        if arcpy.Exists(gdbPath):
            ### Copy tables from local GDB to database
            #*** NOTE: tables have been deleted from SDE previously via 
            #*** CRS2_emptyNDCSTGsde.py - but still check for existence
            # List tables in GDB
            tbll = arcpy.ListTables()
            # Loop through the tables
            log_msg ( 'Copying tables to staging SDE...')
            for tbl in tbll:
                inTBLpath = os.path.join(gdbPath,tbl)
                outTBLname = sdePrefix + tbl
                outTBLpath = os.path.join(sdePath,outTBLname)
                # Check whether table exists in SDE, if so - print warning
                if arcpy.Exists(outTBLpath):
                    log_msg ( 'WARNING: {} exists in staging SDE'.format(outTBLname))
                # Otherwise, copy
                else:
                    # Ignore tables in exclude list
                    if tbl in excludeList:
                        log_msg ( 'Ignoring {}'.format(tbl))                        
                    else:
                        # Copy table from GDB to SDE
                        arcpy.Copy_management(inTBLpath,outTBLpath,"Table") 
                        # Count features and report number - warn if not equal
                        inCount = arcpy.GetCount_management(inTBLpath).getOutput(0)
                        outCount = arcpy.GetCount_management(outTBLpath).getOutput(0)
                        if inCount == outCount:
                            log_msg ('{0} - Copied {1} entries to {2}'.format(tbl,inCount,outTBLname))
                        else:
                            log_msg ( 'ERROR: {0} entries copied from {1} - {2} entries resultant in {3}'.format(inCount,tbl,outCount,outTBLname))                   
        else:
            err_message = 'ERROR: GDB not found - {}'.format(gdbPath)
            
        log_msg ( "Process time: %s \n" % str(datetime.datetime.now()-starttime))  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)

    return err_message, log_messages








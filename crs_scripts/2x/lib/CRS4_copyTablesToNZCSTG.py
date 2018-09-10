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
import etgLib
import datetime
import os  

starttime = datetime.datetime.now()

args = []

def crs4_copy_tbls_stage(args):
    # script name
    script_name = os.path.basename(__file__)

    # script parameters
    sdePath = args[0]  
    gdbPath = args[1]
    sdePrefix = args[2]
    log = args[3]

    # Set environment
    arcpy.env.workspace = gdbPath
    arcpy.env.overwriteOutput = True
    arcpy.env.configkeyword= "GEOMETRY"

    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)

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
            etgLib.log_info(log, 'Copying tables to staging SDE...',True)
            for tbl in tbll:
                inTBLpath = os.path.join(gdbPath,tbl)
                outTBLname = sdePrefix + tbl
                outTBLpath = os.path.join(sdePath,outTBLname)
                # Check whether table exists in SDE, if so - print warning
                if arcpy.Exists(outTBLpath):
                    etgLib.log_info(log, 'WARNING: {} exists in staging SDE'.format(outTBLname))
                # Otherwise, copy
                else:
                    # Ignore tables in exclude list
                    if tbl in excludeList:
                        etgLib.log_info(log, 'Ignoring {}'.format(tbl))                        
                    else:
                        # Copy table from GDB to SDE
                        arcpy.Copy_management(inTBLpath,outTBLpath,"Table") 
                        # Count features and report number - warn if not equal
                        inCount = arcpy.GetCount_management(inTBLpath).getOutput(0)
                        outCount = arcpy.GetCount_management(outTBLpath).getOutput(0)
                        if inCount == outCount:
                            etgLib.log_info(log, '{0} - Copied {1} entries to {2}'.format(tbl,inCount,outTBLname))
                        else:
                            etgLib.log_info(log, 'ERROR: {0} entries copied from {1} - {2} entries resultant in {3}'.format(inCount,tbl,outCount,outTBLname))                   
        else:
            err_message = 'ERROR: GDB not found - {}'.format(gdbPath)
            
        etgLib.log_process_time(log,starttime)  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)

    return err_message

# if __name__ == '__main__':
#     crs4_copy_tbls_stage(args)







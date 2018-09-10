#######################################
###     CRS3_copyFCsToNZCSTG.py     ###
###    Python script to copy FCs    ###
###        to NDCSTG database       ###
### Karen Chadwick    November 2016 ###
### modified by Eagle 2018          ###
#######################################
######################################################
# Loosely based on copy_supply_features_to_NZCSTG.py #
######################################################

### Import modules
import arcpy
import etgLib
import datetime
import os  

starttime = datetime.datetime.now()

args = []

def crs3_copy_fcs_stage(args):
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
       
    try:       
        if arcpy.Exists(gdbPath):
            ### Copy feature classes from local GDB to database
            #*** NOTE: feature classes have been deleted from SDE previously via
            #*** CRS2_emptyNDCSTGsde.py - but still check for existence
            # List feature classes in GDB
            fcl = arcpy.ListFeatureClasses()
            # Loop through the FCs
            etgLib.log_info(log, 'Copying feature classes to staging SDE...',True)
            for fc in fcl:
                inFCpath = os.path.join(gdbPath,fc)
                outFCname = sdePrefix + fc
                outFCpath = os.path.join(sdePath,outFCname)
                # Check whether FC exists in SDE, if so - print warning
                if arcpy.Exists(outFCpath):
                    etgLib.log_info(log, 'WARNING: {} exists in staging SDE'.format(outFCname))
                # Otherwise, copy
                else:
                    # Copy FC from GDB to SDE
                    arcpy.Copy_management(inFCpath,outFCpath,"FeatureClass")
                    # Count features and report number - warn if not equal
                    inCount = arcpy.GetCount_management(inFCpath).getOutput(0)
                    outCount = arcpy.GetCount_management(outFCpath).getOutput(0)
                    if inCount == outCount:
                        etgLib.log_info(log, '{0} - Copied {1} features to {2}'.format(fc,inCount,outFCname))
                    else:
                        etgLib.log_info(log, 'ERROR: {0} features copied from {1} - {2} features resultant in {3}'.format(inCount,fc,outCount,outFCname))
                   
        else:
            err_message = 'ERROR: GDB not found - {}'.format(gdbPath)

        etgLib.log_process_time(log,starttime)  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)

    return err_message








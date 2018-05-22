#######################################
###     CRS3_copyFCsToNZCSTG.py     ###
###    Python script to copy FCs    ###
###        to NDCSTG database       ###
### Karen Chadwick    November 2016 ###
#######################################
######################################################
# Loosely based on copy_supply_features_to_NZCSTG.py #
######################################################

### Import modules
import arcpy,os,datetime,sys

starttime = datetime.datetime.now()

################################################################################
#############  ENSURE YOU ARE USING THE CURRENT MONTH FOR PROCESSING!!!  #######
################################################################################
###################### Only edit items between here -------------------> #######
#gdbPath = r"C:\Data\CRS\2017_Aug\CRS.gdb"  ### Working GDB (local drive)
gdbPath = r"C:\Users\ads.EAGLE\Documents\Transpower\Workflows and Scripts\Aug2017_Transpower_supply\CRS.gdb"
#sdePath = r"Database Connections\pp_Dataloader@NZC_STG@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### Staging SDE path
sdePath = r"C:\Users\ads.EAGLE\Documents\Transpower\Workflows and Scripts\Aug2017_Transpower_supply\NZC_STG.gdb"
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
#sdePrefix = "NZC_STG.MAPDATA."
cutoffage = 20  # cutoff age in days

# Set environment
arcpy.env.workspace = gdbPath
arcpy.env.overwriteOutput = True
arcpy.env.configkeyword= "GEOMETRY"

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

##try:
    ## Test for working folder age -- warn and then exit if older than cutoff
    ## (Extend cutoff age if necessary [to continue processing anyway])
    wkgFldr = os.path.dirname(gdbPath)
    print('Working folder = {}').format(wkgFldr)
    t = os.path.getctime(wkgFldr)
    tt = datetime.datetime.fromtimestamp(t)
    fldrTimeCheck = starttime - tt
    td = datetime.timedelta(days=cutoffage)
    if fldrTimeCheck >= td: # Working folder too old - don't use old data instead of new
        print('WARNING: working folder {} created {} HH:MM:SS.dddddd ago!!!').format(wkgFolder,fldrTimeCheck)
        sys.exit("Folder older than {} days").format(cutoffage)
    else: # Continue processing
        if arcpy.Exists(gdbPath):
            ### Copy feature classes from local GDB to database
            #*** NOTE: feature classes have been deleted from SDE previously via
            #*** CRS2_emptyNDCSTGsde.py - but still check for existence
            # List feature classes in GDB
            fcl = arcpy.ListFeatureClasses()
            # Loop through the FCs
            print('Copying feature classes to staging SDE...')
            for fc in fcl:
                inFCpath = os.path.join(gdbPath,fc)
                #outFCname = sdePrefix + fc
                outfcname = fc
                outFCpath = os.path.join(sdePath,outFCname)
                # Check whether FC exists in SDE, if so - print warning
                if arcpy.Exists(outFCpath):
                    print('WARNING: {} exists in staging SDE').format(outFCname)
                # Otherwise, copy
                else:
                    # Copy FC from GDB to SDE
                    arcpy.Copy_management(inFCpath,outFCpath,"FeatureClass")
                    # Count features and report number - warn if not equal
                    inCount = arcpy.GetCount_management(inFCpath).getOutput(0)
                    outCount = arcpy.GetCount_management(outFCpath).getOutput(0)
                    if inCount == outCount:
                        print('\t{} - Copied {} features to {}').format(fc,inCount,outFCname)
                    else:
                        print('ERROR: {} features copied from {} - {} features resultant in {}').format(inCount,fc,outCount,outFCname)
                    print('\t\t{}').format(datetime.datetime.now())
        else:
            print('ERROR: GDB not found - {}').format(gdbPath)
            sys.exit("Local GDB not found")

        endtime = datetime.datetime.now()
        elapsedtime = endtime - starttime
        print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)

##except:
##    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
##    print arcpy.GetMessages()








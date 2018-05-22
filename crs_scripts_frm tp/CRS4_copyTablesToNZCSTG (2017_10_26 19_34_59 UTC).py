#######################################
###    CRS4_copyTablesToNZCSTG.py   ###
###   Python script to copy tables  ###
###        to NDCSTG database       ###
### Karen Chadwick    November 2016 ###
#######################################
####################################################
# Loosely based on copy_supply_tables_to_NZCSTG.py #
####################################################

### Import modules
import arcpy,os,datetime  

starttime = datetime.datetime.now()

################################################################################
#############  ENSURE YOU ARE USING THE CURRENT MONTH FOR PROCESSING!!!  #######
################################################################################
###################### Only edit items between here -------------------> #######
gdbPath = r"C:\Data\CRS\2017_Aug\CRS.gdb"  ### Working GDB (local drive)
sdePath = r"Database Connections\pp_Dataloader@NZC_STG@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### Staging SDE path
excludeList = ["INSTRUMENT"]
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
sdePrefix = "NZC_STG.MAPDATA."
cutoffage = 20  # cutoff age in days

# Set environment
arcpy.env.workspace = gdbPath
arcpy.env.overwriteOutput = True
arcpy.env.configkeyword= "GEOMETRY"

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

try:
    ## Test for working folder age -- warn and then exit if older than cutoff 
    ## (Extend cutoff age if necessary [to continue processing anyway])
    wkgFldr = os.path.dirname(gdbPath)
    t = os.path.getctime(wkgFldr)
    tt = datetime.datetime.fromtimestamp(t)
    fldrTimeCheck = starttime - tt
    td = datetime.timedelta(days=cutoffage)
    if fldrTimeCheck >= td: # Working folder too old - don't use old data instead of new
        print('WARNING: working folder {} created {} HH:MM:SS.dddddd ago!!!').format(wkgFolder,fldrTimeCheck)
        sys.exit("Folder older than {} days").format(cutoffage)
    else: # Continue processing
        if arcpy.Exists(gdbPath):
            ### Copy tables from local GDB to database
            #*** NOTE: tables have been deleted from SDE previously via 
            #*** CRS2_emptyNDCSTGsde.py - but still check for existence
            # List tables in GDB
            tbll = arcpy.ListTables()
            # Loop through the tables
            print('Copying tables to staging SDE...')
            for tbl in tbll:
                inTBLpath = os.path.join(gdbPath,tbl)
                outTBLname = sdePrefix + tbl
                outTBLpath = os.path.join(sdePath,outTBLname)
                # Check whether table exists in SDE, if so - print warning
                if arcpy.Exists(outTBLpath):
                    print('\tWARNING: {} exists in staging SDE').format(outTBLname)
                # Otherwise, copy
                else:
                    # Ignore tables in exclude list
                    if tbl in excludeList:
                        print('\tIgnoring {}').format(tbl)
                    else:
                        # Copy table from GDB to SDE
                        arcpy.Copy_management(inTBLpath,outTBLpath,"Table") 
                        # Count features and report number - warn if not equal
                        inCount = arcpy.GetCount_management(inTBLpath).getOutput(0)
                        outCount = arcpy.GetCount_management(outTBLpath).getOutput(0)
                        if inCount == outCount:
                            print('\t{} - Copied {} entries to {}').format(tbl,inCount,outTBLname)
                        else:
                            print('ERROR: {} entries copied from {} - {} entries resultant in {}').format(inCount,tbl,outCount,outTBLname)
                        print('\t\t{}').format(datetime.datetime.now())
        else:
            print('ERROR: GDB not found - {}').format(gdbPath)
            sys.exit("Local GDB not found")

        endtime = datetime.datetime.now()
        elapsedtime = endtime - starttime
        print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)  

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print arcpy.GetMessages()








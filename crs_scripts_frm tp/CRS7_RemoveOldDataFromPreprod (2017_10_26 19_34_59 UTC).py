############################################
###   CRS7_RemoveOldDataFromPreprod.py   ###
### Python script to remove all old data ###
###        from preprod NZCONTEXT        ###
###  Karen Chadwick            May 2017  ###
############################################

### Import modules
import arcpy,os,datetime  

starttime = datetime.datetime.now()

################################################################################
###################### Only edit items between here -------------------> #######
preprodPath = r"Database Connections\pp_Dataloader@NZCONTEXT@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### NZContext Staging SDE path
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
preprodPrefix = "NZCONTEXT.MAPDATA."

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

try:
    ##### Find and delete any old data (*_o) from previous month's processing
    # Get lists of tables and FCs
    print('Getting lists of tables and FCs from {} ...').format(preprodPath)
    arcpy.env.workspace = preprodPath
    fcl = arcpy.ListFeatureClasses()
    tbll = arcpy.ListTables()
    # Work through list of feature classes
    print('==> Checking preprod FCs for old data...')
    for fc in fcl:        
        ppfcname = fc[len(preprodPrefix):]
        if fc.endswith("_o") or fc.endswith("_oo"):
            print('\tRemoving {}').format(fc)
            if arcpy.Exists(fc):
                arcpy.Delete_management(fc)
            else:
                print("\t\tERROR: couldn't delete {}").format(fc)
        else:
            print('\t..... ignoring {}').format(fc)
    # Work through list of tables
    print('==> Checking preprod tables for old data...')
    for tbl in tbll:        
        pptblname = tbl[len(preprodPrefix):]
        if tbl.endswith("_o") or tbl.endswith("_oo"):
            print('\tRemoving {}').format(tbl)
            if arcpy.Exists(tbl):
                arcpy.Delete_management(tbl)
            else:
                print("\t\tERROR: couldn't delete {}").format(tbl)
        else:
            print('\t..... ignoring {}').format(tbl)

    endtime = datetime.datetime.now()
    elapsedtime = endtime - starttime
    print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print(arcpy.GetMessages())

#####################################
###     CRS1_repairCRSdata.py     ###
### Python script to list all CRS ###
###  data and repair polygon data ###
### Karen Chadwick  November 2016 ###
#####################################

### Import modules
import arcpy,os,datetime

starttime = datetime.datetime.now()

################################################################################
#############  ENSURE YOU ARE USING THE CURRENT MONTH FOR PROCESSING!!!  #######
################################################################################
###################### Only edit items between here -------------------> #######
wkgFolder = r"C:\Users\ads.EAGLE\Documents\Transpower\Workflows and Scripts\Aug2017_Transpower_supply"  ### Working folder (local drive)
gdbName = "CRS.gdb"  ### Working GDB - default = CRS.gdb - from data provider
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
gdbPath = os.path.join(wkgFolder,gdbName)
cutoffage = 20  # cutoff age in days

# Set environment
arcpy.env.workspace = gdbPath

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

try:
    ### Process CRS data
    print('Working on folder: {}').format(wkgFolder)
    ## Test for working folder age -- warn and then exit if older than cutoff
    ## (Extend cutoff age if necessary [to continue processing anyway])
    t = os.path.getctime(wkgFolder)
    tt = datetime.datetime.fromtimestamp(t)
    fldrTimeCheck = starttime - tt
    td = datetime.timedelta(days=cutoffage)
    if fldrTimeCheck >= td: # Working folder too old - don't use old data instead of new
        print('WARNING: working folder {} created {} HH:MM:SS.dddddd ago!!!').format(wkgFolder,fldrTimeCheck)
        sys.exit("Folder older than {} days").format(cutoffage)
    else: # Continue processing
        ## Delete any extraneous data
        # Delete OWNER_FIXED table
        if arcpy.Exists("OWNER_FIXED"):
            arcpy.Delete_management("OWNER_FIXED")
            print('Deleted OWNER_FIXED table')
        else: print('ERROR: table OWNER_FIXED not found')
        ## Find feature classes
        # Find/report all point feature classes
        pointfcl = arcpy.ListFeatureClasses(feature_type='Point')
        print('Point feature classes:')
        for pointfc in pointfcl:
            print('\t{}').format(pointfc)
        # Find/report all line feature classes
        linefcl = arcpy.ListFeatureClasses(feature_type='Polyline') ## 'Line' also???
        print('Line feature classes:')
        for linefc in linefcl:
            print('\t{}').format(linefc)
        # Find/report all polygon feature classes
        polyfcl = arcpy.ListFeatureClasses(feature_type='Polygon')
        print('Polygon feature classes:')
        for polyfc in polyfcl:
            print('\t{}').format(polyfc)
            # Add field to cadastre dataset
            if polyfc == "CADASTRE":
                print('\t\tAdding field...')
                arcpy.AddField_management(polyfc,"F_issues","TEXT","","",250)
        ## Find tables
        # Find/report all tables
        tbll = arcpy.ListTables()
        print('Tables:')
        for tbl in tbll:
            print('\t{}').format(tbl)
        ## Process feature classes
        # Repair polygon geometry
        print('Repairing polygon geometries...')
        for polyfc in polyfcl:
            pfcPath = os.path.join(gdbPath,polyfc)
            preCount = arcpy.GetCount_management(pfcPath).getOutput(0)
            arcpy.RepairGeometry_management(polyfc)
            postCount = arcpy.GetCount_management(pfcPath).getOutput(0)
            if preCount == postCount:
                print('\t{}: {} - {} features pre- and post-repair').format(datetime.datetime.now(),polyfc,preCount)
            else:
                print('\t{}: {} - {} features pre-repair - {} features post-repair').format(datetime.datetime.now(),
                                                                                            polyfc,preCount,postCount)
        # Rename PLAN to PARCEL_PLAN
        if arcpy.Exists("PLAN"):
            arcpy.Rename_management("PLAN","PARCEL_PLAN")
            print('Renamed PLAN to PARCEL_PLAN')
        else: print('ERROR: feature class PLAN not found')

        endtime = datetime.datetime.now()
        elapsedtime = endtime - starttime
        print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)

        ### Note that number of features pre- and post-repair should be emailed to Technical Specialist
        print('***NOTE: next step/s = email pre- and post-repair feature counts to Technical Specialist...')

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print(arcpy.GetMessages())

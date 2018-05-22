#####################################
###  CRS5_prepareForCRSlabels.py  ###
###  Python script to prepare for ###
###   CRS labels and annotations  ###
### Karen Chadwick  November 2016 ###
#####################################

### Import modules
import arcpy,os,datetime  

starttime = datetime.datetime.now()

################################################################################
#############  ENSURE YOU ARE USING THE CURRENT MONTH FOR PROCESSING!!!  #######
################################################################################
###################### Only edit items between here -------------------> #######
wkgFolder = r"C:\Data\CRS\2017_Aug"  ### Working folder (local drive)
dataSDEpath = r"Database Connections\pp_Dataloader@NZC_STG@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### Staging SDE path
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
dataSDEprefix = "NZC_STG.MAPDATA."
labelGDBname = "labels.gdb"
fcCadastre = "CADASTRE"
tblPrclLabel = "PARCEL_LABEL"
tblCdstrLabel = "CadastreLabel"
pLabelPt = "PARCEL_LABEL_PT"
fcsToCopy = [fcCadastre,"EASEMENT_PARCEL","LEASE_PARCEL","ROAD_CL"]
tblsToCopy = [tblPrclLabel,"TP_PROPERTY","TP_PROPERTY_LINK"]
xlbl = "xlabel"
ylbl = "ylabel"
joinFieldP1 = "PARCEL_ID"
joinFieldP2 = "parcel_id"
outfieldsP1 = ["OBJECTID","parcel_id","full_app","purpose"]
outfieldsP2 = ["area","owner1","owner2","owner3","owner4","title1","title2",
              "title3","title4"]
cutoffage = 20  # cutoff age in days

# Set locations, etc
labelGDBpath = os.path.join(wkgFolder,labelGDBname)
fcCdstrPath = os.path.join(labelGDBpath,fcCadastre)
fcCadP = fcCadastre + "_P"
fcCadPPath = os.path.join(labelGDBpath,fcCadP)
tblPLblPath = os.path.join(labelGDBpath,tblPrclLabel)
tblCLblPath = os.path.join(labelGDBpath,tblCdstrLabel)

# Set environment
arcpy.env.workspace = wkgFolder
arcpy.env.overwriteOutput = True
arcpy.env.configkeyword = "GEOMETRY"

# Set spatial reference - NZTM has WKID = 2193
spRef = arcpy.SpatialReference(2193)

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now()) 

try:
    ##### Process CRS data
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
        ### Create labels GDB - check for existence first
        print('Creating working labels GDB...')
        if arcpy.Exists(labelGDBpath):
            print('WARNING: {} already exists!').format(labelGDBpath)
        else:
            arcpy.CreateFileGDB_management(wkgFolder,labelGDBname)
        ### Copy feature classes from staging database (SDE) to local GDB
        print('Copying feature classes...')
        for fc in fcsToCopy:
            inFCname = dataSDEprefix + fc
            inFCpath = os.path.join(dataSDEpath,inFCname)
            outFCpath = os.path.join(labelGDBpath,fc)
            # Check whether FC exists in GDB, if so - overwrite
            if arcpy.Exists(outFCpath):
                print('\tWARNING: {} already exists - overwriting...').format(fc)
            arcpy.Copy_management(inFCpath,outFCpath)
            # Count features and report number - warn if not equal
            inCount = arcpy.GetCount_management(inFCpath).getOutput(0)
            outCount = arcpy.GetCount_management(outFCpath).getOutput(0)
            if inCount == outCount:
                print('\t{} - Copied {} features to {}').format(inFCname,inCount,fc)
            else:
                print('ERROR: {} features copied from {} - {} features resultant in {}').format(inCount,inFCname,outCount,fc)
            print('\t\t{}').format(datetime.datetime.now())
        ### Copy tables from staging database (SDE) to local GDB
        print('Copying tables...')
        for tbl in tblsToCopy:
            inTBLname = dataSDEprefix + tbl
            inTBLpath = os.path.join(dataSDEpath,inTBLname)
            outTBLpath = os.path.join(labelGDBpath,tbl)
            # Check whether table exists in GDB, if so - overwrite
            if arcpy.Exists(outTBLpath):
                print('\tWARNING: {} already exists - overwriting...').format(tbl)
            arcpy.Copy_management(inTBLpath,outTBLpath)
            # Count features and report number - warn if not equal
            inCount = arcpy.GetCount_management(inTBLpath).getOutput(0)
            outCount = arcpy.GetCount_management(outTBLpath).getOutput(0)
            if inCount == outCount:
                print('\t{} - Copied {} entries to {}').format(inTBLname,inCount,tbl)
            else:
                print('ERROR: {} features copied from {} - {} features resultant in {}').format(inCount,inTBLname,outCount,tbl)
            print('\t\t{}').format(datetime.datetime.now())
        ### Work on cadastre dataset
        print('Adding fields to cadastre...')
        # Change workspace location
        arcpy.env.workspace = labelGDBpath
        ## Add fields for label coordinates
        arcpy.AddField_management(fcCadastre,xlbl,"DOUBLE")
        arcpy.AddField_management(fcCadastre,ylbl,"DOUBLE")
        ## Calculate x,y values
        with arcpy.da.UpdateCursor(fcCdstrPath,["OID@","SHAPE@",xlbl,ylbl]) as cursor:
            for row in cursor:
                lPt = row[1].labelPoint
                row[2] = lPt.X
                row[3] = lPt.Y
                cursor.updateRow(row)
        # Delete cursor and row objects
        del cursor, row        
        ### Select "P" type parcels and export
        # Check whether dataset exists already    
        if arcpy.Exists(fcCadPPath): print('"P" type parcel dataset already exists; overwriting...')
        else: print('Exporting "P" type parcels...')
        # Select "P" type parcels
        arcpy.MakeFeatureLayer_management(fcCdstrPath,"cadastrelyr")
        parcelClause = '"PARCEL_CATEGORY" = ' + "'P'"
        arcpy.SelectLayerByAttribute_management("cadastrelyr","NEW_SELECTION",parcelClause)
        # Export selected parcels
        arcpy.CopyFeatures_management("cadastrelyr",fcCadPPath)            
        print('\t{} created.').format(fcCadP)
        ### Join "P" parcel data to label table and export
        print('Joining "P" type parcels to label table...')
        arcpy.MakeFeatureLayer_management(fcCadPPath,"cadplyr")
        arcpy.MakeTableView_management(tblPLblPath,"labelview")
        arcpy.AddJoin_management("cadplyr",joinFieldP1,tblPLblPath,joinFieldP2,"KEEP_COMMON")
        print('\tJoin successfully created...')
        inCount = arcpy.GetCount_management("cadplyr").getOutput(0)
        print('\tNumber of rows = {}').format(inCount)
        ############################################################################################
        ####################### Block to set field names in parcel_label_pt correctly
        arcpy.TableToTable_conversion("cadplyr",labelGDBpath,"junktable")
        print('\tJunk table created.')
        arcpy.MakeTableView_management("junktable","tmptbl")
        print('\tDescribing temporary table...')
        desc = arcpy.Describe("tmptbl")
        fieldInfo = desc.fieldInfo
        index = 0
        print('\tUpdating field names...')
        while index < fieldInfo.count:
            for of1 in outfieldsP1:
                of1longname = tblPrclLabel + "_" + of1
                of1_1 = of1 + "_1"
                if fieldInfo.getFieldName(index) == of1longname:
                    fieldInfo.setNewName(index,of1_1)
            for of2 in outfieldsP2:
                of2longname = tblPrclLabel + "_" + of2
                if fieldInfo.getFieldName(index) == of2longname:
                    fieldInfo.setNewName(index,of2)
            index += 1
        print('\tField names converted.')    
        arcpy.MakeTableView_management("tmptbl","tmptbl2","","",fieldInfo)
        print('\tMade table view.')
        arcpy.TableToTable_conversion("tmptbl2",labelGDBpath,tblCdstrLabel)
        ### http://gis.stackexchange.com/questions/48353/rename-feature-layer-fields
        ####################### End of block to set field names in parcel_label_pt correctly
        ############################################################################################
        print('\tExported table.')
        arcpy.RemoveJoin_management("cadplyr")
        ### Create a point feature class based on the exported table
        # Make a temporary event layer
        arcpy.MakeXYEventLayer_management(tblCLblPath,xlbl,ylbl,"XYeventlyr",spRef)
        # Output the event layer to the point feature class
        arcpy.FeatureClassToFeatureClass_conversion("XYeventlyr",labelGDBpath,pLabelPt)
                                  
        endtime = datetime.datetime.now()
        elapsedtime = endtime - starttime
        print('{} DONE.  Time taken... {} H:MM:SS.dddddd').format(os.path.basename(__file__),elapsedtime)

        ### Note that mxd should be opened to check extents and create annotations
        print('***NOTE: next step/s = check data extents and create annotations... --> Open ArcGIS')

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print arcpy.GetMessages()

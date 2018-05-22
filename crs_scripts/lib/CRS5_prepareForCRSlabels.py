#####################################
###  CRS_prepareForCRSlabels.py  ###
###  Python script to prepare for ###
###   CRS labels and annotations  ###
### Karen Chadwick  November 2016 ###
### modified by Eagle 2018        ###
#####################################

### Import modules
import arcpy,os,datetime
from config import Settings
import etgLib

arcpy.env.overwriteOutput = True

# Assign values
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
err_message = None

# Set spatial reference - NZTM has WKID = 2193
spRef = arcpy.SpatialReference(2193)

# script name
script_name = os.path.basename(__file__)

args = []

def crs5_prepare_for_labels(args):

    wkgFolder = args[0]
    labelGDBname = args[1]
    sdePath = args[2]
    dataSDEprefix = args[3]
    log = args[4]
    
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

    # variables
    err_message = None
  
    try:

        
        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        etgLib.log_info(log, "working folder: {0}".format(wkgFolder))
        etgLib.log_info(log, "labels gdb: {0}".format(labelGDBpath))        
        etgLib.log_info(log, "sde path: {0}".format(sdePath))
        etgLib.log_info(log, "sde prefix: {0}".format(dataSDEprefix))
        

        # log function
        etgLib.log_info(log, 'calling {}'.format(script_name), True)

   
        ### Create labels GDB - check for existence first    
        etgLib.log_info(log,'Creating working labels GDB...',True)
        if arcpy.Exists(labelGDBpath):
            etgLib.log_info(log,'WARNING: {} already exists!'.format(labelGDBpath))
        else:
            arcpy.CreateFileGDB_management(wkgFolder,labelGDBname)

        ### Copy feature classes from staging database (SDE) to local GDB
        etgLib.log_info(log,'Copying feature classes...',True)
        for fc in fcsToCopy:
            inFCname = dataSDEprefix + fc
            inFCpath = os.path.join(sdePath,inFCname)
            outFCpath = os.path.join(labelGDBpath,fc)
            
            # Check whether FC exists in GDB, if so - overwrite
            if arcpy.Exists(outFCpath):
                 etgLib.log_info(log,'WARNING: {} already exists - overwriting...'.format(fc))
            
            # Check whether table exists in SDE, if so - continue
            if arcpy.Exists(inFCpath):
                arcpy.Copy_management(inFCpath,outFCpath)
                # Count features and report number - warn if not equal
                inCount = arcpy.GetCount_management(inFCpath).getOutput(0)
                outCount = arcpy.GetCount_management(outFCpath).getOutput(0)
                if inCount == outCount:
                    etgLib.log_info(log,'{0} - Copied {1} features to {2}'.format(inFCname,inCount,fc))
                else:
                    etgLib.log_info(log,'ERROR: {0} features copied from {1} - {2} features resultant in {3}'.format(inCount,inFCname,outCount,fc))
            else:
                err_message = '{} does not exist - exit...'.format(fc)
                return err_message

            
        ### Copy tables from staging database (SDE) to local GDB
        etgLib.log_info(log,'Copying tables...',True)
        for tbl in tblsToCopy:
            inTBLname = dataSDEprefix + tbl
            inTBLpath = os.path.join(sdePath,inTBLname)
            outTBLpath = os.path.join(labelGDBpath,tbl)
          
            # Check whether table exists in GDB, if so - overwrite
            if arcpy.Exists(outTBLpath):
                etgLib.log_info(log,'WARNING: {} already exists - overwriting...'.format(tbl))
            
             # Check whether table exists in SDE, if so - continue
            if arcpy.Exists(inTBLpath):
                arcpy.Copy_management(inTBLpath,outTBLpath)
                # Count features and report number - warn if not equal
                inCount = arcpy.GetCount_management(inTBLpath).getOutput(0)
                outCount = arcpy.GetCount_management(outTBLpath).getOutput(0)
                if inCount == outCount:
                    etgLib.log_info(log,'{0} - Copied {1} entries to {2}'.format(inTBLname,inCount,tbl))
                else:
                    etgLib.log_info(log,'ERROR: {0} features copied from {1} - {2} features resultant in {3}'.format(inCount,inTBLname,outCount,tbl))
            else:
                err_message = '{} does not exist - exit...'.format(tbl)
                return err_message
                        
        ### Work on cadastre dataset
        etgLib.log_info(log,'Adding fields to cadastre...',True)
        # Change workspace location
        arcpy.env.workspace = labelGDBpath
        ## Add fields for label coordinates
        arcpy.AddField_management(fcCadastre,xlbl,"DOUBLE")
        arcpy.AddField_management(fcCadastre,ylbl,"DOUBLE")
        ## Calculate x,y values
        etgLib.log_info(log,'calculating  xlabel ylabel field values ...')
        # Change workspace location
        with arcpy.da.UpdateCursor(fcCdstrPath,["OID@","SHAPE@",xlbl,ylbl]) as cursor:
            for row in cursor:
                lPt = row[1].labelPoint
                row[2] = lPt.X
                row[3] = lPt.Y
                cursor.updateRow(row)
        # Delete cursor and row objects
        del cursor, row
               
        ### Select "P" type parcels and export
        etgLib.log_info(log,'Select P type parcels and export ...',True)
        # Check whether dataset exists already    
        if arcpy.Exists(fcCadPPath):
            etgLib.log_info(log,'"P" type parcel dataset already exists; overwriting...')
        else:
            etgLib.log_info(log,'Exporting "P" type parcels...')
        
        # Select "P" type parcels
        etgLib.delete_layer("cadastrelyr")
        arcpy.MakeFeatureLayer_management(fcCdstrPath,"cadastrelyr")
        parcelClause = '"PARCEL_CATEGORY" = ' + "'P'"
        arcpy.SelectLayerByAttribute_management("cadastrelyr","NEW_SELECTION",parcelClause)
        # Export selected parcels
        arcpy.CopyFeatures_management("cadastrelyr",fcCadPPath)            
        # print('\t{} created.').format(fcCadP)
        ### Join "P" parcel data to label table and export
        etgLib.log_info(log,'Joining "P" type parcels to label table...')
        etgLib.delete_layer("cadplyr")
        arcpy.MakeFeatureLayer_management(fcCadPPath,"cadplyr")

        arcpy.MakeTableView_management(tblPLblPath,"labelview")
        arcpy.AddJoin_management("cadplyr",joinFieldP1,tblPLblPath,joinFieldP2,"KEEP_COMMON")
        # # print('\tJoin successfully created...')
        # inCount = arcpy.GetCount_management("cadplyr").getOutput(0)
        # print('\tNumber of rows = {}').format(inCount)
        ############################################################################################
        ####################### Block to set field names in parcel_label_pt correctly
        arcpy.TableToTable_conversion("cadplyr",labelGDBpath,"junktable")
        etgLib.log_info(log,'Junk table created.')
        etgLib.delete_layer("tmptbl")
        arcpy.MakeTableView_management("junktable","tmptbl")
        etgLib.log_info(log,'Describing temporary table...')
        desc = arcpy.Describe("tmptbl")
        fieldInfo = desc.fieldInfo
        index = 0
        etgLib.log_info(log, 'Updating field names...')
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

        etgLib.log_info(log,'Field names converted.')    
        etgLib.delete_layer("tmptbl2")
        arcpy.MakeTableView_management("tmptbl","tmptbl2","","",fieldInfo)
        etgLib.log_info(log,'Made table view.')
        arcpy.TableToTable_conversion("tmptbl2",labelGDBpath,tblCdstrLabel)

        ### http://gis.stackexchange.com/questions/48353/rename-feature-layer-fields
        ####################### End of block to set field names in parcel_label_pt correctly
        ############################################################################################
        etgLib.log_info(log,'Exported table.',True)
        arcpy.RemoveJoin_management("cadplyr")
        ### Create a point feature class based on the exported table
        # Make a temporary event layer
        arcpy.MakeXYEventLayer_management(tblCLblPath,xlbl,ylbl,"XYeventlyr",spRef)
        # Output the event layer to the point feature class
        arcpy.FeatureClassToFeatureClass_conversion("XYeventlyr",labelGDBpath,pLabelPt)
       
    except Exception as e:
        print ("ERROR: {}".format(e))
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
        
    return err_message
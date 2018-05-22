#######################################
###   CRS6_addlDataPreparation.py   ###
### Python script to complete other ###
### CRS data preparation (easement, ###
###     road, connect_property)     ###
### Karen Chadwick    November 2016 ###
#######################################

### Import modules
import arcpy,os,datetime
#import numpy as np  

starttime = datetime.datetime.now()

################################################################################
###################### Only edit items between here -------------------> #######
wkgFolder = r"C:\Data\CRS\2017_Aug"
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
labelGDBname = "labels.gdb" 
fcEsmntPrcl = "EASEMENT_PARCEL"
fcEsmntLease = "EASEMENT_LEASE"
fcLeasePrcl = "LEASE_PARCEL"
fcRoadCL = "ROAD_CL"
#fcRoadCL = "testROAD_CL"
fcRCLdsslv = "ROAD_CL_Dissolve"  ##KC edited "RD_CL_Dissolve" to "ROAD_CL_Dissolve" per discussion with EP 22/6/2017
#fcRCLdsslv = "testRD_CL_Dissolve"
fcCadastre = "CADASTRE"
tblPropLink = "TP_PROPERTY_LINK"
fcPrclPLink = "Parcel_Property_Link"
tblProperty = "TP_PROPERTY"
fcConnectProp = "Connect_Property"
dsslvIDFC = "tempDsslvID"
rfield = "RD_LOC"  # Text field
rfieldlen = 250
statsfields = [["ROAD_NAME1","FIRST"],["LOCATION1","FIRST"]]
propIDfield = "PROPERTY_ID"
parIDfield = "PARCEL_ID"
sfieldlen = 100
cutoffage = 20  # cutoff age in days

# Set locations, etc
labelGDBpath = os.path.join(wkgFolder,labelGDBname)
fcEPrclPath = os.path.join(labelGDBpath,fcEsmntPrcl)
fcELeasePath = os.path.join(labelGDBpath,fcEsmntLease)
fcLPrclPath = os.path.join(labelGDBpath,fcLeasePrcl)
fcRCLPath = os.path.join(labelGDBpath,fcRoadCL)
fcRCdsslvPath = os.path.join(labelGDBpath,fcRCLdsslv)
fcCadP = fcCadastre + "_P"
fcCadPPath = os.path.join(labelGDBpath,fcCadP)
tblPLnkPath = os.path.join(labelGDBpath,tblPropLink)
fcPrclPLPath = os.path.join(labelGDBpath,fcPrclPLink)
tblPropPath = os.path.join(labelGDBpath,tblProperty)
fcCnnctPPath = os.path.join(labelGDBpath,fcConnectProp)
fcDsslvIDPath = os.path.join(labelGDBpath,dsslvIDFC)

# Set environment
arcpy.env.workspace = labelGDBpath
arcpy.env.overwriteOutput = True
arcpy.env.configkeyword= "GEOMETRY"

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

try:
    ##### Process other CRS data
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
        ### Easement lease
        # Copy easement parcel
        print('Copying easement parcel data...')
        arcpy.Copy_management(fcEPrclPath,fcELeasePath)
        # Select records to append
        print('Selecting lease parcels to append...')
        arcpy.MakeFeatureLayer_management(fcLPrclPath,"leaseplyr")
        parcelClause = '"PARCEL_INTENT" = ' + "'LCOV'" + ' OR "PARCEL_INTENT" = ' + "'EASM'"
        arcpy.SelectLayerByAttribute_management("leaseplyr","NEW_SELECTION",parcelClause)
        print('Appending lease parcels...')
        arcpy.Append_management("leaseplyr",fcELeasePath,"NO_TEST")
        ### Road CL
        print('Working on road data...')
        # Add field
        arcpy.AddField_management(fcRoadCL,rfield,"TEXT","","",rfieldlen)
        # Calculate values
        calcexpr = ('!{}!.upper() + ", " + !{}!.upper()').format(statsfields[0][0],statsfields[1][0])
        arcpy.CalculateField_management(fcRoadCL,rfield,calcexpr,"PYTHON_9.3")
        # Dissolve data, using statistics fields
        print('Dissolving...')
        arcpy.Dissolve_management(fcRCLPath,fcRCdsslvPath,rfield,statsfields)
        # Add fields
        arcpy.AddField_management(fcRCLdsslv,statsfields[0][0],"TEXT","","",sfieldlen)
        arcpy.AddField_management(fcRCLdsslv,statsfields[1][0],"TEXT","","",sfieldlen)
        # Calculate values
        sfields = []  
        for i in range(len(statsfields)):
            sfields.append(statsfields[i][0])
            arcpy.AddField_management(fcRCLdsslv,statsfields[i][0],"TEXT","","",sfieldlen)
            sfield = statsfields[i][1] + "_" + statsfields[i][0]
            calcexpr = ('!{}!').format(sfield)
            arcpy.CalculateField_management(fcRCLdsslv,statsfields[i][0],calcexpr,"PYTHON_9.3")
        ### Connect_Property
        print('Working on Connect_Property')
        # Make query table
        mqtblList = [fcCadPPath,tblPLnkPath]
        whereClause = tblPropLink + "." + parIDfield + " = " + fcCadP + "." + parIDfield # NOTE: no quotes - known bug
        arcpy.MakeQueryTable_management(mqtblList,"propQueryTbl","ADD_VIRTUAL_KEY_FIELD","","",whereClause)
        # Get number of rows
        numMQrows = int(arcpy.GetCount_management("propQueryTbl").getOutput(0))
        # Export
        print('Exporting...')
        arcpy.CopyFeatures_management("propQueryTbl",fcPrclPLPath)
        # Check number of rows
        numPPLrows = int(arcpy.GetCount_management(fcPrclPLPath).getOutput(0))
        if numPPLrows != numMQrows:
            print('ERROR: Wrong number of rows exported for link FC; {} versus {}').format(numMQrows,numPPLrows)
            errorLogic = 1
        else:
            print('Correct number of rows exported for link FC.')
        # Dissolve on ID
        print('Dissolving on ID...')
        dfield = tblPropLink + "_" + propIDfield
        sfield = tblPropLink + "_" + parIDfield
        statsfield = [[sfield,"COUNT"]]
        arcpy.Dissolve_management(fcPrclPLink,fcDsslvIDPath,dfield,statsfield)
        # Join the TP_Property table
        print('Preparing to join property table...')
        # Create temporary layer/view
        arcpy.MakeFeatureLayer_management(fcDsslvIDPath,"dsslvlyr")
        arcpy.MakeTableView_management(tblPropPath,"proptblview")
        # Make join
        arcpy.AddJoin_management("dsslvlyr",dfield,"proptblview",propIDfield,"KEEP_ALL")
        print('\tProperty table joined.')
        print('Copying features...')
        # Output
        arcpy.CopyFeatures_management("dsslvlyr",fcCnnctPPath)
        
        endtime = datetime.datetime.now()
        elapsedtime = endtime - starttime
        print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)

        ### Note that Technical Specialist should be advised for copy to pre-prod
        print('***NOTE: next step/s = advise Technical Specialist that data is ready for copy to pre-prod')

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print arcpy.GetMessages()

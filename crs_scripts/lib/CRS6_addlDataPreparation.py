#######################################
###   CRS6_addlDataPreparation.py   ###
### Python script to complete other ###
### CRS data preparation (easement, ###
###     road, connect_property)     ###
### Karen Chadwick    November 2016 ###
### modified by Eagle 2018          ###
#######################################

### Import modules
import arcpy,os,datetime
import etgLib
#import numpy as np  

starttime = datetime.datetime.now()

# Assign values
# labelGDBname = "labels.gdb" 
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

# script name
script_name = os.path.basename(__file__)

args = []

def crs6_add_data_preparation(args):

    # parameters
    wkgFolder = args[0]
    labelGDBname = args[1]   
    log = args[2]

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

    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)

    # variables
    err_message = None

    try:       
        ### Easement lease
        # Copy easement parcel        
        etgLib.log_info(log, 'Copying easement parcel data in labels gdb ...',True)
        arcpy.Copy_management(fcEPrclPath,fcELeasePath)
        
        # Select records to append
        etgLib.log_info(log, 'Selecting lease parcels to append...')
        etgLib.delete_layer("leaseplyr")
        arcpy.MakeFeatureLayer_management(fcLPrclPath,"leaseplyr")
        parcelClause = '"PARCEL_INTENT" = ' + "'LCOV'" + ' OR "PARCEL_INTENT" = ' + "'EASM'"
        arcpy.SelectLayerByAttribute_management("leaseplyr","NEW_SELECTION",parcelClause)

        etgLib.log_info(log, 'Appending lease parcels...')       
        arcpy.Append_management("leaseplyr",fcELeasePath,"NO_TEST")


        ### Road CL        
        etgLib.log_info(log, 'Working on road data...',True)
        if etgLib.field_exist(fcRoadCL, rfield) == False:
            # Add field
            arcpy.AddField_management(fcRoadCL,rfield,"TEXT","","",rfieldlen)
        
        # Calculate values
        etgLib.log_info(log, 'Calculate values: {} ...'.format(rfield))          
        calcexpr = ('!{}!.upper() + ", " + !{}!.upper()').format(statsfields[0][0],statsfields[1][0])
        arcpy.CalculateField_management(fcRoadCL,rfield,calcexpr,"PYTHON_9.3")
        # Dissolve data, using statistics fields
        etgLib.log_info(log, 'Dissolving ...') 
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
        etgLib.log_info(log, 'Working on Connect_Property',True)
        
        # Make query table
        mqtblList = [fcCadPPath,tblPLnkPath]
        whereClause = tblPropLink + "." + parIDfield + " = " + fcCadP + "." + parIDfield # NOTE: no quotes - known bug
        arcpy.MakeQueryTable_management(mqtblList,"propQueryTbl","ADD_VIRTUAL_KEY_FIELD","","",whereClause)
        # Get number of rows
        numMQrows = int(arcpy.GetCount_management("propQueryTbl").getOutput(0))
        # Export        
        etgLib.log_info(log, 'Exporting...') 
        arcpy.CopyFeatures_management("propQueryTbl",fcPrclPLPath)
        # Check number of rows
        numPPLrows = int(arcpy.GetCount_management(fcPrclPLPath).getOutput(0))
        if numPPLrows != numMQrows:
            etgLib.log_error(log, 'ERROR: Wrong number of rows exported for link FC; {} versus {}'.format(numMQrows,numPPLrows))           
        else:
            etgLib.log_info(log, 'Correct number of rows exported for link FC.')


        # Dissolve on ID
        etgLib.log_info(log, 'Dissolving on ID...',True)       
        dfield = tblPropLink + "_" + propIDfield
        sfield = tblPropLink + "_" + parIDfield
        statsfield = [[sfield,"COUNT"]]
        arcpy.Dissolve_management(fcPrclPLink,fcDsslvIDPath,dfield,statsfield)

        # Join the TP_Property table
        etgLib.log_info(log, 'Preparing to join property table...')  
        # Create temporary layer/view
        etgLib.delete_layer('dsslvlyr')
        arcpy.MakeFeatureLayer_management(fcDsslvIDPath,"dsslvlyr")
        etgLib.delete_layer('proptblview')
        arcpy.MakeTableView_management(tblPropPath,"proptblview")

        # Make join
        etgLib.log_info(log, 'Adding join ...') 
        arcpy.AddJoin_management("dsslvlyr",dfield,"proptblview",propIDfield,"KEEP_ALL")
        etgLib.log_info(log, 'Property table joined') 
        
        # Output
        etgLib.log_info(log, 'Copying features...')
        arcpy.CopyFeatures_management("dsslvlyr",fcCnnctPPath)
        
        etgLib.log_process_time(log,starttime)  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message
 
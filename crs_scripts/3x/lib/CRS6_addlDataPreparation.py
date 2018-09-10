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

starttime = datetime.datetime.now()

# Assign values
fcEsmntPrcl = "EASEMENT_PARCEL"
fcEsmntLease = "EASEMENT_LEASE"
fcLeasePrcl = "LEASE_PARCEL"
fcRoadCL = "ROAD_CL"
fcRCLdsslv = "ROAD_CL_Dissolve"  ##KC edited "RD_CL_Dissolve" to "ROAD_CL_Dissolve" per discussion with EP 22/6/2017
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

# variables
args = []
err_message = None
log_messages = []


def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def field_exist (fc, fld):   
    isExist = False
    lstFields = arcpy.ListFields(fc)
    fieldNames = [f.name for f in lstFields]

    if fld in fieldNames:
        print ("field exists - " + fld)
        isExist = True    
    return isExist        

def delete_layer(lyr):
    if arcpy.Exists(lyr):
        print ("{} exists - deleted".format(lyr))
        arcpy.Delete_management(lyr)

def crs6_add_data_preparation(args):

    # parameters
    wkgFolder = args[0]
    labelGDBname = args[1]   

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
    log_msg ('calling {}'.format(script_name))

    # variables
    err_message = None

    try:       
        ### Easement lease
        # Copy easement parcel        
        log_msg ('Copying easement parcel data in labels gdb ...')
        arcpy.Copy_management(fcEPrclPath,fcELeasePath)
        
        # Select records to append
        log_msg ('Selecting lease parcels to append...')
        delete_layer("leaseplyr")
        arcpy.MakeFeatureLayer_management(fcLPrclPath,"leaseplyr")
        parcelClause = '"PARCEL_INTENT" = ' + "'LCOV'" + ' OR "PARCEL_INTENT" = ' + "'EASM'"
        arcpy.SelectLayerByAttribute_management("leaseplyr","NEW_SELECTION",parcelClause)

        log_msg ('Appending lease parcels...')       
        arcpy.Append_management("leaseplyr",fcELeasePath,"NO_TEST")


        ### Road CL        
        log_msg ('Working on road data...')
        if field_exist(fcRoadCL, rfield) == False:
            # Add field
            arcpy.AddField_management(fcRoadCL,rfield,"TEXT","","",rfieldlen)
        
        # Calculate values
        log_msg ('Calculate values: {} ...'.format(rfield))          
        calcexpr = ('!{}!.upper() + ", " + !{}!.upper()').format(statsfields[0][0],statsfields[1][0])
        arcpy.CalculateField_management(fcRoadCL,rfield,calcexpr,"PYTHON_9.3")
        # Dissolve data, using statistics fields
        log_msg ('Dissolving ...') 
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
        log_msg ( 'Working on Connect_Property')
        
        # Make query table
        mqtblList = [fcCadPPath,tblPLnkPath]
        whereClause = tblPropLink + "." + parIDfield + " = " + fcCadP + "." + parIDfield # NOTE: no quotes - known bug
        arcpy.MakeQueryTable_management(mqtblList,"propQueryTbl","ADD_VIRTUAL_KEY_FIELD","","",whereClause)
        # Get number of rows
        numMQrows = int(arcpy.GetCount_management("propQueryTbl").getOutput(0))
        # Export        
        log_msg ('Exporting...') 
        arcpy.CopyFeatures_management("propQueryTbl",fcPrclPLPath)
        # Check number of rows
        numPPLrows = int(arcpy.GetCount_management(fcPrclPLPath).getOutput(0))
        if numPPLrows != numMQrows:
            log_msg ( 'ERROR: Wrong number of rows exported for link FC; {} versus {}'.format(numMQrows,numPPLrows))           
        else:
            log_msg ('Correct number of rows exported for link FC.')


        # Dissolve on ID
        log_msg ( 'Dissolving on ID...')       
        dfield = tblPropLink + "_" + propIDfield
        sfield = tblPropLink + "_" + parIDfield
        statsfield = [[sfield,"COUNT"]]
        arcpy.Dissolve_management(fcPrclPLink,fcDsslvIDPath,dfield,statsfield)

        # Join the TP_Property table
        log_msg ('Preparing to join property table...')  
        # Create temporary layer/view
        delete_layer('dsslvlyr')
        arcpy.MakeFeatureLayer_management(fcDsslvIDPath,"dsslvlyr")
        delete_layer('proptblview')
        arcpy.MakeTableView_management(tblPropPath,"proptblview")

        # Make join
        log_msg ( 'Adding join ...') 
        arcpy.AddJoin_management("dsslvlyr",dfield,"proptblview",propIDfield,"KEEP_ALL")
        log_msg ('Property table joined') 
        
        # Output
        log_msg ('Copying features...')
        arcpy.CopyFeatures_management("dsslvlyr",fcCnnctPPath)
        
        log_msg ( "Process time: %s \n" % str(datetime.datetime.now()-starttime))  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message, log_messages
 
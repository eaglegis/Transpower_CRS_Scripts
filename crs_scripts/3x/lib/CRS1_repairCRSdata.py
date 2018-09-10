#####################################
###     CRS1_repairCRSdata.py     ###
### Python script to list all CRS ###
###  data and repair polygon data ###
### Karen Chadwick  November 2016 ###
### modified by Eagle 2018        ### 
#####################################

### Import modules
import arcpy, os
import datetime, time

# variables
args = []
err_message = None
log_messages = []

def log_msg(msg):
    print (msg)
    log_messages.append(msg)


def print_list(lst):
    for itm in lst:
        print(itm)

def delete_layer(lyr):
    if arcpy.Exists(lyr):
        print ("{} exists - deleted".format(lyr))
        arcpy.Delete_management(lyr)  

def field_exist (fc, fld):   
    isExist = False
    lstFields = arcpy.ListFields(fc)
    fieldNames = [f.name for f in lstFields]

    if fld in fieldNames:
        print ("field exists - " + fld)
        isExist = True
    
    return isExist        

def crs1_repair_crs_data(args):
    # script name
    script_name = os.path.basename(__file__)

    # script parameters
    gdb = args[0]    

    # Set environment
    arcpy.env.workspace = gdb
    
    # log function
    log_msg('calling {}'.format(script_name))

    # start time
    starttime = datetime.datetime.now()

    # variables
    err_message = None
    fc_cadastre = 'CADASTRE'
    fld_cadastre = 'F_issues'
    fc_ownerfixed = 'OWNER_FIXED'
    fc_plan ='PLAN'
    fc_parcelplan = 'PARCEL_PLAN'

    try:
              
        ## Delete any extraneous data
        log_msg('Delete any extraneous data')
        delete_layer(fc_ownerfixed)

        # list all the feature classes
        pointfcl = []
        linefcl = []
        polyfcl = [] 
        tbll = []           

        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:                
            desc = arcpy.Describe(fc)
            if desc.shapeType == 'Point':
                pointfcl.append(fc)
            elif desc.shapeType == 'Polyline':
                linefcl.append(fc)
            elif desc.shapeType == 'Polygon':
                polyfcl.append(fc)
            else:
                pass
        
        log_msg('Point feature classes:\n')
        print_list(pointfcl)
        log_msg('Polyline feature classes:\n')
        print_list(linefcl)
        log_msg('Polygon feature classes:\n')
        print_list(polyfcl)

        log_msg('tables:')
        tbll = arcpy.ListTables()
        print_list(tbll)
                    
        # add field to CADASTRE
        if field_exist(fc_cadastre, fld_cadastre) == False:
            log_msg('adding field [{0}] in {1}'.format(fld_cadastre,fc_cadastre))
            arcpy.AddField_management(fc_cadastre,fld_cadastre,"TEXT","","",250)

        # Repair polygon geometry
        print ('Repairing polygon geometries...')
        for polyfc in polyfcl:                
            preCount = arcpy.GetCount_management(polyfc).getOutput(0)
            arcpy.RepairGeometry_management(polyfc)
            postCount = arcpy.GetCount_management(polyfc).getOutput(0)
            log_msg('{0}: features pre-repair {1} - post-repair {2}'.format(polyfc, preCount, postCount))
            
        # Rename PLAN to PARCEL_PLAN
        if arcpy.Exists(fc_plan):
            arcpy.Rename_management(fc_plan,fc_parcelplan)
            log_msg('Renamed {0} to {1}'.format(fc_plan,fc_parcelplan))
        else:               
            log_msg('ERROR: feature class {} not found'.format(fc_plan))    
        
        log_msg( "Process time: %s \n" % str(datetime.datetime.now()-starttime))
        

        # ### Note that number of features pre- and post-repair should be emailed to Technical Specialist
        # print('***NOTE: next step/s = email pre- and post-repair feature counts to Technical Specialist...')

    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)

    return err_message , log_messages    

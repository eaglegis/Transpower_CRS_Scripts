######################################
###     CRS2_emptyNDCSTGsde.py     ###
###  Python script to remove data  ###
###      from NDCSTG database      ###
### Karen Chadwick   November 2016 ###
######################################

### Import modules
import arcpy,os,datetime  

starttime = datetime.datetime.now()

################################################################################
###################### Only edit items between here -------------------> #######
sdePath = r"Database Connections\pp_Dataloader@NZC_STG@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### Staging SDE path on NDCSTG_SPAT_AG.transpower.co.nz,12426 / NZC_STGDataloader username
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
itemsToKeep = ["NZC_STG.MapData.CRS_AuditTable","NZC_STG.MapData.CRS_SpatialTablesToUpdate",
               "NZC_STG.MapData.CRS_TablesToUpdate","NZC_STG.MapData.DATA_LOAD_DATE",
               "NZC_STG.MapData.tp_parcel_address_vw","NZC_STG.MapData.tp_parcel_title_owner_vw",
               "NZC_STG.MapData.tp_parcel_title_vw","NZC_STG.MapData.tp_title_address_vw",
               "NZC_STG.MapData.tp_title_owner_address_vw","NZC_STG.MapData.vwRecordCounts"]

# Set environment
arcpy.env.workspace = sdePath
                
print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

try:
    ### Prepare staging database
    print('Working on database: {}').format(sdePath)

    # Find all feature classes and delete a subset
    fcl = arcpy.ListFeatureClasses()
    print('Deleting subset of feature classes:')
    for fc in fcl:
        if fc in itemsToKeep:
            print('\tKept: {}').format(fc)
        else:
            try:
                arcpy.Delete_management(fc)
                print('\tDeleted: {}').format(fc)
            except:
                print('***ERROR*** while deleting {} - delete manually!!!').format(fc)
    # Find all tables and delete a subset
    tbll = arcpy.ListTables()
    print('Deleting subset of tables...')
    for tbl in tbll:
        if tbl in itemsToKeep:
            print('\tKept: {}').format(tbl)
        else:
            try:
                arcpy.Delete_management(tbl)
                print('\tDeleted: {}').format(tbl)
            except:
                print('***ERROR*** while deleting {} - delete manually!!!').format(tbl)

    endtime = datetime.datetime.now()
    elapsedtime = endtime - starttime
    print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)  

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print arcpy.GetMessages()
    

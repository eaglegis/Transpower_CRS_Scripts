#########################################
###     CRS9_checkPreprodCounts.py    ###
###   Python script to check counts   ###
###  for all preprod feature classes  ###
###             and tables            ###
###  Karen Chadwick       March 2017  ###
#########################################

### Import modules
import arcpy,os,datetime
import etgLib 

starttime = datetime.datetime.now()


dummyVal = -9999
tblIgnoreList = ["INSTRUMENT"]

# script name
script_name = os.path.basename(__file__)

args = []

def crs9_check_preprod_feature_counts(args):
    # parameters
    labelsPath = args[0]
    preprodPath = args[1]
    preprodPrefix = args[2]
    stagingPath = args[3]  
    stagingPrefix = args[4] 
    log = args[5]

    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)

    # variables
    err_message = None



    try:
       
        ### Get lists of tables and FCs
        # Get tables and FCs from labels GDB
        etgLib.log_info(log, 'Getting lists of tables and FCs from labels GDB...')        
        arcpy.env.workspace = labelsPath
        fcllblg = arcpy.ListFeatureClasses()
        tblllblg = arcpy.ListTables()
        # Get tables and FCs from staging SDE        
        etgLib.log_info(log, 'Getting lists of tables and FCs from staging SDE...')     
        arcpy.env.workspace = stagingPath
        fclstgs = arcpy.ListFeatureClasses()
        tbllstgs = arcpy.ListTables()
        # Get tables and FCs from preprod SDE
        etgLib.log_info(log, 'Getting lists of tables and FCs from preprod SDE...')  
        arcpy.env.workspace = preprodPath
        fclpprs = arcpy.ListFeatureClasses()
        tbllpprs = arcpy.ListTables()
        ### Work through lists of feature classes
        etgLib.log_info(log, '==> Checking FC counts for preprod...', True)  
        arcpy.env.workspace = preprodPath
        # Get preprod values
        for pprsfc in fclpprs:        
            # Ignore views and old data
            pprsfcname = pprsfc[len(preprodPrefix):]
            if pprsfcname.endswith("_1") or pprsfcname.endswith("_o") or pprsfcname.endswith("_vw") or pprsfcname.endswith("_oo"):
                etgLib.log_info(log, '{} - ignoring...'.format(pprsfc) )            
            else:
                # Set prelim values
                pprsfccount = dummyVal
                stgsfccount = dummyVal
                lblgfccount = dummyVal
                # crsgfccount = dummyVal
                # Get preprod count
                pprsfccount = arcpy.GetCount_management(pprsfc).getOutput(0)               
                etgLib.log_info(log, '{} - preprod count = {}'.format(pprsfcname,pprsfccount))
                # Find comparable staging FC
                for stgsfc in fclstgs:
                    stgsfcname = stgsfc[len(stagingPrefix):]
                    if stgsfcname == pprsfcname:
                        # Get staging count
                        stgsfcpath = os.path.join(stagingPath,stgsfc)
                        stgsfccount = arcpy.GetCount_management(stgsfcpath).getOutput(0)
                        stgsfccountname = stgsfcname
                        continue
                # Report staging count status
                if stgsfccount != dummyVal and stgsfccount != pprsfccount:            
                    etgLib.log_info(log, '*****ERROR!!!***** preprod count = {0} but staging count = {1}'.format(pprsfccount,stgsfccount))
                elif stgsfccount == dummyVal:                
                    etgLib.log_info(log, '{} not found in staging SDE'.format(pprsfcname))
                else:                
                    etgLib.log_info(log, '{0} - staging count = {1}'.format(stgsfccountname,stgsfccount))
                # Find comparable labels FC
                for lblgfc in fcllblg:
                    if lblgfc == pprsfcname:
                        # Get labels count
                        lblgfcpath = os.path.join(labelsPath,lblgfc)
                        lblgfccount = arcpy.GetCount_management(lblgfcpath).getOutput(0)
                        lblgfccountname = lblgfc
                        continue
                # Report labels count status
                if lblgfccount != dummyVal and lblgfccount != pprsfccount:                    
                    etgLib.log_info(log, '*****ERROR!!!***** preprod count = {0} but labels count = {1}'.format(pprsfccount,lblgfccount))
                elif lblgfccount == dummyVal:                    
                    etgLib.log_info(log, '{} not found in labels SDE'.format(pprsfcname))
                else:                   
                    etgLib.log_info(log, '{0} - labels count = {1}'.format(lblgfccountname,lblgfccount))
        
        ### Work through lists of tables        
        etgLib.log_info(log, '==> Checking table counts for preprod...', True) 
        # Get preprod values
        for pprstbl in tbllpprs:
            # Ignore views and old data
            pprstblname = pprstbl[len(preprodPrefix):]
            if pprstblname.endswith("_o") or pprstblname.endswith("_vw") or pprstblname.endswith("_oo") or \
            pprstblname.startswith("mv_") or pprstblname.startswith("vw") or pprstblname.startswith("VW_"):                
                etgLib.log_info(log, '{} - ignoring...'.format(pprstblname) )  
            else:
                # Set prelim values
                pprstblcount = dummyVal
                stgstblcount = dummyVal
                lblgtblcount = dummyVal
                # Get preprod count
                #pprstblname = pprstbl[len(preprodPrefix):]
                if pprstblname in tblIgnoreList:
                    etgLib.log_info(log, 'WARNING: ignoring {} ***** manual check required *****'.format(pprstblname))                    
                    continue
                else:
                    pprstblcount = arcpy.GetCount_management(pprstbl).getOutput(0)                    
                    etgLib.log_info(log, '{} - preprod count = {}'.format(pprstblname,pprstblcount))
                    # Find comparable staging table
                    for stgstbl in tbllstgs:
                        stgstblname = stgstbl[len(stagingPrefix):]
                        if stgstblname == pprstblname:
                            # Get staging count
                            stgstblpath = os.path.join(stagingPath,stgstbl)
                            stgstblcount = arcpy.GetCount_management(stgstblpath).getOutput(0)
                            stgstblcountname = stgstblname
                            continue
                    # Report staging count status
                    if stgstblcount != dummyVal and stgstblcount != pprstblcount:                    
                        etgLib.log_info(log, '*****ERROR!!!***** preprod count = {0} but staging count = {1}'.format(pprstblcount,stgstblcount))
                    elif stgstblcount == dummyVal:                        
                        etgLib.log_info(log, '{} not found in staging SDE'.format(pprstblname))
                    else:                        
                        etgLib.log_info(log, '{0} - staging count = {1}'.format(stgstblcountname,stgstblcount))
                    # Find comparable labels table
                    for lblgtbl in tblllblg:
                        if lblgtbl == pprstblname:
                            # Get labels count
                            lblgtblpath = os.path.join(labelsPath,lblgtbl)
                            lblgtblcount = arcpy.GetCount_management(lblgtblpath).getOutput(0)
                            lblgtblcountname = lblgtbl
                            continue
                    # Report labels count status
                    if lblgtblcount != dummyVal and lblgtblcount != pprstblcount:              
                        etgLib.log_info(log, '*****ERROR!!!***** preprod count = {0} but labels count = {1}'.format(pprstblcount,lblgtblcount))
                    elif lblgtblcount == dummyVal:                
                        etgLib.log_info(log, '{} not found in labels GDB'.format(pprstblname))
                    else:                        
                        etgLib.log_info(log, '{0} - labels count = {1}'.format(lblgtblcountname,lblgtblcount))
                
        etgLib.log_process_time(log,starttime)  

    except Exception as e: 
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message

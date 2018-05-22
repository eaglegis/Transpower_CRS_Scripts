#########################################
###     CRS9_checkPreprodCounts.py    ###
###   Python script to check counts   ###
###  for all preprod feature classes  ###
###             and tables            ###
###  Karen Chadwick       March 2017  ###
#########################################

### Import modules
import arcpy,os,datetime  

starttime = datetime.datetime.now()

################################################################################
###################### Only edit items between here -------------------> #######
labelsPath = r"C:\Data\CRS\labels.gdb"
stagingPath = r"Database Connections\pp_Dataloader@NZC_STG@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### Staging SDE path on NDCSTG_SPAT_AG.transpower.co.nz,12426 / NZC_STGDataloader
preprodPath = r"Database Connections\pp_Dataloader@NZCONTEXT@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### Staging SDE path
###################### <--------------------------------------- and here #######
################################################################################

# Assign values
stagingPrefix = "NZC_STG.MapData."
preprodPrefix = "NZCONTEXT.MAPDATA."
dummyVal = -9999
tblIgnoreList = ["INSTRUMENT"]
cutoffage = 30  # cutoff age in days

print('{}: {}').format(os.path.basename(__file__),datetime.datetime.now())

try:
    ##### Check counts for preprod data
    # Test for working folder age -- warn and then exit if older than cutoff 
    # (Extend cutoff age if necessary [to continue processing anyway])
    wkgFolder = os.path.dirname(labelsPath)
    print('Checking {} age...').format(wkgFolder)
    t = os.path.getctime(wkgFolder)
    tt = datetime.datetime.fromtimestamp(t)
    fldrTimeCheck = starttime - tt
    td = datetime.timedelta(days=cutoffage)
    if fldrTimeCheck >= td: # Working folder too old - don't use old data instead of new
        print('WARNING: working folder {} created {} HH:MM:SS.dddddd ago!!!').format(wkgFolder,fldrTimeCheck)
        sys.exit("Folder older than {} days").format(cutoffage)
    else: # Continue processing  
        ### Get lists of tables and FCs
        # Get tables and FCs from labels GDB
        print('Getting lists of tables and FCs from labels GDB...')
        arcpy.env.workspace = labelsPath
        fcllblg = arcpy.ListFeatureClasses()
        tblllblg = arcpy.ListTables()
        # Get tables and FCs from staging SDE
        print('Getting lists of tables and FCs from staging SDE...')
        arcpy.env.workspace = stagingPath
        fclstgs = arcpy.ListFeatureClasses()
        tbllstgs = arcpy.ListTables()
        # Get tables and FCs from preprod SDE
        print('Getting lists of tables and FCs from preprod SDE...')
        arcpy.env.workspace = preprodPath
        fclpprs = arcpy.ListFeatureClasses()
        tbllpprs = arcpy.ListTables()
        ### Work through lists of feature classes
        print('==> Checking FC counts for preprod...')
        # Get preprod values
        for pprsfc in fclpprs:        
            # Ignore views and old data
            pprsfcname = pprsfc[len(preprodPrefix):]
            if pprsfcname.endswith("_1") or pprsfcname.endswith("_o") or pprsfcname.endswith("_vw") or pprsfcname.endswith("_oo"):
                print('\t{} - ignoring...').format(pprsfc)
            else:
                # Set prelim values
                pprsfccount = dummyVal
                stgsfccount = dummyVal
                lblgfccount = dummyVal
                crsgfccount = dummyVal
                # Get preprod count
                pprsfccount = arcpy.GetCount_management(pprsfc).getOutput(0)
                print('\t{} - preprod count = {}').format(pprsfcname,pprsfccount)
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
                    print('\t\t*****ERROR!!!***** preprod count = {} but staging count = {}').format(pprsfccount,stgsfccount)
                elif stgsfccount == dummyVal:
                    print('\t\t{} not found in staging SDE').format(pprsfcname)
                else:
                    print('\t\t{} - staging count = {}').format(stgsfccountname,stgsfccount)
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
                    print('\t\t\t*****ERROR!!!***** preprod count = {} but labels count = {}').format(pprsfccount,lblgfccount)
                elif lblgfccount == dummyVal:
                    print('\t\t\t{} not found in labels GDB').format(pprsfcname)
                else:
                    print('\t\t\t{} - labels count = {}').format(lblgfccountname,lblgfccount)
        ### Work through lists of tables
        print('==> Checking table counts for preprod...')
        # Get preprod values
        for pprstbl in tbllpprs:
            # Ignore views and old data
            pprstblname = pprstbl[len(preprodPrefix):]
            if pprstblname.endswith("_o") or pprstblname.endswith("_vw") or pprstblname.endswith("_oo") or \
               pprstblname.startswith("mv_") or pprstblname.startswith("vw") or pprstblname.startswith("VW_"):
                print('\t{} - ignoring...').format(pprstblname)
            else:
                # Set prelim values
                pprstblcount = dummyVal
                stgstblcount = dummyVal
                lblgtblcount = dummyVal
                # Get preprod count
                #pprstblname = pprstbl[len(preprodPrefix):]
                if pprstblname in tblIgnoreList:
                    print('\tWARNING: ignoring {} ***** manual check required *****').format(pprstblname)
                    continue
                else:
                    pprstblcount = arcpy.GetCount_management(pprstbl).getOutput(0)
                    print('\t{} - preprod count = {}').format(pprstblname,pprstblcount)
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
                        print('\t\t*****ERROR!!!***** preprod count = {} but staging count = {}').format(pprstblcount,stgstblcount)
                    elif stgstblcount == dummyVal:
                        print('\t\t{} not found in staging SDE').format(pprstblname)
                    else:
                        print('\t\t{} - staging count = {}').format(stgstblcountname,stgstblcount)
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
                        print('\t\t\t*****ERROR!!!***** preprod count = {} but labels count = {}').format(pprstblcount,lblgtblcount)
                    elif lblgtblcount == dummyVal:
                        print('\t\t\t{} not found in labels GDB').format(pprstblname)
                    else:
                        print('\t\t\t{} - labels count = {}').format(lblgtblcountname,lblgtblcount)
                
    endtime = datetime.datetime.now()
    elapsedtime = endtime - starttime
    print('DONE.  Time taken... {} H:MM:SS.dddddd').format(elapsedtime)

except:
    print('\nERROR while running script!  Exiting...\n\n***Error messages:\n==================')
    print(arcpy.GetMessages())

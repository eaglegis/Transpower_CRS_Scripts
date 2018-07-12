# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main4_Copy_To_CONTEXT.py
# Created on: 2018-06-08
# 
# Usage: > 
# Description: copy data from Staging database to Context database
# ---------------------------------------------------------------------------

import sys
import arcpy
import os
import datetime, time
from lib import etgLib
from config import Settings

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
labelGDBname = Settings.LABEL_GDB_NAME

contextSdePath = Settings.CONTEXT_SDE_PATH
contextSdePrefix = Settings.CONTEXT_SDE_PREFIX

stgSdePath = Settings.STG_SDE_PATH
stgSdePrefix = Settings.STG_SDE_PREFIX

excludedTables = ['TITLE', 'CRS_AuditTable', 'CRS_SpatialTablesToUpdate', 'CRS_TablesToUpdate', 'tp_parcel_address_vw', 'tp_parcel_title_owner_vw', 'tp_parcel_title_vw', 'tp_title_address_vw', 'tp_title_owner_address_vw','vwRecordCountstp']


# ---------------- email settings ---------------
sendMail = Settings.SEND_EMAIL      # if true, the log file will be sent by email, if false, no email is sent
smtpServer = Settings.SMTP_SERVER
emailFrom = Settings.FROM_EMAIL    
emailTo = Settings.TO_EMAIL  # recipients email list, separated by comma
emailSubject1 = Settings.EMAIL_SUBJECT
emailText = Settings.EMAIL_BODYTEXT
emailAttachments = None

# set workspace
arcpy.env.workspace = stgSdePath

# script name
script_name = os.path.basename(__file__)
# logfile
log_name ='log_{0}'.format(os.path.splitext(script_name)[0])

# outputs for each sub functions
err_msg = None

## ---------------- sub functions ----------------
def exit_sys(log, txt, start, sendmail = False):    
    etgLib.log_error(log, txt)
    etgLib.log_close(log, start)
    if sendmail:
        emailSubject = script_name + " - Failed"        
        etgLib.send_email(emailFrom, emailTo, emailSubject, emailText, emailAttachments, smtpServer)       
    sys.exit()


##  ------------------ main function-------------------------
def main_func():
   
    start=datetime.datetime.now()
    err_msg = None
   
    global emailAttachments

    try:               
        log_path = os.path.join(sys.path[0], 'logs')      
        log, logfile = etgLib.create_log(log_path, log_name)
        if log == None: exit_sys(log, "can't create a log file", start)        

        emailAttachments = [logfile]

        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        etgLib.log_info(log, "Staging sde path: {0}".format(stgSdePath))
        etgLib.log_info(log, "Context sde path: {0}".format(contextSdePath))
        
        ## ========================================
        ## Process: copy data from NZC_STG to NZCONTEXT
        ## ======================================== 
        etgLib.log_info(log,'copy data from NZC_STG to NZCONTEXT ...',True)
        # Get lists of tables and FCs
        etgLib.log_info(log, 'Getting lists of tables and FCs from NZC_STG ...')
        arcpy.env.workspace = stgSdePath
        
        fcl = arcpy.ListFeatureClasses()
        tbll = arcpy.ListTables()  

        # Process: Copy Feature classes
        etgLib.log_info(log,'Copy Features from NZC_STG database to NZCONTEXT pre-prod SDE ...',True)
        for fc in fcl:
            # the feature class name already include the psde prefix name
            fcName =  fc.split(".")[2]
            if fcName not in excludedTables:
                inFCname = stgSdePrefix + fcName            
                inFCpath = os.path.join(stgSdePath,inFCname)           
                out_fc_name = contextSdePrefix + fcName + "_1"
                outFCpath = os.path.join(contextSdePath,out_fc_name)
                etgLib.log_info(log,'in feature class ...: {}'.format(inFCpath))            
                etgLib.log_info(log,'out feature class ...: {}'.format(outFCpath))
                if arcpy.Exists(inFCpath):                          
                    etgLib.log_info(log,'Copying ...: {}'.format(inFCname))
                    arcpy.Copy_management(inFCpath,outFCpath, "FeatureClass")
                else:
                    etgLib.log_info(log,'feature class does not exist ...: {}'.format(inFCname))

        

        # Process: Copy tables
        etgLib.log_info(log,'Copy Tables from NZC_STG database to NZCONTEXT pre-prod SDE ...',True)
        for tbl in tbll:
            tblName =  tbl.split(".")[2]
            if tblName not in excludedTables:                
                inTBLname = stgSdePrefix + tblName
                inTBLpath = os.path.join(stgSdePrefix,inTBLname)               
                out_tbl_name = contextSdePrefix + tblName + "_1"
                outTBLpath = os.path.join(contextSdePath,out_tbl_name)
                etgLib.log_info(log,'in table ...: {}'.format(inFCpath))            
                etgLib.log_info(log,'out table ...: {}'.format(outFCpath))
                if arcpy.Exists(inTBLpath):
                    etgLib.log_info(log,'Copying ...: {}'.format(inTBLname))
                    arcpy.Copy_management(inTBLpath,outTBLpath)
                else:
                    etgLib.log_info(log,'table does not exist ...: {}'.format(inTBLname))
        
        # Copy TITLE in CONTEXT to TITLE_o
        etgLib.log_info(log,'Copy TITLE table to TITLE_o in NZCONTEXT pre-prod SDE ...',True)
        inTBLname = contextSdePrefix + "TITLE"
        inTBLpath = os.path.join(contextSdePath,inTBLname)               
        out_tbl_name = contextSdePrefix + "TITLE_o"
        outTBLpath = os.path.join(contextSdePath,out_tbl_name)
        if arcpy.Exists(inTBLpath):
            etgLib.log_info(log,'Copying ...: {}'.format(inTBLname))
            arcpy.Copy_management(inTBLpath,outTBLpath)

        # truncate and append Title in CONTEXT
        etgLib.log_info(log,'truncate and append TITLE in CONTEXT ...')
        arcpy.TruncateTable_management(inTBLname)

        stg_title_table = stgSdePrefix + "TITLE"   
        in_tables = [stg_title_table]
        arcpy.Append_management(in_tables, inTBLpath, "TEST") 
        
        # copying annotation layers to CONTEXT sde
        etgLib.log_info(log,'copying annotation layers from labels.gdb to CONTEXT sde ...',True)
        annoLayers = ['PARCEL_LABELSAnno2_5k', 'PARCEL_LABELSAnno5k', 'PARCEL_LABELSAnno10k', 'PARCEL_LABELSAnno20k','PARCEL_LABEL_PT', 'EASEMENT_LEASE', 'ROAD_CL_Dissolve']

        lbl_gdb = os.path.join(wkgFolder,labelGDBname)        
        arcpy.env.workspace = lbl_gdb
        
        for fc in annoLayers:                      
            inFCpath = os.path.join(lbl_gdb,fc)
            out_fc_name = contextSdePrefix + fc
            outFCpath = os.path.join(contextSdePath,out_fc_name)
            if arcpy.Exists(inFCpath):
                etgLib.log_info(log,'Copying ...: {}'.format(fc))            
                arcpy.Copy_management(inFCpath,outFCpath, "FeatureClass")

       
    except Exception as e:                     
        err_msg =  "ERROR while running {0}: {1}" .format(script_name,e)

    etgLib.log_close(log, start)
    print ("Finished!!!  Please check the result in ArcMap or ArcCatalog")
    

    if sendMail:
        if err_msg != None:
            emailSubject = 'Run {} - Failed'.format(script_name)
        else:
            emailSubject = 'Run {} - Successful'.format(script_name)

        etgLib.send_email(emailFrom, emailTo, emailSubject, emailText, emailAttachments, smtpServer)

# -------------------- main --------------------
if __name__ == "__main__":  
    main_func()

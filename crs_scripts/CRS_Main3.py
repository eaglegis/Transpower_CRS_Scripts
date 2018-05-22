# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main1.py
# Created on: 2018-04-23
# 
# Usage: > 
# Description: 
# ---------------------------------------------------------------------------

import sys
import arcpy
import os
import datetime, time
from lib import etgLib
from config import Settings
from lib.CRS6_addlDataPreparation import *
from lib.CRS7_RemoveOldDataFromPreprod import *
from lib.CRS8_Extract_for_Connect import *

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
mxdName = Settings.ANNOTATION_MXD_NAME
labelGDBname = Settings.LABEL_GDB_NAME
preprodSdePath = Settings.PREPROD_SDE_PATH
preprodSdePrefix = Settings.PREPROD_SDE_PREFIX

assetsGDBname = Settings.ASSET_GDB_NAME
stgSdePath = Settings.STG_SDE_PATH
stgSdePrefix = Settings.STG_SDE_PREFIX

spreportSdePath = Settings.SPREPORT_SDE_PATH
spreportSdePrefix = Settings.SPREPORT_SDE_PREFIX


# ---------------- email settings ---------------
sendMail = Settings.SEND_EMAIL      # if true, the log file will be sent by email, if false, no email is sent
smtpServer = Settings.SMTP_SERVER
emailFrom = Settings.FROM_EMAIL    
emailTo = Settings.TO_EMAIL  # recipients email list, separated by comma
emailSubject1 = Settings.EMAIL_SUBJECT
emailText = Settings.EMAIL_BODYTEXT
emailAttachments = None

# set workspace
arcpy.env.workspace = wkgFolder

# logfile
script_name = os.path.basename(__file__)
log_name ='{0}_log'.format(script_name)

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
    # dateStamp = start.strftime("%Y%m%d")

    mxd = os.path.join(wkgFolder,mxdName)
    lbl = os.path.join(wkgFolder,labelGDBname)

    err_msg = None
    args = []
    global emailAttachments

    try:               
        log_path = os.path.join(sys.path[0], 'logs')      
        log, logfile = etgLib.create_log(log_path, log_name)
        if log == None: exit_sys(log, "can't create a log file", start)        

        emailAttachments = [logfile]

        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        etgLib.log_info(log, "working folder: {0}".format(wkgFolder))
        etgLib.log_info(log, "mxd: {0}".format(mxd))
        etgLib.log_info(log, "lbl gdb: {0}".format(lbl))

        ## ========================================
        ## Process: call CRS6_addDataPreparation
        ## ========================================       
        args = [wkgFolder,labelGDBname, log]            
        err_msg = crs6_add_data_preparation(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)

        # ## ========================================
        # ## Process: call CRS7_removeOldDataFromPreprod
        # ## ========================================       
        # args = [preprodSdePath,preprodSdePrefix,log]            
        # err_msg = crs7_remove_old_data_from_preprod(args)
        
        # if err_msg != None:
        #     exit_sys(log, err_msg, start,sendMail)            
       
        ## ========================================
        ## Process: call CRS8_Extract_for_Connect
        ## ========================================      
        args = [wkgFolder, assetsGDBname, spreportSdePath,spreportSdePrefix,stgSdePath, stgSdePrefix,log]            
        err_msg = crs8_extract_for_connection(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)  
                
    except Exception as e:       
        err_msg = str(e)        
        etgLib.log_error(log,"error in CRS_Main3: {0}".format(e))

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

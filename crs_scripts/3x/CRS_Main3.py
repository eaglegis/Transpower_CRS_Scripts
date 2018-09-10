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
labelGDBname = Settings.LABEL_GDB_NAME
contextdSdePath = Settings.CONTEXT_SDE_PATH
contextSdePrefix = Settings.CONTEXT_SDE_PREFIX

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
    # dateStamp = start.strftime("%Y%m%d")

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
        

        ## ========================================
        ## Process: call CRS6_addDataPreparation
        ## ========================================       
        args = [wkgFolder,labelGDBname]            
        err_msg, log_msgs = crs6_add_data_preparation(args)
        
        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)

        ## ========================================
        ## Process: call CRS7_removeOldDataFromPreprod
        ## ========================================       
        args = [contextdSdePath,contextSdePrefix]            
        err_msg, log_msgs = crs7_remove_old_data_from_preprod(args)
        
        etgLib.log_info_all(log, log_msgs)
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)            
       
        ## ========================================
        ## Process: call CRS8_Extract_for_Connect
        ## ========================================      
        args = [wkgFolder, assetsGDBname, spreportSdePath,spreportSdePrefix,stgSdePath, stgSdePrefix]            
        err_msg, log_msgs = crs8_extract_for_connection(args)

        etgLib.log_info_all(log, log_msgs)
        
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

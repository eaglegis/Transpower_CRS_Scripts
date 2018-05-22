# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Run_CRS9.py
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
from lib.CRS9_checkPreprodCounts import *

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
labelGDBname = Settings.LABEL_GDB_NAME
preprodSdePath = Settings.PREPROD_SDE_PATH
preprodSdePrefix = Settings.PREPROD_SDE_PREFIX
stgSdePath = Settings.STG_SDE_PATH
stgSdePrefix = Settings.STG_SDE_PREFIX
cutoffage = Settings.CUTOFF_AGE

# ---------------- email settings ---------------
sendMail = Settings.SEND_EMAIL      # if true, the log file will be sent by email, if false, no email is sent
smtpServer = Settings.SMTP_SERVER
emailFrom = Settings.FROM_EMAIL    
emailTo = Settings.TO_EMAIL  # recipients email list, separated by comma
emailSubject1 = Settings.EMAIL_SUBJECT
emailText = Settings.EMAIL_BODYTEXT
emailAttachments = None

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
    labelsPath  = os.path.join(wkgFolder,labelGDBname)
    
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
        etgLib.log_info(log, "preprod sde path: {0}".format(preprodSdePath))
        etgLib.log_info(log, "preprod sde prefix: {0}".format(preprodSdePrefix))
        etgLib.log_info(log, "staging sde path: {0}".format(stgSdePath))
        etgLib.log_info(log, "staging sde prefix: {0}".format(stgSdePrefix))

        ## ========================================
        ## Process: check work folder age
        ## ========================================

        err_msg = etgLib.check_folder_age(wkgFolder, cutoffage)
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)                  
       
        ## ========================================
        ## Process: call CRS9_checkPreprodCounts
        ## ========================================               
        args = [labelsPath,preprodSdePath,preprodSdePrefix,stgSdePath, stgSdePrefix,log]            
        err_msg = crs9_check_preprod_feature_counts(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)            
              
    except Exception as e:       
        err_msg = str(e)        
        etgLib.log_error(log,"error in {0}: {1}".format(script_name,e))

    etgLib.log_close(log, start)

    if sendMail:
        if err_msg != None:
            emailSubject = 'Run {} - Failed'.format(script_name)
        else:
            emailSubject = 'Run {} - Successful'.format(script_name)

        etgLib.send_email(emailFrom, emailTo, emailSubject, emailText, emailAttachments, smtpServer)

# -------------------- main --------------------
if __name__ == "__main__":  
    main_func()

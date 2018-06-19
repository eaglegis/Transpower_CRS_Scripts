# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main2.py
# Created on: 2018-04-23
# 
# Usage: > 
# Description: 
# 1. check working folder age
# 2. check if create_annotation.mxd is in working folder
# 3. call crs5
# 4. check if PARCEL_LABEL_PT data is in NZ boundary
# 5. update datasource of create_annotation.mxd
# ---------------------------------------------------------------------------

import sys
import arcpy
import os
import datetime, time
from lib import etgLib
from config import Settings
from lib.CRS_updateDataSourceMxd import *
from lib.CRS_checkDataExtent import *
from lib.CRS5_prepareForCRSlabels import *

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
mxdName = Settings.ANNOTATION_MXD_NAME
labelGDBname = Settings.LABEL_GDB_NAME
stgSdePath = Settings.STG_SDE_PATH
stgSdePrefix = Settings.STG_SDE_PREFIX
cutoffage = Settings.CUTOFF_AGE
extentString = Settings.EXTENT

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
        etgLib.log_info(log, "extent string: {0}".format(extentString))
        etgLib.log_info(log, "sde path: {0}".format(stgSdePath))

       
        ## ========================================
        ## Process: check work folder age
        ## ========================================
        err_msg = etgLib.check_folder_age(wkgFolder, cutoffage)
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)        

        # =============================
        # Process: check data existance 
        # assume: mxd is in \CRS\MMMYYYY folder, create_Annotations.mxd CRS.GDB is in \CRS\MMMYYY folder
        # =============================
        etgLib.log_info(log, "Checking data existance",True)
        args = [mxd]
        for f in args:           
            if not arcpy.Exists(f):
                err = "file does not exist: {}".format(f)                
                exit_sys(log, err, start, sendMail) 
        
        ## ========================================
        ## Process: call CRS5_prepareForCRSLables
        ## ========================================       
        args = [wkgFolder,labelGDBname,stgSdePath,stgSdePrefix,log]            
        err_msg = crs5_prepare_for_labels(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
       
             
        ## ========================================
        ## Process: check if data is in nz boundary
        ## ========================================
        args = [lbl, extentString, ['PARCEL_LABEL_PT'],log]
        err_msg = crs_check_data_extent(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
        
        ## =====================================
        ## Process: call CRS_updateDataSourceMxd
        ## =====================================
        args = [mxd,lbl,log]        
        err_msg = crs_update_datasource_mxd(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
       
    except Exception as e:       
        err_msg = str(e)        
        etgLib.log_error(log,"error in CRS_Main2: {0}".format(e))

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

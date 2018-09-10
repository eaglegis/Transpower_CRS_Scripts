# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main2.py
# Created on: 2018-04-23
# 
# Usage: > 
# Description: 
# 1. check working folder age
# 2. check if create_annotation.mxd/aprx is in working folder
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
from lib.CRS_checkDataExtent import *
from lib.CRS5_prepareForCRSlabels import *
from lib.CRS_updateDataSourceAprx import *
from lib.CRS_exportLabelToAnnoAprx import *

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
# mxdName = Settings.ANNOTATION_MXD_NAME
prjName = Settings.ANNOTATION_PROJ_NAME
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

    #Change this depending on whether using MXD or APRX (ArcGIS Pro) project   
    prj = os.path.join(wkgFolder,prjName)
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
        etgLib.log_info(log, "arcpro project: {0}".format(prj))
        etgLib.log_info(log, "lbl gdb: {0}".format(lbl))
        etgLib.log_info(log, "extent string: {0}".format(extentString))
        etgLib.log_info(log, "sde path: {0}".format(stgSdePath))  

        # =============================
        # Process: check data existance 
        # check if create_Annotations.mxd/.aprx  is in \CRS\MMMYYY folder
        # =============================
        etgLib.log_info(log, "Checking data existance",True)
        args = [prj]
        for f in args:           
            if not arcpy.Exists(f):
                err_msg = "file does not exist: {}".format(f)                
                exit_sys(log, err_msg, start, sendMail) 
        
        ## ========================================
        ## Process: call CRS5_prepareForCRSLabels
        ## ========================================       
        args = [wkgFolder,labelGDBname,stgSdePath,stgSdePrefix]            
        err_msg, log_msgs = crs5_prepare_for_labels(args)

        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start, sendMail)
       
             
        ## ========================================
        ## Process: check if data is in NZ boundary by calling CRS_checkDataExtent
        ## ========================================
        args = [lbl, extentString, ['PARCEL_LABEL_PT']]
        err_msg, log_msgs = crs_check_data_extent(args)

        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start, sendMail)

        ## =====================================
        ## Process: call CRS_updateDataSourceAprx
        ## =====================================
        etgLib.log_info(log, 'calling CRS_updateDataSourceAprx', True)
        args = [prj,lbl]        
        err_msg, log_msgs = crs_update_datasource(args)

        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
        
        # ## =====================================
        # ## Process: call CRS_exportLabelToAnnoAprx
        # ## =====================================
        # etgLib.log_info(log, 'calling CRS_exportLabelToAnnoAprx', True)
        # args = [prj,lbl]        
        # err_msg, log_msgs = crs_label_to_annotation(args)
        # etgLib.log_info_all(log, log_msgs) 
        # if err_msg != None:
        #     exit_sys(log, err_msg, start,sendMail)
       
       
    except Exception as e:       
        err_msg = str(e)        
        etgLib.log_error(log,"error in CRS_Main2: {0}".format(e))

    etgLib.log_close(log, start)
    print ("Finished!!!  Please check the result in ARcGIS Pro or ArcCatalog")
    

    if sendMail:
        if err_msg != None:
            emailSubject = 'Run {} - Failed'.format(script_name)
        else:
            emailSubject = 'Run {} - Successful'.format(script_name)

        etgLib.send_email(emailFrom, emailTo, emailSubject, emailText, emailAttachments, smtpServer)

# -------------------- main --------------------
if __name__ == "__main__":  
    main_func()

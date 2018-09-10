# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main1.py
# Created on: 2018-04-23
# 
# Usage: > 
# Description: 
# 1. check folder age
# 2. check mxd and crs in the working folder
# 3. check if data is in nz boundary
# 4. update datasource in mxd CRS_updateDataSourceMxd
# 5. call crs1, crs2, crs3, crs4
# ---------------------------------------------------------------------------

import sys
import arcpy
import os
import datetime, time
from lib import etgLib
from config import Settings

from lib.CRS_updateDataSourceMxd import *
from lib.CRS_checkDataExtent import *
# from lib.CRS_updateDataSourceAprx import *
from lib.CRS1_repairCRSdata import *
from lib.CRS2_emptyNDCSTGsde import *
from lib.CRS3_copyFCsToNZCSTG import *
from lib.CRS4_copyTablesToNZCSTG import *



arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
mxdName = Settings.CHECKDATA_MXD_NAME
crsName = Settings.CRS_GDB_NAME
extentString = Settings.EXTENT
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

    crs = os.path.join(wkgFolder,crsName)
    mxd = os.path.join(wkgFolder, mxdName)

    err_msg = None
    args = []
    global emailAttachments

    try:  
        # generate log file
        log_path = os.path.join(sys.path[0], 'logs')      
        log, logfile = etgLib.create_log(log_path, log_name)
        if log == None: exit_sys(log, "Can't create a log file", start)        

        emailAttachments = [logfile]

        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        etgLib.log_info(log, "working folder: {0}".format(wkgFolder))
        etgLib.log_info(log, "mxd name: {0}".format(mxd))
        etgLib.log_info(log, "crs gdb: {0}".format(crs))
        etgLib.log_info(log, "extent string: {0}".format(extentString))
        etgLib.log_info(log, "staging sde path: {0}".format(stgSdePath))

        ## ========================================
        ## Process: check work folder age
        ## ========================================
        err_msg = etgLib.check_folder_age(wkgFolder, cutoffage)
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)        

       
        # =============================
        # Process: check data existance 
        # check if check_data.aprx and CRS.GDB are in \CRS\MMMYYY folder
        # =============================
        etgLib.log_info(log, "Checking data existance",True)
        args = [prj,crs]
        for f in args:           
            if not arcpy.Exists(f):
                err = "file does not exist: {}".format(f)                
                exit_sys(log, err, start, sendMail) 
             
        ## ========================================
        ## Process: check if data is in nz boundary
        ## ========================================
        args = [crs, extentString, []]
        err_msg, log_msgs = crs_check_data_extent(args)
        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)

        ## =====================================
        ## Process: call CRS_updateDataSourceMxd
        ## =====================================
        args = [mxd,crs,log]        
        err_msg = crs_update_datasource_mxd(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
                
        
        ## ================================
        ## Process: call CRS1_repairCRSdata
        ## ================================   
        args = [crs,log]        
        err_msg, log_msgs = crs1_repair_crs_data(args)

        etgLib.log_info_all(log, log_msgs)
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)

        ## ===============================
        ## Process: call CRS2_emptyNDCSTAG
        ## ===============================   
        args = [stgSdePath]        
        err_msg, log_msgs = crs2_empty_stage_sde(args)

        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
              

        ## ===================================
        ## Process: call CRS3_copyFCsToNZCSTAG
        ## ===================================   
        args = [stgSdePath,crs,stgSdePrefix]        
        err_msg, log_msgs = crs3_copy_fcs_stage(args)

        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start, sendMail)
        
        ## ======================================
        ## Process: call CRS4_copyTablesToNZCSTAG
        ## ======================================   
        args = [stgSdePath,crs,stgSdePrefix]        
        err_msg, log_msgs = crs4_copy_tbls_stage(args)

        etgLib.log_info_all(log, log_msgs)
        
        if err_msg != None:
            exit_sys(log, err_msg, start, sendMail)

    except Exception as e:       
        err_msg = str(e)        
        etgLib.log_error(log,"error in CRS_Main1: {0}".format(e))

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

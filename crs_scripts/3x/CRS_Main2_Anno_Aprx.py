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
from lib.CRS_updateDataSourceAprx import *
from lib.CRS_exportLabelToAnnoAprx import *

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
prjName = Settings.ANNOTATION_PROJ_NAME
labelGDBname = Settings.LABEL_GDB_NAME


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
        
        ## =====================================
        ## Process: call CRS_updateDataSourceAprx
        ## =====================================
        etgLib.log_info(log, 'calling CRS_updateDataSourceAprx', True)
        args = [prj,lbl]        
        err_msg = crs_update_datasource(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
        
        ## =====================================
        ## Process: call CRS_exportLabelToAnnoAprx
        ## =====================================
        etgLib.log_info(log, 'calling CRS_exportLabelToAnnoAprx', True)
        args = [prj,lbl]        
        err_msg = crs_label_to_annotation(args)
        
        if err_msg != None:
            exit_sys(log, err_msg, start,sendMail)
       
    except Exception as e:       
        err_msg = str(e)        
        etgLib.log_error(log,"error in {0}: {1}".format(script_name,e))

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

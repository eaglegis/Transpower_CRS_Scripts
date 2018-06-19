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
from lib.CRS10_prodSPREPORTandSPOWNrefresh_with_fieldMap import *

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
prepSPREPORTpath = Settings.PREPROD_SPREPORT_SDE_PATH
prodSPREPORTpath = Settings.PROD_SPREPORT_SDE_PATH
prepSPOWNpath = Settings.PREPROD_SPOWN_SDE_PATH
prodSPOWNpath = Settings.PROD_SPOWN_SDE_PATH

# ---------------- email settings ---------------
sendMail = Settings.SEND_EMAIL      # if true, the log file will be sent by email, if false, no email is sent
smtpServer = Settings.SMTP_SERVER
emailFrom = Settings.FROM_EMAIL    
emailTo = Settings.TO_EMAIL  # recipients email list, separated by comma
emailSubject1 = Settings.EMAIL_SUBJECT
emailText = Settings.EMAIL_BODYTEXT
emailAttachments = None

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
        etgLib.log_info(log, "preprod SPREPORT SDE path: {0}".format(prepSPREPORTpath))
        etgLib.log_info(log, "production SPREPORT SDE path: {0}".format(prodSPREPORTpath))
        etgLib.log_info(log, "preprod SPOWN SDE path: {0}".format(prepSPOWNpath))
        etgLib.log_info(log, "production SPOWN SDE path: {0}".format(prodSPOWNpath))

      
        ## ==============================================================
        ## Process: call .CRS10_prodSPREPORTandSPOWNrefresh_with_fieldMap
        ## ============================================================== 
              
        args = [prepSPREPORTpath,prodSPREPORTpath,prepSPOWNpath,prodSPOWNpath,log]            
        err_msg = crs10_prod_db_refresh(args)
        
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

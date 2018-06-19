# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main7_Add_Attr_Index_CONTEXT.py
# Created on: 2018-06-08
# 
# Usage: 
# Description:  copy Connect_Property from assets.gdb to pre-prod SSREPORT sde database 
# ---------------------------------------------------------------------------

import sys
import arcpy
import os
import datetime, time
from lib import etgLib
from config import Settings
import re

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
# wkgFolder = Settings.WORKING_FOLDER

contextdSdePath = Settings.CONTEXT_SDE_PATH
contextSdePrefix = Settings.CONTEXT_SDE_PREFIX

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

# constants and variables
fc_parcel_label_pt = "PARCEL_LABEL_PT_1"
fc_road_cl_dissolve = "ROAD_CL_Dissolve_1"

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

        # set workspace
        arcpy.env.workspace = contextdSdePath       
                      
        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        # etgLib.log_info(log, "working folder: {0}".format(wkgFolder))
        etgLib.log_info(log, "pre prod CONTEXTSdePath: {0}".format(contextdSdePath))
       
              
        ## ===============================================================
        ## Process: add attribute index to PARCEL_LABEL_PT_1 feature class
        ## ===============================================================
        etgLib.log_info(log,'add attribute indexes to PARCEL_LABEL_PT_1 feature class in CONTEXT sde...',True)
        
        fc_name = contextSdePrefix + fc_parcel_label_pt 
        inFCpath = os.path.join(contextdSdePath,fc_name)        
        if arcpy.Exists(inFCpath) == False:  exit_sys(log, "{} does not exist in context sde database".format(fc_name), start, sendMail)

        indexes = arcpy.ListIndexes(inFCpath) # ----> Lists both attribute and spatial indexes!!!
        indexPrefix = None 
        etgLib.log_info(log,'get the existing index prefix ...')
        for index in indexes:
            m = re.search(r'^R(\d+)_pk', index.name)
            if m!=None:
                indexPrefix = m.group(1)
                break
        
        if indexPrefix == None: exit_sys(log, "no index prefix found in the existing indexes", start, sendMail)

        etgLib.log_info(log,'index prefix : {0}'.format(indexPrefix))
       
        list_index_to_create = []
        list_index_to_create.append(("Owneridx",["Owner1", "Owner2", "Owner3","Owner4"]))
        list_index_to_create.append(("Vestingsurvidx",["VESTING_SURVEY_ID"]))
        list_index_to_create.append(("Fullappidx",["FULL_APP"]))
        list_index_to_create.append(("Parcelidx",["PARCEL_ID"]))
        list_index_to_create.append(("Titleidx",["Title1","Title2","Title3","Title4"]))

        for index_to_create in list_index_to_create:
            newIndex = "R{0}_{1}".format(indexPrefix,index_to_create[0])
            fields = index_to_create[1]
            etgLib.log_info(log,'creating index : {0}'.format(newIndex))
            arcpy.AddIndex_management(inFCpath,fields,newIndex, "NON_UNIQUE", "NON_ASCENDING")

        
        ## ===============================================================
        ## Process: add attribute index to ROAD_CL_Dissove_1 feature class
        ## ===============================================================
        etgLib.log_info(log,'add attribute indexes to ROAD_CL_Dissove_1 feature class...',True)
        
        fc_name = contextSdePrefix + fc_road_cl_dissolve 
        inFCpath = os.path.join(contextdSdePath,fc_name)
        if arcpy.Exists(inFCpath) == False:  exit_sys(log, "{} does not exist in context sde database".format(fc_name), start, sendMail)
        indexes = arcpy.ListIndexes(inFCpath) # ----> Lists both attribute and spatial indexes!!!
        indexPrefix = None 
        etgLib.log_info(log,'get the existing index prefix ...')
        for index in indexes:
            m = re.search(r'^R(\d+)_pk', index.name)
            if m!=None:
                indexPrefix = m.group(1)
                break
        
        if indexPrefix == None: exit_sys(log, "no index prefix found in the existing indexes", start, sendMail)

        etgLib.log_info(log,'index prefix : {0}'.format(indexPrefix))
       
        list_index_to_create = []
        list_index_to_create.append(("Locidx",["RD_LOC"]))
        list_index_to_create.append(("Rdnameidx",["ROAD_NAME1"]))
        list_index_to_create.append(("Locationidx",["LOCATION1"]))       

        for index_to_create in list_index_to_create:
            newIndex = "R{0}_{1}".format(indexPrefix,index_to_create[0])
            fields = index_to_create[1]
            etgLib.log_info(log,'creating index : {0}'.format(newIndex))
            arcpy.AddIndex_management(inFCpath,fields,newIndex, "NON_UNIQUE", "NON_ASCENDING")


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

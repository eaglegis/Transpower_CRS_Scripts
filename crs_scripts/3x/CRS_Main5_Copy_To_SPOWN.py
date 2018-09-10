# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main5_Copy_To_SPOWN.py
# Created on: 2018-06-08
# 
# Usage: 
# Description:  copy Connect_Property from labels.gdb to pre-prod SPOWN sde database 
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
prepSPOWNpath = Settings.PREPROD_SPOWN_SDE_PATH

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
spown_property_connect = "SPOWN.MAPDATA.Connect_Property"
labels_property_connect = "Connect_Property"



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

        lbl_gdb = os.path.join(wkgFolder,labelGDBname)        
        # set workspace
        arcpy.env.workspace = lbl_gdb
        
        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        etgLib.log_info(log, "working folder: {0}".format(wkgFolder))
        etgLib.log_info(log, "prepSPOWNpath: {0}".format(prepSPOWNpath))
        etgLib.log_info(log, "label gdb: {0}".format(lbl_gdb))
        
        ## ========================================
        ## Process: copy data from labels.gdb to SPOWN in pre-prod
        ## ========================================
        etgLib.log_info(log,'copy Connect_Property from labels.gdb to SPOWN in pre-prod',True)
        # copy Connect_Property to *_o in SPOWN sde
        etgLib.log_info(log,'copy Connect_Property to *_o in SPOWN sde ...')
        
        inFCpath = os.path.join(prepSPOWNpath,spown_property_connect)
        if arcpy.Exists(inFCpath):
            out_fc_name = spown_property_connect + "_o"
            outFCpath = os.path.join(prepSPOWNpath,out_fc_name)
            etgLib.log_info(log,'Copying: {0} to {1}'.format(spown_property_connect,out_fc_name ))
            arcpy.Copy_management(inFCpath,outFCpath, "FeatureClass") 

            # truncate and append
            etgLib.log_info(log,'truncate Connect_Property in SPOWN sde ...') 
            arcpy.TruncateTable_management(inFCpath)
        
        # build the FieldMappings
        etgLib.log_info(log,'build the FieldMappings ...') 
        list_fields_to_map = []

        
        list_fields_to_map.append(('TP_PROPERTY_LINK_PROPERTY_ID','tempDsslvID_TP_PROPERTY_LINK_PROPERTY_ID'))
        list_fields_to_map.append(('PROPERTY_ID','tempDsslvID_TP_PROPERTY_LINK_PROPERTY_ID'))
        list_fields_to_map.append(('PARCEL_ID','tempDsslvID_TP_PROPERTY_LINK_PROPERTY_ID'))
        list_fields_to_map.append(('COUNT_PARCEL_ID', 'tempDsslvID_COUNT_TP_PROPERTY_LINK_PARCEL_ID'))

        
##        # Old mappings for old staging dataset
##        list_fields_to_map.append(('PROPERTY_ID','tempDsslvID_TP_PROPERTY_LINK_PROPERTY_ID'))
##        list_fields_to_map.append(('LEGAL_DESCRIPTION','TP_PROPERTY_LEGAL_DESCRIPTION'))
##        list_fields_to_map.append(('TITLE_NO', 'TP_PROPERTY_TITLE_NO'))
##        list_fields_to_map.append(('SUBADDRESS_ID', 'TP_PROPERTY_SUBADDRESS_ID'))
##        list_fields_to_map.append(('ADDRESS_SOURCE', 'TP_PROPERTY_ADDRESS_SOURCE'))
##        list_fields_to_map.append(('COUNT_PARCEL_ID', 'tempDsslvID_COUNT_TP_PROPERTY_LINK_PARCEL_ID'))

        print('Got to in fc name: {0}'.format(labels_property_connect))
        inFCpath = os.path.join(lbl_gdb,labels_property_connect)
        print('InFCPath: {0}'.format(inFCpath))
        outFCpath = os.path.join(prepSPOWNpath,spown_property_connect)        
        print('OutFCPath: {0}'.format(outFCpath))
        
        fieldmappings = etgLib.get_field_mapping(inFCpath, outFCpath, list_fields_to_map)
        
        # appending data from labels.gdb to SPOWN preprod sde 
        etgLib.log_info(log,'appending data from labels.gdb to SPOWN preprod sde  ...')
        arcpy.Append_management([inFCpath],outFCpath, "NO_TEST", field_mapping = fieldmappings) 
                  
                
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

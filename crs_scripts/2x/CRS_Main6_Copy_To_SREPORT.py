# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CRS_Main6_Copy_To_SREPORT.py
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

arcpy.env.overwriteOutput = True

##  ----------------- settings/parameters -----------------------
# Script arguments
wkgFolder = Settings.WORKING_FOLDER
assetsGDBname = Settings.ASSET_GDB_NAME
prepSPREPORTpath = Settings.PREPROD_SPREPORT_SDE_PATH

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
assets_fcs = ['SITE_Parcel', 'SPAN_Parcel', 'STRUCTURE_Parcel', 'Section_Parcel'] 
spreportFClist = ["SPREPORT.MAPDATA.SITE_Parcel","SPREPORT.MAPDATA.SPAN_Parcel","SPREPORT.MAPDATA.STRUCTURE_Parcel","SPREPORT.MAPDATA.SECTION_Parcel"]


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

        assets_gdb = os.path.join(wkgFolder,assetsGDBname)
        # set workspace
        arcpy.env.workspace = assets_gdb       
                      
        etgLib.log_start(log)
        etgLib.log_info(log, "script parameters:")
        etgLib.log_info(log, "------------------------")
        etgLib.log_info(log, "working folder: {0}".format(wkgFolder))
        etgLib.log_info(log, "prepSREPORTpath: {0}".format(prepSPREPORTpath))
        etgLib.log_info(log, "assets gdb: {0}".format(assets_gdb))
              
        
        ## ========================================
        ## Process: copy data from assets.gdb to SPREPORT in pre-prod
        ## ========================================
        etgLib.log_info(log,'copy data from assets.gdb to SPREPORT in pre-prod...',True)
    
        list_of_fields_to_map_List = []

        # Parcel_site
        list_of_fields_to_map = []    
        list_of_fields_to_map.append(('SITE','MXLOCATION'))
        list_of_fields_to_map.append(('SITE_TYPE','type'))
        list_of_fields_to_map.append(('STATUS', 'status'))
        list_of_fields_to_map.append(('SITE_DESC', 'description'))

        list_of_fields_to_map_List.append(list_of_fields_to_map)

        # SPAN_Parcel
        list_of_fields_to_map = []    
        list_of_fields_to_map.append(('TAG_NO','MXLOCATION'))
        list_of_fields_to_map.append(('SITE','site'))

        list_of_fields_to_map_List.append(list_of_fields_to_map)

        # STRUCTURE_Parcel
        list_of_fields_to_map = []    
        list_of_fields_to_map.append(('TAG_NO','MXLOCATION'))
        list_of_fields_to_map.append(('TAG_TYPE','type'))
        list_of_fields_to_map.append(('STATUS', 'status'))
        list_of_fields_to_map.append(('STR_CAT_DESC', 'LongType'))

        list_of_fields_to_map_List.append(list_of_fields_to_map)

        # Section_Parcel
        list_of_fields_to_map = []           
        list_of_fields_to_map_List.append(list_of_fields_to_map)
           
        
        # backup sreport feature classes
        etgLib.log_info(log,'backup sreport feature classes...')
        for fc in spreportFClist:
            inFCpath = os.path.join(prepSPREPORTpath,fc)
            out_fc_name = fc + "_o"
            outFCpath = os.path.join(prepSPREPORTpath,out_fc_name)
            etgLib.log_info(log,'Copying: {0} to {1}'.format(fc,out_fc_name ))
            arcpy.Copy_management(inFCpath,outFCpath, "FeatureClass")

            arcpy.TruncateTable_management(inFCpath)
    
        # append from assets.gdb to SPREPORT
        i = 0
        for fc in assets_fcs:
            inFCpath =  os.path.join(assets_gdb,fc)

            out_fc_name = spreportFClist[i]
            outFCpath = os.path.join(prepSPREPORTpath,out_fc_name)
            
            list_fields_to_map = list_of_fields_to_map_List[i]
            
            if len(list_fields_to_map) > 0:
                fieldmappings = etgLib.get_field_mapping(inFCpath, outFCpath,list_fields_to_map)

                etgLib.log_info(log,'appending data from : {0}'.format(inFCpath))
                arcpy.Append_management(fc,outFCpath, "NO_TEST", fieldmappings)
            else:
                etgLib.log_info(log,'appending data from : {0}'.format(inFCpath))
                arcpy.Append_management(inFCpath,outFCpath, "TEST")
            i = i+1 

        # field calculation
        etgLib.log_info(log,'field calculation...')
        Input_FC = os.path.join(prepSPREPORTpath,"SPREPORT.MAPDATA.SPAN_Parcel")       
        arcpy.CalculateField_management(Input_FC, "EQN_TYPE", "'CON'", "PYTHON_9.3", "")

        Input_FC = os.path.join(prepSPREPORTpath,"SPREPORT.MAPDATA.STRUCTURE_Parcel")       
        arcpy.CalculateField_management(Input_FC, "SITE", "!TAG_NO![:9]", "PYTHON_9.3", "")
               
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

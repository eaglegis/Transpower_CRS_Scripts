import datetime, time
import os
import sys
import urllib
import urllib2
import json
import base64
from base64 import encodestring

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Utils import COMMASPACE, formatdate 
from email import Encoders

import arcpy

class LicenseError(Exception):
    pass

# ------------------------------------------------  
# file process functions
#
# get_filename: extract the file name without extension name from the full file path
# get_filepath: get the file location (full folder text)
# create_subfolder: create a subfolder under the specified main folder
# ------------------------------------------------

def get_filename(thefile):    
    theFileName = os.path.basename(thefile)
    theFileName = os.path.splitext(theFileName)[0]
    return theFileName


def get_filepath(thefile):
    theFilePath = os.path.dirname(os.path.realpath(thefile))
    return theFilePath

def create_subfolder(mainfolder, subfolder):    
    folder = os.path.join(mainfolder, subfolder)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

# ------------------------------------------------
# list functions
#
# list_compare: compare two list, return the add, remove and same list
#               L1 = [1,2,3,4,5,7] L2 = [2,3,6]
#               add = [6]  - exists in L2 but not L1
#               remove = [1,4,5,7]  - exists in L1 but not L2 
#               same = [2,3]  -- same
#
# get_sublists: split the list into sublist by the length
#               L = [1,2,3,4,5,6,7,8,9,10,11]
#               newL = get_sublists(L,3)
#               newL = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11]]
#
# list_to_str : convert a list to comma separated string
#               L = [1,2,3]
#               output: "1,2,3"
#
# list_to_str_with_quote: convert a list to comma separated quoted string
#                         L = [a,b,c]
#                         output = 'a','b','c'
# ------------------------------------------------

def list_compare(l1, l2):
    """ compare two dictionary and return the difference between two """
    try:
        added = [itm for itm in l2 if itm not in l1]
        same = list(set(l1).intersection(set(l2)))
        removed = [itm for itm in l1 if itm not in l2]
        return added, removed, same
    except Exception as e:
        msg ="ERROR in comparing two lists: {0}".format(e)
        raise ValueError (msg)

def get_sublists(lst,length):
    return [lst[i:length +i] for i in range(0,len(lst), length)]

def list_to_str(lst):
    """ if object is a list, it creates a
        comma seperated string.
    """
    if not lst:
        return ''
    if isinstance(lst, list):
        return ','.join(lst)
    return str(lst)

def list_to_str_with_quote(lst):
    """ if object is a list, it creates a
        comma seperated quoted string.
    """
    if not lst:
        return ''
    if isinstance(lst, list):
        return ','.join("'{0}'".format(x) for x in lst)
    return str(lst)

# ------------------------------------------------
# log file functions
#
# create_log: create a log file with datetimestamp: [logfilename]_datetimestamp i.e. insert_rem_log_20151203135302.txt
# log_start: log the start time
# log_end: log the process finished time
# log_close: log the final finished time and close the log file
# log_info: log a message
# ------------------------------------------------  

def create_log(logPath, logName):
    log = None
    ## log file
    dateStamp = datetime.datetime.now().strftime("%Y%m%d")
    # logName = logName + "_"+ dateStamp + ".log"
    logName = logName + "_"+ dateStamp + ".txt"
    logfile = os.path.join(logPath, logName)
 
    try:
        if not os.path.isdir(logPath):
           os.makedirs(logPath)
        log = open(logfile,'w')
    except IOError:
        print ("ERROR while opening the log file")     
        return log, logfile

    return log, logfile

def log_start(log):
    if not log is None:
        log.write("======= start ==============" + "\n")
        log.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n")
        log.write("============================" + "\n")

def log_end(log, start):    
    if not log is None:
        log.write("======== end ===============" + "\n")
        log.write("process time: %s " % str(datetime.datetime.now()-start)+ "\n")
        log.write("============================" + "\n")

def log_close(log, start):    
    if not log is None:
        log.write("======== end ===============" + "\n")
        log.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n")
        log.write("============================" + "\n")
        log.write("Total process time: %s " % str(datetime.datetime.now()-start))
        log.close()

def log_info(log, txt, addline = False):    
    if not txt is None:
        print (txt)
        if not log is None:
            if addline:
                log.write("-------------------------------\n")      
            log.write(txt + "\n")
            if addline:
                log.write("-------------------------------\n")            
            log.flush()
        arcpy.AddMessage(txt)
    
def log_error(log, txt):
    if not txt is None:
        print (txt)
        if not log is None:
            log.write("ERROR:{}\n".format(txt))
            log.flush()
        arcpy.AddWarning(txt)

def log_process_time(log, start):    
    if not log is None:
        log.write("Process time: %s \n" % str(datetime.datetime.now()-start))
        
def create_csv(csvFile):
    csv = None
    ## csv file   
    csvPath = os.path.dirname(csvFile)   
    try:
        if not os.path.isdir(csvPath):
           os.makedirs(csvPath)
        csv = open(csvFile,'w')
    except IOError:
        print ("there was an error create the csv file")     
        return csv

    return csv
# ------------------------------------------------
# string and json function
#
# validate_json: check if the string is the json format
# ------------------------------------------------  
def str_to_bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def validate_json(jsonString):
    """ validate the json string and convert into json object"""
    in_json = None      
    try:
        in_json = json.loads(jsonString)
    except:       
        arcpy.AddMessage ("invalid  json string")             
        return None       
    return in_json

# ------------------------------------------------
# email function
#
# send_email: use smtp sever to send the email with attachment
# ------------------------------------------------  

def send_email(sender, to, subject, text, files=[],server="localhost"):
    assert type(to)==list 
    assert type(files)==list 
       
    try:       
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach( MIMEText(text) )
        
        for f in files:
            # print (f)
            if os.path.exists(f) == True:
                part = MIMEBase('application', "octet-stream")
                part.set_payload( open(f,'rb').read() )
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"'
                               % os.path.basename(f))
                msg.attach(part)
               
        s = smtplib.SMTP(server)       
        s.sendmail(sender, to, msg.as_string() )
        s.close()
    except Exception as e:
        print ("ERROR in sending email: {} \n".format(e))   


# ------------------------------------------------
# display message
# ------------------------------------------------  
def msg(txt):
    # log messages for any environment
    print (txt)

# ------------------------------------------------
# parse user name and password
# ------------------------------------------------  

def get_username_password(authString):
    """ extract the username and password from authorization code """  
    u = None
    p = None
    try:       
        decoded_string = base64.b64decode(authString)      
        u = decoded_string.split(":")[0]
        p = decoded_string.split(":")[1]       
    except:       
        arcpy.AddMessage ("invalid authorization string")             
            
    return u, p




def delete_layer(lyr):
    if arcpy.Exists(lyr):
        print ("{} exists - deleted".format(lyr))
        arcpy.Delete_management(lyr)     
   

def field_exist (fc, fld):   
    isExist = False
    lstFields = arcpy.ListFields(fc)
    fieldNames = [f.name for f in lstFields]

    if fld in fieldNames:
        print ("field exists - " + fld)
        isExist = True
    
    return isExist


def checkout_3D():
    try:
        if arcpy.CheckExtension("3D") == "Available":
            arcpy.CheckOutExtension("3D")
        else:
            # raise a custom exception
            raise LicenseError

    
    except LicenseError:
        print("3D Analyst license is unavailable")
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))


def checkin_3D():
    arcpy.CheckInExtension("3D")

def check_folder_age(folder,cutoffage):
    err = None
    starttime = datetime.datetime.now()
    t = os.path.getctime(folder)
    tt = datetime.datetime.fromtimestamp(t)
    fldrTimeCheck = starttime - tt
    td = datetime.timedelta(days=cutoffage)
    if fldrTimeCheck >= td: # Working folder too old 
        # err = 'WARNING: working folder {} created {} HH:MM:SS.dddddd ago!!!'.format(folder,fldrTimeCheck) 
        err = 'WARNING: working folder {} created {} ago!!!'.format(folder,fldrTimeCheck)        
    return err

# create field mapping
def get_field_mapping (inFCpath, outFCpath, list_of_fields_we_will_map):
     
    # build the fieldmap
    # Create FieldMappings object to manage merge output fields
    fieldmappings = arcpy.FieldMappings()

    fieldmappings.addTable(outFCpath)
    fieldmappings.addTable(inFCpath)
   
    for field_map in list_of_fields_we_will_map:           
        #Find the fields index by name. e.g 'PROPERTY_ID'
        field_to_map_index = fieldmappings.findFieldMapIndex(field_map[0])
    
        #Grab "A copy" of the current field map object for this particular field
        field_to_map = fieldmappings.getFieldMap(field_to_map_index)

        field_to_map.addInputField(inFCpath, field_map[1])
        
        #We edited a copy, update our data grid object with it
        fieldmappings.replaceFieldMap(field_to_map_index, field_to_map)

    return fieldmappings
       


    
    


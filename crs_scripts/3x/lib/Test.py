import arcpy, os


sr = arcpy.SpatialReference(2193)
args = []
log_messages = []
err = None

def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def call_fun():
    err = "ERROR"
    

    log_msg ("TEST sub")
    log_msg ("test1")
    log_msg("test 2")

    return err, log_messages

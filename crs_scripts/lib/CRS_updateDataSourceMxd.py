import arcpy
import os
import etgLib

args = []

def crs_update_datasource_mxd(args):

    # script name
    script_name = os.path.basename(__file__)
    
    # script parameters
    mxd = args[0]
    gdb = args[1]
    log = args[2]
    
    err_message = None
    
    # log function
    etgLib.log_info(log, 'calling {}'.format(script_name), True)
    try:             
        mxdDoc = arcpy.mapping.MapDocument(mxd)
        for lyr in arcpy.mapping.ListLayers(mxdDoc):
            # if lyr.isBroken:               
            lyr.findAndReplaceWorkspacePath(lyr.workspacePath, gdb)
           
        # mxd.findAndReplaceWorkspacePaths(r"C:\Project\Data", r"C:\Project\Data2")
        mxdDoc.save()
        del mxdDoc
        
    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message      

# if __name__ == '__main__':
#     main(args)
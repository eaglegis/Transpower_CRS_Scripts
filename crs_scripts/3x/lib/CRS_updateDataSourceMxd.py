import arcpy
import os



def crs_update_datasource_mxd(args):

    # script name
    script_name = os.path.basename(__file__)
    
    # script parameters
    mxd = args[0]
    gdb = args[1]
    
    
    err_message = None
    
    # log function
    print ('calling {}'.format(script_name))
    try:             
        mxdDoc = arcpy.mapping.MapDocument(mxd)
        for lyr in arcpy.mapping.ListLayers(mxdDoc):
            ## Changed this as logic was only looking for Broken layers which from month to month wouldn't happen
            if lyr.isBroken:
            # if lyr.name.upper() == 'PARCEL_LABEL_PT':
                lyr.findAndReplaceWorkspacePath(lyr.workspacePath, gdb)
                  
        mxdDoc.save()
        del mxdDoc
        
    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
    
    return err_message      

# if __name__ == '__main__':
#     main(args)

import arcpy
import os
import etgLib

err_message = None
args = []

def main(args):
    
    err_message = None
    try:
        theMxd = args[0]
        gdb = args[1]
       
        mxd = arcpy.mapping.MapDocument(theMxd)
        
        for lyr in arcpy.mapping.ListLayers(mxd):
##            print lyr.workspacePath
            if lyr.isBroken:
                print (lyr.dataSource)
                lyr.findAndReplaceWorkspacePath(lyr.workspacePath, gdb)
                print "broken"
            
           
            
        # mxd.findAndReplaceWorkspacePaths(r"C:\Project\Data", r"C:\Project\Data2")
        mxd.save()
        # del mxd
        return err_message
    except Exception as e:        
        err_message =  "error in CSR_updateDataSourceMxd: {0}" .format(e)
       
        print (err_message)

if __name__ == '__main__':
    mxd = r'C:\Developments\transpower\mxd\Check_data.mxd'
    gdb = r'C:\Developments\transpower\2018_APR\CRS.gdb'
    args = [mxd, gdb]
    main(args)

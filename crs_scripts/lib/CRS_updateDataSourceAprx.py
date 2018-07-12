import arcpy
import os
# import etgLib

args = []

def crs_update_datasource(args):
   
    # script name
    script_name = os.path.basename(__file__)
    
    # script parameters
    prj = args[0]
    gdb = args[1]
    
    err_message = None
    
    # log function
    # etgLib.log_info(log, 'calling {}'.format(script_name), True)
    try:
       
        aprx = arcpy.mp.ArcGISProject(prj)
        for m in aprx.listMaps():
            for l in m.listLayers():
                print (m.name)
                if l.connectionProperties != None:
                    # print (l.connectionProperties)
                    o_conProp = l.connectionProperties
                    n_conProp = l.connectionProperties                    
                    n_conProp['connection_info']['database'] = gdb                    
                    l.updateConnectionProperties (o_conProp, n_conProp)
      
        aprx.save()
        del aprx             
       
        
    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
        print (err_message)
    
    return err_message      

# if __name__ == '__main__':
#     main(args)

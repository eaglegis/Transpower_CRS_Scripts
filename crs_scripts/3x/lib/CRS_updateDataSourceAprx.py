import arcpy
import os

# variables
args = []
err_message = None
log_messages = []


def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def crs_update_datasource(args):
   
    # script name
    script_name = os.path.basename(__file__)
    
    # script parameters
    prj = args[0]
    gdb = args[1]
    
    err_message = None
    
    # log function
    log_msg ('calling {}'.format(script_name))
    try:
       
        aprx = arcpy.mp.ArcGISProject(prj)
        for m in aprx.listMaps():
            for l in m.listLayers():
                log_msg (m.name)
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
    
    return err_message, log_messages     


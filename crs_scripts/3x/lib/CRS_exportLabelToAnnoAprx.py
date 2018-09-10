import arcpy
import os

# variables
args = []
err_message = None
log_messages = []


def log_msg(msg):
    print (msg)
    log_messages.append(msg)

def crs_label_to_annotation(args):
   
    # script name
    script_name = os.path.basename(__file__)
    
    # script parameters
    prj = args[0]
    gdb = args[1]


    dictScale = {'Anno_2_5k': 2500, 'Anno_5k':5000, 'Anno_10k':10000}   #add this back , 'Anno_20k':20000}
    print (dictScale)
    
    err_message = None
    
    # log function
    log_msg('calling {}'.format(script_name))
    try:
       
        aprx = arcpy.mp.ArcGISProject(prj)       
        for m in aprx.listMaps():
            log_msg("Converting labels to annotation for: " + m.name)
            scale = dictScale[m.name]
            log_msg("Converting scale: {}".format(scale))
            arcpy.cartography.ConvertLabelsToAnnotation(m, scale, gdb, 
                                                 m.name, 'MAXOF', 'GENERATE_UNPLACED', 'NO_REQUIRE_ID', 
                                                'STANDARD', '', '', 'AnnoLayers_' + m.name) #Change from 'FEATURE_LINKED' to 'STANDARD' and from 'REQUIRE_ID' to 'NO_REQUIRE_ID' 
            
        del aprx             
       
        
    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
        print (err_message)
    
    return err_message, log_messages      


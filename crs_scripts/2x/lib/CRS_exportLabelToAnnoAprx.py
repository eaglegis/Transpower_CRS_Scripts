import arcpy
import os
# import etgLib

args = []

def crs_label_to_annotation(args):
   
    # script name
    script_name = os.path.basename(__file__)
    
    # script parameters
    prj = args[0]
    gdb = args[1]


    dictScale = {'Anno_2_5k': 2500, 'Anno_5k':5000, 'Anno_10k':10000, 'Anno_20k':20000}
    print (dictScale)
    
    err_message = None
    
    # log function
    # etgLib.log_info(log, 'calling {}'.format(script_name), True)
    try:
       
        aprx = arcpy.mp.ArcGISProject(prj)       
        for m in aprx.listMaps():
            print("Converting labels to annotation for: " + m.name)
            scale = dictScale[m.name]
            print("Converting scale: {}".format(scale))
            arcpy.cartography.ConvertLabelsToAnnotation(m, scale, gdb, 
                                                 m.name, 'MAXOF', 'GENERATE_UNPLACED', 'NO_REQUIRE_ID', 
                                                'STANDARD', '', '', 'AnnoLayers_' + m.name)
            
        del aprx             
       
        
    except Exception as e:        
        err_message =  "ERROR while running {0}: {1}" .format(script_name,e)
        print (err_message)
    
    return err_message      


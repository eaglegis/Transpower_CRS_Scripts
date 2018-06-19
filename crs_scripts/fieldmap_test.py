import arcpy
arcpy.env.overwriteOutput = True


append_layer = r'C:\Developments\transpower\data\labels.gdb\Connect_Property'
target_layer = r'C:\Developments\transpower\spowndata\spown.gdb\Connect_Property'

# set workspace
arcpy.env.workspace = append_layer



#This object looks like the empty grid of fields 
#you see when you first open the append tool in the toolbox
fieldmappings = arcpy.FieldMappings()

#Like when you manually choose a layer in the toolbox and it adds the fields to grid
fieldmappings.addTable(target_layer)
fieldmappings.addTable(append_layer)

##print ("fieldmapping")
##print (fieldmappings)
##
#####Lets map fields that have different names!
list_of_fields_we_will_map = []
#Lets chuck some tuples into the list we made
##list_of_fields_we_will_map.append(('tempDsslvID_TP_PROPERTY_LINK_PROPERTY_ID', 'PROPERTY_ID'))
##list_of_fields_we_will_map.append(('TP_PROPERTY_LEGAL_DESCRIPTION', 'LEGAL_DESCRIPTION'))
##list_of_fields_we_will_map.append(('TP_PROPERTY_TITLE_NO', 'TITLE_NO'))
##list_of_fields_we_will_map.append(('TP_PROPERTY_SUBADDRESS_ID', 'SUBADDRESS_ID'))
##list_of_fields_we_will_map.append(('TP_PROPERTY_ADDRESS_SOURCE', 'ADDRESS_SOURCE'))
##list_of_fields_we_will_map.append(('tempDsslvID_COUNT_TP_PROPERTY_LINK_PARCEL_ID', 'COUNT_PARCEL_ID'))

list_of_fields_we_will_map.append(('PROPERTY_ID','tempDsslvID_TP_PROPERTY_LINK_PROPERTY_ID'))
list_of_fields_we_will_map.append(('LEGAL_DESCRIPTION','TP_PROPERTY_LEGAL_DESCRIPTION'))
list_of_fields_we_will_map.append(('TITLE_NO', 'TP_PROPERTY_TITLE_NO'))
list_of_fields_we_will_map.append(('SUBADDRESS_ID', 'TP_PROPERTY_SUBADDRESS_ID'))
list_of_fields_we_will_map.append(('ADDRESS_SOURCE', 'TP_PROPERTY_ADDRESS_SOURCE'))
list_of_fields_we_will_map.append(('COUNT_PARCEL_ID', 'tempDsslvID_COUNT_TP_PROPERTY_LINK_PARCEL_ID'))




for field_map in list_of_fields_we_will_map:
    print (field_map)
    #Find the fields index by name. e.g 'TaxPin'
    field_to_map_index = fieldmappings.findFieldMapIndex(field_map[0])
##    print (field_to_map_index)
##    print (field_map[1])
##    print ("------")
    #Grab "A copy" of the current field map object for this particular field
    field_to_map = fieldmappings.getFieldMap(field_to_map_index)

##    print (field_to_map)
##    print (field_to_map.inputFieldCount)
##    print (field_to_map.outputField.name)
##    fm1 = arcpy.FieldMap()
    #Update its data source to add the input from the the append layer
##    fm1.addInputField(append_layer, field_map[1])
    
    field_to_map.addInputField(append_layer, field_map[1])
    
    #We edited a copy, update our data grid object with it
    fieldmappings.replaceFieldMap(field_to_map_index, field_to_map)
##    fieldmappings.replaceFieldMap(field_to_map_index, fm1)

#Create a list of append datasets and run the the tool
inData = [append_layer]
arcpy.Append_management(inData, target_layer, schema_type = "NO_TEST", field_mapping=fieldmappings)

import arcpy
mxdPath = r"C:\Developments\transpower\mxd\Create_Annotations2.mxd"
mxd = arcpy.mapping.MapDocument(mxdPath)
df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
print arcpy.mapping.ListLayers(mxd, "", df)[0].name
expr = "def FindLabel ( [PARCEL_ID], [FULL_APP_1], [PURPOSE] , [SURVEY_AREA] , [TOTAL_AREA], [OWNER1] , [OWNER2], [OWNER3] , [OWNER4] , [TITLE1] , [TITLE2] , [TITLE3] , [TITLE4], [CALC_AREA]):\n
    FindLabel = '' \n  
    if [CALC_AREA] >50000 :\n
        FindLabel = [PARCEL_ID] + '\n' + [full_app_1]\n
    return FindLabe"

for lyr in arcpy.mapping.ListLayers(mxd):
    
    if lyr.supports("LABELCLASSES"):
        print ("has label class")
        for lblClass in lyr.labelClasses:
            expr = lblClass.expression
            print (expr)
            
    else:
        print ("no label class")
        # for lblClass in lyr.labelClasses:
        #     lblClass.SQLQuery = lblClass.SQLQuery.replace("[", "\"")
        #     lblClass.SQLQuery = lblClass.SQLQuery.replace("]", "\"")
        #     lblClass.SQLQuery = lblClass.SQLQuery.replace("*", "%")
mxd.saveACopy(r"C:\Developments\transpower\mxd\test2.mxd")
del mxd

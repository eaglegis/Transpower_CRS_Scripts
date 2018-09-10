# config.py
# 2018-04
# created by Yongji Zhang (Eagle)
#
# this file is the application setting file for "CRS_Main1.py"
#
#
# when deploying to the Server, this file needs to be somewhere Python knows about, for example, "C:\Python27\ArcGIS10.5\Lib"
# alternatively add its location to the PYTHONPATH variable
# or put this file in the same location as the application file "TP_SCRIPT.py"

# modify these, always use "/", paths should always finish with a "/"
# this file is in python format, be default, the indent is 4 spaces, when edit it parameters below, make sure the format is correct



class Settings:
    # WORKING_FOLDER = r'D:\CRS\Data\Jul2018'
    CHECKDATA_MXD_NAME = 'Check_data.mxd'
    ANNOTATION_MXD_NAME = 'Create_Annotations.mxd'
    CRS_GDB_NAME = 'CRS.gdb'
    LABEL_GDB_NAME = 'labels.gdb'
    ASSET_GDB_NAME = 'Assets.gdb'
    EXTENT = '1080000,4730000,2100000,6230000'
    # STG_SDE_PATH = r'D:\CRS\SDEConnections\dataloader@NZC_STG@cdcspa-tstdbs80.tptest.transpower.co.nz.sde'    
    # STG_SDE_PREFIX = 'NZC_STG.MAPDATA.'   
    CONTEXT_SDE_PATH = r'D:\CRS\SDEConnections\dataloader@NZCONTEXT@cdcspa-tstdbs80.tptest.transpower.co.nz.sde'    
    CONTEXT_SDE_PREFIX = 'NZCONTEXT.MAPDATA.'
    # SPREPORT_SDE_PATH = r'D:\CRS\SDEConnections\map_user@SPREPORT@SQLPRD-SPATIAL.transpower.co.nz.sde'       
    # SPREPORT_SDE_PREFIX = "SPREPORT.MAPDATA."
    ANNOTATION_PROJ_NAME = 'create_annotations.aprx'
    CHECKDATA_PROJ_NAME = 'Check_data.aprx'
    
    CUTOFF_AGE= 30

    # TESTING 
    WORKING_FOLDER = r'C:\Developments\transpower\AUG2018'
    STG_SDE_PATH = r'C:\Developments\transpower\stagedata\stg.gdb'    
    STG_SDE_PREFIX = ''
    SPREPORT_SDE_PATH = r'C:\Developments\transpower\spreportdata\spreport.gdb'
    SPREPORT_SDE_PREFIX =''

    #  for crs10, Preprod SPOWN also used in CRS_Main5, CRS_Main6
    PREPROD_SPREPORT_SDE_PATH = r'D:\CRS\SDEConnections\dataloader@SPREPORT@cdcspa-tstdbs80.tptest.transpower.co.nz.sde' #r"Database Connections\pp_Dataloader@SPREPORT@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### preprod SPREPORT SDE path
    PROD_SPREPORT_SDE_PATH = r"Database Connections\p_dataloader@SPREPORT@SQLPRD-SPATIAL.transpower.co.nz.sde"  ### production SPREPORT SDE path
    PREPROD_SPOWN_SDE_PATH = r'D:\CRS\SDEConnections\dataloader@SPOWN@cdcspa-tstdbs80.tptest.transpower.co.nz.sde'  ##r"Database Connections\pp_Dataloader@SPOWN@NDCSTG_SPAT_AG.transpower.co.nz.sde"  ### preprod SPOWN SDE path
    PROD_SPOWN_SDE_PATH = r"Database Connections\p_dataloader@SPOWN@SQLPRD-SPATIAL.transpower.co.nz.sde"  ### production SPOWN SDE path
    
          
    #log file name
    LOG_NAME = 'crs_log'

    # email settings
    # SEND_EMAIL = True
    # SMTP_SERVER = 'smtp.transpower.co.nz'
    # FROM_EMAIL = 'CRS_Processing@transpower.co.nz '
    # TO_EMAIL = ['mark.peacey@transpower.co.nz']
    # EMAIL_SUBJECT = 'CRS Process Script'
    # EMAIL_BODYTEXT = 'Processing log file is attached'
    SEND_EMAIL = True
    SMTP_SERVER = 'www1.eagle.co.nz'
    FROM_EMAIL = 'beth-anne_lee@eagle.co.nz'
    TO_EMAIL = ['yongji_zhang@eagle.co.nz']
    EMAIL_SUBJECT = 'CRS Processs Script'
    EMAIL_BODYTEXT = 'process log file is attached'
 

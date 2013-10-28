# -*- coding: utf-8 -*-
#
# 定义全局变量

gl_sqlite = 'sqlite'
gl_mysql = 'mysql'

gl_tmanager_port = '46669'
gl_mmi_int_step = 100
gl_mmi_int_ratio = 0

gl_fail = 'failure'
gl_suc = 'success'
gl_NULL = 'NULL'

gl_test_result_old = '2011-01-01'
gl_check_box_checked = 'checked'


gl_test_xml = 'test_xml'
gl_test_list_model = 'test_list_model'
gl_home_share = '/home/share' 
gl_testcaselist_root = 'D:\\site\\trac\\htdocs\\iTestCTSCase' #'/home/share/test_xml' 
gl_testcasemodel_root = 'D:\\site\\trac\\htdocs\\iTestCTSCaseModel' #'/home/share/test_list_model' 
gl_prj_log_root = 'D:\\site\\trac\\log'#'/trac/Projects/iTest/log'
gl_win_testcaselist_root = '\\\\10.0.0.221\\iTestCTSCase'#'\\\\itest-center\\share\\test_xml'

gl_table_build = 'bitten_build'

gl_PS_12B = 'PS_12B'
gl_PS = 'PS'

gl_bt_uploadcaselist_txt = 'bt_uploadcaselist_txt'
gl_t_uploadcaselist_txt = 't_uploadcaselist_txt'

#################################
gl_SC7702 = 'SC7702'
gl_SC8800G = 'SC8800G'

gl_6820 = 'fp880xg2_dualsim_rf9810_no_tdas'
gl_6820_new = 'sc6820_modem_vlx_sr1019_tri'
gl_7702 = 'sc7702_datacard_new_usb_sprdv110'
gl_7702_new = 'sc7702_datacard_new_usb_sprdv110_band125'
gl_7702_new_pclint = 'sc7702_modem_dualsim'
gl_sc7702_modem = 'sc7702_modem'

gl_arm_12B_mtcoffset = 'fp880xg2_dualsim_mc'
gl_arm_mtcoffset = 'fp880xg2_dualsim_rf9810'

gl_8810 = 'sc8810_modem_bandE_vlx' #sc8810_modem_vlx
gl_8825 = 'sc8825_modem_vlx'
gl_8501c = 'sc8501c_320X240TK_QW' #'sc8501c_sp8502_modem' #sc8501c_320X240TK_QW
gl_9810 = 'fp880xg2_dualsim_rf9810'
gl_sc8800g2_sp8803g_le = 'sc8800g2_sp8803g_le'

gl_7702_L1IT = 'sc7702_datacard_L1IT_new_usb_sprdv110'
gl_8800g_L1IT = 'sc8800g2_L1IT_sp8803g_le'

#################################
gl_psit_version = 'TDPS_UEIT'
gl_ueit = 'ueit'
gl_psit_ = 'psit'
gl_rrm_version = 'RRM'
gl_ARM = 'ARM'
gl_ARM_8810 = 'ARM_8810'
gl_ARM_6820 = 'ARM_6820'


#################################
_gl_versionnum_prefix = 'DM_BASE_W13.'

gl_Disconnect = 'Disconnect'

gl_all_tests = 'All Tests'

###########################################

gl_Psit_Log = 'Psit_Log'
gl_Gen_Log = 'Gen_Log'
gl_Arm_Log = 'Arm_Log'
gl_Other_Log = 'Other_Log'
gl_Saved_Log = 'Saved_Log'
gl_Temp = 'Temp'
 
gl_searchrules = ['Creator', 'ReqName']
gl_ps_tmangertypes = ['Formal']


gl_casefilter_class = ['From_PassList','Not_Filter']
gl_From_PassList = 'From_PassList'
gl_Not_Filter = 'Not_Filter'

gl_little_verfies = ['CR', 'DB', 'NULL']
gl_verfies = ['CR', 'DB', 'BASE', 'MP', 'NULL']
gl_CR = 'CR'
gl_DB = 'DB'
gl_MP = 'MP'
gl_BASE = 'BASE'

gl_versiondeltypes = ['Yes', 'No']
gl_Yes = 'Yes'
gl_No = 'No'
####################
gl_TestID = 'TestID'

gl_href_watingtest = 'watingtest'
gl_href_inprogresstest = 'inprogresstest'

####################

gl_new_priorities = ['Low', 'Middle', 'High', 'Highest']
gl_new_Low = 'Low'
gl_new_Middle = 'Middle'
gl_new_High = 'High' 
gl_new_Highest = 'Highest'


###############################
gl_SVN_Comm = 'SVN_Comm'


#######################################################
#MSIT/RDIT 平台定以如下：
#1)  MSITSINGLE : MSIT 单卡手机
#2)  MSITDUAL   : MSIT 双卡手机
gl_msitPlatforms = ['MSITSINGLE', 'MSITDUAL']
gl_psitPlatforms = ['WINDOWS']

#2）PlatForm去掉。//PlatForm不能去掉，显示如下，因为用户可以自定义 List 测试，这时需要 Platform
#1-singlesim_le
#2-dualsim
#3-dualsim_rf9810
#保留平台信息如下：
#dual_sim(rf9810)
#single_sim
#dual_sim
#gl_rditPlatforms = ['DUAL_SIM(rf9810)', 'SINGLE_SIM']
gl_rditPlatforms = ['T2(8810)','T2(9810)', 'T1', 'T2', 'W1', 'T2W1', 'T2(9810)W1']
gl_rditPlatforms_2 = ['T2(8810)','T2(9810)','T2(8501c)','T1', 'T2', 'W1']
gl_T2_9810 = 'T2(9810)'
gl_T2_8810 = 'T2(8810)'
gl_T2_8501c = 'T2(8501c)'
#######################################################
#tManagertype        
#gl_servertypes = ['NULL', 'PSIT','RDIT','MSIT','L1IT','PLD_SRT','PLD_Monkey', 'DEBUG']
gl_servertypes = ['CTS']

gl_test_type_st = 'ST'
gl_test_type_debug = 'DEBUG'

gl_normal = 'normal'
gl_low = 'low'
gl_high = 'high'
gl_extreme = 'extreme'

gl_yes = 'YES'
gl_no = 'NO'

gl_ProductIDs = ['sc6530', 'sc8501C', 'sc6531', 'sc6500', \
                'sc7701', 'sc7702', 'sc8502']

gl_ProductPatterns = ['bar_op','bar_qw','fpga','fpga_rvds','le', \
                              'pda','pda_formal','pda_le','pda_op' \
                              'pda_rvct_le', 'pda_rvct_le','pda2', \
                              'tk_inside_op', 'tk_op', 'tk_op_formal', 'tk_qw', \
                              '3G', 'TD']
gl_MemoryWidths = ['16*16','32*64','64*64','128*64','512*256','32*32']
gl_ScreenSizes = ['240*320','320*240','240*400','320*480','220*176','128*160']


gl_default_reruntimes = '4'

gl_passlist_path2 = '/netdisk/q/PS/PSIT/PassList'
hsit_passlist_txt = 'hsit_passlist.txt'
hsit_passlist_temp_txt = 'hsit_passlist_temp.txt'
hsit_wholelist_txt = 'hsit_wholelist.txt'
hsit_passlist_cr_txt = 'passlist_cr.txt'



gl_itestbackup_path = '/netdisk/q/PS/PSIT/iTest_Backup'
gl_log = 'log'


gl_pclint_result = 'pclint_result'
gl_init_env = 'init_env'

gl_polling_time_file_name = 'polling_time.txt'
gl_polling_time_file = '/trac/Projects/iTest/log/init_env/polling_time.txt'
gl_rpc_svr_polling_time_file_name = 'rpcsrv_polling_time.txt'
gl_rpc_svr_polling_time_file = '/trac/Projects/iTest/log/init_env/rpcsrv_polling_time.txt'
gl_auto_dailybuild_file_name = 'auto_daily_build.txt'
gl_auto_dailybuild_file = '/trac/Projects/iTest/log/init_env/auto_daily_build.txt'

gl_guardprocess_flag = 'When Restart iTest, Please Click This Button!'

gl_tmanager_busy = 'BUSY'
gl_tmanager_free = 'FREE'


##############################
gl_testtypes = ['CTS']#['HSIT','RDIT','MSIT', 'L1IT', 'PLD_Monkey', 'PLD_SRT']                    
gl_debug = 'DEBUG'
#PSIT
gl_psit = 'PSIT'
gl_HSIT = 'HSIT'

gl_subtypes_CUSTOM = ['CUSTOM'] 

gl_psit_types = ['CR_Admission', 'PASSLIST', 'FULL_TEST', 'DUAL_SMOKE','DUAL_L1_SMOKE', \
                    'DUAL_L1_PASSLIST', \
                    'DUAL_L2_SMOKE', \
                    'DUAL_L2_PASSLIST', \
                    'DUAL_BCFE_SMOKE', \
                    'DUAL_DCFE_SMOKE', \
                    'DUAL_DM_SMOKE','DUAL_NAS_SMOKE', 'DUAL_L4_SMOKE', \
                    'SMOKE','BCFE_SMOKE','DCFE_SMOKE','DM_SMOKE', \
                    'NAS_SMOKE','L4_SMOKE','WG_SMOKE', \
                    'LTE_SMOKE', 'WDUAL_SMOKE'] 

gl_SMOKE = 'SMOKE'
gl_CUSTOM = 'CUSTOM'
gl_DUAL_L1_PASSLIST = 'DUAL_L1_PASSLIST'
gl_DUAL_L2_PASSLIST = 'DUAL_L2_PASSLIST'

gl_FULL_TEST = 'FULL_TEST'
gl_PASSLIST = 'PASSLIST'
gl_PASSLIST_TEST = 'PASSLIST_TEST'
gl_PASSLIST_T = 'PASSLIST_T'
gl_PASSLIST_CR = 'CR_Admission'

                    
#rdit
gl_rdit = 'RDIT'
gl_rdit_types = ['DualSim_SMOKE', 'DualSim_FULL', 'SingleSim_SMOKE', 'SingleSim_FULL', 'AT_Modem']
gl_DualSim_SMOKE = 'DualSim_SMOKE'
gl_SingleSim_SMOKE = 'SingleSim_SMOKE'
gl_DualSim_FULL = 'DualSim_FULL'
gl_SingleSim_FULL = 'SingleSim_FULL'

#MSIT
gl_msit = 'MSIT'
gl_msit_types = ['SMOKE']

#L1IT
gl_l1it = 'L1IT'
gl_l1it_types = ['WDM_SMOKE','WDM_PassList','TDDM_SMOKE','TDDM_12B_SMOKE','TDDM_12A_SMOKE', \
                'WDM_SMOKE_CMU200_ONLY', 'WDM_SMOKE_SMU200_ONLY', 'LTE_CR_TEST', 'LTE_SMOKE_TEST']
#L1IT 平台定义目前如下：


gl_l1itPlatforms = ['8800G', '8810', '6820', 'SC7702', '8501C', '8825', 'LTE9610']
gl_l1itPlatforms_2 = ['SC7702', '8800G']
gl_8800G = '8800G'
gl_SC7702 = 'SC7702'

#RRM
gl_rrm = 'RRM'

#PLD
gl_buildtype_pld = 'PLD'
gl_pld_srt = 'PLD_SRT'
gl_pld_monkey = 'PLD_Monkey'
gl_pld_srt_types = ['SMOKE']
gl_cts_types = ['TestPackageList_Android4.0.3']
##############################
#mmi
gl_all = 'all'
gl_user = 'loginer'
gl_search = 'search'


gl_enablestart = 'enablestart'
gl_disablestart = 'disablestart'
gl_rebootstart = 'rebootstart'

##############################
gl_TestCreated = 'TestCreated'
gl_TestWaitingVersion = 'TestWaitingVersion'
gl_TestVersionReady = 'TestVersionReady'
gl_TestReady = 'TestReady'
gl_TestInProgress = 'TestInProgress'
gl_TestWaitingStop = 'TestWaitingStop'
gl_TestStopAndDelete = 'TestStopAndDelete'
gl_TestStopped = 'TestStopped'
gl_TestFinish = 'TestFinish'
gl_TestError = 'TestError'

##############################
#email
gl_cathy = 'cathy.wang'
gl_admin_psit = ['song.shan','junbo.han','cathy.wang']
gl_admin_rdit = ['song.shan','junbo.han','cuilian.yang', 'zhaozeng.wang']
gl_admin_l1it = ['song.shan','junbo.han','chenglin.xu','zhidong.liu']
gl_admin_msit = ['song.shan','junbo.han','tommy.tang', 'zhaozeng.wang']
gl_admin_build = ['song.shan']

##############################
gl_b_submittest = 'submittest'
gl_b_saveandstarttest = 'saveandstarttest'
gl_b_test_search = 'TestSearchButton'
gl_b_remove_tests = 'remove_tests'
gl_b_connect = 'connect_test_server'
gl_b_disconnect = 'disconnect_connection'
gl_b_uploadcaselist_txt = 'uploadcaselist_txt'

gl_versionpath = 'versionpath'
gl_dspversionpath = 'dspversionpath'
gl_name = 'name'
gl_dummy = 'dummy'
gl_creator = 'creator'
gl_versionnum = 'versionnum'
gl_test_type_mode = 'test_type_mode'
gl_versiondeltype = 'versiondeltype'
gl_casefilterclass = 'casefilterclass'
gl_priority = 'priority'
gl_verify = 'verify'
gl_caselist_file = 'caselist_file'
gl_srv_testlist = 'caselist_txtfile'

gl_testserverip = 'testserverip'
gl_testserverport = 'testserverport'
gl_testservertype = 'servertype'


gl_server_monitor_polling_time = 'server_monitor_polling_time'
gl_server_monitor = 'server_monitor'
gl_rpc_server_monitor = 'rpc_server_monitor'

gl_rpcsvr_testreport = "http://172.16.0.61:8888"  #"http://172.16.15.41:8888"


def  url_starter_busyagent(tmanager_type, starter):
        tmp = "?StarterIP=" + starter
        url = 'http://itest-center/iTest/itest/ServerMonitor/home/'+tmanager_type+tmp  
        return url

def  url_starter(tmanager_type, starter):
        tmp = "?StarterIP=" + starter
        url = 'http://itest-center/iTest/itest/ServerManager/home/'+tmanager_type+tmp  
        return url   

def  url_inprogress_test_nums(tmanager_type, test):
        tmp = "?testid=" + str(test.id)  
        tmp += "&testname=" + test.name   
        #self.data['inprogress_test_nums_url'] = "http://itest-center/iTest/build?inprogress_test_nums=all" +tmp
        url = 'http://itest-center/iTest/itest/SearchTest/home/'+tmanager_type+tmp  
        return url

def  url_log_testid(req, test):  
    return req.href('/itest/SearchTest/home')+'/TestID'+'?testid='+str(test.id)        


def  url_log_testid_(test):  
    return 'http://itest-center/iTest/itest/SearchTest/home/TestID'+'?testid='+str(test.id)          

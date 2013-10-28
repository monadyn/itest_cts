# -*- coding: utf-8 -*-
#



import os
import thread
import threading
import socket
import sys
import time
import ConfigParser

from datetime import datetime

from xmlrpclib import ServerProxy
from SimpleXMLRPCServer import SimpleXMLRPCServer

from trac.config import BoolOption, IntOption, Option
from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_link, add_stylesheet, add_ctxtnav, \
                            prevnext_nav, add_script, add_stylesheet, add_script, add_warning, add_notice
from trac.util import escape, pretty_timedelta, format_datetime, shorten_line, \
                      Markup

import gl
import itest_mmi_data
import test_action
import utils
import slave_utils
import web_utils 
#from iTest.model import TManager  
import tmanager_model

class TManagerSrv(object):
    def __init__(self, env, db_conn, table_tmanager,ip='', port=None, tmanager='', sub_tmanager=''):
        self.env = env
        self.log = env.log
        self.tmanager = tmanager        

        self.sub_tmanager = tmanager + '_MANAGER1'        
        self.max_tmanagernum = 0
        self.ip = ip
        self.port = port
        self.svr = None
        self.test = None #itest DB inprogresstest
        self.tStatus = 0 #tmanager stutus
        self.ttest = '' #tmanager inprogresstest name

        self.table_tmanager = table_tmanager                        
        self.tmanager_svr = None      
        self.testaction = test_action.TestAction(self.env, db_conn)

        #rpc_opt
        self.allstartinfo = ''
        self.alluagertinfo = ''


    def delete(self):         
        if self.table_tmanager is not None:
            self.table_tmanager.delete() 

    def insert(self,env):
        #self.table_tmanager = TManager(env)               
        self.log.debug('test_svr_con insert: table_tmanager=%s',self.table_tmanager)            
        self.table_tmanager['name'] = self.sub_tmanager
        self.table_tmanager['type'] = self.tmanager
        self.table_tmanager['ip'] = self.ip
        self.table_tmanager['port'] = 1 #diconncet
        self.table_tmanager['active'] = 'Yes'
        self.table_tmanager['connect_status'] = ''
        self.table_tmanager['inprogress_test'] = '' 
        self.table_tmanager['test_status'] = 0         
        self.table_tmanager.insert() 
        self.log.debug('test_svr_con insert: ID=%s',self.table_tmanager.ID)            
        
    def max_num(self, env):         

        self.max_tmanagernum = 1   
        

    def get_all_ips(self):
        ips = []
        server_nums = 0
        for tmanager in TManager.select(self.env):   
            server_nums = server_nums + 1
            ips.append(tmanager.ip)  
        return (server_nums,ips)


    def get_all_subtypes(self):
        sub_tmanagetypes = []
        server_nums = 0
        for tmanager in TManager.select(self.env):   
            server_nums = server_nums + 1
            sub_tmanagetypes.append(tmanager.name)  
        return (server_nums,sub_tmanagetypes)
        
    
    def check_num(self, env, req): 
        server_num = itest_mmi_data._server_tmanager_nums(self.env, req, self.tmanager)                          
        self.max_num(self.env)
        #self.log.debug('check_num: %s', str(self.max_tmanagernum))
        
        #检查最大支持个数        
        if server_num >= self.max_tmanagernum :         
            add_notice(req,"TManager nums has been limited. JUST Permiss Max (%s) TManager!",str(self.max_tmanagernum))        
            return False
        else:
            return True


    def check_subtype(self, env, req): 
        return True
        #检查子类型是否重名
        (server_nums, sub_tmanagetypes) = self.get_all_subtypes()        
        if server_nums == 0:
            return True
        else:
            #ret = sub_tmanagetypes.index(sub_tmanagetype)
            #list.index(x): x not in list
            ret = self.sub_tmanager in sub_tmanagetypes
            self.log.debug('check_subtype: ret %s',ret) 
            if ret == True:                
                self.log.debug('check_subtype: %s, ret=%s', self.sub_tmanager, ret)  
                add_notice(req,"Server Sub Type has been used!") 
                return False   
            else:
                
                return True

    def check_ip(self, env, req): 	
        return True
        #检查ip 是否重用
        (server_nums, ips) = self.get_all_ips()    
        if server_nums == 0:
            return True
        else:
            ret = self.ip in ips
            if ret == True:
                self.log.debug('check_ip: %s, ret=%s', self.ip, ret)  
                add_notice(req,"Server IP has been used!") 
                return False   
            else:
                return True
  
    def valid(self, env, req): 
        ret1 = self.check_num(self.env, req)
        ret3 = self.check_subtype(self.env, req)
        ret4 = self.check_ip(self.env, req)
        
        if ret1 == False or ret3 == False or ret4 == False:            
            ret = False 
        else:
            ret = True         
        return ret
               
    def link(self, env):
        if self.ip != '':
            connect_url = 'http://' + self.ip + ':46669' #+ self.port
            self.log.debug('T link: %s',connect_url) 
            self.svr = ServerProxy(connect_url) 
            if self.svr is not None:
                self.log.debug('T link: svr=%s',self.svr) 
                return True
            else:
                self.log.error('T link: %s, ret false',connect_url) 
                return False
        else:
            return False
             

    def thread(self, env, req):           
        if self.svr is None:
            return False            

        #self.log.debug('thread: %s %s %s',os.getppid(), self.sub_tmanager)
        thread.start_new_thread(self.schedule, (self.env, req, 'haha'))   
        return True


    def schedule(self, env, req, cc): 
        locked_num = 0
        while 1: 
            #polling_time = utils._show_current_time()         
            #self.log.debug('=========start %s(%s)', sub_tmanagetype, polling_time)
            #self.log.debug('=========schedule %s(%s)', self.sub_tmanager, str(locked_num))

            #lock = FileLock(self.env, tmanager=self.tmanager, sub_tmanager=self.sub_tmanager)
            #ret = lock.acquire()

            #self.log.debug('schedule: ++ %s', self.sub_tmanager)
            #if ret == True:                   
                ret = self.process(self.env, req)                   
                #lock.release() 
                #self.log.debug('schedule: ret = %s', ret)
                
                if ret == False:
                    break                                                      
                
                time.sleep(30)
                #locked_num = 0
                #self.log.debug('schedule: locked_num = %s', locked_num)
            #else:
            #    time.sleep(5)
            #    locked_num = locked_num + 1
                #self.log.debug('schedule: %s(%s) wait_lock', self.sub_tmanager, str(locked_num))            
            # #   if locked_num > 3:
            #        lock.release()
            #        locked_num = 0 

            #self.log.debug('schedule: -- %s', self.sub_tmanager)
        self.log.warning('schedule: jump while %s', self.sub_tmanager) 
    

    def R_GetTaskInfoFromStart(self, env, nTaskID):
        socket.setdefaulttimeout(15) 
        try:     
#LPCTSTR	CApplicationOprImp::GetTaskInfoFromStart(int nTaskID)

#返回值：   172.16.15.135:2|172.16.0.67:84
            #self.log.error('GetTaskInfoFromStart: nTaskID=%s', nTaskID) 
            ret = self.svr.GetTaskInfoFromStart(int(nTaskID))
            #返回值10个  20|20|20|*****|90
            #self.log.error('GetTaskInfoFromStart: -- %s', ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('GetTaskInfoFromStart socket.error, nTaskID=%s', nTaskID)  
            socket.setdefaulttimeout(None)
            return None

    def R_GetBuzyAgentNum(self, env, ip):
        socket.setdefaulttimeout(15) 
        try:     
            #ret = None
            #self.log.error('R_GetBuzyAgentNum: ++ %s,%s,%s,%s', ip, section, key, cfg_type)  
            ret = self.svr.GetBuzyAgentNum(ip) 
            #返回值10个  20|20|20|*****|90
            self.log.error('R_GetBuzyAgentNum: -- %s ', ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_GetBuzyAgentNum socket.error, %s', ip)  
            socket.setdefaulttimeout(None)
            return None

    def R_GetCgfParameter(self, env, ip, section, key, cfg_type):
        socket.setdefaulttimeout(15) 
        try:     
            ret = None
            self.log.error('R_GetCgfParameter: ++ %s,%s,%s,%s', ip, section, key, cfg_type)  
            ret = self.svr.GetCgfParameter(ip, section, key, cfg_type) 
            self.log.error('R_GetCgfParameter: -- %s ', ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_GetCgfParameter socket.error, %s,%s,%s,%s', ip, section, key, cfg_type)  
            socket.setdefaulttimeout(None)
            return None

    def R_SetCgfParameter(self, env, ip, section, key, string, cfg_type):
        socket.setdefaulttimeout(15) 
        try:     
#void  SetCgfParameter(#
#	LPCTSTR lpIPAddr,       		// start IP Address
#	LPCTSTR lpSectionName,    	// section name
#	LPCTSTR lpKeyName,       	// key name
#	LPCTSTR lpString,			    // string to add
#	int 	nCfgType;				//Config type
#);

#	E_CFG_TMANAGER = 0,		//Configured tManager.ini
#	E_CFG_START,				//Configured Starter.ini
#	E_CFG_UAGENT				//Configured UAgent.ini     
            self.log.error('R_SetCgfParameter: ++ %s,%s,%s,%s,%s', ip, section, key, string, cfg_type)  
            ret = self.svr.SetCgfParameter(ip, section, key, string, cfg_type) 
            self.log.error('R_SetCgfParameter: -- %s ', ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_SetCgfParameter socket.error, %s,%s,%s,%s,%s', ip, section, key, string, cfg_type)  
            socket.setdefaulttimeout(None)
            return ''  
            

    def R_CtrlServer(self, env, ip, ctrl_type):
        socket.setdefaulttimeout(15)        
        try: 
            if ctrl_type == gl.gl_enablestart:
                int_ctrl_type = 1
            elif ctrl_type == gl.gl_disablestart:
                int_ctrl_type = 0
            elif ctrl_type == gl.gl_rebootstart:
                int_ctrl_type = 2
            else:
                int_ctrl_type = 99
                
            if int_ctrl_type == 99:
                self.log.error('R_CtrlServer: ip=%s, ctrl_type=%s, not support', ip, ctrl_type) 
            else:
                self.svr.CtrlAppointedSrv(ip, int_ctrl_type)
#	E_DISABLE_START=0,		//Disable start
#	E_ENABLE_START,			//Enable start
#	E_REBOOT_SRV				//Reboot strat            
            self.log.error('R_CtrlServer: ip=%s, ctrl_type=%s', ip, ctrl_type) 
            socket.setdefaulttimeout(None)
            return                
        except socket.error,e:
            self.log.error('R_CtrlServer socket.error, ip=%s', ip)  
            socket.setdefaulttimeout(None)
            return 

    def R_DelVersion(self, env, ip, testid, testname):
        socket.setdefaulttimeout(15)        
        try:   
            #ip ='NULL', 删除所有服务器的版本
            self.svr.DelVerPackage(int(testid), testname, ip)       
            self.log.error('R_DelVersion: ip=%s, testid=%s', ip, testid) 
            socket.setdefaulttimeout(None)
            return                
        except socket.error,e:
            self.log.error('R_DelVersion socket.error, ip=%s', ip)  
            socket.setdefaulttimeout(None)
            return 


    def R_ServerInfo(self, env, ip):
        socket.setdefaulttimeout(15)        
        try:     
            #elf.allstartinfo = self.svr.GetAllStartInfo() 
            #self.log.error('R_ServerInfo: --GetAllStartInfo=%s ', self.allstartinfo) 
            #if ip == '0':
            #    self.allstartinfo = self.svr.GetStartInfo('NULL')
            #else:
            #    self.allstartinfo = self.svr.GetStartInfo(ip)
            self.allstartinfo = self.svr.GetStartInfo(ip)
            #self.log.error('R_ServerInfo: ip=%s, allstartinfo=%s ', ip, self.allstartinfo) 
            socket.setdefaulttimeout(None)
            return self.allstartinfo                     
        except socket.error,e:
            self.log.error('R_ServerInfo: socket.error, ip=%s', self.ip)  
            socket.setdefaulttimeout(None)
            return ''              
           
    def R_UAgentInfo(self, env, ip, port=0):
        socket.setdefaulttimeout(15)        
        try:     
            #self.log.error('R_UAgentInfo: ++alluagertinfo=%s ', self.allstartinfo) 
            self.alluagertinfo = self.svr.GetUagentInfo(ip, port) #接收来自ITest的查询对应测试类型的分控中的所有启动器信息
            #self.log.error('R_UAgentInfo: --alluagertinfo=%s ', self.allstartinfo) 
            socket.setdefaulttimeout(None)
            return self.alluagertinfo                     
        except socket.error,e:
            self.log.error('RPC_OPT: R_UAgentInfo socket.error, ip=%s, ip=%s', self.ip, ip)  
            socket.setdefaulttimeout(None)
            return '' 


    def R_SrvMonitorInfo(self, env, ip, minitor_type):
        socket.setdefaulttimeout(15) 
        try:     
            ret = self.svr.NoticeAppointedSrv(ip, minitor_type) 
            self.log.error('R_SrvMonitorInfo: minitor_type=%s , %s ', minitor_type, ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_SrvMonitorInfo socket.error, ip=%s, ip=%s', self.ip, ip)  
            socket.setdefaulttimeout(None)
            return '' 

    def R_RunningCaseInfo(self, env, testid, testname):
        socket.setdefaulttimeout(15) 
        try:     
            ret = self.svr.GetTaskRunningCaseList(int(testid), testname) 
            #self.log.error('R_RunningCaseInfo: %s ', ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_RunningCaseInfo socket.error, testid=%s, testname=%s', testid, testname)  
            socket.setdefaulttimeout(None)
            return '' 


    def R_FailCaseInfo(self, env, testid, testname):
        socket.setdefaulttimeout(15) 
        try:     
            ret = self.svr.GetTaskFailedCaseList(int(testid), testname) 
            #self.log.error('R_FailCaseInfo: ret=%s, %s,%s', ret,testid, testname) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_FailCaseInfo socket.error, testid=%s, testname=%s', testid, testname)  
            socket.setdefaulttimeout(None)
            return '' 

        except socket.timeout:
            self.log.error('R_FailCaseInfo socket.timeout, testid=%s, testname=%s', testid, testname)  
            socket.setdefaulttimeout(None) 
            return 'NULL'         
        except socket.error,e:
            self.log.error('R_FailCaseInfo socket.error, testid=%s, testname=%s', testid, testname)  
            socket.setdefaulttimeout(None) 
            return 'NULL' 
        except socket.gaierror,e:
            self.log.error('R_FailCaseInfo socket.gaierror, testid=%s, testname=%s', testid, testname)  
            socket.setdefaulttimeout(None) 
            return 'NULL' 

    def R_PassedNum(self, env, testid, testname):
        socket.setdefaulttimeout(15) 
        try:     
            ret = self.svr.GetPassCount(int(testid), testname) 
            #self.log.error('R_RunningCaseInfo: %s ', ret) 
            socket.setdefaulttimeout(None)
            return ret                     
        except socket.error,e:
            self.log.error('R_PassedNum socket.error, testid=%s, testname=%s', testid, testname)  
            socket.setdefaulttimeout(None)
            return '' 


class MutilTManagerSrv(TManagerSrv):
    def __init__(self, env, db_conn, table_tmanager, ip='', port='', \
                tmanager='', sub_tmanager=''):
        TManagerSrv.__init__(self, env, db_conn, table_tmanager, ip=ip, port=port, tmanager=tmanager, sub_tmanager=sub_tmanager)
        #self.log.debug('MutilTManagerSrv: %s, ip(%s)', self.sub_tmanager, self.ip) 
        self.inprogresstests_num = None #tmanager inprogresstest num
        self.inprogresstests = None #itest DB inprogresstest
        self.tStatuses = '' #tmanager stutus
        self.ttests = '' #tmanager inprogresstest name
        self.ttests_num = 0
        self.allstartinfo_test = ''
        self.db_type = gl.gl_mysql
        
    def upload_testreport(self, env, test): 
        testdata = {}
        testname = test.name
        testreportpath = itest_mmi_data._test_reportpath(self.env, test)  
        test_type = itest_mmi_data._test_type(self.env, test)            
        testdata['creator'] = test.creator
        testdata['testreportpath'] = testreportpath
        testdata['id'] = test.id
        testdata['versionpath'] = test.versionpath
        testdata['testname'] = testname
        testdata['versionnum'] = test.version_num
        testdata['testtype'] = test_type
        #self.log.error('upload_testreport: %s %s testreportpath=%s', self.sub_tmanager, testname, testreportpath)            
            
        if test_type == gl.gl_pld_srt \
                    or test_type == gl.gl_pld_monkey:  
            case = itest_mmi_data._test_one_case(self.env, test)               
            testdata['case'] = case
            self.log.error('gl_pld_monkey case=%s', case)
            rpc_slv_pld(self.env, testdata)
        elif test_type == gl.gl_psit \
                    or test_type == gl.gl_l1it \
                    or test_type == gl.gl_msit \
                    or test_type == gl.gl_rdit:           
            testdata['verfy_type'] = itest_mmi_data._test_verfy_type(self.env, test)                                       
            rpc_slv_testreport(self.env, testdata)

    def update_bz_comment(self, env, test):    
        #builddata = {}
        testdata = {}
        testname = test.name
        self.log.error('update_bz_comment: 1update_bz_comment , %s', testname)
        test_type = itest_mmi_data._test_type(env, test)  
        
        test_url=gl.url_log_testid_(test) #'http://itest-center/iTest/build/testresult/' + str(test.id)
        self.log.error('update_bz_comment: 2update_bz_comment , test_url %s', test_url)
        
        #priority=test.priority
        versionpath=test.versionpath
        version_num = test.version_num
        passratio=itest_mmi_data._test_passratio(env, test)
        self.log.error('update_bz_comment: 4update_bz_comment , passratio %s', passratio)
        total=itest_mmi_data._test_total_num(env, test)
        self.log.error('update_bz_comment: 4update_bz_comment , total %s', total)
        passed=test.passed
        failed=test.failed
        start_t=format_datetime(test.started)
        end=format_datetime(test.stopped)
        
        timecost=itest_mmi_data._test_timecost(env, test.started, test.stopped)
        self.log.error('update_bz_comment: 4update_bz_comment , timecost %s', timecost)
        result_path=itest_mmi_data._test_reportpath(env, test)
        self.log.error('update_bz_comment: 4update_bz_comment , result_path %s', result_path)
        caselist=itest_mmi_data._test_xmlfile_mmipath(env, test)        
        self.log.error('update_bz_comment: 4update_bz_comment , caselist %s', caselist)

        int_passratio = itest_mmi_data._test_int_passratio(env, test) 
        if int_passratio < 90:
            #测试完成后的ResultInfo如果有效（通过率>90%)，则自动写入到Bugzilla对应Bug号的Comment字段中
            return
            
        self.log.error('update_bz_comment testname=%s', testname)   
        #self.log.error('update_bz_comment test_type=%s', test_type)   
        if test_type == gl.gl_psit \
                    or test_type == gl.gl_HSIT:  
            testname_subs = testname.split('_',testname.count('_'))
            testdata['comment_content'] = "---------------------------------------\n"
            testdata['comment_content'] += "TestName:"+testname+"\n"    
            testdata['comment_content'] += "TestType:"+test_type+"\n"   
            testdata['comment_content'] += "VersionNum:"+version_num+"\n"   
            testdata['comment_content'] += "TotalCasesNum:"+str(total)+"\n"  
            testdata['comment_content'] += "PassedCasesNum:"+str(passed)+"\n"   
            testdata['comment_content'] += "FailedCasesNum:"+str(failed)+"\n"    
            testdata['comment_content'] += "PassRatio:"+passratio+"\n"   
            #testdata['comment_content'] += "StartTime:"+start_t+"\n"    
            #testdata['comment_content'] += "EndTime:"+end+"\n"    
            #testdata['comment_content'] += "TimeCost:"+timecost+"\n"
            #self.log.error('update_bz_comment comment_content=%s', testdata['comment_content'])
            testdata['comment_content'] += "ResultPath:"+result_path+"\n"   
            testdata['comment_content'] += "CaseListPath:"+caselist+"\n"   
            testdata['comment_content'] += "VersionPath:"+versionpath+"\n" 
            testdata['comment_content'] += "TestURL:"+test_url+"\n"  
            testdata['comment_content'] += "---------------------------------------\n"
            #self.log.error('update_bz_comment comment_content=%s', testdata['comment_content'])

            #config = BuildConfig.fetch(self.env, testname)  
            #if config is not None:
            #builddata['comment_content'] = "---------------------------------------\n"           
            #all_builds = Build.select(self.env, config=testname)
            #for build in all_builds:  
            #    versionnum = itest_mmi_data._build_versionnum(self.env, build)
            #    baseurl = itest_mmi_data._build_url(self.env, build)
            #    patchfile_sharedpath = itest_mmi_data._build_mail_patchfile(self.env, build)
            #    patch_path = itest_mmi_data._build_mail_patch_basepath(self.env, build)
            #    build_url = 'http://itest-center/iTest/build/' + testname + '/' + str(build.id)
            #    builddata['comment_content'] += "BuildName:"+testname+"\n"  
            #    builddata['comment_content'] += "VersionNum:"+versionnum+"\n"  
            #    builddata['comment_content'] += "VersionURL:"+baseurl+"\n"  
            #    builddata['comment_content'] += "Patch:"+patchfile_sharedpath+"\n"  
            #    builddata['comment_content'] += "RelativePath:"+patch_path+"\n"  
            #    builddata['comment_content'] += "BuildURL:"+build_url+"\n"  
            #    break
            #builddata['comment_content'] += "---------------------------------------\n"
            
            for testname_sub in testname_subs:
                self.log.error('update_bz_comment testname_sub=%s', testname_sub)
                if slave_utils.check_string(testname_sub, 'bug') == True \
                        or slave_utils.check_string(testname_sub, 'Bug') == True:                         
                    bug_id = testname_sub
                    bug_id = bug_id.replace('bug','')
                    bug_id = bug_id.replace('Bug','')
                    if bug_id != '':
                        self.log.error('update_bz_comment bug_id=%s', bug_id)
                        testdata['bug_id'] = bug_id                                
                        rpc_slv_Add_BZ_Comment(self.env, testdata)

                        #builddata['bug_id'] = bug_id 
                        #rpc_slv_Add_BZ_Comment(self.env, builddata)



    def update_tmanager(self, status=None, inprogress_id=None):           	  
        if self.table_tmanager is None:
            self.log.debug('update_tmanager: table_tmanager=%s',self.table_tmanager)
            return
        else:   
            self.log.debug('update_tmanager: table_tmanager=%s',self.table_tmanager)
            if status is not None:            
                self.table_tmanager['connect_status'] = status
            if inprogress_id is not None:          
                self.table_tmanager['inprogress_test'] = inprogress_id

            polling_time = datetime.utcnow()
            polling_time = polling_time.isoformat()
            polling_time = int(utils._format_datetime(polling_time))
            self.table_tmanager['port'] = polling_time  
            self.log.error('update_tmanager: polling_time=%s, polling_time',polling_time)
            self.table_tmanager.save_changes() #update()   
            self.log.error('update_tmanager: polling_time=%s, ok',polling_time)

    def stop_repeat_testids(self, status, repeated_tests): 
        status_tests = []
        if self.tmanager == gl.gl_psit \
                or self.tmanager == gl.gl_HSIT:
            for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=status, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True):  
                testname = test.build 
                testname_subs = testname.split('_',testname.count('_'))            
                for testname_sub in testname_subs:
                    if slave_utils.check_string(testname_sub, 'bug') == True \
                                or slave_utils.check_string(testname_sub, 'Bug') == True:                         
                        bug_id = testname_sub.replace('bug','')
                        bug_id = bug_id.replace('Bug','')
                        if bug_id != '':
                            status_tests.append(bug_id)  
            
            myset = set(status_tests)
            for item in myset:
                if status_tests.count(item) > 1:
                    repeated_tests.append(item)
                    
            #self.log.error('stop_repeat_testids: repeated_tests=%s', repeated_tests) 

    def stop_repeat_tests(self, status, repeated_tests, all_repeated_tests): 
        if self.tmanager == gl.gl_psit \
                or self.tmanager == gl.gl_HSIT:      
            #self.log.error('stop_repeat_tests: repeated_tests=%s', repeated_tests)  
            for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=status, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True):   
                testname = test.build
                version_num = test.version_num
                
                repeat_flag = False
                testname_subs = testname.split('_',testname.count('_'))  
                a_repeated_test = {}
                for testname_sub in testname_subs:
                    if slave_utils.check_string(testname_sub, 'bug') == True \
                                    or slave_utils.check_string(testname_sub, 'Bug') == True:                         
                            bug_id = testname_sub.replace('bug','')
                            bug_id = bug_id.replace('Bug','')
                            if bug_id != '':                                
                                if bug_id in repeated_tests and repeat_flag == False:
                                    a_repeated_test['bug_id'] = bug_id
                                    a_repeated_test['testname'] = testname
                                    a_repeated_test['version_num'] = version_num
                                    repeat_flag = True
                    elif utils.checknums(self.env, testname_sub) == True:
                            #self.log.error('process_inprogress6: testname_sub %s', testname_sub) 
                            if repeat_flag == True:
                                a_repeated_test['time'] = int(testname_sub)
                                all_repeated_tests.append(a_repeated_test)
                                break
                                #repeat_flag = False
            #self.log.error('stop_repeat_tests: all_repeated_tests=%s', all_repeated_tests)                     
            

    
    def stop_repeat(self):
        if self.tmanager == gl.gl_psit \
                or self.tmanager == gl.gl_HSIT:     
            pass
        else:
            return
            
        repeated_tests = []
        self.stop_repeat_testids(gl.gl_TestInProgress, repeated_tests)
        self.stop_repeat_testids(gl.gl_TestVersionReady, repeated_tests)
        self.stop_repeat_testids(gl.gl_TestReady, repeated_tests)
       
        all_repeated_tests = []   
        self.stop_repeat_tests(gl.gl_TestInProgress, repeated_tests, all_repeated_tests)
        self.stop_repeat_tests(gl.gl_TestVersionReady, repeated_tests, all_repeated_tests)
        self.stop_repeat_tests(gl.gl_TestReady, repeated_tests, all_repeated_tests) 
            
        #5)	针对同一版本，当相同测试单同时出现时
        #（单子的前面部分相同，只是后面添加的时间不同， 并且状态不是finish），只保留最后一个，其余的都stop掉。           
        for repeated_bug_id in repeated_tests: 
            self.log.error('stop_repeat: all_repeated_tests=%s', all_repeated_tests) 
            self.log.error('stop_repeat: repeated_tests=%s', repeated_tests)          
            stoped_time = 30001231245959
            stoped_name = ''
            version_num = ''
            for a_repeated_test in all_repeated_tests:
                bug_id = a_repeated_test['bug_id']
                time = a_repeated_test['time']
                if bug_id != repeated_bug_id:
                    continue    
                if stoped_time > time:
                    stoped_time = time#最早提交的单子
                    testname = a_repeated_test['testname']
                    version_num = a_repeated_test['version_num']

            Stop_Flag = False
            #self.log.error('stop_repeat: ag %s,%s', testname, version_num)   
            for a_repeated_test in all_repeated_tests: 
                bug_id = a_repeated_test['bug_id']
                if bug_id != repeated_bug_id or testname == a_repeated_test['testname']:
                    continue    
                    
                if version_num == a_repeated_test['version_num']:   
                    Stop_Flag = True
                    break
                #else:                    
                #    self.log.error('stop_repeat: version_num=%s', version_num) 
                #    self.log.error('stop_repeat: a_repeated_test[version_num]=%s', a_repeated_test['version_num']) 

            if Stop_Flag == True:
                self.log.error('stop_repeat: stoped_name=%s', stoped_name) 
                stoped_test = self.testaction.T_Fetch(test_name = stoped_name)   
                self.M_Stop(stoped_test)
                
        
    def process_versionready(self):  
        self.log.debug('process_versionready: %s, ttests=%s, ttests_num=%s',self.tmanager, self.ttests, self.ttests_num) 
        for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=gl.gl_TestVersionReady, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True): 
            self.M_Load(test)    #versionready->ready
            
    def process_ready(self, env, req):  
        self.log.debug('process_ready: ttests=%s, ttests_num=%s', self.ttests, self.ttests_num) 
        for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=gl.gl_TestReady, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True):                             
            self.log.debug('MutilTManagerSrv: process_ready %s', test.build) 
            #获得状态，根据状态处理
            self.idlerun(self.env, req, test)

    def process_inprogress(self, env, req):  
        self.log.debug('process_inprogress: +++%s  ttests=%s, ttests_num=%s', self.sub_tmanager, self.ttests, self.ttests_num) 
        tInprogress = self.ttests
          
        for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=gl.gl_TestInProgress, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True):   
            self.log.debug('process_inprogress:  %s', test.build) 
            testname = test.build
            if slave_utils.check_string(tInprogress, testname) == True:           
                self.M_Run(self.env, req, test)  
                tInprogress = tInprogress.replace(test.build+';','')
                self.ttests_num = self.ttests_num -1                
            #else:#会被错误的stop
                #self.log.error('process_inprogress: %s: testname=%s', self.sub_tmanager, testname) 
                #self.M_Stop(test)
                #self.log.error('process_inprogress: %s: M_Stop testname=%s', self.sub_tmanager, testname)
            #    continue
            
                
        if tInprogress != '':
            module_count = tInprogress.count(';')
            modules = tInprogress.split(';',module_count) 
            self.log.debug('process_inprogressP: %s ttests=%s, ttests_num=%s, tInprogress=%s', self.sub_tmanager, self.ttests, self.ttests_num, tInprogress)
            i = 0
            while (module_count > 0):             
                self.log.debug('process_inprogress: left testname=%s', modules[i])

                #容错      
                if modules[i] is not None and modules[i] != '':
                    test = self.testaction.T_Fetch(test_name = modules[i], env=self.env)                    
                    if test is not None:
                        if test.category == gl.gl_TestFinish:
                            ret_delete = self.svr.Delete(test.id, test.name)   
                        elif test.category == gl.gl_TestVersionReady:
                            self.log.error('process_inprogress: %s %s',self.sub_tmanager, test.name)  
                            self.testaction.update_startp(test=test)
                            self.log.error('process_inprogress: %s %s VERSION_READY->IN_PROGRESS',self.sub_tmanager, test.name)                              
                i = i + 1
                module_count = module_count -1 
        self.log.debug('process_inprogress: ---%s  ttests=%s, ttests_num=%s', self.sub_tmanager, self.ttests, self.ttests_num)         
                


    def process_stopping(self):  
        for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=gl.gl_TestWaitingStop, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True):                              
            self.log.debug('MutilTManagerSrv: process_stopping %s', test.build) 
            #获得状态，根据状态处理
            self.M_Stop(test)
        #self.log.debug('MutilTManagerSrv: process_stopping -- %s', self.sub_tmanager) 


    def process_stopanddelete(self):  
        for test in self.testaction.T_Select(db_type=self.db_type, \
                            env=self.env, \
                            status=gl.gl_TestStopAndDelete, \
                            tmanager=self.tmanager, \
                            is_run_waiting_queue=True):                               
            self.log.debug('MutilTManagerSrv: process_stopanddelete %s', test.build) 
            #获得状态，根据状态处理
            self.M_Delete(test)
        #self.log.debug('MutilTManagerSrv: process_stopping -- %s', self.sub_tmanager) 
                            
    def process(self, env, req):   
        socket.setdefaulttimeout(15)        
        try:       
            #self.log.error('process: CTS IN') 
            #self.log.error('sub_tmanager=%s', self.sub_tmanager)
            #self.log.error('svr=%s', self.svr)
            self.tStatuses = self.ttests = self.svr.GetCurInProgressTest()  
            self.ttests_num = self.ttests.count(';')            
            self.log.error('%s: ttests=%s ttests_num=%s', self.sub_tmanager, self.ttests, self.ttests_num) 
                  
        except socket.error,e:
            self.log.error('iTest HeatBeat: Socket Error, %s', self.tmanager) 
            #发邮件
            socket.setdefaulttimeout(None)                       
            return False   
        socket.setdefaulttimeout(None)

        #self.stop_repeat()  
        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('%s:  1  tStatuses=%s ttests=%s', self.sub_tmanager, self.tStatuses, self.ttests) 
            
        self.process_stopping()   
        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('%s:  2', self.sub_tmanager) 
            
        self.process_stopanddelete()
        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('%s:  3', self.sub_tmanager) 
            
        self.process_versionready() 
        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('%s:  4', self.sub_tmanager) 
            
        self.process_ready(self.env, req)      #处理ready, starttime          
        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('%s:  5', self.sub_tmanager) 
            
        self.process_inprogress(self.env, req)    #处理, pass/fail
        #self.log.error('%s:  inprogress  tStatuses=%s ttests=%s', self.sub_tmanager, self.tStatuses, self.ttests)           
        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('%s:  6', self.sub_tmanager) 
            
        self.update_tmanager(status=self.tStatuses, inprogress_id=self.ttests)
        #self.log.error('%s:  done, server status tStatuses=%s ttests=%s', self.sub_tmanager, self.tStatuses, self.ttests) 
            
        return True

        
    def realstop(self, env, req, test):  
        
        #if inttimecost > 60*60*24*30:       #1month           
        #    self.M_Stop(test)
        #    self.log.error('realstop: tmanager(%s) inttimecost=%s', self.tmanager, inttimecost)
        #    self.log.error('realstop: stop=%s', test.name)  
            
        if self.tmanager == gl.gl_l1it \
                or self.tmanager == gl.gl_pld_monkey:
            return

        pri = test.priority  
        if pri == gl.gl_new_Highest:             
            return

        inttimecost = itest_mmi_data._test_inttimecost(self.env, test)
        stop_during = 60*60*24*7
        pass_count = int(test.passed)
        fail_count = int(test.failed)
        total_count = pass_count + fail_count
        int_passratio = itest_mmi_data._test_int_temppassratio(self.env, test)
        subtype = itest_mmi_data._test_subtype(self.env, test)  

        #超时stop机制对smoke单
        if self.tmanager == gl.gl_psit:
            if slave_utils._is_fulltest(subtype) == True: 
                stop_during = 60*60*24*14 #14day
            else:
                stop_during = 60*60*3
        elif self.tmanager == gl.gl_rdit:
            if subtype == gl.gl_DualSim_SMOKE or subtype == gl.gl_SingleSim_SMOKE:
                stop_during = 60*30*3
        else:
            stop_during = 60*60*24*7
            
        #self.log.error('realstop1: tmanager(%s) name=%s', self.tmanager, test.name)
        if inttimecost > stop_during:                  
            self.M_Stop(test)
            self.log.error('realstop: tmanager(%s) inttimecost=%s', self.tmanager, inttimecost)
            self.log.error('realstop: stop=%s', test.name)   
              
        #低于一定的通过率，比如70%, 自动stop的机制还存在吗？如果没有的话要加上。
        #以后每个Cr都是全测试，如果没有的话占用资源太浪费。
        #self.log.error('realstop2: total_count=%s int_passratio=%s', total_count, int_passratio)
        if total_count > 400 and int_passratio < 70:
            self.M_Stop(test)
            self.log.error('realstop: total_count=%s int_passratio=%s', total_count, int_passratio)
            self.log.error('realstop: stop=%s', test.name)         

    def realratio(self, env, req, test): 
        testid = test.id
        testname = test.name    
        ret_passcount = 0
        ret_failcount = 0
        ret_tmp_failcount = None
        test_type = itest_mmi_data._test_type(self.env, test) 
        try:
            ret_passcount = self.svr.GetPassCount(testid, testname)  
            if test_type == gl.gl_psit \
                    or test_type == gl.gl_HSIT:
                ret_failcount = self.svr.GetRelFailCount(int(testid), testname)
                ret_tmp_failcount = self.svr.GetFailCount(testid, testname)
            else:
                ret_failcount = self.svr.GetFailCount(testid, testname)
            self.log.debug('MutilTManagerSrv: GetPassCount(%s),GetFailCount(%s) %s', ret_passcount,ret_failcount,test.name)
            result_path = self.svr.GetResultPath(testid, testname)

            if test_type == gl.gl_pld_srt \
                    or test_type == gl.gl_pld_monkey:
                pre_fail = int(test.failed)
                if ret_failcount > pre_fail:
                    #实时上报bug
                    self.log.error('MutilTManagerSrv: upload_testreport %s > %s', ret_failcount, pre_fail) 
                    self.upload_testreport(self.env, test)
                     
                    #self.update_bz_comment(self.env, test)
            self.testaction.update_passratio(str(ret_passcount),str(ret_failcount), result_path, \
                                    test=test, tmp_failed_nums=ret_tmp_failcount)            
            
        except socket.error,e:
            self.log.error('MutilTManagerSrv: realratio: socket.error')
            return 

    def idlerun(self, env, req, test): 
        testid = test.id
        testname = test.name
        self.change_pri(test)          
        pri = itest_mmi_data._test_pri_int(test) 
        self.svr.SetTaskPrior(testid, testname, pri)
        self.log.debug('idlerun: SetTaskPrior (%s) pri=%s',self.tmanager, pri)
        
        tStatus = self.svr.IsTestDone(testid, testname) 
        #self.log.debug('MutilTManagerSrv: idlerun: testname=%s, tStatus=%s',testname,tStatus)
                        
        #0 ：初始状态； 1 ：运行结束； 2 ：启动失败； 3 ：启动完成； 4 ：正在运行； 5 ：运行失败；  6 ：运行暂停， 后面的数值都作为reserved                         
        if tStatus == 1:  #运行结束  
            #服务器断了，继续连上
            self.realratio(self.env, req, test)
            #db_file._test_update_end(self.env, test, gl.gl_TestFinish)
            self.testaction.update_endp(gl.gl_TestFinish, test=test)
            self.log.debug('idlerun1: %s %s READY->DONE',self.sub_tmanager, testname)
            ret_delete = self.svr.Delete(testid, testname) 
            self.log.debug('idlerun1: %s ret_delete=%s', testname, ret_delete)        
        elif tStatus == 4:  #test running                                            
            #db_file._test_update_start(self.env, test)    
            self.testaction.update_startp(test=test)
            self.log.debug('idlerun4: %s %s READY->IN_PROGRESS',self.sub_tmanager, testname)
        elif tStatus == 5:     # test fail            
            self.testaction.T_Update(new_status=gl.gl_TestStopped, test=test)
            self.M_Stop(test)
            self.log.debug('idlerun5: %s %s READY->STOPPED',self.sub_tmanager, testname)
        elif tStatus == 9:
            self.log.debug('idlerun9: %s %s',self.sub_tmanager, testname) 
        elif tStatus == -1:     # tmanager crash, ready->versionready
            self.log.debug('idlerun-1: %s %s',self.sub_tmanager, testname) 
            #db_file._test_update_status(self.env, gl.gl_TestReady, gl.gl_TestVersionReady, test)
        elif tStatus == 0: 
            self.testaction.T_Update(new_status=gl.gl_TestVersionReady, test=test)
            self.log.debug('idlerun0: %s %s READY->VERSION_READY',self.sub_tmanager, testname)
        else:
            self.log.debug('idlerun: tmanager (%s %s %s)',self.sub_tmanager, testname, tStatus)                    
            self.tStatuses = self.tStatuses.replace(testname, '(ready)')
                
    def M_Run(self, env, req, test): 
        testid = test.id
        testname = test.name
        self.change_pri(test)  
        pri = itest_mmi_data._test_pri_int(test) 
        self.svr.SetTaskPrior(testid, testname, pri)
        #self.log.debug('Run: SetTaskPrior (%s) pri=%s',self.tmanager, pri)
        
        tStatus = self.svr.IsTestDone(testid, testname) 
                        
        #0 ：初始状态； 1 ：运行结束； 2 ：启动失败； 3 ：启动完成； 4 ：正在运行； 5 ：运行失败；  6 ：运行暂停， 后面的数值都作为reserved                         
        if tStatus == 0:  #初始状态
            pass
            self.log.error('Run: 0 %s %s',self.sub_tmanager, testname)             
        elif tStatus == 1:  #运行结束    
            self.realratio(self.env, req, test)
            ret_delete = self.svr.Delete(testid, testname) 

            self.log.error('Run1: %s %s ret_delete=%s, IN_PROGRESS->DONE', self.sub_tmanager, testname, ret_delete)
            self.testaction.update_endp(gl.gl_TestFinish, test=test)
            
            self.log.error('Run1: 1=========== testname=%s', testname)            
            self.upload_testreport(self.env, test) 
            self.log.error('Run1: 2=========== testname=%s', testname)  
            self.update_bz_comment(self.env, test)
            self.log.error('Run1: 3=========== testname=%s', testname)  
            
            #删除版本
            versiondel_type = itest_mmi_data._test_versiondel_type(self.env, test)    
            if versiondel_type == gl.gl_Yes:
                self.log.error('Run1: R_DelVersion %s %s %s', self.sub_tmanager, testid, testname)
                self.R_DelVersion(self.env, 'NULL', testid, testname)
                #rpc_server.R_DelVersion(env, starter, testid, testname)
                
        elif tStatus == 4:  #test running                                                        
            self.log.debug('Run4: %s %s realratio',self.sub_tmanager, testname)  
            self.realratio(self.env, req, test)
        elif tStatus == 5:  #test err   
            self.M_Stop(test)
            self.log.error('Run5: 0 %s %s IN_PROGRESS->Stopping',self.sub_tmanager, testname)                
        elif tStatus == -1:
            self.log.debug('Run-1: %s %s',self.sub_tmanager, testname)  
        elif tStatus == 9:  #test running                                                        
            self.log.debug('Run9: %s %s',self.sub_tmanager, testname)       
        else:
            self.log.error('Run: tmanager (%s %s %s)',self.sub_tmanager, testname, tStatus) 

        self.tStatuses = self.tStatuses.replace(testname, str(tStatus))   

        self.realstop(self.env, req, test)

    def change_pri(self, test):
#5)	针对同一版本，当相同测试单同时出现时（单子的前面部分相同，只是后面添加的时间不同， 并且状态不是finish），只保留最后一个，其余的都stop掉。
        if self.tmanager == gl.gl_psit \
                or self.tmanager == gl.gl_HSIT:
            pass
        else:
            return

        subtype = itest_mmi_data._test_subtype(self.env, test)
        case_nums = itest_mmi_data._test_total_num(self.env, test) 
        prio = itest_mmi_data._test_pri(test) 
        verfy_type = itest_mmi_data._test_verfy_type(self.env, test)

        left = itest_mmi_data._test_Left(self.env, test)
        if left < 101:
            #=>High
            if prio != gl.gl_new_Highest:
                self.testaction.T_Update(priority=gl.gl_new_High, test=test)
                return

        #3)	针对"LOW"优先级的测试单，在提单12小时后还没有测试完成的，将优先级提到"MIDDLE"
        if prio == gl.gl_new_Low:
            inttimecost = itest_mmi_data._test_intwaittime(self.env, test)
            #self.log.error('change_pri: %s inttimecost=%s',self.sub_tmanager, inttimecost) 
            stop_during = 60*60*12 #12 hour              
            if inttimecost > stop_during:               
                self.testaction.T_Update(priority=gl.gl_new_Middle, test=test)
                return
                
        if prio == gl.gl_new_Middle:
            inttimecost = itest_mmi_data._test_intwaittime(self.env, test)
            #self.log.error('change_pri: %s inttimecost=%s',self.sub_tmanager, inttimecost) 
            stop_during = 60*60*12*5 #5day          
            if inttimecost > stop_during:               
                self.testaction.T_Update(priority=gl.gl_new_High, test=test)
                return

        #4)	将DB单的优先级设置为"HIGH"(周二测试，需要更快的出结果)。BASE和MP单的优先级设置为MIDDLE(一般周末测试)
        if verfy_type == gl.gl_DB and prio != gl.gl_new_Highest:
            self.testaction.T_Update(priority=gl.gl_new_High, test=test)
            return
        elif verfy_type == gl.gl_MP or verfy_type == gl.gl_BASE:
            if prio == gl.gl_new_Low:
                self.testaction.T_Update(priority=gl.gl_new_Middle, test=test)
                return            
        
        if subtype == gl.gl_CUSTOM and case_nums > 5000 and prio == gl.gl_new_Middle:
            #1)	当itest单为CUSTOM时，如果case数量<=5000 则保持middle优先级权限，否则将其权限设置为"LOW"
            self.testaction.T_Update(priority=gl.gl_new_Low, test=test)          
        elif subtype == gl.gl_PASSLIST_CR:
            #2)	当选择是类型"CR_Admission"时，将初始优先级设置为"MIDDLE"
            self.testaction.T_Update(priority=gl.gl_new_Middle, test=test)


        
    def M_Load(self, test):
        testid = test.id
        testname = test.name
        #升级waiting time
        self.testaction.update_waitingtime(test)
        self.change_pri(test)        

        tStatus = self.svr.IsTestDone(testid, testname) 
        #self.log.error('MutilTManagerSrv: Load testname=%s, testid=%s, tStatus=%s',testname, testid, tStatus)
        if tStatus == 4:  #test running                                                        
            self.log.error('M_Load: %s %s',self.sub_tmanager, testname)  
            self.testaction.update_startp(test=test)
            self.log.error('M_Load: %s %s VERSION_READY->IN_PROGRESS',self.sub_tmanager, testname)   
            return

        #if self.tmanager == gl.gl_pld_monkey:
        #    self.log.error('M_Load: %s %s %s',self.sub_tmanager, testname, tStatus) 
        
        version_path = test.versionpath
        caselist_path = itest_mmi_data._test_xmlfile_mmipath(self.env, test)        
        version_path = version_path.replace('/','\\')
        version_path = version_path.replace('iTest_center_build','')        
        #caselist_path = caselist_path.replace('/','\\')
        version_num = test.version_num
        pri = itest_mmi_data._test_pri_int(test)  
        plinfo = itest_mmi_data._test_plinfo(self.tmanager, test.reserved8)        
        if self.tmanager == gl.gl_pld_monkey:
                self.log.error('M_Load: 2%s %s %s',self.sub_tmanager, testname, tStatus) 
                
        try:
            if self.tmanager == gl.gl_l1it:                
                dsp_version_path = itest_mmi_data._test_dspversionpath(test)
                version_origin_flag = itest_mmi_data._test_versionorigin(test)
                    
                self.svr.SetDspVersionPath(testid, testname, dsp_version_path)
                self.log.debug('MutilTManagerSrv: Load: dsp_version_path=%s ',dsp_version_path)                 
                                       
                self.svr.SetVersionNo(testid, testname, version_num)
                self.svr.SetVersionType(testid, testname, version_origin_flag)                
               
            elif self.tmanager == gl.gl_psit \
                    or self.tmanager == gl.gl_HSIT:
                verfy_type = itest_mmi_data._test_verfy_type(self.env, test)  
                if verfy_type == 'CR' or verfy_type == 'DB':# CR DB
                    self.svr.SetReRunTimeEx(testid, testname, 9)     
                else:
                    self.svr.SetReRunTimeEx(testid, testname, 5)            
            elif self.tmanager == gl.gl_pld_monkey:
                self.svr.SetReRunTimeEx(testid, testname, 0)
            elif self.tmanager == gl.gl_pld_srt:
                self.svr.SetReRunTimeEx(testid, testname, 2)                
            else:
                self.svr.SetReRunTimeEx(testid, testname, 5)

            #第一个参数为任务标示的整数值，第二个参数为任务名的字符串； 第三个参数为测试类型的字符串（比如 RDIT,PSIT ）。
            self.svr.SetTestType(testid, testname, self.tmanager)             
            self.svr.SetVersionPath(testid, testname, version_path)
            self.svr.SetXmlPath(testid, testname, caselist_path)
            self.log.debug('MutilTManagerSrv: Load: %s (%s)(%s)(%s)',testname, version_path, caselist_path, version_num)             

            #SetTaskPrior: 第一个参数为任务标示的整数值，第二个参数为任务名的字符串；第三个参数为任务的优先级 (int) 。
            #在多任务并行中，优先级调度放在分控中心实现
            self.svr.SetTaskPrior(testid, testname, pri)
            self.log.debug('MutilTManagerSrv: Load: SetTaskPrior (%s) pri=%s',testname, pri)             
            
            #SetTaskPLInfo: 第一个参数为任务标示的整数值，第二个参数为任务名的字符串；第三个参数为任务的平台信息的字符串
            #在类似 RDIT 的测试子系统中，通过这个平台信息以及 agent 反馈上来的所支持的平台信息进行比对，
            #从而将 CASE 分配给合适的 agent 运行
            if self.tmanager == gl.gl_pld_monkey:
                self.log.error('M_Load: 3%s %s %s',self.sub_tmanager, testname, tStatus) 
                
            if self.tmanager == gl.gl_l1it \
                    or self.tmanager == gl.gl_rdit \
                    or self.tmanager == gl.gl_msit \
                    or self.tmanager == gl.gl_pld_monkey \
                    or self.tmanager == gl.gl_pld_srt:
                #self.log.debug('MutilTManagerSrv: Load: SetTaskPLInfo+ (%s) %s',testname, plinfo) 
                self.svr.SetTaskPLInfo(testid, testname, plinfo)
                self.log.debug('MutilTManagerSrv: Load: SetTaskPLInfo (%s) %s',testname, plinfo)                  
            
            #第一个参数为任务标示的整数值，第二个参数为任务名的字符串 。
            #在多任务中，这个函数必须在调用了 SetVersionPath,SetXmlPath 等等设置函数后调用。
            ret_load = self.svr.Load(testid, testname) 
            self.log.debug('MutilTManagerSrv: Load: ret_load=%s ', ret_load)
            if ret_load == 1:                    
                self.testaction.T_Update(new_status=gl.gl_TestReady, test=test)
                self.log.debug('MutilTManagerSrv: Load Suc: %s %s %s',self.tmanager, self.sub_tmanager,testname)                     

            if self.tmanager == gl.gl_pld_monkey:
                self.log.error('M_Load: 4%s %s ret_load=%s',self.sub_tmanager, testname, ret_load)                 
        except socket.timeout:
            self.log.debug('MutilTManagerSrv: Load: socket.timeout') 
        except socket.error,e:
            self.log.debug('MutilTManagerSrv: Load: socket.error')  
        except socket.gaierror,e:
            self.log.debug('MutilTManagerSrv: Load: socket.gaierror') 
        return                    



    def M_Delete(self, test): 
        #在delete单子时加个判断，如delete返回值为FALSE,请加个retry机制
        locked_num = 0
        while 1:             
            ret = self.M_Stop(test)
            if ret == True:
                test.delete()
                locked_num = 0
                break                
            else:
                locked_num = locked_num + 1
                if locked_num > 3:
                    test.delete()
                    locked_num = 0
                    break

                    
    
    def M_Stop(self, test):               
        try:                   
            if test is None:
                self.log.error('M_Stop: test=is None ')
                return False 
            testid = test.id
            testname = test.name
            self.log.error('MutilTManagerSrv: Stop: (%s)(%s) ', testid, testname)
            socket.setdefaulttimeout(15)

            try:  
                ret_stop = self.svr.Stop(testid,testname)
                if ret_stop == 0:
                    self.log.error('MutilTManagerSrv: Stop: %s Fail!', testname)                
                    #return False   
                self.log.error('MutilTManagerSrv: Stop: ret_stop=%s (%s) ', ret_stop, testname)
                
            except socket.timeout:
                self.log.debug('MutilTManagerSrv: Load: socket.timeout') 
                return False 
            except socket.error,e:
                self.log.debug('MutilTManagerSrv: Load: socket.error')  
                return False 
            except socket.gaierror,e:
                self.log.debug('MutilTManagerSrv: Load: socket.gaierror')  
                return False 
            
            ret_delete = self.svr.Delete(testid,testname)             
            if ret_delete == 0:
                self.log.error('MutilTManagerSrv: Delete: %s Fail!', testname)                
                #return False
            #self.log.debug('MutilTManagerSrv: Stop: ret_delete=%s (%s) ', ret_delete, testname)

            #db_file._test_update_end(self.env, test, gl.gl_TestStopped)  
            self.testaction.update_endp(gl.gl_TestStopped, test=test)

            test_type = itest_mmi_data._test_type(self.env, test)           
            testreportpath = itest_mmi_data._test_reportpath(self.env, test) 
            testdata = {}
            
            testdata['creator'] = test.creator
            testdata['testreportpath'] = testreportpath

            total_count = int(test.passed) + int(test.failed)
            submit_total_count = itest_mmi_data._test_total_num(self.env, test)
            self.log.error('MutilTManagerSrv: total_count=(%s), target=%s, %s', str(total_count), str(0.95 * submit_total_count), testname)
        
            #两个条件，一是运行的case超过总数的95%（pass case num + fail case num >= 0.95 * total case num），
            #二是测试单没有被系统stop（手动stop不算）
            if test_type == gl.gl_psit \
                    and total_count > (0.95 * submit_total_count):                    
                testdata['id'] = test.id
                testdata['verfy_type'] = itest_mmi_data._test_verfy_type(self.env, test)
                testdata['testname'] = testname
                testdata['versionnum'] = test.version_num 
                testdata['versionpath'] = test.versionpath
                testdata['testtype'] = test_type
                
                #rpc_slv_testreport(self.env, testdata)                
                #self.update_bz_comment(self.env, test)
                
            socket.setdefaulttimeout(None)            
            
            self.log.error('MutilTManagerSrv: Stop: %s Succ!', testname)                                                     
            return True            
        except socket.error,e:
            self.log.error('MutilTManagerSrv: Stop: socket.error')
            socket.setdefaulttimeout(None)
            #db_file._test_update_end(self.env, test, gl.gl_TestStopped)    
            self.testaction.update_endp(gl.gl_TestStopped, test=test)
            return False 
            

class ServerButton(object):
    def __init__(self, env, table_tmanager, tmanager='', sub_tmanager='', \
                        ip='', port=''):
        self.env = env
        self.log = env.log
        #self.db_conn = db_conn
        self.tmanager = tmanager
        if sub_tmanager != '':
            self.sub_tmanager = sub_tmanager
        else:
            if tmanager != '':
                self.sub_tmanager = tmanager + '_MANAGER1'  
            else:
                self.sub_tmanager = ''
            
        self.ip = ip
        self.port = port    
        self.table_tmanager = table_tmanager
        #if self.sub_tmanager != '':            
        if 0:
            QF = {}
            QF['field_name'] = self.sub_tmanager
            querylist = self.table_tmanager.select(QF) 
            
            if len(list(querylist)) == 1:            
                self.ip = q_row['ip']
                self.port = q_row['port']
                self.tmanager = q_row['type']        
        self.tmanager_svr = None                


    def disconnect(self,req): 
        #if req is not None:
        #    req.perm.assert_permission('BUILD_ADMIN')           
        if self.table_tmanager is not None:
            self.table_tmanager.delete() 
        else:          
            self.log.error('test_svr_discon: tmanager_svr is None')

    def connect_svr(self, req, db_conn, flag=''):                
        if flag == 'new':
            self.ip = req.args.get('testserverip', '')
            self.tmanager = req.args.get('servertype', '')  
            self.sub_tmanager = req.args.get('serversubtype', '') 
            ret = tmanager_svr.valid(self.env, req)    
            if ret == False:
                self.log.debug('test_svr_con: ret_valid is false') 
                add_notice(req,"Sorry, Server Configuarion is invalid.")
                return False  
            tmanager_svr.insert(self.env) 
        
        tmanager_svr = MutilTManagerSrv(self.env, db_conn, \
                        self.table_tmanager, ip=self.ip, \
                        tmanager=self.tmanager, \
                        sub_tmanager=self.sub_tmanager)
                        
        self.log.debug('test_svr_con: %s',self.sub_tmanager)          
        ret = tmanager_svr.link(self.env)        
        if ret == False:
            self.log.debug('test_svr_con: svr is None')  
            add_notice(req,"Sorry, Server ServerProxy fail.")
            return False  

        #free lock
        #lock = FileLock(self.env, tmanager=tmanagetype, \
        #                sub_tmanager=sub_tmanagetype)
        #ret = lock.release() 
        
        ret = tmanager_svr.thread(self.env, req)
        if ret == False:   
            add_notice(req, "Error Action! socket.error!")
            add_notice(req, "Please Check tManager!")
            return False             
        
        return ret



class FileLock(object):
    def __init__(self, env, tmanager='', sub_tmanager=''):
        self.env = env
        self.log = env.log
        self.tmanager = tmanager
        self.sub_tmanager = sub_tmanager
        
        self.init_env = utils.get_file_dir(self.env, utils.get_itest_log_dir(self.env), gl.gl_init_env) 
        if not os.path.exists(self.init_env):  
	        os.mkdir(self.init_env)  

        if self.tmanager != '':
            lock_filename = self.tmanager + '.txt'
            self.lock_file = utils.get_file_dir(self.env, self.init_env, lock_filename)
            if os.path.isfile(self.lock_file):                    
                lock_status = slave_utils.read_file(self.lock_file)            
                if lock_status == gl.gl_tmanager_busy:
                    self.locked = True
                elif lock_status == gl.gl_tmanager_free:
                    self.locked = False
            else:
                #第一次
                slave_utils.write_file(self.lock_file,gl.gl_tmanager_free) 
                self.locked = False
        
    def acquire(self): 
        #self.log.debug('acquire: %s %s %s %s', self.tmanager, self.sub_tmanager, self.lock_file, self.locked)
        if self.tmanager != '':
            if self.locked == False: 
                ret = True
                slave_utils.write_file(self.lock_file,gl.gl_tmanager_busy)   
            elif self.locked == True: 
                #获得lock后，就加锁
                ret = False                
        else:
            ret = False
        return ret
         
    def release(self):
        #self.log.debug('release: %s %s %s %s', self.tmanager, self.sub_tmanager, self.lock_file, self.locked)
        if self.tmanager != '':
            slave_utils.write_file(self.lock_file, gl.gl_tmanager_free)
            self.locked = False 
        return True
            

    def init_release(self):  
        i = 0        
        nums = len(gl.gl_servertypes)
        tmanager = gl.gl_servertypes        
        while nums > 0:         
            lock_filename = tmanager[i] + '.txt'
            lock_file = utils.get_file_dir(self.env, self.init_env, lock_filename)    
            slave_utils.write_file(lock_file, gl.gl_tmanager_free)        
            self.log.debug('init_release: %s', lock_file)
            nums = nums - 1
            i = i + 1         

      
     
   
def iTestHeartBeat(env,req, table_tmanager, db_conn):  
    current_int_time = utils._get_current_int_time()
    #env.log.error('monitor_tmanager: ++current_int_time = %s',current_int_time)
    QF = {}
    querylist = table_tmanager.select(QF) 
              
    #env.log.error('iTestHeartBeat: querylist=%s',querylist)             
    for tmanager in querylist:                     
        duration_int = current_int_time - int(tmanager['port'])
        #env.log.error('iTestHeartBeat: a_tmanager = %s',tmanager)  
        env.log.error('iTestHeartBeat: duration_int = %s',duration_int)        
        if duration_int > 1*60:    #  dead_while周期  
        #if tmanager['port'] == '1':#bug: port is int in db, but return str
            #自动重联所有disconnect的tmanager
            ID = tmanager['ID']
            a_new_table = tmanager_model.TManager(ID, db_conn) 
            env.log.error('iTestHeartBeat: disconnect')    
            server = ServerButton(env, a_new_table,\
                            sub_tmanager=tmanager['name'], \
                            ip=tmanager['ip'], tmanager=tmanager['type'])
            ret = server.connect_svr(req, db_conn)  #server.test_svr_recon_(req, server.sub_tmanager)
            if ret == True:
                #env.log.error('monitor_tmanager: auto recon suc(%s)(%s)',tmanager.name,tmanager.ip)
                pass
        else:
            env.log.error('iTestHeartBeat: connect')   
            #    #发送邮件                      
            #    if duration_int > 3*60 and duration_int < (3*60+30*1):    #  dead_while周期                 
            #        env.log.error('_itest_tmanager_monitor: sendmail %s',tmanager.name)
            #        for listener in BuildSystem(env).listeners:
            #            listener.tmanager_disconnected(tmanager)   
            

def iTestRPCServer(env,req, polling_time_file_name, cc):       
    while 1:
        env.log.debug('rpc_svr_monitor: while =%s', polling_time_file_name)
        if not os.path.isfile(polling_time_file_name):
            polling_time = gl.gl_guardprocess_flag
        else:
            polling_time = slave_utils.read_file(polling_time_file_name) 
            
        env.log.debug('rpc_svr_monitor: polling_time=%s', polling_time) 
        
        if polling_time == gl.gl_guardprocess_flag: 
            env.log.debug('rpc_svr_monitor: in polling_time=%s', polling_time) 

            thread.start_new_thread(iTestRPCMain, (env,'haha'))

    
            env.log.debug('rpc_svr_monitor: out polling_time=%s', polling_time) 
        else:
            env.log.debug('rpc_svr_monitor: --no triger')    

        polling_time = utils._show_current_time()                         
        slave_utils.write_file(polling_time_file_name,polling_time)

        time.sleep(30*1)
        env.log.debug('rpc_svr_monitor: while out')
        
    env.log.warning('rpc_svr_monitor: while jump')  

def iTestRPCMain(env,cc): 
    svr=SimpleXMLRPCServer(('172.16.0.167', 8888))

    env.log.error('rpc_main: triger 1') 
    
    svr.register_function(rpc_Hello, "rpc_Hello") 
    env.log.error('rpc_main: register rpc_Hello')
    #svr.register_function(rpc_GenTestList, "rpc_GenTestList")     
    #svr.register_function(rpc_SubmitTest, "rpc_SubmitTest")  
    #svr.register_function(rpc_StartTest, "rpc_StartTest")
    svr.register_function(web_utils.iTest_New, "iTest_New") 
    env.log.error('rpc_main: register rpc_NewTest')

    env.log.error('rpc_main: triger 2') 

    svr.serve_forever()  
    env.log.error('rpc_main: triger 3') 
    

def Component_Checkbox(name): 
        js = '' 
        js += "<input type=\"checkbox\" id=\""+name+"\" name=\""+name+"\" value=\""+name+"\""
        #js += "  checked=\"${"+name+" and 'checked' or None}\" /><label for=\""+name+"\">"+name+":</label>   " 
        #js += "  checked=\"${"+name+" or None}\" /><label for=\""+name+"\">"+name+":</label>   " 
        js += "  /><label for=\""+name+"\">"+name+":</label>   "
        return js        

def Component_Select(id, name, options): 
        js = '' 
        js += "  <select id=\""+id+"\" name=\""+id+"\">"
        for option in options:
            js += "    <option value=\""+option+"\">"+option+"</option>"       
        js += "   </select>"
        return js

def Tag_td(content): 
        js = ''  
        js += " <td>"
        js += content
        js += " </td>"
        return js

def Tag_tr(content): 
        js = ''  
        js += "<tr class=\"field\">"
        js += content
        js += "</tr>" 
        return js    

def Tag_th(content): 
        js = ''  
        js += " <th>"
        js += "<label>"+content+":</label>"
        js += "</th>" 
        return js              


def Tag_table(width, content): 
        js = ''  
        js += "<table width=\""+width+"\" style=\"BORDER:1px #333333 solid;\"> "        
        js += content
        js += "</table> "
        return js  
        

def NewTest_Priority(req, priority=None): 
        js = ''
        ###Priority
        js += "<tr class=\"field\">"
        js += "<th><label for=\"priority\">Priority:</label></th>"
        js += "<td>"
        js += "  <select id=\"priority\" name=\"priority\">"
        if priority is not None:
            js += "    <option value=\""+priority+"\">"+priority+"</option>"
            
        js += "    <option value=\""+gl.gl_NULL+"\">"+gl.gl_NULL+"</option>"            
        if req.perm.has_permission('TEST_HIGHEST'):
            js += "    <option value=\""+gl.gl_new_Low+"\">"+gl.gl_new_Low+"</option>"
            js += "    <option value=\""+gl.gl_new_Middle+"\">"+gl.gl_new_Middle+"</option>"
            js += "    <option value=\""+gl.gl_new_High+"\">"+gl.gl_new_High+"</option>"
            js += "    <option value=\""+gl.gl_new_Highest+"\">"+gl.gl_new_Highest+"</option>"
        elif req.perm.has_permission('TEST_FORMAL_VERSION'):
            js += "    <option value=\""+gl.gl_new_Low+"\">"+gl.gl_new_Low+"</option>"
            js += "    <option value=\""+gl.gl_new_Middle+"\">"+gl.gl_new_Middle+"</option>"
            js += "    <option value=\""+gl.gl_new_High+"\">"+gl.gl_new_High+"</option>"
        elif req.perm.has_permission('TEST_DAYLI_VERSION'):
            js += "    <option value=\""+gl.gl_new_Low+"\">"+gl.gl_new_Low+"</option>"
            js += "    <option value=\""+gl.gl_new_Middle+"\">"+gl.gl_new_Middle+"</option>"            
        js += "  </select>"
        js += "</td>"
        js += "</tr> "        
        return js 

def NewTest_VerifyType(req, verify_type=None): 
        js = ''
        ###Verify Type
        js += "<tr class=\"field\">"
        js += "<th><label for=\"verify\">Verify Type:</label></th>"
        js += "<td>"
        js += "  <select id=\"verify\" name=\"verify\">"
        #js += "    <option py:for=\"verify in verifies\">$verify</option>"
        if verify_type is not None:
            js += "    <option value=\""+verify_type+"\">"+verify_type+"</option>"        
        if req.perm.has_permission('BUILD_ADMIN'):
            js += "    <option value=\""+gl.gl_CR+"\">"+gl.gl_CR+"</option>"
            js += "    <option value=\""+gl.gl_DB+"\">"+gl.gl_DB+"</option>"
            js += "    <option value=\""+gl.gl_MP+"\">"+gl.gl_MP+"</option>"
            js += "    <option value=\""+gl.gl_BASE+"\">"+gl.gl_BASE+"</option>"            
        else:
            js += "    <option value=\""+gl.gl_CR+"\">"+gl.gl_CR+"</option>"
            js += "    <option value=\""+gl.gl_DB+"\">"+gl.gl_DB+"</option>"
            if req.perm.has_permission(gl.gl_MP):
                js += "    <option value=\""+gl.gl_MP+"\">"+gl.gl_MP+"</option>"
            if req.perm.has_permission(gl.gl_BASE):
                js += "    <option value=\""+gl.gl_BASE+"\">"+gl.gl_BASE+"</option>"           
        js += "  </select>"
        js += "</td>"
        js += "</tr> "
        return js         

def NewTest_AutoDel(): 
        js = ''
        ###Version Auto Del:
        js += "<tr class=\"field\">"
        js += "<th><label for=\"versiondeltype\">Version Auto Del:</label></th>"
        js += "<td>"
        js += "  <select id=\"versiondeltype\" name=\"versiondeltype\">"
        #js += "    <option py:for=\"versiondeltype in versiondeltypes\">$versiondeltype</option>"
        js += "    <option value=\""+gl.gl_Yes+"\">"+gl.gl_Yes+"</option>"
        js += "    <option value=\""+gl.gl_No+"\">"+gl.gl_No+"</option>"        
        js += "  </select>"
        js += "</td>"
        js += "</tr>  "
        return js        
        
def NewTest_CaseFilterClass(): 
        js = ''        
        ###Case Filter Class
        js += "<tr class=\"field\">"
        js += " <th><label for=\"casefilterclass\">Case Filter Class:</label></th>"
        js += " <td>"
        js += "  <select id=\"casefilterclass\" name=\"casefilterclass\">"
        #js += "    <option py:for="casefilterclass in casefilterclasses">$casefilterclass</option>"
        js += "    <option value=\""+gl.gl_From_PassList+"\">"+gl.gl_From_PassList+"</option>"
        js += "    <option value=\""+gl.gl_Not_Filter+"\">"+gl.gl_Not_Filter+"</option>"          
        js += "   </select>"
        js += " </td>"
        js += "</tr>      "  

        return js

def NewTest_VersionNum(): 
        js = ''        
        ###VersionNum
        js += "<tr class=\"field\">"
        js += "	<th><label for=\"versionnum\">VersionNum:</label></th>"
        js += "	<td colspan=\"3\"><input id=\"versionnum\" type=\"text\" name=\"versionnum\" size=\"40\" value=\""+gl._gl_versionnum_prefix+"\" /></td>"
        js += "</tr>  "
        return js



def NewTest_Name(req, name=None): 
        if name is not None:
            default = name
        else:
            default = req.session.sid + '_bug'
        js = ''        
        ###Name
        js += "<tr class=\"field\">"
        js += "	<th><label for=\"name\">Name:</label></th>"
        js += "	<td colspan=\"3\"><input id=\"name\" type=\"text\" name=\"name\" size=\"40\" value=\""+default+"\" /></td>"
        js += "</tr>  "
        return js
        
def NewTest_Creator(req, creator=None): 
        if creator is not None:
            default = creator
        else:
            default = req.session.sid
        js = ''        
        ###Creator
        js += "<tr class=\"field\">"
        js += "	<th><label for=\"creator\">Creator:</label></th>"
        js += "	<td colspan=\"3\"><input id=\"creator\" type=\"text\" name=\"creator\" size=\"40\" value=\""+default+"\" /></td>"
        js += "</tr>  "
        return js

def NewTest_CaseTxtFile(caselistfile=None): 
        default = ''
        if caselistfile is not None:
            default = caselistfile              
        js = ''        
        ###CaseList Txt File
        js += "<tr class=\"field\">"
        js += "	<th><label for=\"caselist_txtfile\">CaseList Txt File:</label></th>"
        js += "	<td colspan=\"3\"><input id=\"caselist_txtfile\" type=\"text\" name=\"caselist_txtfile\" size=\"40\" value=\""+default+"\" readonly=\"1\"/></td>"
        js += "</tr>  "
        
        return js



def ModifyTest(req, priority=None, verify_type=None, name=None, creator=None): 
    if 1:
        js = ''
        js += NewTest_Name(req, name=name)
        js += NewTest_Creator(req, creator=creator)
        #js += NewTest_VersionNum() 
        
        js += NewTest_Priority(req, priority=priority)
        js += NewTest_VerifyType(req, verify_type=verify_type)
        #js += NewTest_AutoDel() 
        #js += NewTest_CaseFilterClass()
        

    return js



        

def rpc_GenTestList(src_txt_path):#not used
    dest_xml_path = src_txt_path
    dest_xml_path = dest_xml_path.replace('.txt','.xml')
    dest_xml_path = dest_xml_path.replace('.TXT','.xml')

    utils.trans_case_from_txt_to_xml(src_txt_path, dest_xml_path)

    return dest_xml_path

def rpc_Hello(id): 
    return id




def rpc_slv_pld(env, testdata): 
#RPC的URL :http://172.16.4.44:5555
#172.16.0.37
#RPC的函数:SetTestCaseInfo
#P:\PHY\DSP_TD\DSP_L1IT\Itest_DTS_Report\Main_Task\CR_TEST\MOCOR880XGMODEMW1226PRETEST8800gts01_0001\ 
     #参数：test_case_path      string类型  值为:\\shengzhupc\Tcl\lib\monkey_test\test\TestReport.txt
   #返回值：true->正确获取case   boolean类型   
        creator = testdata['creator']        
        testreportpath = testdata['testreportpath']
        testreportpath = testreportpath.replace('/','\\')        
        versionpath = testdata['versionpath']
        testname = testdata['testname']
        case = testdata['case']
        env.log.error('rpc_slv_pld: testname=%s,case=%s',testname,case)

        mydic={}
        server = ServerProxy("http://172.16.0.37:5555")
        mydic['test_case_path'] = testreportpath        
        mydic['reporter'] = creator
        #testname - case        
        #mydic['submit_app_name'] = testname.replace('_'+case,'')
        mydic['submit_app_name'] = testname
        mydic['version_path'] = versionpath
#PC的函数:SetTestCaseInfo
#    参数：test_case_path      string类型 
#　　参数：reporter          string类型    （指登录iTest的用户名）
#   参数：submit_app_name    string类型    (提交case list的名称，这个名称有一定限制：a.一个case list中的所有case都有相同的submit_app_name名称;b.不同							case list的submit_app_name要不一样)
#   参数：version_path       string类型    （版本路径，就是用户在web页面所提交的那个路径）
#   返回值：true->正确获取case   boolean类型    
        
        try:
            ret = server.SetTestCaseInfo(mydic) 
            env.log.error('rpc_slv_pld: testreportpath=%s', testreportpath)
            #ret = server.SetTestCaseInfo(testreportpath, creator)       

            env.log.debug('rpc_slv_pld: ret= %s ', ret)
        except socket.error,e:
            env.log.error('rpc_slv_pld: socket.error ')


def rpc_slv_testreport(env, testdata): 
        verfy_type = testdata['verfy_type']
        if verfy_type == gl.gl_NULL:
            env.log.error('rpc_slv_psit: verfy_type=%s, return ', verfy_type)    
            return
            
        testreportpath = testdata['testreportpath'] 
        testreportpath = testreportpath.replace('/','\\')
   
        server = ServerProxy(gl.gl_rpcsvr_testreport)
        mydic={}
        #env.log.error('rpc_slv_psit: --server creator=%s testid=%s', creator, testid)    
        try:   
            mydic['iTestID'] = testdata['id'] 
            mydic['Tester'] = testdata['creator']     
            mydic['verfy_type'] = verfy_type
            mydic['excel_path'] = testreportpath
            mydic['testname'] = testdata['testname']
            mydic['versionnum'] = testdata['versionnum'] 
            mydic['versionpath'] = testdata['versionpath']
            #env.log.error('rpc_slv_psit: creator=%s id=%s', testdata['creator'], testdata['id'])
            if testdata['testtype'] == gl.gl_psit:
                mydic['testtype'] = gl.gl_HSIT
            else:
                mydic['testtype'] = testdata['testtype']
            #env.log.error('rpc_slv_psit: testtype=%s ', mydic['testtype'])
            socket.setdefaulttimeout(30)
            try:  
                ret = server.import_excel(mydic)
                env.log.error('rpc_slv_psit: ret= %s, creator=%s id=%s ', ret, testdata['creator'], testdata['id'])                  
            except socket.timeout:
                env.log.error('rpc_slv_psit: socket.timeout')                 
            socket.setdefaulttimeout(None)
        except socket.error,e:
            env.log.error('rpc_slv_psit: socket.error ')  

def rpc_slv_Add_BZ_Comment(env, testdata): 
#mydic['bug_id'] = 100402           //整形
#mydic['comment_content'] = 'test song'  //字符串

        server = ServerProxy(gl.gl_rpcsvr_testreport)
        mydic={}
        try:   
            mydic['bug_id'] = testdata['bug_id']
            mydic['comment_content'] = testdata['comment_content']        
            socket.setdefaulttimeout(15)
            env.log.error('rpc_slv_Add_BZ_Comment: s')  
            try:  
                ret = server.Add_BZ_Comment(mydic)
                env.log.error('rpc_slv_Add_BZ_Comment: ret= %s, bug_id=%s comment_content=%s ', ret, mydic['bug_id'], mydic['comment_content'])                  
            except socket.timeout:
                env.log.error('rpc_slv_Add_BZ_Comment: socket.timeout')                 
            socket.setdefaulttimeout(None)
        except socket.error,e:
            env.log.error('rpc_slv_Add_BZ_Comment: socket.error ')  


def rpc_tmanger(env, tmanager_type):                     
                if tmanager_type == gl.gl_pld_srt \
                        or tmanager_type == gl.gl_psit \
                        or tmanager_type == gl.gl_HSIT:
                    pass
                else:
                    #env.log.error('_rpc_tmanger: 1 tmanager_type = %s',tmanager_type) 
                    return None
                   
                sub_tmanagetype = tmanager_type + '_MANAGER1'
                tmanager = TManager.fetch(env, sub_tmanagetype)               
                if tmanager is None:
                    #env.log.error('_rpc_tmanger: 2 none %s',sub_tmanagetype) 
                    return None
                else:               
                    testserverip = tmanager.ip
                    testserverport = str(gl.gl_tmanager_port)     
                    rpc_server = TManagerSrv(env, ip=testserverip, port=testserverport)
                        
                ret = rpc_server.link(env)
                if ret == False:
                    rpc_server = None  
                    env.log.error('_rpc_tmanger: 3 rpc_server =none %s',tmanager_type) 
                    
                return rpc_server


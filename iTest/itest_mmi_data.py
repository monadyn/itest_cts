# -*- coding: utf-8 -*-
#
from __future__ import division

import os
import thread
import socket
import sys
import time

import test_action
import gl
import slave_utils
import model
import utils
import rpc_server
import web_utils 

from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import datetime
from genshi import HTML   

from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_link, add_stylesheet, add_ctxtnav, \
                            prevnext_nav, add_script, add_stylesheet, add_script, add_warning, add_notice                       
from trac.util import escape, pretty_timedelta, format_datetime, shorten_line, Markup
from trac.util.datefmt import to_timestamp, to_datetime, utc, _units


from iTest.model import Report,TManager  
import test_model
    
def _test_reportpath(env, test): 
#    \\itest-psit14\TestReport\tianming.wu_fastmoving_v3_XML_PSIT_23302
    test_reportpath = test.reserved7
    if test.reserved7 == '':
        test_reportpath = '\\\\itest-psit14\\TestReport\\'+test.build+'_'+str(test.id)

    return test_reportpath
    
def _test_versionorigin(test):  
    return 0
    ##agent与adapter的接口是，0表示版本来自发布包，1表示来自用户，但我觉得在界面上最好是字符串，直观一点。 
    #version_origin = test.reserved5 
    #if version_origin == gl.gl_version_origin_CMO:
    #    version_origin_flag = 0
    #elif version_origin == gl.gl_CUSTOM:
    #    version_origin_flag = 1
                    
def _test_plinfo(tmanager_type, plinfo):        
#MSIT 平台定义目前如下：
#1)  MSITSINGLE : MSIT 单卡手机----------------  201
#2)  MSITDUAL   : MSIT 双卡手机----------------  202

    plinfo_value = 0
    #if plinfo == 'SINGLE_SIM':
    #    plinfo_value = 1
    #elif plinfo == 'DUAL_SIM':
    #    plinfo_value = 2
    #elif plinfo == gl.gl_dual_sim_rf9810 \
    #        or slave_utils._is_SVN_Td(plinfo) == True \
    #        or slave_utils._is_svn_comm(plinfo) == True:
    #    plinfo_value = 3     

    if plinfo == 'MSITSINGLE':
        plinfo_value = 201
    elif plinfo == 'MSITDUAL':
        plinfo_value = 202   
        
    elif plinfo == '8800G':
        plinfo_value = 301   
    elif plinfo == '8810':
        plinfo_value = 302       
    elif plinfo == '6820':
        plinfo_value = 303 
    elif plinfo == 'SC7702':
        plinfo_value = 304 
    elif plinfo == '8501C':
        plinfo_value = 305  
    elif plinfo == '8825':
        plinfo_value = 306          
    elif plinfo == 'LTE9610':
        plinfo_value = 307

    if tmanager_type == gl.gl_pld_monkey \
            or tmanager_type == gl.gl_rdit:
        plinfo_value = int(plinfo)
        
    return plinfo_value  
    
def _test_rrmenv(mmi_extreme_value):
    #页面上增加极限电压测试选择和极限温度测试选择，这两种选择都分别有三个选项，
    #即low、normal和high，分别用0、1和2表示，默认为1，表示normal；
    extreme_value = 1
    if mmi_extreme_value == gl.gl_normal:
        extreme_value = 1
    elif mmi_extreme_value == gl.gl_low or mmi_extreme_value == gl.gl_extreme:
        extreme_value = 0
    elif mmi_extreme_value == gl.gl_high:
        extreme_value = 2        
    return extreme_value    

def _test_pri(test):
    pri_str = test.generator 
    return pri_str       

def _test_pri_int(test):
    pri_str = test.generator
    pri_int = 2
    #优先级传整形值，数字越大，优先级越高。
    if pri_str == gl.gl_new_Low:
        pri_int = 2
    elif pri_str == gl.gl_new_Middle:
        pri_int = 3         
    elif pri_str == gl.gl_new_High:
        pri_int = 4   
    elif pri_str == gl.gl_new_Highest:
        pri_int = 7
        
    return pri_int  


def _test_xlmfile(env, test):
    caselist_file = _test_type(env, test)
    if caselist_file is not None:
        #env.log.error('_test_xlmfile: name =%s', str(test.name))
        #env.log.error('_test_xlmfile: id=%s', str(test.id))
        caselist_file += str(test.id)+'.xml'
    else:
        caselist_file = 'error db'
    return caselist_file

def  _test_xmlfile_path(env, test):    
    testxmlfile = _test_xlmfile(env, test)

    return utils.get_file_dir(env, utils.get_test_xml_dir(env), testxmlfile) 

def  _test_xmlfile_mmipath(env, test, rrm_flag=False):  
    test_type = _test_type(env, test)
    
    if test_type == gl.gl_rrm and rrm_flag == False:
        caselist_path = _test_xlmfilepath(env, test) 
    else:
        testxmlfile = _test_xlmfile(env, test)

        father_dir = utils.get_network_test_xml_dir(env)
        caselist_path = utils.get_file_dir(env, father_dir, testxmlfile) 

    caselist_path = caselist_path.replace('/','\\') 
    return caselist_path 
        

def _test_status(test):
    status = ''
    if test.status == gl.gl_TestCreated:
        status = 'Created'
    elif test.status == gl.gl_TestWaitingVersion:
        status = 'WaitingVersion'
    elif test.status == gl.gl_TestVersionReady:
        status = 'VersionReady'
    elif test.status == gl.gl_TestReady:
        status = 'Ready'
    elif test.status == gl.gl_TestInProgress:
        status = 'InProgress'
    elif test.status == gl.gl_TestStopAndDelete:
        status = 'WaitStopAndDelete'  
    elif test.status == gl.gl_TestWaitingStop:
        status = 'Stopping' 
    elif test.status == gl.gl_TestStopped:
        status = 'Stopped'
    elif test.status == gl.gl_TestFinish:
        status = 'Finish'
    elif test.status == gl.gl_TestError:
        status = 'Error'  

    return status

def _test_total_num_by_xml(env, testxmlfile):
    if not os.path.isfile(testxmlfile):
        #env.log.debug('_test_total_num_by_xml: (%s)',testxmlfile)
        return 0
    else:
        failed = True
    
        testcase_data = slave_utils.read_file(testxmlfile)
        totalnum = testcase_data.count('<case>')

        if totalnum < 0:
            totalnum = 0

        return totalnum

def _test_total_num(env, test):
    testxmlfile = _test_xmlfile_path(env, test)
    total_num = _test_total_num_by_xml(env, testxmlfile)

    return total_num
 

def _test_int_passratio(env, test):
    if test.passed is None or test.failed is None :
        return 0

    if test.passed == '' or test.failed == '' :
        return 0
        
    passed = int(test.passed)
    fail = int(test.failed)
    
    pass_and_fail = passed + fail
    if pass_and_fail == 0:
        int_passratio = 0
    else:
        int_passratio = (passed/pass_and_fail)*100

    return int_passratio    

def _test_int_temppassratio(env, test):
    if test.passed is None or test.failed is None:
        return 0

    if test.passed == '' or test.failed == '' :
        return 0

    if _test_type(env, test) != gl.gl_psit:
        return 100
        
    passed = int(test.passed)
    fail = int(test.ueitreruntimes)
    
    pass_and_fail = passed + fail
    if pass_and_fail == 0:
        int_passratio = 0
    else:
        int_passratio = (passed/pass_and_fail)*100

    return int_passratio  

def _test_temppassratio(env, test):
    #页面上的通过率和临时通过率百分比需要小数多显示两位，你那能改下吗？因为20000+个case跑下来如果只失败1个case的话会四舍五入变成100%，我们希望显示成99.9951%这样。
    int_passratio = _test_int_temppassratio(env, test)
    passratio = "%.4f%%" % (int_passratio,)

    return passratio


def _test_passratio(env, test):
    int_passratio = _test_int_passratio(env, test)
    passratio = "%.4f%%" % (int_passratio,)

    return passratio


def _test_Left(env, test):
    total = _test_total_num(env, test)
        
    passed = int(test.passed)
    fail = int(test.failed)
    
    pass_and_fail = passed + fail
    left = total - pass_and_fail
    
    return left

def _test_LeftRatio(env, test):
    total = _test_total_num(env, test)
    left = _test_Left(env, test)
    if total == 0:
        return 'Error'
    else:   
        int_leftratio = (left/total)*100
        if int_leftratio == 0:
            return 'Finished'
        else:        
            leftratio = "%.4f%%" % (int_leftratio,)
            return leftratio+'('+str(left)+')'
    
def _test_timecost(env, time1, time2):
    time1 = to_datetime(time1)
    time2 = to_datetime(time2)
    if time1 > time2:
        time2, time1 = time1, time2
    
    diff = time2 - time1
    return diff    

def _test_intwaittime(env, test):        
    start_time_int = test.waiting_time    
    if start_time_int == 0:
        timecost = 0
    else:
        current = ''
        current = datetime.utcnow()
        current = current.isoformat()
        current_int = int(utils._format_datetime(current))  
        
        start_test_time = format_datetime(start_time_int)
        timecost = current_int - start_time_int

    return timecost

def _test_inttimecost(env, test):  
    #测试相关时间
    current = ''
    current = datetime.utcnow()
    current = current.isoformat()
    current_int = int(utils._format_datetime(current))  
    current = format_datetime(current_int)  
       
    start_time_int = test.started
    end_time_int = test.stopped  
    
    if start_time_int == 0:
        start_test_time = ''
        end = ''
        timecost = 0
    else:
        start_test_time = format_datetime(start_time_int)
        if end_time_int == 0:  
            end = ''
            timecost = current_int - start_time_int
        else:
            end = format_datetime(end_time_int)
            timecost = end_time_int - start_time_int

    return timecost

def  _test_versiondel_type(env, test):
    #'Yes', 'No'
    # 1      2       
    verfy_type = ''
    if test.reserved4 is not None:
        verfy_type = test.reserved4
        if slave_utils.check_string(verfy_type, '\\') == True:
            verfy_type = ''
        ret = verfy_type.isdigit()
        length = len(verfy_type)
        if ret == True:
            #env.log.error('_test_versiondel_type: verfy_type=%s, ret=%s, %s ', verfy_type, ret, verfy_type[0])
            if length > 1:
                if verfy_type[1] == '1':
                    verfy_type = 'Yes'
                elif verfy_type[1] == '2':
                    verfy_type = 'No'
                else:
                    verfy_type = ''
            else:
                verfy_type = ''
        else:
            verfy_type = ''
        #env.log.error('_test_versiondel_type: verfy_type=%s, ret=%s, %s ', verfy_type, ret, verfy_type[0])             
    
    return verfy_type

def  _test_verfy_type(env, test):
    #['CR', 'DB', 'BASE', 'MP', 'NULL']
    # 1      2      3      4     0    
    verfy_type = ''
    if test.reserved4 is not None:
        verfy_type = test.reserved4
        if slave_utils.check_string(verfy_type, '\\') == True:
            verfy_type = ''
        ret = verfy_type.isdigit()
        if ret == True:
            #env.log.error('_test_verfy_type: verfy_type=%s, ret=%s, %s ', verfy_type, ret, verfy_type[0])  
            if verfy_type[0] == '1':
                verfy_type = 'CR'
            elif verfy_type[0] == '2':
                verfy_type = 'DB'
            elif verfy_type[0] == '3':
                verfy_type = 'BASE'
            elif verfy_type[0] == '4':
                verfy_type = 'MP'
            else:
                verfy_type = ''
            #env.log.error('_test_verfy_type: verfy_type=%s, ret=%s, %s ', verfy_type, ret, verfy_type[0]) 
            
    return verfy_type

def  _test_name(test):     
    return test.name
    
def  _test_type(env, test):  
    if test is not None:
        return test.tmanager
    else:
        return ''

def  _test_xlmfilepath(env, test):     
    return test.reserved6   

def  _test_dspversionpath(test): 
    dspversionpath = ''
    if test.subtmanager is not None:
        dspversionpath = test.subtmanager   
    return dspversionpath    

def  _test_subtype(env, test):    
    if test.total is not None and test.total != '':
        subtype = test.total
    else:
        subtype = gl.gl_NULL
            
    return subtype

def _test_del_caselistfile(env, test):  
    #src: /trac/Projects/iTest/attachments/iTest/song.shan_psit/bcfe_sam_list.xml
    caselist_file = _test_type(env, test)
    caselist_file += "%s.xml" % (test.id,)                
    xml_file = utils.get_file_dir(env, utils.get_test_xml_dir(env), caselist_file)#/home/share/test_xml
    _remove_file(env, xml_file)    

    #if self.xmlfile is not None and self.xmlfile != gl.gl_NULL:
    #        if os.path.exists(self.xmlfile): 
    #            os.unlink(self.xmlfile)     


def _test_one_case(env, test): 
    from iTest.util import xmlio

    case = ''
    
    testtype = _test_type(env, test)    
    if testtype == gl.gl_pld_monkey:
        env.log.error('_test_one_case: testtype = %s', testtype)
        caselistpath = _test_xmlfile_path(env, test)
        env.log.error('_test_one_case: caselistpath = %s', caselistpath)
        try:
            elem = xmlio.parse(slave_utils.read_file(caselistpath))
        except xmlio.ParseError, e:
            env.log.error('_test_one_case: caselistpath=%s',caselistpath)

        
        for child in elem.children():
            #if child.name == 'Cases':
                #caselistnum = len(list(child.children()))
                #env.log.error('_test_one_case: caselistnum = %s', caselistnum)
                #if caselistnum > 10:
                #            add_notice(req, "max num of caselist is 10!") 
                #            return False 
                            
                #for child2 in child.children():
                #    if child2.name == 'case':                      
                #        case = child2.gettext()
                #        case = case.replace('\r\n','')
                #        case = case.replace('\r','')
                #        case = case.replace('\n','')
                #        case = case.replace(' ','')
                #        case = case.replace('\t','')
                #        env.log.error('_test_one_case: case = %s',case )                                    
                #        return case
            if child.name == 'case':      
                case = child.gettext()
                env.log.error('_test_one_case: case = %s',case )                                                                                 
                return case
    return case


def _test_inprogresscases(env, in_str):                     
    if in_str == '' or in_str == 'NULL':
        return (0, [])
        
    infos = []  
    total_number = 0
    module_count = in_str.count('|')
    index = 1
    case = ''
    #env.log.error('_test_inprogresscases: in_str = %s ', in_str)
    #UagentIP1:UagentPort1:RunningCase1|…|UagentIPN:UagentPortN:RunningCaseN
    if module_count == 0:
        one_module = in_str        
        module_count = one_module.count(':')
        total_number = 1
        #env.log.error('_server_agentinfo: module_count = %s ', module_count)
        #if module_count == 3:
        modules = one_module.split(':',module_count) 
        infos.append({
                    'ip': modules[0], 
                    'port': modules[1],
                    'case': modules[2],
                    'id': str(index),
                    'number': str(total_number)
                })  
        index += 1
        case = ''
        
    else:
        modules = in_str.split('|',module_count) 
        #env.log.error('_test_inprogresscases: modules = %s ', modules) 
        
        tmp_ip = ''
        for one_module in modules: 
            #env.log.error('_test_inprogresscases: one_module = %s ', one_module)  
            module_count = one_module.count(':')
            #env.log.error('_test_inprogresscases: module_count = %s ', module_count)
            #if module_count == 3:  
            modules = one_module.split(':',module_count) 
            #if '172.16.0.246' == modules[0]:
                #env.log.error('_test_inprogresscases: modules[2] = %s ', modules[2])
                #env.log.error('_test_inprogresscases: modules[0] = %s ', modules[0])
                #env.log.error('_test_inprogresscases: tmp_ip= %s ', tmp_ip)
                #env.log.error('_test_inprogresscases: case= %s ', case)
            if modules[2] != '':                
                if tmp_ip == '' or tmp_ip == modules[0]:
                    case += modules[2]+';'
                    tmp_ip = modules[0]
                else:  
                    #env.log.error('_test_inprogresscases: append tmp_ip= %s ', tmp_ip)
                    #env.log.error('_test_inprogresscases: append case= %s ', case)                    
                    number = case.count(';')
                    infos.append({
                                'ip': tmp_ip, #modules[0], 
                                'port': modules[1],
                                'case': case, #modules[2],
                                'id': str(index),
                                'number': str(number)
                            }) 
                    index += 1
                    total_number += number
                        
                    if modules[2] != '':                        
                        case = modules[2]+';'
                        tmp_ip = modules[0]                     

    if case != '':
                    number = case.count(';')
                    infos.append({
                                'ip': tmp_ip, #modules[0], 
                                'port': modules[1],
                                'case': case, #modules[2],
                                'id': str(index),
                                'number': str(number)
                            }) 
                    #index += 1
                    total_number += number        
    #env.log.error('_test_inprogresscases: infos = %s ', infos)
    return (total_number, infos)
    

def _test_inprogresscases_data(env, rpc_server, testid, name): 
    if rpc_server is not None:                    
        return _test_inprogresscases(env, rpc_server.R_RunningCaseInfo(env, testid, name)) 
    else:
        return (0, [])



def _test_passednum(env, req, tmanager_type, testid, testname):   
    #rpc_server = _rpc_tmanger(env, req, tmanager_type) 
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    passednum = 0
    if _rpc_server is not None:                    
        passednum = _rpc_server.R_PassedNum(env, testid, testname)    
        
    return passednum    

def _test_agentlength(env, req, rpc_server):     
    startinfos = _start_data(env, req, rpc_server, 'NULL')     

    all_total_agents = 0
    
    if startinfos is not None:     
        for one_info in startinfos:  
            starter = one_info['ip']
            uagentinfos = _agent_data(env, req, rpc_server, starter, 0) 
            total_agents = 0           
            if uagentinfos is not None:                   
                total_agents = len(uagentinfos)

            all_total_agents += total_agents

    return all_total_agents

def _test_starter_dyn(env, testid, rpc_server):     
    in_str = _start_dyn(env, rpc_server, testid) 
    
    if in_str is None or in_str == '' or in_str == 'NULL':
        return None
    #env.log.error('_test_starter_dyn: in_str = %s ', in_str)   
    
    infos = []      
    module_count = in_str.count('|')
    #172.16.15.135:2|172.16.0.67:84    
    if module_count == 0:
        one_module = in_str
        
        module_count = one_module.count(':')
        if module_count == 1:
            modules = one_module.split(':',module_count)  
            infos.append({
                    'startip': modules[0], 
                    'busyagents': modules[1]
                })          
    else:
        modules = in_str.split('|',module_count) 
        #env.log.error('_server_diskversioninfo: modules = %s ', modules)      
        for one_module in modules: 
            #env.log.error('_server_diskversioninfo: one_module = %s ', one_module)  
            module_count = one_module.count(':')
            #env.log.error('_server_diskversioninfo: module_count = %s ', module_count)
            modules = one_module.split(':',module_count)  
            infos.append({
                    'startip': modules[0], 
                    'busyagents': modules[1]
                })  
                
    #env.log.error('_server_diskversioninfo: infos = %s ', infos)
    return infos


def _test_failcases(env, in_str):
    #failed_case1;failed_case2;…;fialed_caseN
    if in_str == '' or in_str == 'NULL':
        return []
        
    infos = []   
    index = 1
    module_count = in_str.count(';')
    #env.log.error('_test_failcases: in_str = %s ', in_str)
    if module_count == 0:
        infos.append({
                    'case': in_str,
                    'id': str(index)
                })  
        index += 1
    else:
        modules = in_str.split(';',module_count) 
        #env.log.error('_test_inprogresscases: modules = %s ', modules)      
        for one_module in modules:
            if one_module != '':
                infos.append({
                    'case': one_module,
                    'id': str(index)
                })  
                index += 1
                
    #env.log.error('_test_failcases: infos = %s ', infos)
    return infos
    
def _test_failcases_data(env, rpc_server, testid, name): 
    if rpc_server is not None:                    
        return _test_failcases(env, rpc_server.R_FailCaseInfo(env, testid, name)) 
    else:
        return []

def _test_status_gif(env, test):           
    return '/iTest/chrome/hw/'+test.status+'.gif'
    
def _test_data(env, req, test):   
    #测试相关时间
    current = ''
    current = datetime.utcnow()
    current = current.isoformat()
    current_int = int(utils._format_datetime(current))  
    current = format_datetime(current_int)  
       
    start_time_int = test.started
    end_time_int = test.stopped  
    waiting_time_int = test.waiting_time
    if waiting_time_int == 0:
        waiting_time = ''
        waiting_duration = ''
    else:
        waiting_time = format_datetime(waiting_time_int)
        if start_time_int == 0:
            waiting_duration = _test_timecost(env, waiting_time_int, current_int)
        else:
            waiting_duration = _test_timecost(env, waiting_time_int, start_time_int)
    
    if start_time_int == 0:
        start_test_time = ''
        end = ''
        timecost = '' 
    else:
        start_test_time = format_datetime(start_time_int)
        if end_time_int == 0:  
            end = ''
            timecost = _test_timecost(env, start_time_int, current_int)
        else:
            end = format_datetime(end_time_int)
            timecost = _test_timecost(env, start_time_int, end_time_int)  

            

    subtype = _test_subtype(env, test)
    test_type = _test_type(env, test)

    versiondel_type = _test_versiondel_type(env, test)    
    
    verify = _test_verfy_type(env, test)
    if test_type == gl.gl_psit:        
        test_type = gl.gl_HSIT
    
    test_date = start_test_time
    test_data = {
        'id': test.id,
        'name': test.name, 
        'creator': test.creator,         
        'priority': test.priority,
        'versionpath': test.versionpath,
        'dspversionpath': _test_dspversionpath(test),
        'versionorigin': test.reserved5,
        'version': test.version_num,
        'buildtype': test_type,
        'subtype': subtype,
        'caselist': _test_xmlfile_mmipath(env, test),
        'status': _test_status(test),
        'result_href': gl.url_log_testid(req, test),
        'testhref': gl.url_log_testid(req, test), 
        'testreport': _test_passratio(env, test),
        'UnFinishedRatio': _test_LeftRatio(env, test),
        'total': _test_total_num(env, test),
        'passed': test.passed,
        'fail': test.failed,
        'date': test_date,
        'waiting_time': waiting_time,
        'waiting_duration': waiting_duration,
        'start': start_test_time,
        'current': current,
        'end': end,
        'timecost': timecost,
        'result_path': _test_reportpath(env, test),
        'verify': verify,
        'versiondel_type': versiondel_type,
        'status_gif': _test_status_gif(env, test)
    }
    #http://itest-center/iTest/testmanage/test/report_ueit?id=2185
      
    return test_data




        
        
def  _server_util_hostname1(env, hostname, index, in_str):
    if index == 0:
        out_str = in_str.replace('a', hostname)
    elif index == 1:
        out_str = in_str.replace('b', hostname)
    elif index == 2:
        out_str = in_str.replace('c', hostname)
    elif index == 3:
        out_str = in_str.replace('d', hostname)
    else:
        out_str = in_str

    return out_str

def  _server_util_hostname2(env, in_str):
    out_str = in_str.replace('\'a\'', '\'\'')
    out_str = out_str.replace('\'b\'', '\'\'')
    out_str = out_str.replace('\'c\'', '\'\'')
    out_str = out_str.replace('\'d\'', '\'\'')

    return out_str

    
def  _server_agentgif(env, status): 	
#enum 
#{
#	E_AGENT_IS_BUSY=0,		//Agent is busy
#	E_AGENT_IS_IDLE,			//Agent is idle
#	E_AGENT_IS_ABNORMAL		//Agent is abnormal#};   
                if status == '0':
                    gif = 'busy.gif'
                elif status == '1':
                    gif = 'idle.gif' 
                else:  
                    gif = 'abnormal.gif'  

                return gif


def  _server_agentdiscription(env, status): 
    if status == '0':
        return 'Agent is busy'
    elif status == '1':
        return 'Agent is idle'
    elif status == '2':
        return 'Agent is abnormal'
    else:
        return status  

def  _server_startgif(env, status): 	
                if status == '0':#'Start is disabled'
                    gif = 'disabled.gif'
                elif status == '1':#'Start is enabled'
                    gif = 'enabled.gif' 
                elif status == '2':#'Start is disabling'
                    gif = 'disabling.gif' 
                elif status == '3':#'Start is rebooting'
                    gif = 'rebooting.gif' 
                elif status == '4':# 'Start is invalid' 
                    gif = 'invalid.gif'                   
                else: #                 
                    gif = 'unkown.gif'  

                return gif



def  _server_startdiscription(env, status): 
#enum 
#{
#	E_START_STATUS_DISABLED=0,	//Start is disabled
#	E_START_STATUS_ENABLED,		//Start is enabled#
#	E_START_STATUS_DISABLING,	//Start is disabling
#	E_START_STATUS_REBOOTING,	//Start is rebooting
#	E_START_STATUS_INVALID		//Start is invalid
#};
    if status == '0':
        return 'Start is disabled'
    elif status == '1':
        return 'Start is enabled'
    elif status == '2':
        return 'Start is disabling'
    elif status == '3':
        return 'Start is rebooting'
    elif status == '4':
        return 'Start is invalid'
    else:
        return status      

def  _server_diskreportinfo(env, in_str):      
    if in_str == '' or in_str == 'NULL':
        return None
        
    infos = []      
    module_count = in_str.count('|')
    #TotalSize|FreeSpace  (单位MB)
    if module_count == 1:     
        modules = in_str.split('|',module_count)  
        infos.append({
                    'totalsize': modules[0], 
                    'freesize': modules[1]
                })          
    else:
        return None
                
    #env.log.error('_server_diskreportinfo: infos = %s ', infos)
    return infos
    
def  _server_diskversioninfo(env, in_str):      
    if in_str == '' or in_str == 'NULL':
        return None
        
    infos = []      
    module_count = in_str.count('|')
    #TaskID1:name1|TaskID2|..|taskIDN
    if module_count == 0:
        one_module = in_str
        
        module_count = one_module.count(':')
        if module_count == 1:
            modules = one_module.split(':',module_count)  
            infos.append({
                    'testid': modules[0], 
                    'testname': modules[1]
                })          
    else:
        modules = in_str.split('|',module_count) 
        #env.log.error('_server_diskversioninfo: modules = %s ', modules)      
        for one_module in modules: 
            #env.log.error('_server_diskversioninfo: one_module = %s ', one_module)  
            module_count = one_module.count(':')
            #env.log.error('_server_diskversioninfo: module_count = %s ', module_count)
            modules = one_module.split(':',module_count)  
            infos.append({
                    'testid': modules[0], 
                    'testname': modules[1]
                })  
                
    #env.log.error('_server_diskversioninfo: infos = %s ', infos)
    return infos

    
def  _server_diskinfo(env, in_str):  
    if in_str == '' or in_str == 'NULL':
        return None
        
    infos = []      
    module_count = in_str.count('|')
    #TotalSize|FreeSpace  (单位MB)
    if module_count == 1:     
        modules = in_str.split('|',module_count)  
        infos.append({
                    'totalsize': modules[0], 
                    'freesize': modules[1]
                })          
    else:
        return None
                
    #env.log.error('_server_diskinfo: infos = %s ', infos)
    return infos


def  _server_agentinfo(env, in_str):  
    if in_str == '' or in_str == 'NULL':
        return None
        
    infos = []      
    module_count = in_str.count('|')
    #305:xx5xx:0:task/case |306:1: |307:2:copyfail|38111:0:1:idle
    if module_count == 0:
        one_module = in_str
        
        module_count = one_module.count(':')
        #env.log.error('_server_agentinfo: module_count = %s ', module_count)
        #if module_count == 3:
        modules = one_module.split(':',module_count) 
        performance = modules[1]
        status = modules[2]
        if status == '0':
            sub_modules = modules[3].split('/',1)            
            task = sub_modules[0]
            case = sub_modules[1]
        else:            
            task = ''
            case = ''
        infos.append({
                    'port': modules[0], 
                    'status': status,
                    'discription': _server_agentdiscription(env, status),
                    'task': task,
                    'case': case,
                    'performance': performance
                })          
    else:
        modules = in_str.split('|',module_count)                 
        
        #env.log.error('_server_agentinfo: modules = %s ', modules)      
        for one_module in modules: 
            #env.log.error('_server_agentinfo: one_module = %s ', one_module)  
            sub_module_count = one_module.count(':')
            #env.log.error('_server_agentinfo: module_count = %s ', module_count) 
            modules = one_module.split(':',sub_module_count) 

            if modules is not None and sub_module_count >= 3:
                performance = modules[1]
                status = modules[2]
                if status == '0':
                    sub_modules = modules[3].split('/',1)                
                    task = sub_modules[0]
                    case = sub_modules[1]                
                else:                
                    task = ''
                    case = ''                
                infos.append({
                    'port': modules[0], 
                    'status': status,
                    'discription': _server_agentdiscription(env, status),
                    'task': task,
                    'case': case,
                    'performance': performance
                    })  
                
    #env.log.error('_server_agentinfo: infos = %s ', infos)
    return infos

     
def  _server_startinfo(env, in_str):  
    if in_str == '' or in_str == 'NULL':
        return None
        
    infos = []      
    #hostname1:IP1:port1:Status1|…|hostnameN:IPN:portN:StatusN
    #taoyangpc:172.16.15.135:37800:4|...   
    module_count = in_str.count('|')
    if module_count == 0:
        one_module = in_str        
        module_count = one_module.count(':')
        if module_count == 3:   
            modules = one_module.split(':',module_count)  
            infos.append({
                    'hostname': modules[0], 
                    'ip': modules[1], 
                    'port': modules[2], 
                    'status': modules[3],
                    'discription': _server_startdiscription(env, modules[3])
                })          
    else:
        modules = in_str.split('|',module_count)                 
        
        #env.log.error('_server_startinfo: modules = %s ', modules)      
        for one_module in modules: 
            #env.log.error('_server_startinfo: one_start = %s ', one_module)  
            module_count = one_module.count(':')
            #env.log.error('_server_startinfo: module_count = %s ', module_count)
            if module_count == 3:   
                modules = one_module.split(':',module_count)  
                infos.append({
                    'hostname': modules[0], 
                    'ip': modules[1], 
                    'port': modules[2], 
                    'status': modules[3],
                    'discription': _server_startdiscription(env, modules[3])
                })  
                
    #env.log.error('_server_startinfo: startinfos = %s ', infos)
    return infos





def _server_mmi_tmanager_status(env, teststatus, tmanagetype): 
    if 1:
#0 ：初始状态； 1 ：运行结束； 2 ：启动失败； 3 ：启动完成； 4 ：正在运行； 5 ：运行失败；  6 ：运行暂停， 后面的数值都作为reserved                             
        if teststatus is None:
            return 'itest err'
        teststatus = teststatus.replace('0;','idle(0);')
        teststatus = teststatus.replace('1;','finish(1);')    
        teststatus = teststatus.replace('2;','start fail(2);') 
        teststatus = teststatus.replace('3;','start suc(3);') 
        teststatus = teststatus.replace('4;','running(4);')
        teststatus = teststatus.replace('5;','running error(5);')
        teststatus = teststatus.replace('6;','stop(6);')
        teststatus = teststatus.replace(';','\n') 
        test_status = teststatus
    else:
        if teststatus == 0:  
            test_status = '0: idle'        
        elif teststatus == 1:  
            test_status = '1: test done'
        elif teststatus == 2:  
            test_status = '2: start fail'        
        elif teststatus == 3:  
            test_status = '3: coping version'  
        elif teststatus == 4:  
            test_status = '4: test running'               
        elif teststatus == 5:  
            test_status = '5: test error'                
        else:
            test_status = str(teststatus)  
                            
    return test_status

def _server_tmanager_nums(env, req, tmanager_type):
    server_nums = len(list(TManager.select(env,type=tmanager_type)))
    env.log.debug('_server_tmanager_nums: server_nums=%s',server_nums)                
    return int(server_nums)

def _server_tmanager_url(env, ip):              
    return 'http://'+ip+':'+gl.gl_tmanager_port      
   
    


def _server_onetype_testserver_data(env, req, Tmanager, test_servers=None):
    if test_servers is None:
        test_servers = []
        
    i = 0

    if 1:
        for tmanager in TManager.select(env, type=Tmanager):              
            if tmanager.reserved3 == 0:
                inprogresstest = ''
            else:   
                test = Report.fetch(env, id=tmanager.reserved3) 
                if test is None:
                    inprogresstest = ''
                else:
                    inprogresstest = test.name           

            if 1:
                inprogresstest = tmanager.inprogress_test.replace(';','\n')
                inprogresstest_href = req.href('/itest/AllTests/home')+'/'+tmanager.type
                teststatus = _server_mmi_tmanager_status(env, tmanager.connect_status, tmanager.type)

            current_int_time = utils._get_current_int_time()
            duration_int = current_int_time - tmanager.port           
            if duration_int <= 60:#留些冗余量             
                pollingduration = pretty_timedelta(tmanager.port, current_int_time)   
            else:
                pollingduration = gl.gl_Disconnect
            
            
            test_servers.append({
                        'id': (i + 1), 
                        'ip': _server_tmanager_url(env, tmanager.ip),
                        'type': tmanager.type,
                        'tmanager_href': req.href('/itest/ServerManager/home')+'/'+tmanager.type, #req.href.build(buildservers=tmanager.type),
                        'subtype': tmanager.name,
                        'status': tmanager.active,
                        'connectstatus': tmanager.connect_status,
                        'inprogresstest': inprogresstest, 
                        'teststatus': teststatus, 
                        'inprogresstest_href': inprogresstest_href,
                        'pollingtime': format_datetime(tmanager.port),
                        'pollingduration': pollingduration,
                        'cardtype': tmanager.reserved2
                }) 
            i = i + 1  

    return test_servers  

def Ajax_Test_INum(env, req, tmanager_type, testid, testname):   
    #rpc_server = _rpc_tmanger(env, req, tmanager_type) 
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    inprogresscase_length = 0
    (inprogresscase_length, infos) = _test_inprogresscases_data(env, _rpc_server, testid, testname)

    y_data = inprogresscase_length        
        
    return y_data
    
def Ajax_Agent(env, req, tmanager_type, starter, agent): 
        _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
        uagentinfos = _agent_data(env, req, _rpc_server, starter, int(agent))#<Fault -1: 'type error'>        
       
        out_string=''  
        out_string+= u'<h1>'+tmanager_type+'&nbsp;&nbsp;&nbsp;&nbsp;<font size=\'1\'></h1>'
        out_string+= u'<p><b>Basic info</b></p>'                
        out_string+= u'<table  id="myBaseInfoTable" name="myBaseInfoTable"   width="700px" class="buglisting" style="word-wrap:break-word;word-break:break-all;"   cellspacing="0" cellpadding="0" border="1">'
        out_string+= u"<tr><td style='background: #f7f7f0;' width='100px'>ServerType</td>" + u"<td>" + tmanager_type + u"</td></tr>"
        out_string+= u"<tr><td style='background: #f7f7f0;'>ServerIP</td>" + u"<td>" + starter + u"</td></tr>"                
        out_string+= u"<tr><td style='background: #f7f7f0;'>AgentPort</td>" + u"<td>" + agent + u"</td></tr>"        
        if uagentinfos is not None:  
            for one_info in uagentinfos:
                test_name = one_info['task']
                out_string+= u"<tr><td style='background: #f7f7f0;'>Status</td>" + u"<td>" + one_info['status'] + u"</td></tr>"
                out_string+= u"<tr><td style='background: #f7f7f0;'>Discription</td>" + u"<td>" + one_info['discription'] + u"</td></tr>"                                                
                test_name_url = '' 

                test = Report.fetch(name=test_name)
                test_name_url = gl.url_log_testid_(test)#'http://itest-center/iTest/build/testresult/'+str(test.id)
                if test_name_url == '':
                    out_string+= u"<tr><td style='background: #f7f7f0;'>Test Name</td>" + u"<td>" + test_name + u"</td></tr>"                
                else:
                    out_string+= u"<tr><td style='background: #f7f7f0;'>Test Name</td>" + u"<td><a href='" + test_name_url +  "' target='_blank'>" + test_name + u"</a></td></tr>"
                out_string+= u"<tr><td style='background: #f7f7f0;'>Test Case</td>" + u"<td>" + one_info['case'] + u"</td></tr>"                
        out_string+= u"</table>"                  
                
        out_string+= u"<br /><br /><br /><br />"
        req.send(out_string.encode('utf-8'))

def Ajax_Starter_BusyAgent(env, req, tmanager_type, starter):   
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    #rpc_server = _rpc_tmanger(env, req, tmanager_type) 
    uagentinfos = _agent_data(env, req, _rpc_server, starter, 0) 

    if 1:              
            total_agents = 0
            running_agents = 0
            idle_agents = 0              
            if uagentinfos is not None:  
                    total_agents = len(uagentinfos)
                    for one_info in uagentinfos:
                        status = one_info['status']
                        if status == '0':
                            running_agents += 1
                        elif status == '1':
                            idle_agents += 1  

            y_data = str(running_agents)               
    return y_data
    
def Ajax_Starter(env, req, tmanager_type, starter):
        _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
        startinfos = _start_data(env, req, _rpc_server, starter)
        uagentinfos = _agent_data(env, req, _rpc_server, starter, 0)  
        diskinfo = _srv_monitor_data(env, req, _rpc_server, starter, 0)
        testversioninfos = _srv_monitor_data(env, req, _rpc_server, starter, 1)

        if diskinfo is not None: 
            for one_info in diskinfo:
                totalsize = one_info['totalsize']+'MB'
                freesize = one_info['freesize']+'MB'
        else:
            totalsize = ' '
            freesize = ' '   
            
        out_string=''  
        test = 'test'

        starter_url = gl.url_starter(tmanager_type, starter)

        tmp = "?tmanager="+tmanager_type
        tmp += "&tmanagerserver=" + tmanager_type
        tmanager_url = 'http://itest-center/iTest/build'+tmp

        out_string+= u'<p><b>Basic info</b></p>' 
        out_string+= u'<table  id="myBaseInfoTable" name="myBaseInfoTable"   width="700px" class="buglisting" style="word-wrap:break-word;word-break:break-all;"   cellspacing="0" cellpadding="0" border="1">'                
        #out_string+= u"<tr><td style='background: #f7f7f0;'>ServerType</td>" + u"<td><a href='" + tmanager_url +  "' target='_blank'>" + tmanager_type + u"</a></td></tr>" 
        out_string+= u"<tr><td style='background: #f7f7f0;'>IP</td>" + u"<td><a href='" + starter_url +  "' target='_blank'>" + starter + u"</a></td></tr>" 
        #env.log.error('Ajax_Starter2: %s,%s _bar_pie_resource', tmanager_type, starter)
        if startinfos is not None:         
            for one_startinfo in startinfos:
                out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>HostName</td>" + u"<td><a href='" + starter_url +  "' target='_blank'>" + one_startinfo['hostname'] + u"</td></tr>" 
                out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>Port</td>" + u"<td>" + one_startinfo['port'] + u"</td></tr>"
                out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>Status</td>" + u"<td>" + one_startinfo['status'] + u"</td></tr>"
                out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>Discription</td>" + u"<td>" + one_startinfo['discription'] + u"</td></tr>"
                break
        out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>DiskTotalSize</td>" + u"<td>" + totalsize + u"</td></tr>"
        out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>DiskFreeSize</td>" + u"<td>" + freesize + u"</td></tr>"  
        out_string+= u"</table>"  
              
        if uagentinfos is not None:     
            lengths = len(uagentinfos)
            server = starter+' Agents'
            out_string+= u"<p><b> "+tmanager_type+" &nbsp;" + server + " &nbsp;&nbsp;(<font color='red'>" + str(lengths) +"</font>)</b>"
            out_string+= u"&nbsp;&nbsp;<a href=\"javascript:display_hidn('myCRListTable_" + server + "');\">Hide/Show</a>&nbsp;&nbsp;"

            out_string+= u'<table  id="myCRListTable_' + server + '" name="myCRListTable_' + server +'"   width="700px" class="buglisting" style="word-wrap:break-word;word-break:break-all;display:none;"   cellspacing="0" cellpadding="0" border="1">'
            
            out_string+= u"<thead><tr><th style='background: #f7f7f0;'>No</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Port</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Status</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Discription</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Status</th>"
            out_string+= u"<th style='background: #f7f7f0;'>TestName</th>"
            out_string+= u"<th style='background: #f7f7f0;'>TestCase</th>"
            out_string+= u"</tr></thead>" 
            
            index = 0  
            for one_info in uagentinfos:
                index = index + 1

                gif = _server_agentgif(env, one_info['status'])
                
                out_string+= u"<tr>"
                out_string+= u'<td>' + str(index) + '</td> '
                out_string+= u'<td>' + one_info['port'] + '</td> '
                out_string+= u'<td>' + one_info['status'] + '</td> '
                out_string+= u'<td>' + one_info['discription'] + '</td> '
                out_string+= u'<td>' + '<img src=\"/iTest/chrome/hw/'+gif+'\" alt=\"iTest\" height=\"30\" width=\"30\" />' + '</td> '
                out_string+= u'<td>' + one_info['task'] + '</td> '
                out_string+= u'<td>' + one_info['case'] + '</td> '
                out_string+= u"</tr>"                     
            out_string+= u"</table><br /><br />" 
        #env.log.error('Ajax_Starter3: %s,%s _bar_pie_resource', tmanager_type, starter)
        if testversioninfos is not None:                  
            #table    
            lengths = len(testversioninfos)
            server = starter+' Versions'
            out_string+= u"<p><b> "+tmanager_type+" &nbsp;" + server + " &nbsp;&nbsp;(<font color='red'>" + str(lengths) +"</font>)</b>"
            out_string+= u"&nbsp;&nbsp;<a href=\"javascript:display_hidn('myCRListTable_" + server + "');\">Hide/Show</a>&nbsp;&nbsp;"
            out_string+= u'<table  id="myCRListTable_' + server + '" name="myCRListTable_' + server +'"   width="700px" class="buglisting" style="word-wrap:break-word;word-break:break-all;display:none;"   cellspacing="0" cellpadding="0" border="1">'
            
            out_string+= u"<thead><tr><th style='background: #f7f7f0;'>No</th>"
            out_string+= u"<th style='background: #f7f7f0;'>TestId</th>"
            out_string+= u"<th style='background: #f7f7f0;'>TestName</th>"
            out_string+= u"</tr></thead>"
            
            index = 0        
            for one_info in testversioninfos:
                    index = index + 1
                    out_string+= u"<tr>"
                    out_string+= u'<td>' + str(index) + '</td> '
                    out_string+= u'<td>' + one_info['testid'] + '</td> '
                    out_string+= u'<td>' + one_info['testname'] + '</td> '
                    
                    out_string+= u"</tr>"                
            out_string+= u"</table><br /><br />"                 
        out_string += u"<br /><br /><br /><br />"    
        req.send(out_string.encode('utf-8'))

def Ajax_tManager(env, req, tmanager_type): 
        _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
        
        startinfos = _start_data(env, req, _rpc_server, 'NULL')
        testreportinfos = _srv_monitor_data(env, req, _rpc_server, '0', 2)
        
        if testreportinfos is not None: 
            for one_info in testreportinfos:
                int_ratio = (int(one_info['freesize'])/int(one_info['totalsize']))*100
                ratio = "%.1f%%" % (int_ratio,)            
                testreport_totalsize = one_info['totalsize']+'MB'
                testreport_freesize = one_info['freesize']+'MB'+'('+ratio+')'
        else:
            testreport_totalsize = ' '
            testreport_freesize = ' '

        out_string=''  

        tmp = "?tmanager="+tmanager_type
        tmp += "&tmanagerserver=" + tmanager_type
        tmanager_url = 'http://itest-center/iTest/build'+tmp
        
        out_string=''  
        out_string+= u'<h1>'+tmanager_type+'&nbsp;&nbsp;&nbsp;&nbsp;<font size=\'1\'></h1>'
        if 1:        
            #table   
            out_string+= u'<p><b>Basic info</b></p>' 
            out_string+= u'<table  id="myBaseInfoTable" name="myBaseInfoTable"   width="700px" class="buglisting" style="word-wrap:break-word;word-break:break-all;"   cellspacing="0" cellpadding="0" border="1">'                      
            #out_string+= u"<tr><td style='background: #f7f7f0;'>ServerType</td>" + u"<td><a href='" + tmanager_url +  "' target='_blank'>" + tmanager_type + u"</a></td></tr>" 
            out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>TestReportTotalSize</td>" + u"<td>" + testreport_totalsize + u"</td></tr>"                
            out_string+= u"<tr><td style='background: #f7f7f0;' width='150px'>TestReportFreeSize</td>" + u"<td>" + testreport_freesize + u"</td></tr>"            
            out_string+= u"</table>"  
            
        if startinfos is not None:                               
            #table    
            lengths = len(startinfos)
            server = ' Starts'
            out_string+= u"<p><b> "+tmanager_type+" &nbsp;" + server + " &nbsp;&nbsp;(<font color='red'>" + str(lengths) +"</font>)</b>"
            out_string+= u"&nbsp;&nbsp;<a href=\"javascript:display_hidn('myCRListTable_" + server + "');\">Hide/Show</a>&nbsp;&nbsp;"

            out_string+= u'<table  id="myCRListTable_' + server + '" name="myCRListTable_' + server +'"   width="700px" class="buglisting" style="word-wrap:break-word;word-break:break-all;display:none;"   cellspacing="0" cellpadding="0" border="1">'
            out_string+= u"<thead><tr><th style='background: #f7f7f0;'>No</th>"
            out_string+= u"<th style='background: #f7f7f0;'>HostName</th>"
            out_string+= u"<th style='background: #f7f7f0;'>IP</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Port</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Status</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Discription</th>"
            out_string+= u"<th style='background: #f7f7f0;'>Status</th>"
            out_string+= u"<th style='background: #f7f7f0;'>DiskTotal</th>"
            out_string+= u"<th style='background: #f7f7f0;'>DiskFree</th>"            
            out_string+= u"</tr></thead>"
            index = 0   
        
            for one_info in startinfos:
                index = index + 1

                diskinfo = _srv_monitor_data(env, req, _rpc_server, one_info['ip'], 0)

                if diskinfo is not None: 
                    for one_diskinfo in diskinfo:
                        int_ratio = (int(one_diskinfo['freesize'])/int(one_diskinfo['totalsize']))*100

                        ratio = "%.1f%%" % (int_ratio,)
                        totalsize = one_diskinfo['totalsize']+'MB'
                        freesize = one_diskinfo['freesize']+'MB'+'('+ratio+')'
                else:
                    totalsize = ' '
                    freesize = ' ' 
            
                gif = _server_startgif(env, one_info['status'])
                out_string+= u"<tr>"
                out_string+= u'<td>' + str(index) + '</td> '
                out_string+= u'<td>' + one_info['hostname'] + '</td> '
                out_string+= u'<td>' + one_info['ip'] + '</td> '
                out_string+= u'<td>' + one_info['port'] + '</td> '
                out_string+= u'<td>' + one_info['status'] + '</td> '
                out_string+= u'<td>' + one_info['discription'] + '</td> '
                out_string+= u'<td>' + '<img src=\"/iTest/chrome/hw/'+gif+'\" alt=\"iTest\" height=\"30\" width=\"30\" />' + '</td> '
                out_string+= u'<td>' + totalsize + '</td> '
                out_string+= u'<td>' + freesize + '</td> '
                out_string+= u"</tr>"                   
            out_string+= u"</table><br /><br />" 

        
        out_string = out_string + u"<br /><br /><br /><br />"                
        req.send(out_string.encode('utf-8'))


        
def iTest_tManagerTree(env, req, tmanager_type): 
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    startinfos = _start_data(env, req, _rpc_server, 'NULL')
   
    data = {}
            
    js = "d = new dTree('d');"
    if startinfos is not None:    
        index = 0
        father_id = -1
        js += '\r\nd.add('
        js += '\''+str(index)+'\''
        js += ',\''+str(father_id)+'\''
        js += ',\''+tmanager_type+'\',\"javascript:tManagerTree_tManager(0'        
        js += ',\''+tmanager_type+'\''
        js += ',\''+'null'+'\''
        js += ',\''+'null'+'\''
        js += ');\");'

        father_id = index
        for one_startinfo in startinfos:            
            uagentinfos = _agent_data(env, req, _rpc_server, one_startinfo['ip'], 0) 
            index = index + 1
            js += '\r\nd.add('
            js += '\''+str(index)+'\''
            js += ',\''+str(father_id)+'\''
            js += ',\''+one_startinfo['ip']+'\',\"javascript:tManagerTree_Starter(0'
            js += ',\''+tmanager_type+'\''
            js += ',\''+one_startinfo['ip']+'\''
            js += ',\''+'null'+'\''
            js += ');\");'     

            sec_father_id = index
            if uagentinfos is not None:
                for one_info in uagentinfos:                    
                    index = index + 1
                    js += '\r\nd.add('
                    js += '\''+str(index)+'\''
                    js += ',\''+str(sec_father_id)+'\''
                    js += ',\''+one_info['port']+'\',\"javascript:tManagerTree_Agent(0'
                    js += ',\''+tmanager_type+'\''
                    js += ',\''+one_startinfo['ip']+'\''
                    js += ',\''+one_info['port']+'\''
                    js += ');\");'  
                            
    js += "\r\n" + "document.write(d);"
    data.update({'dtree_js':HTML(js)})
    #_bar_pie_resource(env, req)
   
    return data

def iTest_Starter(env, req, tmanager_type, starter):  
    data = {}

    #rpc_server = _rpc_tmanger(env, req, tmanager_type)
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    
    diskinfo = _srv_monitor_data(env, req, _rpc_server, starter, 0)
    startinfos = _start_data(env, req, _rpc_server, starter)
    uagentinfos = _agent_data(env, req, _rpc_server, starter, 0)  
    testversioninfos = _srv_monitor_data(env, req, _rpc_server, starter, 1)
    agentnum = _start_getini(env, req, _rpc_server, starter, 'Agent', 'Count')
    
    if agentnum is None:  
        agentnum = '0'
        
    status = ''
    discription = ''
    hostname = ''
    port = ''
    if startinfos is not None:         
        for one_startinfo in startinfos:
            status = one_startinfo['status']
            discription = one_startinfo['discription']
            hostname = one_startinfo['hostname']
            port = one_startinfo['port']
            break   
            
    free = '0'
    used = '0'
    total = '0'
    pre_id = '0'
    next_id = '0'       
    
    if diskinfo is not None: 
        for one_info in diskinfo:
            used_size = int(one_info['totalsize']) - int(one_info['freesize'])
            free = one_info['freesize']
            used = str(used_size)
            total = one_info['totalsize']    
            break

    if testversioninfos is not None:
        lengths = len(testversioninfos)
        index = 0        
        for one_info in testversioninfos:
            if index == 0:
                pre_id = one_info['testid']
            if index == lengths-1:
                next_id = one_info['testid']
            index = index + 1            
            
    data = {
            'free': free,
            'used': used,
            'total': total,
            'tmanager_type': tmanager_type,
            'starter': starter,
            'status': status,
            'discription': discription,
            'hostname': hostname,
            'port': port,
            'pre_id': pre_id,
            'next_id': next_id,
            'agentnum': agentnum
            }
              
                    
    js = ''
    status_gif = ''
    discription = discription + '('+status+')'
    if status == '0':
        js += "<input type=\"submit\" name=\"enablestart\" value=\"Enable\" />"
        js += "<input type=\"submit\" name=\"rebootstart\" value=\"Reboot\" />"
    elif status == '1':
        js += "<input type=\"submit\" name=\"disablestart\" value=\"Disable\" />" 
        js += "<input type=\"submit\" name=\"rebootstart\" value=\"Reboot\" />"
    elif status == '2':
        js += "<input type=\"submit\" name=\"enablestart\" value=\"Enable\" />"
    elif status == '3':
        js += "<input type=\"submit\" name=\"disablestart\" value=\"Disable\" />"
    else:  
        js += "<input type=\"submit\" name=\"enablestart\" value=\"Enable\" />"
        js += "<input type=\"submit\" name=\"disablestart\" value=\"Disable\" />"
        js += "<input type=\"submit\" name=\"rebootstart\" value=\"Reboot\" />"

    gif = _server_startgif(env, status) 
    status_gif += "<p>   Status:  "+discription+" <img src=\"/iTest/chrome/hw/"+gif+"\" alt=\"iTest\" height=\"30\" width=\"30\" /></p>"
    data.update({'dym_button':HTML(js)})
    data.update({'status_gif':HTML(status_gif)})  

    js = ''
    if uagentinfos is not None:                  
        lengths = len(uagentinfos)
        index = 0
        if lengths == 1:
            js += "[['"+one_info['port']+"', "+one_info['performance']+"]]" 
        else:           
            
            js += "["
            for one_info in uagentinfos:
                if index == lengths - 1:
                    js += "['"+one_info['port']+"', "+one_info['performance']+"]" 
                else:
                    js += "['"+one_info['port']+"', "+one_info['performance']+"]," 
                index += 1
            js += "]"
            
    data.update({'agents_performance_data': HTML(js)})    
    #_bar_pie_resource(env, req)
        
    return data
        
def iTest_Server_Manager(env, req, data=None):  
    test_servers = []
    serversubtypes = [] 
    if data is None:
        data = {}
        
    data['servertypes'] = gl.gl_servertypes 
    tmanager_nums = len(gl.gl_servertypes)
    i = 0
    while (tmanager_nums != 0):
        serversubtypes.append( data['servertypes'][i] + '_MANAGER1' ) 
        test_servers = _server_onetype_testserver_data(env, req, \
                    data['servertypes'][i],  test_servers = test_servers)        
        i = i + 1
        tmanager_nums = tmanager_nums - 1 

    data['serversubtypes'] = serversubtypes 
    data['test_servers'] = test_servers

    js = web_utils.iTest_ServerManager_table_new(req)
    data.update({'table_NewTestManager':HTML(js)})  

    #js = web_utils.iTest_ServerManager_table_auto(env, req)
    #data.update({'table_ServerMonitor':HTML(js)})  

    #js = web_utils.iTest_table_RPCServer(env, req)
    #data.update({'table_RPCServer':HTML(js)}) 
    
    #_bar_pie_resource(env, req)      
    return data

def iTest_Server_Monitor(env, req, data=None):  
    if data is None:
        data = {}

    tmanager_type = gl.gl_psit
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    startinfos = _start_data(env, req, _rpc_server, 'NULL')     

    #一行5个
    from genshi import HTML  
    js = ''
    all_total_agents = 0
    all_running_agents = 0
    all_idle_agents = 0     
    
    col_num = 5 
    starts = []
    y_max = 0
    
    if startinfos is not None:   
        js += "<tr> "
        js += "<td>"
        js += "<table width=\"100%\" border=\"0\" cellspacing=\"2\" cellpadding=\"2\" align=\"center\">"
        js += "<tr> "

        lengths = len(startinfos)  
              
        index = 0     
        for one_info in startinfos:            
            starter = one_info['ip']
            hostname = one_info['hostname']  
            
            starter_data_url = gl.url_starter_busyagent(tmanager_type, starter)
            starter_url = gl.url_starter(tmanager_type, starter)
            
            uagentinfos = _agent_data(env, req, _rpc_server, starter, 0) 
            statics_data = _start_statics_data(env, req, _rpc_server, starter)
            total_agents = 0
            running_agents = 0
            idle_agents = 0              
            if uagentinfos is not None:  
                if uagentinfos is not None:     
                    total_agents = len(uagentinfos)

                    for one_info in uagentinfos:
                        status = one_info['status']
                        if status == '0':
                            running_agents += 1
                        elif status == '1':
                            idle_agents += 1  

            all_total_agents += total_agents
            all_running_agents += running_agents
            all_idle_agents += idle_agents 

            if total_agents > y_max:
                y_max = total_agents
            
            one_start = {
                'hostname': hostname,
                'starter_data_url': starter_data_url,
                'statics_data': statics_data,
                'x_data': index+1,
                'y_data': running_agents
                }            
            starts.append(one_start) 
            
            index = index + 1               
            if index == 1 \
                    or index == 3 \
                    or index == 5 \
                    or index == 7 \
                    or index == 9 \
                    or index == 11 \
                    or index == 13 \
                    or index == 15 \
                    or index == 17 \
                    or index == 19 \
                    or index == 21:
                js += "<td width=\"500\" valign=\"top\">"
                js += "<table width=\"98%\" border=\"0\" cellspacing=\"1\" cellpadding=\"1\">"	             

            js += "<tr> "
            js += "   <td align='center' style='background: #f7f7f0;' class=\"topbar\"> <span class=\"headerwhite\">"
            js += "        <a href='" + starter_url +  "' target='_blank'>" + hostname+"("+str(running_agents)+"/"+str(total_agents)+")"+ u"</a>"
            js += "            </span></td>"
            js += "</tr>"
            js += " <tr>     "
            js += "          <tr> "  
            js += "             <td align='center' class=\"table\">"              

            js += "<div id=\""+hostname+"\"></div>"              
            js += " 			</td>"  
            js += "          </tr>"  
            js += "" 
            
            if index == 2 \
                    or index == 4 \
                    or index == 6 \
                    or index == 8 \
                    or index == 10 \
                    or index == 12 \
                    or index == 14 \
                    or index == 16 \
                    or index == 18 \
                    or index == 20 \
                    or index == 30:            
                js += "</table>"  
                js += "</td> "  

        js += "</tr>"  
        js += "</table>"  
        js += "</td>"  
        js += "</tr>"             

        
    data.update({'start_performance':HTML(js)})

    data['all_total_agents'] = all_total_agents
    data['all_running_agents'] = all_running_agents
    data['all_idle_agents'] = all_idle_agents    
    data['starts'] = starts
    data['y_max'] = y_max
    
 

    #_bar_pie_resource(env, req)  
    
    return data 



def _srv_monitor_data(env, req, rpc_server, ip, minitor_type):  
    if rpc_server is not None:
        if minitor_type == 0:
            return _server_diskinfo(env, rpc_server.R_SrvMonitorInfo(env, ip, minitor_type)) 
        elif minitor_type == 1:
            return _server_diskversioninfo(env, rpc_server.R_SrvMonitorInfo(env, ip, minitor_type)) 
        elif minitor_type == 2:
            return _server_diskreportinfo(env, rpc_server.R_SrvMonitorInfo(env, ip, minitor_type))  
        else:
            return None
    else:
        return None


def _agent_data(env, req, rpc_server, ip, port):  
    if rpc_server is not None:
        return _server_agentinfo(env, rpc_server.R_UAgentInfo(env, ip, port=port)) 
    else:
        return None
    
def _start_data(env, req, rpc_server, ip):   
    if rpc_server is not None:
        return _server_startinfo(env, rpc_server.R_ServerInfo(env, ip))  
    else:
        return None        

def _start_dyn(env, rpc_server, testid):   
    if rpc_server is not None:
        return rpc_server.R_GetTaskInfoFromStart(env, testid)  
    else:
        return None   

def _start_statics_data(env, req, rpc_server, ip):   
    if rpc_server is not None:
        return rpc_server.R_GetBuzyAgentNum(env, ip)  
    else:
        return None 

def _start_ctrl(env, req, tmanager_type, starter, ctrl_type): 
    #rpc_server = _rpc_tmanger(env, req, tmanager_type)
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    if _rpc_server is not None:        
        _rpc_server.R_CtrlServer(env, starter, ctrl_type)
        return
    else:
        return None

def _start_cfg(env, req, tmanager_type, starter): 
    #rpc_server = _rpc_tmanger(env, req, tmanager_type)
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    if _rpc_server is not None:
        agentnum = req.args.get('agentnum') 
        if agentnum is not None:
            section = 'Agent'
            key = 'Count'
            string = agentnum
            _rpc_server.R_SetCgfParameter(env, starter, section, key, string, 1)
            
        return
    else:
        return None     


def _start_getini(env, req, rpc_server, starter, section, key): 
    if rpc_server is not None: 
        string = rpc_server.R_GetCgfParameter(env, starter, section, key, 1)            
        return string
    else:
        return None         
        


        
def _start_delversion(env, req, tmanager_type, starter):  
    #rpc_server = _rpc_tmanger(env, req, tmanager_type)   
    _rpc_server = rpc_server.rpc_tmanger(env, tmanager_type)
    if _rpc_server is not None:
        pre_id = req.args.get('pre_id') 
        next_id = req.args.get('next_id')
        testversioninfos = _srv_monitor_data(env, req, _rpc_server, starter, 1)

        if testversioninfos is None:
            return
        if int(next_id) < int(pre_id):
            return
            
        #lengths = len(testversioninfos)                 
        for one_info in testversioninfos:
            testid = one_info['testid']
            int_testid = int(testid)
            testname = one_info['testname'] 
            if int_testid == int(pre_id):
                _rpc_server.R_DelVersion(env, starter, testid, testname)
            elif int_testid > int(pre_id):
                if int_testid > int(next_id):
                    return
                else:
                    _rpc_server.R_DelVersion(env, starter, testid, testname)

        return
    else:
        return None



        






    


def ajax_inprogress_testcase(env, req, test_id, is_init=False):       
    test = Report.fetch(env, id=test_id) 

    out_string=''
    if 1:
            testreport=' '
            TempPassRatio=' '
            total=' '
            passed=' '
            fail=' '
            status=' ' 
            
    if test is not None:
        testreport=_test_passratio(env, test)
        TempPassRatio=_test_temppassratio(env, test)
        total=_test_total_num(env, test)
        passed=test.passed
        fail=test.failed   
        status=_test_status(test)
            
        if test.status == gl.gl_TestInProgress \
                or is_init == True:
            out_string+= u'<table  width="400px" class="buglisting" style="word-wrap:break-word;word-break:break-all;"   cellspacing="0" cellpadding="0" border="1">'                      
   
            out_string+= u'<tr class="field">'
            out_string+= u'  <th><label for="total">Total Cases Num:</label></th>'
            out_string+= u'  <td colspan="3"><dd class="test">'+str(total)+'</dd></td>             '
            out_string+= u'</tr>	'
            out_string+= u'<tr class="field">'
            out_string+= u'  <th><label for="passed">Passed:</label></th>'
            out_string+= u'  <td colspan="3"><dd class="test">'+passed+'</dd></td>          '   
            out_string+= u'</tr>'
            out_string+= u'<tr class="field">'
            out_string+= u'  <th><label for="fail">Failed:</label></th>'
            out_string+= u'  <td colspan="3"><dd class="test">'+fail+'</dd></td>  '
            out_string+= u'</tr> '
            out_string+= u'<tr class="field">'
            out_string+= u'  <th><label for="TempPassRatio">Temp Pass Ratio:</label></th>'
            out_string+= u'  <td colspan="3"><dd class="test">'+TempPassRatio+'</dd></td>  '
            out_string+= u'</tr>           '
            out_string+= u'<tr class="field">'
            out_string+= u'  <th><label for="version">Pass Ratio:</label></th>'
            out_string+= u'  <td colspan="3"><dd class="test">'+testreport+'</dd></td>  '
            out_string+= u'</tr>  '   
            out_string+= u'<tr class="field">'
            out_string+= u'<th><label for="status">Status:</label></th>'
            out_string+= u'<td colspan="3"><dd class="test">'+status+'</dd></td>  '
            out_string+= u'</tr>  '  
            
            out_string+= u"</table>"  
            

    return out_string  


class MMIData(object):
    def __init__(self, env, db_conn, showtype=gl.gl_all, min_id=None, max_id=None, \
                            step_build=None, start_day='', end_day='', build_id='', test_id=''):
        self.env = env
        self.log = env.log
        self.showtype = showtype
        
        self.min_id = min_id
        self.max_id = max_id
        self.step_build = step_build
        
        self.totalnum = 0
        self.totalnum_finish  = 0
        self.totalnum_stopped = 0
        self.totalnum_smoke = 0
        self.totalnum_passlist = 0

        self.start_day = start_day
        self.end_day = ''

        self.build_id = build_id
        self.test_id = test_id

        self.test_data = {}
        self.build_data = {}
        self.buildandtest_data = {}

        self.loginer = ''

        self.key = ''
        self.rule = ''

        self.testaction = test_action.TestAction(self.env,db_conn)


    def get_testdata(self, req):    
        tests = []  
        db_type = gl.gl_mysql
        loginer = req.session.sid 
        ratio_thread = float(req.args.get('ratio_thread') or str(gl.gl_mmi_int_ratio))
         
        name = req.args.get('name') 
        creator = req.args.get('creator') 
        
        last_tests = self.testaction.T_Select(env=self.env)
        lasttest_id = 100
        for test in last_tests:
            lasttest_id = test.id
            break
        pre_id = str(lasttest_id - gl.gl_mmi_int_step)
        next_id = str(lasttest_id)
             
        if self.max_id is not None and self.step_build is not None:
            self.min_id = str(int(self.max_id) - int(self.step_build))                        
        else:              
            self.min_id = pre_id   
            self.max_id = next_id
            self.step_build = str(gl.gl_mmi_int_step)
        
        if name is not None and name != '': #only one
            test = self.testaction.T_Fetch(test_name=name)
            if test is not None:
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)
        elif creator is not None and creator != '': 
            self.totalnum_finish = len(list(self.testaction.T_Select( \
                                        status=gl.gl_TestFinish, \
                                        creator=creator, \
                                        env=self.env)))
            self.totalnum_stopped = len(list(self.testaction.T_Select( \
                                        status=gl.gl_TestStopped, \
                                        creator=creator, \
                                        env=self.env)))
                                        
            self.totalnum = self.totalnum_finish + self.totalnum_stopped    

            self.totalnum_passlist = \
                            len(list(self.testaction.T_Select( \
                            creator=creator, \
                            sub_testtype=gl.gl_PASSLIST, \
                            env=self.env))) \
                            + \
                            len(list(self.testaction.T_Select( \
                            creator=creator, \
                            sub_testtype=gl.gl_FULL_TEST, \
                            env=self.env))) \
                            + \
                            len(list(self.testaction.T_Select( \
                            creator=creator, \
                            sub_testtype=gl.gl_PASSLIST_TEST, \
                            env=self.env)))
                            
            self.totalnum_smoke = self.totalnum - self.totalnum_passlist   
            for test in list(self.testaction.T_Select(creator=creator, \
                                        env=self.env)):  
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)                  
        elif self.showtype == gl.gl_user:
            creator = loginer
            self.totalnum_finish = len(list(self.testaction.T_Select( \
                                        status=gl.gl_TestFinish, \
                                        creator=creator, \
                                        env=self.env)))
            self.totalnum_stopped = len(list(self.testaction.T_Select( \
                                        status=gl.gl_TestStopped, \
                                        creator=creator, \
                                        env=self.env)))
            self.totalnum = self.totalnum_finish + self.totalnum_stopped    

            creator = loginer
            self.totalnum_passlist = \
                            len(list(self.testaction.T_Select( \
                            creator=creator, \
                            sub_testtype=gl.gl_PASSLIST, \
                            env=self.env))) \
                            + \
                            len(list(self.testaction.T_Select( \
                            creator=creator, \
                            sub_testtype=gl.gl_FULL_TEST, \
                            env=self.env))) \
                            + \
                            len(list(self.testaction.T_Select( \
                            creator=creator, \
                            sub_testtype=gl.gl_PASSLIST_TEST, \
                            env=self.env)))                     
                            
            self.totalnum_smoke = self.totalnum - self.totalnum_passlist   
            
            for test in list(self.testaction.T_Select(creator=creator, \
                                        env=self.env)):      
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)                
        elif self.showtype == gl.gl_href_watingtest:
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        status=gl.gl_TestVersionReady, \
                                        env=self.env)):      
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data) 
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        status=gl.gl_TestReady, \
                                        env=self.env)):      
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)   
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        status=gl.gl_TestWaitingStop, \
                                        env=self.env)):      
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)    
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        status=gl.gl_TestStopAndDelete, \
                                        env=self.env)):      
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)                  
        elif self.showtype == gl.gl_href_inprogresstest:                
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        status=gl.gl_TestInProgress, \
                                        env=self.env)):      
                one_test_data = _test_data(self.env, req, test)
                tests.append(one_test_data)  
        elif self.showtype == gl.gl_all:

            
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        min_id=self.min_id, max_id=self.max_id, \
                                        env=self.env)): 
                if test.category != gl.gl_TestCreated:      
                    one_test_data = _test_data(self.env, req, test)
                    tests.append(one_test_data)             
        else:     
            
            for test in list(self.testaction.T_Select(db_type=db_type, \
                                        min_id=self.min_id, max_id=self.max_id, \
                                        tmanager=self.showtype, \
                                        env=self.env)):  
                if test.category != gl.gl_TestCreated: 
                    one_test_data = _test_data(self.env, req, test)
                    tests.append(one_test_data)   
                    

        if req.args.get('tests') is None or req.args.get('tests') == '':
            self.test_data['testtype'] = self.showtype
        else:
            self.test_data['testtype'] = req.args.get('tests')
        
        self.test_data['pre_id'] = self.min_id
        self.test_data['next_id'] = self.max_id
        self.test_data['step_build'] = self.step_build  
        self.test_data['ratio_thread'] = ratio_thread
        
        self.test_data['tests'] = tests[:int(self.step_build)]        
        
        self.test_data['tab'] = ' \t '
        self.test_data['all_test_href'] = req.href.build(tests=gl.gl_all) 
        self.test_data['all_psit_test_href'] = req.href.build(tests=gl.gl_psit) 
        self.test_data['all_rdit_test_href'] = req.href.build(tests=gl.gl_rdit) 
        self.test_data['all_msit_test_href'] = req.href.build(tests=gl.gl_msit) 
        self.test_data['all_l1it_test_href'] = req.href.build(tests=gl.gl_l1it)
        self.test_data['all_pld_monkey_href'] = req.href.build(tests=gl.gl_pld_monkey)
        self.test_data['all_loginer_href'] = req.href.build(tests=gl.gl_user)   

        self.test_data['all_waiting_href'] = req.href.build(tests=gl.gl_href_watingtest) 
        self.test_data['all_inprogress_href'] = req.href.build(tests=gl.gl_href_inprogresstest) 
        self.test_data['loginer'] = loginer
        
        self.test_data['totalnum'] = str(self.totalnum)
        self.test_data['totalnum_finish'] = str(self.totalnum_finish)
        self.test_data['totalnum_stopped'] = str(self.totalnum_stopped)
        self.test_data['totalnum_passlist'] = str(self.totalnum_passlist)
        self.test_data['totalnum_smoke'] = str(self.totalnum_smoke)

        self.test_data['creator'] = creator

        #test_table
        from genshi import HTML    
                    
        js = ''
        js += "<table class=\"listing\" id=\"test\">"
        js += "    <thead>"
        js += "      <tr>"
        js += "      <th class=\"sel\">&nbsp;</th>  "
        js += "      <th>ID</th>"
        js += "      <th>Creator</th>"
        js += "      <th>Type</th> "
        js += "      <th>SubType</th>    "     
        js += "      <th>Started</th>   " 
        js += "      <th>Stopped</th>"
        js += "      <th>Duration</th>"
        js += "      <th>Status</th>  "
        js += "      <th>PassRatio</th>"
        js += "      <th>Priority</th>"
        js += "      <th>Verify</th>"
        js += "      <th>AutoDel</th>"
        js += "      <th>Version</th>  "  
        js += "      </tr>"
        js += "    </thead>"

        js += "    <tbody>"
        js += "    <tr py:for=\"test in tests\">"
        js += "      <td class=\"sel\">"
        js += "        <input type=\"checkbox\" name=\"sel\" value=\"$test.id\" />"
        js += "      </td>"
        js += "      <td class=\"creator\"><code>$test.id</code></td>"
        js += "      <td class=\"name\"><a href=\"$test.testhref\">$test.name</a></td>"
        js += "      <td class=\"buildtype\"><code>$test.buildtype</code></td>"
        js += "      <td class=\"subtype\"><code>$test.subtype</code></td>"
        js += "      <td class=\"start\"><code>$test.start</code></td> "
        js += "      <td class=\"end\"><code>$test.end</code></td>  "
        js += "      <td class=\"timecost\"><code>$test.timecost</code></td>"
        js += "      <td class=\"teststatus\"><a href=\"$test.result_href\">$test.status</a></td>   " 
        js += "      <td class=\"testreport\"><a href=\"$test.result_href\">$test.testreport</a></td>"
        js += "      <td class=\"priority\"><code>$test.priority</code></td> "
        js += "      <td class=\"verify\"><code>$test.verify</code></td>"
        js += "      <td class=\"versiondel_type\"><code>$test.versiondel_type</code></td>"
        js += "      <td class=\"version\"><code>$test.version</code></td>"
        js += "    </tr>"
        js += "  </tbody>      "
        js += "</table>"
    
        self.test_data.update({'test_table':HTML(js)})

        
        js  = web_utils.iTest_nav(req)
        self.test_data.update({'nav':HTML(js)}) 
        return self.test_data        

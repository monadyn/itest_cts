# -*- coding: utf-8 -*-
#
import os

import gl

def iTest_report(env, test):
        import itest_mmi_data
        from trac.util import format_datetime
        
        testname = test.name        
        test_type = itest_mmi_data._test_type(env, test)          
        test_url=gl.url_log_testid_(test) #'http://itest-center/iTest/build/testresult/' + str(test.id)
        versionpath=test.versionpath
        version_num = test.version_num
        passratio=itest_mmi_data._test_passratio(env, test)
        total=itest_mmi_data._test_total_num(env, test)
        passed=test.passed
        failed=test.failed
        start_t=format_datetime(test.started)
        end=format_datetime(test.stopped)
        timecost=itest_mmi_data._test_timecost(env, test.started, test.stopped)
        result_path=itest_mmi_data._test_reportpath(env, test)
        caselist=itest_mmi_data._test_xmlfile_mmipath(env, test)        

        #if 1:
        #    comment_content = "---------------------------------------\n"
        #    comment_content += "---------------------------------------\n"

        js = ''
        js += "<br /><br /><br /><br />" 
        js += web_li('Test Name', testname)           
        js += "<br />"
        js += web_li('Version Num', version_num)           
        js += "<br />"        
        js += web_li('Type', test_type)           
        js += "<br />"          
        js += web_li('Total Cases Num', str(total))           
        js += "<br />"  
        js += web_li('Passed Cases Num', str(passed))           
        js += "<br />"  
        js += web_li('Failed Cases Num', str(failed))           
        js += "<br />"  
        js += web_li('Pass Ratio', passratio)           
        js += "<br />"  
        #js += web_li('Start Time', test.start)           
        #js += "<br />"  
        #js += web_li('End Time', test.end)           
        js += "<br />"  
        #js += web_li('Time Cost', test.timecost)           
        #js += "<br />"  
        #js += web_li('Status', test.status)           
        js += "<br />"  
        js += web_li('Result Path', result_path)           
        js += "<br />"          
        js += web_li('CaseList Path', caselist)           
        js += "<br />"  
        js += web_li('Version Path', versionpath )           
        js += "<br />"    
        js += web_li('Test URL', test_url )           
        js += "<br /><br />" 
        
        js += "<br />" 
        return js    

def iTest_nav(req):
    js = ''
    if 1:
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_user)+"\">"+req.session.sid+"</a><code> | </code>"       
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_all)+"\">All</a><code> | </code>" 
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_psit)+"\">HSIT</a><code> | </code>" 
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_rdit)+"\">RDIT</a><code> | </code>" 
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_msit)+"\">MSIT</a><code> | </code>"   
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_l1it)+"\">L1IT</a><code> | </code>" 
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_pld_monkey)+"\">Pld_Monkey</a><code> | </code>"    
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_href_watingtest)+"\">Waiting</a><code> | </code>"       
        js += "<a href=\""+req.href('/itest/AllTests/home/'+gl.gl_href_inprogresstest)+"\">InProgress</a>"     
   
         
    js += "<br /><br />"         
    return js


def iTest_table_RPCServer(env, req): 
    import utils
    import slave_utils

    polling_time = ''
    init_env_dir = utils.get_file_dir(env, utils.get_itest_log_dir(env), gl.gl_init_env)     
    
    rpcserver_file_name = utils.get_file_dir(env, init_env_dir, gl.gl_rpc_svr_polling_time_file_name)
    if not os.path.isfile(rpcserver_file_name):
        polling_time = gl.gl_guardprocess_flag
    else:
        polling_time = slave_utils.read_file(rpcserver_file_name)       	

    js = ''    
    js += web_b("Polling Time".decode('GBK'))
    js += web_input('rpcserver', 'text', polling_time, size='50', readonly=True)
       
    js += web_button(gl.gl_rpc_server_monitor, 'iTestRPCServer')  
    js += "<br />"  
    return js 

def iTest_ServerManager_table_auto(env, req): 
    import utils
    import slave_utils
        
    polling_time = ''
    init_env_dir = utils.get_file_dir(env, utils.get_itest_log_dir(env), gl.gl_init_env) 
    
    polling_time_file_name = utils.get_file_dir(env, init_env_dir, gl.gl_polling_time_file_name)
    if not os.path.isfile(polling_time_file_name):
        polling_time = gl.gl_guardprocess_flag
    else:
        polling_time = slave_utils.read_file(polling_time_file_name)     

    js = ''    
    js += web_b("Polling Time".decode('GBK'))
    js += web_input(gl.gl_server_monitor_polling_time, 'text', polling_time, size='50', readonly=True)
       
    js += web_button(gl.gl_server_monitor, 'iTestHeartBeat')  
    js += "<br />"  
    return js 

def iTest_ServerManager_table_new(req): 
    js = ''    
    js += web_b("IP".decode('GBK'))
    js += web_input(gl.gl_testserverip, 'text', '') 
          
    js += web_b("Port".decode('GBK'))
    js += web_input(gl.gl_testserverport, 'text', gl.gl_tmanager_port) 
    
    js += web_b("Type".decode('GBK'))
    js += web_single_sel(gl.gl_servertypes, gl.gl_testservertype)           
    #js += "<br />"  

    js += web_button(gl.gl_b_connect, 'Connect')        
    js += web_button(gl.gl_b_disconnect, 'DisConnect')  
    js += "<br />"  
    return js 
    

def iTest_New_table_name(req, uploadcaselist_txt, caselistfile=None, has_build=False): 
    if req.perm.has_permission('TEST_HIGHEST'):
        test_priority = ['NULL', 'Low', 'Middle', 'High', 'Highest']
    elif req.perm.has_permission('TEST_FORMAL_VERSION'):
        test_priority = ['NULL', 'Low', 'Middle', 'High']
    elif req.perm.has_permission('TEST_DAYLI_VERSION'):
        test_priority = ['NULL', 'Low', 'Middle']
    else:
        test_priority = ['NULL']    

    if req.perm.has_permission('BUILD_ADMIN') \
            or req.perm.has_permission(gl.gl_BASE) \
            or req.perm.has_permission(gl.gl_MP):
        test_verify = ['CR', 'DB', 'BASE', 'MP']
    #elif req.perm.has_permission(gl.gl_BASE):
        #test_verify = ['CR', 'DB', 'BASE']         
    #elif req.perm.has_permission(gl.gl_MP):
        #test_verify = ['CR', 'DB', 'MP']
    else:
        test_verify = ['CR', 'DB'] 

    value = req.args.get(gl.gl_name)
    if value is None:
        value = req.session.sid + '_bug'        
    #js = web_td_text("*测试单名".decode('GBK'), gl.gl_name, req.session.sid + '_bug')     
    js = "<td><font color=\"#FF0000\">"+"*".decode('GBK')+"</font>"+"测试单名".decode('GBK')+"</td>"
    js += "<td>"
    js += web_input(gl.gl_name, 'text', value)
    js += "</td>" 
        
    js += web_td_single_sel("优先级".decode('GBK'), gl.gl_priority, test_priority)
    js += web_td_single_sel("测试结果确认级别".decode('GBK'), gl.gl_verify, test_verify)
    return js
    
def iTest_New_table_versionnum(req, uploadcaselist_txt, caselistfile=None, has_build=False):  
    #js = web_td_text("*版本号".decode('GBK'), gl.gl_versionnum, gl._gl_versionnum_prefix)

    js = "<td><font color=\"#FF0000\">"+"*".decode('GBK')+"</font>"+"测试类型".decode('GBK')+"</td>"	
    js += "<td>"
    js += web_single_sel(gl.gl_testtypes, gl.gl_test_type_mode, 'chgmode') 
    js += "</td>" 

    value = req.args.get(gl.gl_versionnum)
    if value is None:
        value = gl._gl_versionnum_prefix     
    js += "<td><font color=\"#FF0000\">"+"*".decode('GBK')+"</font>"+"版本号".decode('GBK')+"</td>"
    js += "<td>"
    js += web_input(gl.gl_versionnum, 'text', value)
    js += "</td>" 
        
    js += web_td_single_sel("测完版本是否自动删除".decode('GBK'), gl.gl_versiondeltype, gl.gl_versiondeltypes)   
    return js


def iTest_New_table_testversion(req, uploadcaselist_txt, caselistfile=None, has_build=False): 
    value = req.args.get(gl.gl_versionpath)
    if value is None:
        value = '\\\\'
        
    js = ''  
    #js += web_td_text("*版本路径".decode('GBK'), gl.gl_versionpath, '\\\\')
    #js += "<td bgcolor=\"red\">"+"*".decode('GBK')+"</td>"
    js += "<td><font color=\"#FF0000\">"+"*".decode('GBK')+"</font>"+"版本路径".decode('GBK')+"</td>"
    
    js += "<td>"
    #js += web_input(gl.gl_versionpath, 'text', '\\\\')
    js += "<td colspan=\"3\"><input value=\""+value+"\" name=\""+gl.gl_versionpath+"\" size=\"100\" /> </td>"
    js += "</td>"  
    
    #js += "<span><font size=\"8\" color=\"#FF0000\">"+"对于HSIT,注意:(1)由于访问用户数限制,请务必将测试版本放在服务器上.".decode('GBK')+"</font>"+"</span>"
    #js += "<span><font color=\"#FF0000\">"+"对于HSIT,注意:(1)由于访问用户数限制,请务必将测试版本放在服务器上.(2)一定要是TDPS_UEIT或psit目录的上一级目录，目录下不要包含其他文件，否则影响测试时间.".decode('GBK')+"</font>"+"</span>"

    
    return js   
    

def iTest_New_table_testlist(req, uploadcaselist_txt, caselistfile=None, has_build=False):   

    if uploadcaselist_txt is not None:
        uploadcaselist_txt = uploadcaselist_txt
    else:
        uploadcaselist_txt = gl.gl_bt_uploadcaselist_txt  
        
    #js += web_input(gl.gl_caselist_file, 'file', '')
    #js += web_input(uploadcaselist_txt, 'submit', 'Upload')
    
    js = ''  
    #js += web_span("如果自定义测试用例，首先Upload，然后再填写其他选项.".decode('GBK')) 
    js += "<span><font face=\"Arial\" color=\"red\">"+"如果自定义测试用例，首先Upload，然后再填写其他选项.".decode('GBK')+"</font>"+"</span>"
    js += "<td>"+"本地测试用例(Txt文件)".decode('GBK')+"</td>"	
    js += "<td>"
    js += "	<input id=\""+gl.gl_caselist_file+"\" type=\""+'file'+"\" name=\""+gl.gl_caselist_file+"\" value=\"\" />"
    js += web_input(uploadcaselist_txt, 'submit', 'Upload')
    js += "</td>" 
       
    #js += web_input(gl.gl_caselist_txtfile, 'text', caselistfile, readonly=True) 
    js += web_td_text("服务器测试用例(Txt文件)".decode('GBK'), gl.gl_srv_testlist, caselistfile) 
    return js 

def iTest_New_table_HSIT(env, req, srv_testlist): 
    #env.log.error('iTest_New_table_HSIT: srv_testlist=%s', srv_testlist)
    if srv_testlist is None or srv_testlist == '':
        sels = gl.gl_psit_types
    else:
        sels = gl.gl_subtypes_CUSTOM
    js = ''    
    js += "<td><font color=\"#FF0000\">"+"*".decode('GBK')+"</font>"+"测试用例".decode('GBK')+"</td>"	
    js += "<td>"
    js += web_single_sel(sels, 'PSITtype', 'chgmode') 
    js += "</td>" 

    js += web_td_single_sel("平台信息".decode('GBK'), 'psitPlatform', gl.gl_psitPlatforms) 
    js += web_td_single_sel("测试列表是否过滤".decode('GBK'), gl.gl_casefilterclass, gl.gl_casefilter_class)    
    return js 
    
def iTest_New_table_L1IT(env, req, srv_testlist): 
    if srv_testlist is None or srv_testlist == '':
        sels = gl.gl_l1it_types
    else:
        sels = gl.gl_subtypes_CUSTOM
    js = ''    
    js += "<td><font color=\"#FF0000\">"+"*".decode('GBK')+"</font>"+"测试用例".decode('GBK')+"</td>"	
    js += "<td>"
    js += web_single_sel(sels, 'L1ITtype', 'chgmode') 
    js += "</td>" 

    js += web_td_single_sel("平台信息".decode('GBK'), 'l1itPlatform', gl.gl_l1itPlatforms)  
    js += web_td_text("DSP版本路径".decode('GBK'), gl.gl_dspversionpath, '\\\\') 
    return js 

    
def iTest_New_table_PLD_SRT(env, req, srv_testlist):   
    if srv_testlist is None or srv_testlist == '':
        sels = gl.gl_pld_srt_types
    else:
        sels = gl.gl_subtypes_CUSTOM		
    js = ''    
    js += "<td>"+"*测试用例".decode('GBK')+"</td>"	
    js += "<td>"
    js += web_single_sel(sels, 'PLD_SRTtype', 'chgmode') 
    js += "</td>" 
       
    return js  



def iTest_New_table_RDIT(env, req, srv_testlist):   
    if srv_testlist is None or srv_testlist == '':
        sels = gl.gl_rdit_types
    else:
        sels = gl.gl_subtypes_CUSTOM	
    js = ''    
    js += "<td>"+"*测试用例".decode('GBK')+"</td>"	
    js += "<td>"
    js += web_single_sel(sels, 'RDITtype', 'chgmode') 
    js += "</td>" 
    
    js += web_td_single_sel("平台信息".decode('GBK'), 'rditPlatform', gl.gl_rditPlatforms_2)   
    return js  

def iTest_New_table_MSIT(env, req, srv_testlist): 
    if srv_testlist is None or srv_testlist == '':
        sels = gl.gl_msit_types
    else:
        sels = gl.gl_subtypes_CUSTOM	
    js = ''    
    js += "<td>"+"*测试用例".decode('GBK')+"</td>"	
    js += "<td>"
    js += web_single_sel(sels, 'MSITtype', 'chgmode') 
    js += "</td>" 
    
    js += web_td_single_sel("平台信息".decode('GBK'), 'msitPlatform', gl.gl_msitPlatforms)   
    return js 
    
def iTest_New(req): 
    
    js = ''

    js += "<fieldset id=\"iTest_New\">   "
    js += "<legend>iTest NewTest</legend>   "  

    js += "</fieldset>" 
    return js        


def web_input( name, input_type, default, size='20', readonly=False):
    if default is None:
        default = ''
    js = ''    
    if readonly == False:
        js += "	<input id=\""+name+"\" type=\""+input_type+"\" name=\""+name+"\" size=\""+size+"\" value=\""+default+"\" />"
    else:
        js += "	<input id=\""+name+"\" type=\""+input_type+"\" name=\""+name+"\" size=\""+size+"\" value=\""+default+"\" readonly=\"1\"/></td>"
    return js    

def web_td_text(name, id, value):				
        js = ''    
        js += "<td>"+name+"</td>"
        js += "<td>"
        js += web_input(id, 'text', value)
        js += "</td>" 
        return js 

def web_td_single_sel(name, id, value):				
        js = ''    
        js += "<td>"+name+"</td>"
        js += "<td>"
        js += web_single_sel(value, id) 
        js += "</td>" 
        return js         
    
def web_p(data):
        js = ''    
        js += "<p>"+data+"</p>"
        return js 
        
def web_span(data):
        js = ''    
        js += "<span>"+data+"</span>"
        return js 

def web_b(name):
        js = ''    
        js += "	<b style=\"background: #eee\">"+name+":</b>"
        return js 
        

        
def web_radio(name, value, checked):
        js = ''  

        #<input type="radio" id="Data_Type" name="Data_Type" value="Percent" checked="checked" />Percent    
        #<input type="radio" id="Data_Type" name="Data_Type" value="Hours" />Hours
        #js += "	<b style=\"background: #eee\">"+id+":</b>"
        if checked == True:
            js += "	<input id=\""+name+"\" type=\"radio\" name=\""+name+"\" value=\""+value+"\" checked=\"checked\" />"+value
        else:
            js += "	<input id=\""+name+"\" type=\"radio\" name=\""+name+"\" value=\""+value+"\" />"+value
                        
        return js 


def web_button(name, value):
        js = ''
        js += "<input type=\"submit\" name=\""+name+"\" value=\""+value+"\" />"   

        return js   

def web_mutls_sel(mutls_sel, name):
        js = ''
  
        js += "<span class=\"field_label  required\"    id=\""+name+"\">"
        js += "<b style=\"background: #eee\">"+name+":</b>"
        js += "</span>"
        js += "      <select name=\""+name+"\" id=\""+name+"\"  multiple=\"multiple\" size=\"7\">"
        nums = 0
        while len(mutls_sel) > nums:
            x = mutls_sel[nums].decode('utf-8')            
            nums += 1  
            js += "                        <option value=\""+x+"\">"+x+"</option>"            
        js += "      </select>"
        return js    

def web_single_sel(sels, name, onclick=''):
        js = ''
        if onclick == '':
            js += "<select name=\""+name+"\" id=\""+name+"\"  >"
        else:
            js += "<select name=\""+name+"\" id=\""+name+"\"  onclick=\""+onclick+"();\">"
        nums = 0
        while len(sels) > nums:
            x = sels[nums].decode('utf-8')            
            nums += 1  
            js += "                        <option value=\""+x+"\">"+x+"</option>"            
        js += "      </select>"
        return js  

def web_li(id, infos):  
        if infos is None or infos == '':
            infos = '---' 
        js = ''    
        #js += "<li>"        
        js += "<strong>"+id+":</strong>"+infos+"      "
        #js += "</li>"
        return js      

def tree_add_node(id, father_id, name, name_id, is_null=False): 
        js = ''
        js += '\r\nd.add('
        js += '\''+id+'\''
        js += ',\''+father_id+'\''
        if is_null == True:
            js += ',\''+name+'\',\"javascript:test();\");'   
        else:
            js += ',\''+name+'\',\"javascript:Bz_QueryTree(\''+name_id+'\',\''+name+'\');\");'      
        return js
  

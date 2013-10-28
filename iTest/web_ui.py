# -*- coding: utf-8 -*-
#


from __future__ import division

import socket
import thread
import time
import os
import posixpath
import re
import shutil
import unicodedata
import pkg_resources

import os.path
import sys,MySQLdb
import traceback

from genshi import HTML   
from StringIO import StringIO
from datetime import datetime
from genshi.builder import tag

from trac.util.translation import _, ngettext, tag_
from trac.attachment import Attachment
from trac.attachment import AttachmentModule
from trac.core import *
from trac.mimeview.api import Context
from trac.resource import Resource
from trac.timeline import ITimelineEventProvider
from trac.util import escape, pretty_timedelta, format_datetime, shorten_line, \
                      Markup
from trac.util.datefmt import to_timestamp, to_datetime, utc, _units
from trac.util.html import html
from trac.web import IRequestHandler, IRequestFilter, HTTPNotFound
from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_link, add_stylesheet, add_ctxtnav, \
                            prevnext_nav, add_script, add_warning, add_notice
from trac.wiki import wiki_to_html, wiki_to_oneliner


import gl
import rpc_server
import schedule
import utils
import itest_mmi_data
import test_action
import slave_utils
import web_utils
import tmanager_model

from iTest.api import ILogFormatter, IReportChartGenerator, IReportSummarizer                   
from iTest.model import Report  
from iTest.itest_mmi_data import MMIData

db_conn=None        

class IModuleProvider(Interface):
    def get_module(req):
        """
        `(category, page)`.
        """

    def render_module(req, category, page, path_info):
        """
        """   

class AdminModule(Component):
    """Web administration interface provider and panel manager."""

    implements(INavigationContributor, IRequestHandler, ITemplateProvider)
    module_providers = ExtensionPoint(IModuleProvider)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return 'itest'

    def get_navigation_items(self, req):
        #if req.session.sid == 'song.shan':        
        #    yield 'mainnav', 'itest', tag.a(_('iTest'), href=req.href('itest/NewTest/home'), accesskey=15, title=_('itest'))
        #yield 'mainnav', 'idata', tag.a(_('iData'), href=req.href('/idata/report/home'), title=_('report'))
            yield 'mainnav', 'itest', tag.a(_('iTestCTS'), href=req.href('itest/CTS/home'), accesskey=15, title=_('itest'))
    # IRequestHandler methods

    def match_request(self, req):        
        match = re.match('/itest(?:/([^/]+)(?:/([^/]+)(?:/(.+))?)?)?$', req.path_info)
        if match:
            req.args['cat_id'] = match.group(1)
            req.args['panel_id'] = match.group(2)
            req.args['path_info'] = match.group(3)
            return True                      

    def process_request(self, req):    
        Current_User = req.authname.lower()
        if req.authname.lower()=='anonymous':
            add_warning(req, 'Please login first!')  
            add_warning(req, "用户名: 内网账号（小写，例如song.shan），密码：内网开机密码".decode('GBK'))  
            data = {}
            return 'iTest_Blank.html', data, None 
            
        global db_conn
        #import ilog_model        
        db_conn=MySQLdb.connect(host='10.0.0.175',port=3306,user='ilogadmin', passwd='SPD@ilogservice99', db='ilog',charset='utf8')#ilog_model.sqldb()
        table_tmanager = tmanager_model.TManager(None, db_conn) 

        self.log.debug('AdminModule: .%s, dog in', Current_User)
        #iTest_WatchDog(self.env, req, table_tmanager)
        rpc_server.iTestHeartBeat(self.env,req, table_tmanager, db_conn) 
        self.log.error('AdminModule: .dog out')
        
        # Include javascript libraries
        add_script(req, 'hw/js/jquery.js')
        add_script(req, 'hw/js/jquery-ui.min.js')
        
        #tablequery     ok  
        add_script(req, 'hw/js/jquery.dataTables.min.js')          
        add_stylesheet(req, 'hw/css/jquery-ui.css')
        add_stylesheet(req, 'hw/css/demo_table.css')            

        #dtree        
        add_script(req, 'hw/iTest_DTree.js') 
        add_stylesheet(req, 'hw/iTest_DTree.css')
        #
        add_script(req, 'hw/iTest_Ajax.js')  
        add_script(req, 'hw/iTest_ShowHide.js') 

        #highcharts      
        add_script(req, 'hw/iTest_HighCharts.js')
        #add_script(req, 'hw/exporting.js')


        
        providers = self._get_providers(req)
        cat_id = req.args.get('cat_id') 
        panel_id = req.args.get('panel_id')
        path_info = req.args.get('path_info')
        provider = providers.get((cat_id, panel_id), None)
        
        if not provider:
            raise HTTPNotFound(_('Unknown administration module'))

        template, data = provider.render_module(req, cat_id, panel_id, path_info)
        #self.log.error('AdminModule: .%s,%s,%s.', cat_id, panel_id, Current_User)
        data.update({
                'active_cat': cat_id, 
                'active_panel': panel_id,
                #'SiteRoot':SiteRoot, 
                'CurrentUser':Current_User, 
            })
        return template, data, None

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return [('hw', pkg_resources.resource_filename(__name__, 'htdocs'))]
        #return [('bitten', pkg_resources.resource_filename(__name__, 'htdocs'))]
        
    def get_templates_dirs(self):
        return [pkg_resources.resource_filename(__name__, 'templates')]        


    def _get_providers(self, req):
        providers = {}

        for provider in self.module_providers:
            p = list(provider.get_module(req) or [])
            for panel in p:
                providers[(panel[0], panel[1])] = provider
                
        return providers        

class CTS_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('CTS'), href=req.href('/itest/CTS/home'))
        yield ('CTS','home')

    def render_module(self, req, cat, page, path_info):
        templates = 'iTest_CTS.html'
        
        templates = 'iTest_Help.html'
        data = {}
        return templates, data
        


class iBuild_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('iBuild'), href='http://imanage.sprd.com/build#')
        
    def render_module(self, req, cat, page, path_info):
        """
        """         


class NewTest_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('NewTest'), href=req.href('/itest/NewTest/home'))
        yield ('NewTest','home')

    def render_module(self, req, cat, page, path_info):
        global db_conn
        testaction = test_action.TestAction(self.env, db_conn, req=req) 
        templates = 'iTest_NewTest.html'
        if gl.gl_b_submittest in req.args \
                        or gl.gl_b_saveandstarttest in req.args: 
        
            testtype = req.args.get(gl.gl_test_type_mode)             
            if testtype == gl.gl_HSIT:
                testtype = gl.gl_psit    
            name = req.args.get(gl.gl_name, '') 
            name = utils.name_filter_dirty_symbol(self.env, str(name))
            if testtype == gl.gl_rdit:      
                rditPlatform = req.args.get('rditPlatform') 
                pre_name = name
                if rditPlatform == 'T2W1' \
                        or rditPlatform == 'T2(9810)W1':#两个单子
                    #1-- 'W1'
                    name = pre_name + '_' + 'W1'
                    name += '_' + utils._get_current_time_str()
                    ret = testaction.B_Save2start(req, testtype=testtype, name=name, rditPlatform=rditPlatform)
                    #2-- 'W1'
                    if rditPlatform == 'T2W1':
                        name = pre_name + '_' + 'T2'
                        name += '_' + utils._get_current_time_str()
                        ret = testaction.B_Save2start(req, testtype=testtype, name=name, rditPlatform=rditPlatform) 
                    elif rditPlatform == 'T2(9810)W1': 
                        name = pre_name + '_' + 'T2_9810'
                        name += '_' + utils._get_current_time_str()
                        ret = testaction.B_Save2start(req, testtype=testtype, name=name, rditPlatform=rditPlatform)           
                else:#单个
                    if rditPlatform == gl.gl_T2_9810:
                        name += '_T2_9810'
                    elif rditPlatform == gl.gl_T2_8810:
                        name += '_T2_8810'   
                    elif rditPlatform == gl.gl_T2_8501c:
                        name += '_T2_8501c'                      
                    else:
                        name += '_' + rditPlatform
                    name += '_' + utils._get_current_time_str()
                    ret = testaction.B_Save2start(req, testtype=testtype, name=name, rditPlatform=rditPlatform)
            else:
                time_string = utils.curtime_string()                
                time_string = re.sub('[\D]', '', time_string)
                self.log.debug('NewTest: time_string,%s', time_string) 
                name += '_' + time_string
                ret = testaction.B_Save2start(req, testtype=testtype, name=name)            
                     
            if ret == True: 
                templates = 'iTest_Server_Manager.html'
                data = itest_mmi_data.iTest_Server_Manager(self.env, req)  
            else:
                add_notice(req, "Error, Plz Check.") 
                data = test_action.iTest_NewTest(self.env,req)
        elif gl.gl_b_uploadcaselist_txt in req.args:
            txt_file = test_action.iTest_UploadCaselist(self.env, req)                     
            data = test_action.iTest_NewTest(self.env, req, txt_file_name=txt_file)
        else:  
            data = test_action.iTest_NewTest(self.env,req)        
        return templates, data

class SearchTest_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('SearchTest'), href=req.href('/itest/SearchTest/home'))
        yield ('SearchTest','home')

    def render_module(self, req, cat, page, path_info):
        global db_conn
        if path_info == gl.gl_psit \
                or path_info == gl.gl_HSIT \
                or path_info == gl.gl_pld_srt:
            tManager = path_info     
            testid = req.args.get('testid')       
            testname = req.args.get('testname')  
            if testid is not None and testname is not None: 
                y_data = itest_mmi_data.Ajax_Test_INum(self.env, req, tManager, testid, testname)
                req.send(str(y_data))
                return
        elif path_info == gl.gl_TestID:
            templates = 'iTest_LogTest.html' 
            testaction = test_action.TestAction(self.env, db_conn,req=req) 
            testid = req.args.get('testid') 
            sel_test = req.args.get('sel_test')                  
            if sel_test is not None:
                testid = sel_test
                test = testaction.T_Fetch(id = testid)
                if 'starttest' in req.args: 
                    testaction.B_Start(req=req,test=test)
                elif 'stoptest' in req.args: 
                    testaction.B_Stop(test=test)
                elif 'submitmodifytest' in req.args:
                    testaction.B_Modify2save(req=req,test=test)
                elif 'resettest' in req.args:
                    testaction.B_Reset(test=test)   
                elif 'testSendReport' in req.args:  
                    testaction.B_SendReport(test)
                elif 'testAddReport2Bugz' in req.args:  
                    testaction.B_AddReport2Bugz(test)  
                elif 'modifytest' in req.args:
                    templates = 'iTest_ModifyTest.html'
                    data = testaction.B_Modify(req=req,test=test)
                    return templates, data
            data = testaction.T_MMI(req, testid=testid)
        else:
            templates = 'iTest_SearchTest.html'
            testdata = MMIData(self.env, db_conn, showtype=gl.gl_user)            
            data = testdata.get_testdata(req)  
        return templates, data

class AllTests_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('AllTests'), href=req.href('/itest/AllTests/home'))
        yield ('AllTests','home')

    def render_module(self, req, cat, page, path_info):
        templates = 'iTest_AllTests.html'
        global db_conn 
        
        testaction = test_action.TestAction(self.env, db_conn, req=req) 
        testdata = None
        if gl.gl_b_remove_tests in req.args:             
            sel = req.args.get('sel')    
            if not sel:
                raise TracError('No tests selected')                    
            ids = isinstance(sel, list) and sel or [sel]
            for index in ids:
                testaction.B_Remove(req=req, id=index)
            path_info = gl.gl_user  

        elif 'update_tests' in req.args \
                    or 'pre_tests' in req.args \
                    or 'next_tests' in req.args: 
                pre_id = req.args.get('pre_id') or '0'
                next_id = req.args.get('next_id') or str(gl.gl_mmi_int_step)
                step_build = req.args.get('step_build') or str(gl.gl_mmi_int_step)

                if 'next_tests' in req.args:
                    pre_id = str(int(pre_id) + int(step_build))
                    next_id = str(int(next_id) + int(step_build))                       
                elif 'pre_tests' in req.args:
                    pre_id = str(int(pre_id) - int(step_build))
                    next_id = str(int(next_id) - int(step_build))

                testtype = req.args.get('testtype')                
                testdata = MMIData(self.env, min_id=pre_id, \
                            max_id=next_id, step_build=step_build, showtype=testtype)  
                
        if path_info is None:  
            path_info = gl.gl_href_inprogresstest   
            
        if testdata is None:
            testdata = MMIData(self.env, db_conn, showtype=path_info)            
        data = testdata.get_testdata(req)  
                     
        return templates, data
        
class ServerManager_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('ServerManager'), href=req.href('/itest/ServerManager/home'))
        yield ('ServerManager','home')

    def render_module(self, req, cat, page, path_info):  
        global db_conn
        
        table_tmanager = tmanager_model.TManager(None, db_conn) 
        
        if gl.gl_server_monitor in req.args:
            self.B_iTestHeartBeat(req)  
        elif gl.gl_rpc_server_monitor in req.args:
            self.B_iTestRPCServer(req)  
        elif gl.gl_b_disconnect in req.args \
                    or gl.gl_b_connect in req.args: 
                tmanager = req.args.get('servertype', '')  
                testserverip = req.args.get('testserverip', '')
                server = rpc_server.ServerButton(self.env,table_tmanager,\
                            ip=testserverip, tmanager=tmanager)
        
                if gl.gl_b_disconnect in req.args:
                    server.disconnect(req)
                elif gl.gl_b_connect in req.args:
                    server.connect_svr(req, db_conn, flag='new')  
                    
        #self.log.error('ServerManager_Module: %s,%s,%s', cat, page, path_info)     
        if path_info == gl.gl_psit \
                or path_info == gl.gl_pld_srt:
            tManager = path_info
            ajax = req.args.get('ajax') 
            StarterIP = req.args.get('StarterIP') 
            if ajax is not None: 
                if ajax == 'tManager':
                    itest_mmi_data.Ajax_tManager(self.env, req, tManager)  
                elif ajax == 'Starter':
                    #self.log.error('ServerManager_Module: %s,%s,%s,StarterIP=%s', cat, page, path_info, StarterIP)  
                    itest_mmi_data.Ajax_Starter(self.env, req, tManager, StarterIP)
                elif ajax == 'Agent': 
                    AgentPort = req.args.get('AgentPort') 
                    #self.log.error('ServerManager_Module: %s,%s,%s,StarterIP=%s', cat, page, path_info, StarterIP)  
                    itest_mmi_data.Ajax_Agent(self.env, req, tManager, StarterIP, AgentPort) 
                return
            
            if StarterIP is not None:  
                if 'removetestversion' in req.args:
                    itest_mmi_data._start_delversion(self.env,req, tManager, StarterIP)
                elif 'enablestart' in req.args:
                    itest_mmi_data._start_ctrl(self.env,req, tManager, StarterIP, gl.gl_enablestart)   
                elif 'disablestart' in req.args:
                    itest_mmi_data._start_ctrl(self.env,req, tManager, StarterIP, gl.gl_disablestart)
                elif 'rebootstart' in req.args:
                    itest_mmi_data._start_ctrl(self.env,req, tManager, StarterIP, gl.gl_rebootstart)
                elif 'configstart' in req.args:
                    itest_mmi_data._start_cfg(self.env,req, tManager, StarterIP)  
            
                templates = 'iTest_Starter.html'    
                data = itest_mmi_data.iTest_Starter(self.env,req, tManager, StarterIP)
            else:
                templates = 'iTest_tManagerTree.html'
                data = itest_mmi_data.iTest_tManagerTree(self.env,req, tManager) 
        else:
            templates = 'iTest_Server_Manager.html'
            data = itest_mmi_data.iTest_Server_Manager(self.env, req)
        return templates, data

    def B_iTestHeartBeat(self, req):
        #req.perm.assert_permission('BUILD_ADMIN') 
        iTest_WatchDog(self.env, req)
        #thread.start_new_thread(rpc_server.iTestHeartBeat, 
        #                (self.env, req, \
        #                gl.gl_polling_time_file, \
        #                gl.gl_auto_dailybuild_file, \
        #                'haha')
        #                ) 

    def B_iTestRPCServer(self, req):
        if req is not None:
            req.perm.assert_permission('BUILD_ADMIN')                   
        thread.start_new_thread(rpc_server.iTestRPCServer, 
                        (self.env, req, \
                        gl.gl_rpc_svr_polling_time_file, \
                        'haha')
                        ) 

class ServerMonitor_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('ServerMonitor'), href=req.href('/itest/ServerMonitor/home'))
        yield ('ServerMonitor','home')

    def render_module(self, req, cat, page, path_info): 
        if path_info == gl.gl_psit \
                or path_info == gl.gl_pld_srt:
            tManager = path_info            
            StarterIP = req.args.get('StarterIP')             
            if StarterIP is not None:  
                y_data = itest_mmi_data.Ajax_Starter_BusyAgent(self.env,req, tManager, StarterIP)
                req.send('5,'+y_data)
            
        templates = 'iTest_Server_Monitor.html'
        data = itest_mmi_data.iTest_Server_Monitor(self.env, req)
        return templates, data

class TestStatics_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('Statics'), href=req.href('/itest/Statics/home'))
        yield ('Statics','home')

    def render_module(self, req, cat, page, path_info):
        templates = 'iTest_Statics.html'
        data = {}
        return templates, data
        
class Help_Module(Component):
    implements(IModuleProvider)
    def get_module(self, req):
        add_ctxtnav(req, _('Help'), href=req.href('/itest/Help/home'))
        yield ('Help','home')

    def render_module(self, req, cat, page, path_info):
        templates = 'iTest_Help.html'
        data = {}
        return templates, data
        


def FeedDog(env, req, table_tmanager, cc):
    global db_conn
    schedule_event = schedule.Schedule(env)
    env.log.error('Feed_Dog: ++')

    #rpc_server.iTestRPCMain(env,'haha')
    #thread.start_new_thread(rpc_server.iTestRPCMain, (env,'haha'))
        
    while 1:        
        #env.log.error('_monitor_tmanager: ++while')        
        rpc_server.iTestHeartBeat(env,req, table_tmanager, db_conn)        
        schedule_event.trigger()
        #env.log.error('_monitor_tmanager: --while')
        time.sleep(30*1)

    env.log.error('Feed_Dog: --')

def iTest_WatchDog(env, req, table_tmanager):
        polling_time = ''
        init_env_dir = utils.get_file_dir(env, utils.get_itest_log_dir(env), gl.gl_init_env)   
        polling_time_file_name = utils.get_file_dir(env, init_env_dir, gl.gl_polling_time_file_name)        

        if not os.path.isfile(polling_time_file_name):
            polling_time = gl.gl_guardprocess_flag
        else:
            polling_time = slave_utils.read_file(polling_time_file_name) 

        if polling_time == gl.gl_guardprocess_flag:   
            polling_time = utils._show_current_time()                         
            slave_utils.write_file(polling_time_file_name,polling_time)        
            env.log.error('_guard_tmanager: ++polling_time %s',polling_time) 
            thread.start_new_thread(FeedDog, (env, req, table_tmanager, 'haha'))
            env.log.error('_guard_tmanager: --polling_time %s',polling_time)



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

from genshi import HTML  
from StringIO import StringIO
from datetime import datetime
from genshi.builder import tag
from trac.util.translation import _, ngettext, tag_
from xmlrpclib import ServerProxy

from trac.attachment import Attachment
from trac.attachment import AttachmentModule
from trac.core import *
from trac.mimeview.api import Context
from trac.resource import Resource
from trac.timeline import ITimelineEventProvider
from trac.util import escape, pretty_timedelta, format_datetime, shorten_line, Markup
from trac.util.datefmt import to_timestamp, to_datetime, utc, _units
from trac.util.html import html
from trac.web import IRequestHandler, IRequestFilter, HTTPNotFound
from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_link, add_stylesheet, add_ctxtnav, \
                            prevnext_nav, add_script, add_stylesheet, add_script, add_warning, add_notice
from trac.wiki import wiki_to_html, wiki_to_oneliner
                          
from iTest.util import xmlio
#from iTest.model import Report, TManager

import gl
import rpc_server
import utils
import slave_utils
import itest_mmi_data
import test_model
from iTest.model import Report


class TestAction(object):
    #only one test
    def __init__(self, env, db_conn, db_type=gl.gl_mysql,test=None, req=None, \
                            is_start=True, \
                            creator='', versionnum='', \
                            versionpath='', dspversionpath='', \
                            priority='', tmanager='', \
                            rerun_times='', \
                            versionorigin='', \
                            subtype='', \
                            name='', \
                            platform='', \
                            testtype='', xmlfile=''):  
        self.env = env
        if env is not None:
            self.log = env.log

        self.has_build = False
        self.db_conn = db_conn
        self.test = test
        self.req = req
        self.priorities = ['NULL']

        self.is_start = is_start
        self.creator = creator
        self.versionnum = versionnum  
        self.versionpath = versionpath 
        self.dspversionpath = dspversionpath
        self.name = name
        self.priority = priority
        self.tmanager = tmanager
        self.rerun_times = rerun_times
        self.versionorigin = versionorigin
        self.testtype = testtype
        self.sub_testtype = subtype
        self.platform = platform
        self.casetxtfile = ''
        self.passlistfile = ''
        self.passlist = ''
        self.fulllistfile = ''
        self.xmlfile = ''
        self.verify = ''
        self.versiondeltype = ''
        self.filter_flag = False
        self.case = ''

        self.db_type = db_type
        
        self.casexml = xmlio.Element('Task', desc='NULL')[
                xmlio.Element('Cases'),
            ] 
                #xml = xmlio.Element('Task', desc='NULL')[
                #    xmlio.Element('Cases')[
                #        xmlio.Element('case')[case],
                #    ],
                #]     
                    

        self.test_id = 0
        self.filter_class = ''
        self.test_dic = {}

        self.data = {}
        
        self.data['PSITtypes'] = gl.gl_psit_types 
        self.data['RDITtypes'] = gl.gl_rdit_types 
        self.data['MSITtypes'] = gl.gl_msit_types
        self.data['L1ITtypes'] = gl.gl_l1it_types
        self.data['PLD_SRTtypes'] = gl.gl_pld_srt_types
        self.data['PLD_Monkeytypes'] = gl.gl_pld_srt_types
        #self.data['CTStypes'] = gl.gl_cts_types        

        self.data['ower'] = '' #ower
        self.data['verifies'] = gl.gl_verfies  
        self.data['l1itPlatforms'] = gl.gl_l1itPlatforms 
        self.data['psitPlatforms'] = gl.gl_psitPlatforms 
        
        self.data['prioritys'] = ['NULL'] 
        self.data['tmangertypes'] = gl.gl_ps_tmangertypes


    def T_Fetch(self, db_type=gl.gl_mysql, env=None, \
                test_name=None, id=None):
        fetch_test = None
        if test_name is not None:
            fetch_test = Report.fetch(name=test_name)        
        elif id is not None:
            fetch_test = Report.fetch(id=id)           
            
        return fetch_test

    def T_Select2(self, field_hash): 
        QF = {}
        for key in field_hash:
            QF['field_'+key] = field_hash['key']
        
        return table_test.select(QF) 

    def T_Select(self, db_type=gl.gl_mysql, env=None, config=None, \
               build=None, creator=None, status=None, \
               generator=None, tmanager=None, \
               subtmanager=None, sub_testtype=None, \
               is_run_waiting_queue=False, \
               min_id=None, max_id=None): 
        return Report.select(env=env, config=config, \
               build=build, step=creator, category=status, \
               generator=generator, tmanager=tmanager, \
               subtmanager=subtmanager, total=sub_testtype, \
               is_run_waiting_queue=is_run_waiting_queue, \
               min_id=min_id, max_id=max_id)        

    def delete(self, check_last_flag=True):
        ret = self.test.delete(check_last_flag=check_last_flag)
        return ret 
        
        
    def update(self):
        self.test.update() 
        return True

    def T_Update(self, name=None, new_status=None, waitingtime=None, \
                    priority=None, test=None):
        if name is not None:
            self.test = self.T_Fetch(db_type=gl.gl_mysql, test_name = name)
        if test is not None:
            self.test = test            
            
        if self.test is not None:
            if self.sub_testtype is not None and self.sub_testtype != '':
                self.test.total = self.sub_testtype 
            if self.versionpath is not None and self.versionpath != '':    
                self.test.versionpath = self.versionpath
            if new_status is not None:
                self.test.status = new_status  
            if waitingtime is not None:
                self.test.waiting_time = waitingtime   
            if priority is not None:
                self.test.generator = priority                  
            self.test.update() 
        return True     



    def update_waitingtime(self, test):   
        if test is not None:
            self.test = test
        else:
            return 
            
        waitingtime = self.test.waiting_time  
        if waitingtime is None or waitingtime == '' or waitingtime == 0:        
            test_time = datetime.utcnow()
            test_time = test_time.isoformat()
            test_time = int(utils._format_datetime(test_time)) 
            self.T_Update(waitingtime=test_time) 


    def update_startp(self, test=None):   
        if test is not None:
            self.test = test
        else:
            return  
            
        test_time = datetime.utcnow()
        test_time = test_time.isoformat()
        test_time = int(utils._format_datetime(test_time))
    
        self.test.started = test_time
        self.test.stopped = 0
        self.test.status = gl.gl_TestInProgress
        self.update() 

    def update_endp(self, status, test=None):  
        if test is not None:
            self.test = test
        else:
            return      
        test_time = datetime.utcnow()
        test_time = test_time.isoformat()
        test_time = int(utils._format_datetime(test_time))
    
        self.test.stopped = test_time
        self.test.status = status
        self.update()  

        #发邮件 
        self.T_SendReportMail(self.test)

    def update_passratio(self, pass_nums,failed_nums,result_path,test=None, \
                                tmp_failed_nums=None):
        if test is not None:
            self.test = test
        else:
            return
            
        self.test.passed = pass_nums
        self.test.failed = failed_nums
        self.test.reserved7 = result_path
        if tmp_failed_nums is not None:
            self.test.ueitreruntimes = tmp_failed_nums
        self.update()         


    def T_V_Version(self, req=None):  
        if self.versionpath is None \
                    or self.versionpath == '':      
            if req is not None:
                #add_notice(req, "Version Path is error!")   
                add_notice(req, "Version Path Cann't be Null!")  
                add_notice(req, "Or Can not Summbit!")                
            return False         
        else:
            #一是给的路径一定要是TDPS_UEIT目录的上一级目录，最后不带“\”符号。
            if self.versionpath[-1] == '\\':
                self.versionpath = self.versionpath[:-1] #删除最后一个“\”符号
            #二是路径一定要大于等于3级目录，即至少形如\\a\b\c。
            #比如\\itest-psit1\versions_for_test\DM_BASE_W12.02是正确的，
            #而\\itest-psit1\versions_for_test\DM_BASE_W12.02\和\\itest-psit1\DM_BASE_W12.02都是不行的           
            #module_count = self.versionpath.count('\\')
            #if module_count < 4:
            #    if req is not None:
            #        add_notice(req, "Version Path is error!")    
            #        add_notice(req, "Or Can not Summbit!")                
            #    return False
       
            return True


    def valid_subtesttype(self, req=None):  
        if self.sub_testtype is None \
                    or self.sub_testtype == gl.gl_NULL \
                    or self.sub_testtype == '':
            if req is not None:
                add_notice(req, "Please choose psit case type!")   
                add_notice(req, "Or Can not Summbit!")                
                return False         
        else:
            return True       

    def valid_testplatform(self, req=None):  
        int_platform = int(self.platform)
        if int_platform > 99999999:
            add_notice(req, "Invalid Custom Platform! Must < 99999999! ")   
            return False  
        else:
            return True 

    def valid_casenum(self):        
        case_nums = itest_mmi_data._test_total_num(self.env, self.test)                        
        if case_nums == 0:
            #self.log.debug('valid_casenum: case_nums is 0')         
            return False
            
        return True

    def valid_versionpath(self):
        if self.test.versionpath is None or self.test.versionpath == '':
            #self.log.debug('valid_versionpath: + %s',self.test.versionpath)  
            return False
    
        return True

    def valid_start(self, req=None):
        if self.valid_casenum() == False:
            if req is not None:
                add_notice(req, "Test(%s) case_nums is 0!",self.test.name)      
                add_notice(req, "Please check and resubmit!")        
            return False 
    
        if self.valid_versionpath() == False:
            if req is not None:
                add_notice(req, "Test(%s) versionpath is invalid!",self.test.name)      
                add_notice(req, "Please check and resubmit!")         
            return False    
        return True
        
    def T_Valid(self, req):
        if self.testtype == gl.gl_psit:
            if self.valid_subtesttype(req=req) == False:            
                return False
            if self.T_V_Version(req=req) == False:            
                return False
        elif self.testtype == gl.gl_l1it:
            return True
        elif self.testtype == gl.gl_rdit:
            return True         
        elif self.testtype == gl.gl_pld_monkey:
            if self.valid_testplatform(req=req) == False:            
                return False
                                
        return True  

    def T_New(self, req, \
                testtype='', txt_file=''):  
        return
        
    def T_Caselist_GenXml(self): 
        #最好检查一个是否是0个
        case_file = itest_mmi_data._test_xmlfile_path(self.env, self.test)#linux path
        body = str(self.casexml)
        #self.log.error('body = %s',body ) 
        slave_utils.write_file(case_file,body) 
        
        self.xmlfile = itest_mmi_data._test_xmlfile_mmipath(self.env, self.test)#window path
        
        self.test.reserved6 = self.xmlfile
        #self.log.error('gencasexml: 1self.xmlfile = %s',self.xmlfile)
        self.T_Update() 
        #self.log.error('gencasexml: 2self.xmlfile = %s',self.xmlfile)
        
        self.casexml = xmlio.Element('Task', desc='NULL')[
                    xmlio.Element('Cases'),
                ]   

    def T_Caselist_AppendCase(self, req, case, filter_flag=False):         
        #case = case.replace('Save by tool','')
        #case = case.replace('\t','')
        #case = case.replace('\r','')
        case = case.replace('\n','')   
        #case = case.replace(' ','')
        if case != '':            
            if filter_flag == True:                                
                if slave_utils.check_string(self.passlist, case) == True:                               
                    self.casexml.append(xmlio.Element('case')[case]) 
                else:
                    #add_notice(req, "Case(%s) is not existed in the passlist of %s.",case, self.versionnum)    
                    add_notice(req, "Case(%s) is not existed in the passlist of %s.",case, req.args.get('versionnum'))   
            else:
                self.casexml.append(xmlio.Element('case')[case])
                
    def T_Caselist_Plst(self, req):  #passlist 
        versionnum = req.args.get('versionnum')
        list_version_dir = utils.get_file_dir(self.env, gl.gl_passlist_path2, versionnum)
        hsit_passlist_txt_file = gl.hsit_passlist_txt
        passlistfile = utils.get_file_dir(self.env, list_version_dir, hsit_passlist_txt_file)              
        if os.path.exists(passlistfile):         
            self.passlist = slave_utils.read_file(passlistfile)  #不能放在for里面 
        
            
    def T_Caselist_PlstFile(self, req, testtype):  #passlist File   
        sub_testtype = req.args.get(testtype+'type')                 
        if os.path.exists(gl.gl_passlist_path2):   
            versionnum = req.args.get('versionnum')
            list_version_dir = utils.get_file_dir(self.env, gl.gl_passlist_path2, versionnum)
            hsit_passlist_txt_file = gl.hsit_passlist_txt
            hsit_wholelist_txt_file = gl.hsit_wholelist_txt
        else:
            return 'Error: /netdisk/q/PS/PSIT/PassList is not Existed!'  
        
        if slave_utils._is_passlisttest(sub_testtype) == True:  
            passlistfile = utils.get_file_dir(self.env, list_version_dir, hsit_passlist_txt_file)
            passlisttmpfile = passlistfile.replace(gl.hsit_passlist_txt, gl.hsit_passlist_temp_txt)         
            if os.path.exists(passlistfile): 
                add_notice(req, "passlistfile is %s!", passlistfile) 
                return passlistfile
            elif os.path.exists(passlisttmpfile):  
                add_notice(req, "passlistfile is %s, not existed!", passlistfile) 
                add_notice(req, "use passlisttmpfile is %s!", passlisttmpfile) 
                return passlisttmpfile           
        elif sub_testtype == gl.gl_FULL_TEST:            
            fulllistfile = utils.get_file_dir(self.env, list_version_dir, hsit_wholelist_txt_file)
            if os.path.exists(fulllistfile): 
                add_notice(req, "fulllist is %s!", fulllistfile) 
                return fulllistfile
        elif sub_testtype == gl.gl_PASSLIST_CR: 
            #7)	如果passlist_cr.txt文件不存在，则使用相应的hsit_passlist.txt替代
            passlistfile = utils.get_file_dir(self.env, list_version_dir, hsit_passlist_txt_file)
            passlist_crfile = passlistfile.replace(gl.hsit_passlist_txt ,gl.hsit_passlist_cr_txt)         
            if os.path.exists(passlist_crfile):   
                add_notice(req, "passlist_cr is %s!", passlist_crfile) 
                return passlist_crfile
            elif os.path.exists(passlistfile):  
                add_notice(req, "passlist_cr is %s, not existed!", passlist_crfile) 
                add_notice(req, "use passlistfile is %s!", passlistfile) 
                return passlistfile 
        
        return 'Error: sub_testtype'    
        
    def T_CaselistTxtFile(self,req, testtype):
        casetxtfile = 'Error'
        sub_testtype = req.args.get(testtype+'type') 
        smoke_dir = utils.get_test_list_model_dir(self.env)
        casetxtfile = utils.get_file_dir(self.env, smoke_dir, testtype+'_'+sub_testtype+'.txt')  
                
        if sub_testtype == gl.gl_CUSTOM:
            casetxtfile = req.args.get(gl.gl_srv_testlist)
        else:                                        
            if testtype == gl.gl_psit: 
                if slave_utils._is_passlisttest(sub_testtype) == True \
                        or sub_testtype == gl.gl_PASSLIST_CR \
                        or sub_testtype == gl.gl_FULL_TEST:
                    casetxtfile = self.T_Caselist_PlstFile(req, testtype)  
        
        if os.path.exists(casetxtfile):
            add_notice(req, "CaseList File is %s!", casetxtfile) 
            return casetxtfile 
        else: 
            add_notice(req, "Error, CaseList File(%s) is not existed!", casetxtfile) 
            return ''

    def T_CaselistMonkey(self, req):
        # 所有的都是CUSTOM
        casetxtfile = req.args.get(gl.gl_srv_testlist)  
        rerun_times = req.args.get('rerun_times')   
        model_list_data = slave_utils.read_file(casetxtfile)
        module_count = model_list_data.count('\n')   
        cases = model_list_data.split('\n',module_count)
        for case in cases:
            if case != '':                   
                case = case.replace('\r','')
                case = case.replace('\n','')
                case = case.replace(' ','')
                case = case.replace('\t','')
                self.log.error('case = %s',case )     
                break 
                
        if case != '':                
            i = 0
            while i < int(rerun_times):
                i = i + 1
                self.T_Caselist_AppendCase(req, case)
            self.T_Caselist_GenXml()  
            return True
        else:
            add_notice(req, "Fail to create test(%s)!", self.name) 
            #add_notice(req, "caselist file name(%s) is not supported!", self.xmlfile)
            #self.log.error('caselist file name(%s) is not supported!',self.xmlfile)
            return False         
    
    def T_Caselist(self, req, testtype, case='', buildtype=''):                       
        casetxtfile = self.T_CaselistTxtFile(req, testtype)   
        self.log.error('T_Caselist: casetxtfile = %s', casetxtfile)
        if casetxtfile == '':
            add_notice(req, "Caselist file is not existed. Please check!")                                    
            return False
              
        model_list_data = slave_utils.read_file(casetxtfile)  
        model_list_data = model_list_data.replace('Save by tool','')
        model_list_data = model_list_data.replace('\t','')
        model_list_data = model_list_data.replace('\r','')
        model_list_data = model_list_data.replace(' ','')              
        module_count = model_list_data.count('\n')    
            
        if module_count != 0:
            cases = model_list_data.split('\n',module_count)

            filter_class = req.args.get(gl.gl_casefilterclass)            
            if testtype == gl.gl_psit and filter_class == gl.gl_From_PassList:
                self.T_Caselist_Plst(req)
                filter_flag = True
            else:
                filter_flag = False 
                    
            sub_testtype = req.args.get(testtype+'type') 
            if slave_utils._is_passlisttest(sub_testtype) == True \
                        or sub_testtype == gl.gl_FULL_TEST:                        
                for case in cases:
                    self.casexml.append(xmlio.Element('case')[case])
            elif sub_testtype == gl.gl_PASSLIST_CR:                
                if filter_flag == True:
                    for case in cases:
                        if slave_utils.check_string(self.passlist, case) == True:                               
                            self.casexml.append(xmlio.Element('case')[case]) 
                        else:                           
                            add_notice(req, "Case(%s) is not existed in the passlist of %s.",case, req.args.get('versionnum'))   
                else:
                    for case in cases:
                        self.casexml.append(xmlio.Element('case')[case])
            else:                   
                for case in cases:
                    self.T_Caselist_AppendCase(req, case, filter_flag=filter_flag)
        else:
            if model_list_data != '':
                self.T_Caselist_AppendCase(req, model_list_data)
            else:                
                add_notice(req, "No Case. Please check!")         
                return False
                
        self.T_Caselist_GenXml()     
        return True
        
    def T_SendReportMail(self, test): 
        import web_utils
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        
        creator = test.step
        email_list = []
        email_list.append(creator)
        #email_list = list(creator)
        
        mail_content = ''        
        mail_content += web_utils.iTest_report(self.env, test)
        maildic = {}
        maildic['title'] = 'iTest TestReport: ' + test.name 
        maildic['to'] = email_list
        maildic['content'] = mail_content #mail_content.decode('utf-8') 
        utils.sendmail(self.env, maildic) 

    def T_Build2start(self, req=None, test=None, test_name=None,versionpath=''): 
        if test_name is not None:
            self.test = self.T_Fetch(db_type=gl.gl_mysql, test_name = test_name)    
        elif test is not None:
            self.test = test        
            
        if self.test is not None and versionpath is not None and versionpath != '':
            self.versionpath = versionpath.replace('/','\\')  
            
            test_time = datetime.utcnow()
            test_time = test_time.isoformat()
            test_time = int(utils._format_datetime(test_time))  
            self.T_Update(waitingtime=test_time)  
        
            self.testtype = itest_mmi_data._test_type(self.env, self.test)
            ret = self.B_Start(req=req)
        else:
            ret = False
            
        return ret
        
    def T_I_SpecialProperty(self, verify, versiondeltype):   
        if verify == 'CR':
            ret = '1'
        elif verify == 'DB':
            ret = '2'
        elif verify == 'BASE':
            ret = '3'
        elif verify == 'MP':
            ret = '4'
        else:  
            ret = '0'

        if versiondeltype == 'Yes':
            ret += '1'
        elif versiondeltype == 'No':
            ret += '2'
        else:  
            ret += '0'
            
        return ret 
       
    def T_Insert2(self):         
        self.test = test_model.iTest(None, self.db_conn)  

        self.test['step'] = self.test_dic['creator']  
        self.test['generator'] = self.test_dic['priority']         
        self.test['build'] = self.test_dic['name']
        self.test['version_num'] = self.test_dic['versionnum']
        self.test['tmanager'] = self.test_dic['tmanager']
        self.test['total'] = self.test_dic['sub_testtype'] 
        self.test['ueitreruntimes'] = self.test_dic['rerun_times']        
        self.test['reserved8'] = self.test_dic['platform']  
        self.test['versionpath'] = self.test_dic['versionpath']        
        self.test['reserved4'] = self.T_I_SpecialProperty(self.test_dic['verify'], self.test_dic['versiondeltype'])                
        self.test['reserved6'] = ''
        self.test['status'] = gl.gl_TestCreated 
        self.test.insert() 
        
        self.test_id = self.test['ID']
        self.name = self.test_dic['name']
        return True    

    def T_Insert(self):         
        self.test = Report(self.env)  

        self.test.step = self.test_dic['creator']  
        self.test.generator = self.test_dic['priority']         
        self.test.build = self.test_dic['name']
        self.test.version_num = self.test_dic['versionnum']
        self.test.tmanager = self.test_dic['tmanager']
        self.test.total = self.test_dic['sub_testtype'] 
        self.test.ueitreruntimes = self.test_dic['rerun_times']        
        self.test.reserved8 = self.test_dic['platform']  
        self.test.versionpath = self.test_dic['versionpath']        
        self.test.reserved4 = self.T_I_SpecialProperty(self.test_dic['verify'], self.test_dic['versiondeltype'])                
        self.test.reserved6 = ''
        self.test.status = gl.gl_TestCreated 
        self.test.insert() 

        QF = {}
        QF ['field_build'] = self.test_dic['name'] 
        a_new_table = test_model.iTest(None, self.db_conn) 
        querylist = a_new_table.select(QF)               
        self.log.error('T_Insert: querylist=%s',querylist)
        self.log.error('T_Insert: self.test.id=%s',self.test.id)
        for tmanager in querylist:                     
            ID = tmanager['ID'] 
            break
        self.test_id = self.test.id#ID #self.test.id
        self.name = self.test_dic['name']  
        self.log.debug('T_Insert: %s,%s', self.test_id,self.name)
        
        return True 

    def T_S_Platform(self, req, testtype, rditPlatform):   
        if testtype == gl.gl_msit:
            platform = req.args.get('msitPlatform')    
        elif testtype == gl.gl_l1it:            
            platform = req.args.get('l1itPlatform')
        elif testtype == gl.gl_pld_monkey:
           PldCustomPlatform = req.args.get('PldCustomPlatform')
           
           #格式为：产品编号+内存宽度+屏幕尺寸+产品形态
           #手机信息为sc6530、128*64、320*480、pda的编码为 11141416
           ProductID = req.args.get('ProductID')
           ProductPattern = req.args.get('ProductPattern')
           MemoryWidth = req.args.get('MemoryWidth')
           ScreenSize = req.args.get('ScreenSize') 

           if ProductID == 'sc6530':
               platform = '11'
           elif ProductID == 'sc8501C':
               platform = '12'
           elif ProductID == 'sc6531':
               platform = '13'
           elif ProductID == 'sc6500':
               platform = '14'
           elif ProductID == 'sc7701':
               platform = '15'
           elif ProductID == 'sc7702':
               platform = '16'   
           elif ProductID == 'sc8502':
               platform = '17'                
           else:
               platform = '00'               

           #无效值	0
           if MemoryWidth == '16*16':
               platform += '11' 
           elif MemoryWidth == '32*64':
               platform += '12' 
           elif MemoryWidth == '64*64':
               platform += '13' 
           elif MemoryWidth == '128*64':
               platform += '14' 
           elif MemoryWidth == '512*256':
               platform += '15'
           elif MemoryWidth == '32*32':
               platform += '16'               
           else:
               platform += '00' 
               

           #无效值	0
           if ScreenSize == '240*320':
               platform += '11' 
           elif ScreenSize == '320*240':
               platform += '12' 
           elif ScreenSize == '240*400':
               platform += '13' 
           elif ScreenSize == '320*480':
               platform += '14' 
           elif ScreenSize == '220*176':
               platform += '15'
           elif ScreenSize == '128*160':
               platform += '16'               
           else:
               platform += '00'    

           #无效值	00
           if ProductPattern == 'bar_op':
               platform += '11' 
           elif ProductPattern == 'bar_qw':
               platform += '12' 
           elif ProductPattern == 'fpga':
               platform += '13' 
           elif ProductPattern == 'fpga_rvds':
               platform += '14' 
           elif ProductPattern == 'le':
               platform += '15' 
           elif ProductPattern == 'pda':
               platform += '16'                
           elif ProductPattern == 'pda_formal':
               platform += '17' 
           elif ProductPattern == 'pda_le':
               platform += '18' 
           elif ProductPattern == 'pda_op':
               platform += '19' 
           elif ProductPattern == 'pda_rvct_le':
               platform += '21' 
           elif ProductPattern == 'pda2':
               platform += '22' 
           elif ProductPattern == 'tk_inside_op':
               platform += '23' 
           elif ProductPattern == 'tk_op':
               platform += '24' 
           elif ProductPattern == 'tk_op_formal':
               platform += '25' 
           elif ProductPattern == 'tk_qw':
               platform += '26' 
           elif ProductPattern == '3G':
               platform += '27'    
           elif ProductPattern == 'TD':
               platform += '28'                
           else:
               platform += '00'   

           if PldCustomPlatform != '0':    
               platform = PldCustomPlatform
               #int_platform = int(platform)
               #if platform > 99999999:
               #    add_notice(req, "Invalid Custom Platform! Must < 99999999! ")   
               #else:
               #    self.log.error('testplatform=%s,name=%s', platform, self.name)               
        elif testtype == gl.gl_rdit:             
            if rditPlatform == 'T1':
                platform = '0001' 
            elif rditPlatform == 'T2':
                platform = '0002' 
            elif rditPlatform == gl.gl_T2_9810:
                platform = '0003' 
            elif rditPlatform == gl.gl_T2_8810:
                platform = '0004'  
            elif rditPlatform == gl.gl_T2_8501c:
                platform = '0005'                  
            elif rditPlatform == 'W1':
                platform = '0101' 
            else:
                platform = '0'  
        else:
            platform = '0'  

        return platform

    def T_Save(self, req, testtype, name, rditPlatform=None):  
        self.test_dic['name'] = name #*        
        self.test_dic['testtype'] = testtype #*
        self.test_dic['tmanager'] = testtype  
        self.test_dic['sub_testtype'] = req.args.get(testtype+'type') 
        
        self.test_dic['creator'] = req.session.sid       
        self.test_dic['versionnum'] = req.args.get('versionnum')             
        self.test_dic['priority'] = req.args.get('priority')
        self.test_dic['verify'] = req.args.get('verify')
        self.test_dic['versiondeltype'] = req.args.get('versiondeltype') 
        self.test_dic['dspversionpath'] = req.args.get(gl.gl_dspversionpath)
        self.test_dic['versionpath'] = req.args.get(gl.gl_versionpath)
        self.test_dic['priority'] = req.args.get('priority') 
        if testtype == gl.gl_psit:            
            if self.test_dic['priority'] == gl.gl_NULL:               
                if self.test_dic['sub_testtype'] == gl.gl_DUAL_L1_PASSLIST \
                        or self.test_dic['sub_testtype'] == gl.gl_DUAL_L2_PASSLIST \
                        or self.test_dic['sub_testtype'] == gl.gl_CUSTOM:
                    self.test_dic['priority'] = gl.gl_new_Middle 
                elif slave_utils._is_fulltest(self.test_dic['sub_testtype']) == True: 
                    self.test_dic['priority'] = gl.gl_new_Low              
                else:
                    self.test_dic['priority'] = gl.gl_new_High  
                    
        if testtype == gl.gl_pld_monkey:
            self.test_dic['rerun_times'] = req.args.get('rerun_times')    
        else:
            self.test_dic['rerun_times'] = '4'   
        
        self.test_dic['platform'] = self.T_S_Platform(req, testtype, rditPlatform) 
        #if self.T_Valid(req) == False:
        #    add_notice(req, "Fail to create test(%s)!", self.name) 
        #    return False

        ret = self.T_Insert()
        #if ret == True:            
        #    add_notice(req, "Success to create test (%s)!", self.name) 
        #    self.log.debug('test save: name=%s,ret=%s',self.name, ret) 
        #else:
        #    add_notice(req, "Fail to create test(%s)!", self.name) 
        #    self.log.error('test save: name=%s,ret=%s',self.name, ret) 
        return ret  
                                        
  

    def B_Start(self, req=None, test=None, test_name=None):  
        if test is not None:
            self.test = test

        if self.test is None:
            if self.db_type == gl.gl_mysql:
                self.test = self.T_Fetch(test_name = test_name)
            
        if self.valid_start(req=req) == False:
            if req is not None:
                add_notice(req, "Fail to start (%s)!", self.name) 
            return False
            
        if self.is_start == True and self.test is not None:            
            if self.test.status == gl.gl_TestCreated: 
                self.test.status = gl.gl_TestVersionReady                 
                self.update()          
                if req is not None: 
                    add_notice(req, "Test(%s) has been started now.",self.test.name)
            elif self.test.status == gl.gl_TestStopped \
                        or self.test.status == gl.gl_TestError:
                self.test.passed = '0'
                self.test.failed = '0'
                self.test.started = 0
                self.test.stopped = 0        	  
                self.test.status = gl.gl_TestVersionReady                 
                self.update()          
            elif self.test.status == gl.gl_TestReady \
                        or self.test.status == gl.gl_TestInProgress \
                        or self.test.status == gl.gl_TestVersionReady: 
                if req is not None:
                    add_notice(req, "Test(%s) is in queue now.",self.test.name)      
                    add_notice(req, "Please wait patiently!") 
            elif self.test.status == gl.gl_TestFinish: 
                if req is not None:            
                    add_notice(req, "Test(%s) has been finished. Can not Start.",self.test.name)      
                    add_notice(req, "Please resubmit one new 'build and test!'")            
        return True                        

    def B_Save2start(self, req, testtype=None, name=None, rditPlatform=None): 
        if testtype is None:
            return False
        if name is None:
            return False
                 
        ret = self.T_Save(req, testtype, name, rditPlatform=rditPlatform)
        if ret == True:
            if testtype == gl.gl_pld_monkey:   
                ret = self.T_CaselistMonkey(req)  
            else:
                ret = self.T_Caselist(req, testtype)
            if ret == False:
                self.delete(check_last_flag=False)
                return False
            ret = self.B_Start(req=req)   
        return ret     

   

    def B_Stop(self, req=None, test=None):        
        if test is not None:
            self.test = test
            
        test_time = datetime.utcnow()
        test_time = test_time.isoformat()
        test_time = int(utils._format_datetime(test_time))
    
        self.test.stopped = test_time
        self.test.status = gl.gl_TestWaitingStop     
        self.update()
        
        return True   

    def B_Reset(self, req=None, test=None):
        if test is not None:
            self.test = test      
          
        self.test.status = gl.gl_TestCreated
        self.update()  
        return True

    def B_Modify(self, req, test):   
        verify_type = itest_mmi_data._test_verfy_type(self.env, test)    
        versiondel_type = itest_mmi_data._test_versiondel_type(self.env, test)    
        priority = test.generator        
        self.data['title'] = 'Modify '+str(test.build) 
        self.data['id'] = test.id
        self.data['name'] = test.name

        #必须留着
        self.data['test'] = {
                    'name': test.name
                    }

        #self.log.error('T_Modify, %s', test.name)

        #test_table
        from genshi import HTML   
        js = rpc_server.ModifyTest(req, priority=priority, verify_type=verify_type, name=test.name, creator=test.creator)          
        #js = rpc_server.rpc_NewTest(req)    
        self.data.update({'test_table':HTML(js)}) 
        
        #self.log.error('T_Modify, %s', self.data)
        return self.data
        
    def B_SendReport(self, test): 
        import rpc_server
        rpc_server = rpc_server.MutilTManagerSrv(self.env)
        rpc_server.upload_testreport(self.env, test)

        

    def B_AddReport2Bugz(self, test): 
        import rpc_server
        rpc_server = rpc_server.MutilTManagerSrv(self.env)
        rpc_server.update_bz_comment(self.env, test)
        
    
    def B_Modify2save(self, req, test):  
        if test is not None:
            self.test = test
        
        self.test.generator = req.args.get('priority') 

        verify = req.args.get('verify') 
        versiondeltype = req.args.get('versiondeltype') 
        self.test.reserved4 = self.T_I_SpecialProperty(verify, versiondeltype)  
        
        self.test.update() 
        return True


    def B_Remove(self, req=None, test=None, id=None):
        if id is not None:             
            self.test = self.T_Fetch(db_type=gl.gl_mysql, id = id)
            if self.test is None:
                add_notice(req, "Test (%s) not found!!!", str(id))
                return None         
        elif test is not None:
            self.test = test  
            
        if req is not None:
            if req.perm.has_permission('BUILD_ADMIN'):
                self.log.debug('remove: BUILD_ADMIN delete test(%s)', str(self.test.build))            
            else:                
                if self.test.step != req.session.sid: 
                    add_notice(req, "No Permission! Only Creator Can Take this Action!!!")  
                    return None 
                    
        testtype = itest_mmi_data._test_type(self.env, self.test)  
        if testtype is None or testtype == '':
        	self.test.status = gl.gl_TestFinish

        flag = False
        for tmanager in TManager.select(self.env):                     
            if testtype == tmanager.type: 
                flag = False
                break  
            flag = True             
        	
        if self.test.status == gl.gl_TestCreated \
                or self.test.status == gl.gl_TestFinish \
                or self.test.status == gl.gl_TestStopped \
                or flag == True:
            ret = self.test.delete()
            if ret == True:
                add_notice(req, _('Delete Test "%(test_id)s".', test_id=str(self.test.build)))
            else:
                add_notice(req, _('Test "%(test_id)s" is last test, can not delete!', test_id=str(self.test.build))) 
        else:
            #stop, 先给tmanger发stop命令            
            self.test.status = gl.gl_TestStopAndDelete        
            self.update()
            add_notice(req, _('Stop Test "%(test_id)s, and will be delete after 1min".', test_id=str(self.test.build)))

        test_name = itest_mmi_data._test_name(self.test)     
        return test_name
   


    def T_MMI(self, req, testid=0):
        if testid != 0:
            self.test = self.T_Fetch(db_type=gl.gl_mysql, id = testid)
        self.T_MMI_Data(req)
        return self.data


    def T_MMI_Data(self, req):
        #测试相关时间
        current = ''
        current = datetime.utcnow()
        current = current.isoformat()
        current_int = int(utils._format_datetime(current))  
        current = format_datetime(current_int)  

        start_time_int = self.test.started
        end_time_int = self.test.stopped
    
        if start_time_int == 0:
            start_test_time = ''
            end = ''
            timecost = '' 
        else:
            start_test_time = format_datetime(start_time_int)
            if end_time_int == 0:  
                end = ''
                timecost = itest_mmi_data._test_timecost(self.env, start_time_int, current_int)
            else:
                end = format_datetime(end_time_int)
                timecost = itest_mmi_data._test_timecost(self.env, start_time_int, end_time_int)                

        if self.test.total is not None and self.test.total != '':
            subtype = self.test.total
        else:
            subtype = '' 
        
        test_date = start_test_time

        left_case = int(itest_mmi_data._test_total_num(self.env, self.test)) - int(self.test.passed) - int(self.test.failed)
        tmanager_type = itest_mmi_data._test_type(self.env, self.test)
        testid = self.test.id
        name = self.test.name  
        inprogresscase_length = 0
        failcase_length = 0
        self.data = {
            'id': self.test.id,
            'name': self.test.name, 
            'creator': self.test.creator,         
            'priority': self.test.priority,
            'versionpath': self.test.versionpath,
            'dspversionpath': itest_mmi_data._test_dspversionpath(self.test), 
            'versionorigin': self.test.reserved5,
            'version': self.test.version_num,
            'buildtype': tmanager_type,
            'subtype': subtype,
            'caselist': itest_mmi_data._test_xmlfile_mmipath(self.env, self.test),
            'status': itest_mmi_data._test_status(self.test),
            'result_href': gl.url_log_testid(req, self.test), #req.href.build(gl.gl_href_testresult, self.test.id),
            'testhref': gl.url_log_testid(req, self.test),
            'testreport': itest_mmi_data._test_passratio(self.env, self.test),
            'TempPassRatio': itest_mmi_data._test_temppassratio(self.env, self.test),
            'tManager': self.test.tmanager,
            'total': itest_mmi_data._test_total_num(self.env, self.test),
            'passed': self.test.passed,
            'fail': self.test.failed,
            'left_case': str(left_case), 
            'date': test_date,
            'start': start_test_time,
            'current': current,
            'end': end,
            'timecost': timecost,
            'result_path': itest_mmi_data._test_reportpath(self.env, self.test),
            'testplatform': self.test.reserved8,
            'inprogresscase_length': 'init',
            'failcase_length': 'init'
            }   

        _rpc_server = rpc_server.rpc_tmanger(self.env, tmanager_type)
        self.data['failcases'] = itest_mmi_data._test_failcases_data(self.env, _rpc_server, testid, name)         
        (inprogresscase_length, self.data['inprogresscases']) = itest_mmi_data._test_inprogresscases_data(self.env, _rpc_server, testid, name)    

        failcase_length = len(self.data['failcases'])         

        self.data['inprogresscase_length'] = str(inprogresscase_length)
        self.data['failcase_length'] = str(failcase_length)        
        self.data['y_max'] = itest_mmi_data._test_agentlength(self.env, req, _rpc_server)
        self.data['inprogress_test_nums_url'] = gl.url_inprogress_test_nums(tmanager_type, self.test) 
          
        js = itest_mmi_data.ajax_inprogress_testcase(self.env, req, self.test.id, is_init=True)  
        self.data.update({'mainframe':HTML(js)})        
          
        ret = itest_mmi_data._test_starter_dyn(self.env, self.test.id, _rpc_server)
        if ret is not None:                
            index = 1  
            total_D = 0

            for one_info in ret:            
                self.data['N'+str(index)] = one_info['startip']
                self.data['D'+str(index)] = one_info['busyagents']  
                index = index + 1
                total_D += int(one_info['busyagents'])
            while index < 21:
                self.data['N'+str(index)] = ''
                self.data['D'+str(index)] = '0'
                index = index + 1    
            self.data['total_D'] = str(total_D)
            
        
  
                
def iTest_NewTest(env, req, data = {}, \
                            xml_file_name='', \
                            txt_file_name='', \
                            has_build = False):  
        testtype = req.args.get(gl.gl_test_type_mode)         
        #test = Report(env)  

        default_testname = req.session.sid + '_test'
        mmi_testname = req.args.get('name','')
         
        #if mmi_testname == default_testname \
        #        or mmi_testname is None \
        #        or mmi_testname == '':
        #    test.build = default_testname
        #else:
        #    test.build = mmi_testname
            
        #test.category = req.session.sid 
        #test.generator = req.args.get('versionpath')        
        data['versionpath'] = ''#test.generator

        #context = Context.from_request(req, test.new_resource) 
        #data['context'] = context       
        data['attachment'] = Attachment(env, 'iTest', 1)                       
        data['PLD_Monkeytypes'] = gl.gl_subtypes_CUSTOM
        data['CTStypes'] = gl.gl_cts_types
        
        if txt_file_name != '':
            if has_build == False:
                data['PLD_Monkeytypes'] = gl.gl_subtypes_CUSTOM         

        if has_build == True:
            uploadcaselist_txt = gl.gl_bt_uploadcaselist_txt
        else: 
            uploadcaselist_txt = 'uploadcaselist_txt'

        import web_utils         

        js = web_utils.iTest_New_table_name(req, uploadcaselist_txt, caselistfile=txt_file_name, has_build=has_build)
        data.update({'table_name':HTML(js)})  
        
        js = web_utils.iTest_New_table_versionnum(req, uploadcaselist_txt, caselistfile=txt_file_name, has_build=has_build)
        data.update({'table_versionnum':HTML(js)}) 

        js = web_utils.iTest_New_table_testversion(req, uploadcaselist_txt, caselistfile=txt_file_name, has_build=has_build)
        data.update({'table_testversion':HTML(js)})   
        
        #js = web_utils.iTest_New_table_testlist(req, uploadcaselist_txt, caselistfile=txt_file_name, has_build=has_build)
        #data.update({'table_testlist':HTML(js)})  

        js = web_utils.iTest_New_table_PLD_SRT(env, req, txt_file_name)
        data.update({'table_PLD_SRT':HTML(js)})

        js = web_utils.iTest_New_table_HSIT(env, req, txt_file_name)
        data.update({'table_HSIT':HTML(js)})

        js = web_utils.iTest_New_table_RDIT(env, req, txt_file_name)
        data.update({'table_RDIT':HTML(js)})

        js = web_utils.iTest_New_table_L1IT(env, req, txt_file_name)
        data.update({'table_L1IT':HTML(js)})
        
        js = web_utils.iTest_New_table_MSIT(env, req, txt_file_name)
        data.update({'table_MSIT':HTML(js)})
             
        data['ProductIDs'] = gl.gl_ProductIDs 
        data['ProductPatterns'] = gl.gl_ProductPatterns
        data['MemoryWidths'] = gl.gl_MemoryWidths 
        data['ScreenSizes'] = gl.gl_ScreenSizes

        return data


def _upload_attachment(env, req, uploadfile):     
        sid = req.session.sid
        
        parent_id = None
        parent_realm = 'build'
        filename = None        
        parent_realm = Resource(parent_realm)          
           
        Attachment.delete_all(env, 'iTest', sid) 
        attachment = Attachment(env, 'iTest', sid)
        attachment.description = sid

        if not hasattr(uploadfile, 'filename') or not uploadfile.filename:            
            raise TracError(_('No file uploaded1'))
        if hasattr(uploadfile.file, 'fileno'):
            size = os.fstat(uploadfile.file.fileno())[6]
        else:
            uploadfile.file.seek(0, 2) # seek to end of file
            size = uploadfile.file.tell()
            uploadfile.file.seek(0)
        
        if size == 0:
            raise TracError(_("Can't upload empty file"))

        # We try to normalize the filename to unicode NFC if we can.
        # Files uploaded from OS X might be in NFD.
        filename = unicodedata.normalize('NFC', unicode(uploadfile.filename,
                                                        'utf-8'))
        filename = filename.replace('\\', '/').replace(':', '/')
        filename = os.path.basename(filename)
        
        if not filename:
            raise TracError(_('No file uploaded2'))
        
        attachment.insert(filename, uploadfile.file, size)  
        return attachment

def iTest_UploadCaselist(env,req):  
    uploadfile = req.args.get('caselist_file')    
    if hasattr(uploadfile, 'filename'):
        pass
    else:
        uploadfile = ''
        
    attachment = _upload_attachment(env,req, uploadfile)
    filename = attachment.filename
    username = req.session.sid    
    #'/trac/Projects/iTest/attachments/iTest/'
    txt_file_name = env.path + '/attachments'
    txt_file_name += '/iTest/' + username + '/' + filename
        
    #src: /trac/Projects/iTest/attachments/iTest/song.shan_psit/bcfe_sam_list.txt
    #dest: /home/share/test_xml/song.shan_psit/bcfe_sam_list.txt(linux)
    #dest: \\itest-center\share\test_xml\song.shan_psit\bcfe_sam_list.txt(win)                
    src_file = txt_file_name 
    dest_file = utils.get_file_dir(env, utils.get_test_xml_dir(env), filename)
    utils._copy_file(env, src_file,  dest_file) 
    attachment.delete()
    txt_file_name = dest_file
    return txt_file_name       
                        
def _test_type_nums(env, req):
    num = 0
    test_type = []
    #mmi 上面换名字 PSIT=>HSIT
    if req.args.get(gl.gl_HSIT) == gl.gl_HSIT:
        num += 1
        test_type.append(gl.gl_psit)   
    if req.args.get(gl.gl_msit) == gl.gl_msit:
        num += 1
        test_type.append(gl.gl_msit) 
    if req.args.get(gl.gl_rdit) == gl.gl_rdit:
        num += 1 
        test_type.append(gl.gl_rdit)            
    if req.args.get(gl.gl_l1it) == gl.gl_l1it:
        num += 1 
        test_type.append(gl.gl_l1it)
    if req.args.get(gl.gl_pld_srt) == gl.gl_pld_srt:
        num += 1 
        test_type.append(gl.gl_pld_srt)
    if req.args.get(gl.gl_pld_monkey) == gl.gl_pld_monkey:
        num += 1 
        test_type.append(gl.gl_pld_monkey)
                
    return (num, test_type)

      

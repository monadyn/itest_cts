# -*- coding: utf-8 -*-
#

import shutil
import calendar
import time
import struct
import posixpath
import os, sys, re 

import gl
import itest_mmi_data
import slave_utils

from StringIO import StringIO
from datetime import datetime

from trac.util import escape, format_datetime, shorten_line, Markup
from trac.web.chrome import INavigationContributor, ITemplateProvider
                    

newdir = "" 


def save_xls_file(env, xlsfile, title_cols, rows_data):
        import xlwt
        
        # Create workbook and worksheet
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('itest_xls')

        row = 0  # row counter
        col = 0
        f = ["product", "component", "bug_status", \
                        "bug_severity", "reporter", "assigned_to",\
                        "cf_come_from", "cf_base_on_ver", "cf_fix_on_ver", "changeddate"]

        for title in title_cols:
            # Write the data, using the style defined above.
            sheet.write(row, col, title.decode('GBK'))
            col += 1     

        for line in rows_data:
            # separate fields by commas
            col = 0
            for title in title_cols:
                sheet.write(row, col, line[title].decode('GBK'))
                col += 1   

            row += 1

        #xlsfile ='/home/share/data2.xls'
        wbk.save(xlsfile)
        

def sendmail(env, maildic):    
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    if 1:
        import smtplib  
        from email.MIMEText import MIMEText  
        #from email.header import Header
        #from email.mime.multipart import MIMEMultipart
        
        Subject = maildic['title']
        sender = "itest@spreadtrum.com"
        #rcpt = maildic['to']
        rcpts = maildic['to']
        env.log.error('sendmail %s',rcpts)
        
        #rcpt = "song.shan@spreadtrum.com"
        html = '<html><body>'+maildic['content']+'</body></html>'
        
        #msg = MIMEMultipart('alternatvie')
        msg = MIMEText(html, 'html') #ʵ����Ϊhtml����
        #html_part = MIMEText(html, "plain", "utf-8")
        #html2_part = MIMEText(html, "html", "utf-8")
        
        #msg.set_charset('utf-8') #���ñ���
        msg['Subject'] = Subject
        msg['From'] = sender #ʹ�ù��ʻ�����
        
        
        #html = open('html.tpl').read() #��ȡHTMLģ��        
        #html_part = MIMEText(html,'html') 
        #html_part.set_charset('utf-8') #���ñ���
        #msg.attach(html_part) #�󶨵�message�� 
        #msg.attach(html2_part)
        try:
            s = smtplib.SMTP('172.16.0.25') #��¼SMTP������,����
            for rcpt in rcpts:
                if rcpt != '':
                    rcpt = rcpt+'@spreadtrum.com'
                    msg['To'] = rcpt
                    env.log.error('sendmail rcpt = %s',rcpt)
                    s.sendmail(sender,rcpt,msg.as_string())
        except Exception,e:
            env.log.exception("Failure sending notification "
                               "%s", e) 
           

#�ݹ��������� 
def search(env, rootdir,searchdirname): 
    if os.path.isdir(rootdir): 
                #print rootdir 
                #����·�����ļ��� 
                split1 = os.path.split(rootdir) 
                #print split1[1] 

                #�ж��Ƿ�Ϊָ�����ļ��� 
                if split1[1] == searchdirname: 
                        print "�ҵ��ļ��У�%s" % (rootdir) 
                        try: 
                                #���ļ������Ƹ�Ϊ�µ��ļ������� 
                                os.rename(rootdir,split1[0]+"\\"+newdir) 
                                print "�ļ��� [%s] �Ѹ���Ϊ [%s]" % (rootdir,newdir) 
                        except: 
                                pass 

                #����ָ���ļ����µ����ݣ��ļ����ļ����б� 
                listnew = os.listdir(rootdir) 

                for l1 in listnew: 
                        path = rootdir + "\\" + l1 
                        #�ݹ���� 
                        search(path,searchdirname) 
    else: 
                #print '�����ļ��У�%s' % (rootdir) 
                return 
         
#����ָ����ʽ���ļ�           
#if __name__ == '__main__': 
#        root=raw_input("��������Ŀ¼:") 
#        key=raw_input("������������ļ�������:") 
#        #newdir = raw_input("�ļ��и���Ϊ��") 
#        #serchDir(root,key) 
#        base="".join([root,key]) 
#        fileName=raw_input("������Ҫ���ҵ��ļ����ƻ��׺��:") 
#        for result in find_file_by_pattern(fileName,base): 
#                print result


#���Ҫ����ָ�����ֵ��ļ�ֻ��Ҫ�����´���ע�ͼ���
#if full_path.endswith(pattern):#����д�ɵ����ţ������Ŵﲻ��Ԥ�ڵ�Ч�� 
#...... 
#...... 
#...... 
#else: 
#                        continue

def find_file_by_pattern(env, pattern, base):     
#pattern: ���ҵ��ļ����ƻ��׺��
#base: ����Ŀ¼ + ���������ļ�������
    #'''''���Ҹ����ļ����������� '''     
    re_file = re.compile(pattern)        
    #if base == ".":        
    #    base = os.getcwd()        
                        
    final_file_list = []        
    #print base      
    env.log.debug('find_file_by_pattern: base=(%s) ', base)
    env.log.debug('find_file_by_pattern: pattern=(%s) ', pattern)
    cur_list = os.listdir(base) 
    env.log.debug('find_file_by_pattern: cur_list=(%s) ', cur_list)
    for item in cur_list:        
        #print item
        env.log.debug('find_file_by_pattern: item=(%s) ', item)
        full_path = os.path.join(base, item)        
        if full_path.endswith(pattern):#����д�ɵ����ţ������Ŵﲻ��Ԥ�ڵ�Ч��                                         
                # print full_path        
                        #bfile = os.path.isfile(item) 
            if os.path.isfile(full_path): 
                if re_file.search(full_path): 
                                 #print re_file.search(full_path).group()
                     env.log.debug('find_file_by_pattern: search=(%s) ', re_file.search(full_path).group())
                     final_file_list.append(full_path)        
            #else:        
            #    final_file_list += find_file_by_pattern(pattern,full_path) 
            #    #for filename in re_file.findall(final_file_list): 
            #         # print filename 
        else: 
            continue 
    return final_file_list 

def serchDir(startdir,dirname): 
    search(startdir,dirname)         


      
def _show_current_time():
    current = datetime.utcnow()
    current = current.isoformat()
    current_int = int(_format_datetime(current))  
    current = format_datetime(current_int)  
    return current

def _get_current_time_str():
    polling_time = _show_current_time() 
    polling_times1 = polling_time.split(' ',polling_time.count(' '))
                    
    polling_times2 = polling_times1[0].split('/',polling_times1[0].count('/'))
    polling_times3 = polling_times1[1].split(':',polling_times1[1].count(':'))

    time = '2013'+polling_times2[0]+polling_times2[1]+polling_times3[0]+polling_times3[1]+polling_times3[2]
    return time 

def curtime_string():
        from datetime import datetime
        
        Now = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        return Now

def _get_current_int_time():
    current = datetime.utcnow()
    current = current.isoformat()
    current_int = int(_format_datetime(current))  
    return current_int    

def _format_datetime(string):
    """Minimal parser for ISO date-time strings.
    
    Return the time as floating point number. Only handles UTC timestamps
    without time zone information."""
    try:
        string = string.split('.', 1)[0] # strip out microseconds
        return calendar.timegm(time.strptime(string, '%Y-%m-%dT%H:%M:%S'))
    except ValueError, e:
        raise ValueError('Invalid ISO date/time %r' % string)

def _copy_file(env, src_file, dest_file):     
    env.log.debug('_copy_file: + src(%s), dest(%s) ', src_file, dest_file)
    if os.path.exists(dest_file):         
        os.unlink(dest_file) 
        env.log.debug('_copy_file: + unlink:if dest(%s) ', dest_file)
    else:
        env.log.debug('_copy_file: + unlink:else dest(%s) ', dest_file)
    #shutil.copy2(src_file, dest_file) 
    shutil.copy(src_file, dest_file) 
    env.log.debug('_copy_file: + copy:dest(%s) ', dest_file)
    env.log.debug('_copy_file: - src(%s), dest(%s) ', src_file, dest_file)

def _remove_file(env,filename): 
    if os.path.exists(filename):
        try:
            os.remove(filename)
            env.log.debug('_remove_file: suc %s',filename)
        except Exception, e:
            env.log.warning("_remove_file: Error removing filename %s: %s" % (filename, e))
    else:
        env.log.debug('_remove_file: %s',filename)


def _get_filesize(env, filepath):     
    env.log.error('_get_filesize: filepath(%s)', filepath)
    if os.path.exists(filepath):         
        size = os.path.getsize(filepath) 
        env.log.error('_get_filesize: size(%s)', size)
        return size
    else:
        return 0
 
                    
def get_file_dir(env, father_dir, filename):
    if filename != os.path.basename(filename):
        raise ValueError("Filename may not contain path: %s" % (filename,))
    return os.path.join(father_dir, filename)

def get_itest_log_dir(env):
    #'/trac/Projects/iTest/log'
    return gl.gl_prj_log_root

def get_network_test_xml_dir(env):
    #'\\\\itest-center\\share\\test_xml' 
    return gl.gl_win_testcaselist_root
    

def get_test_xml_dir(env):
    return gl.gl_testcaselist_root     

def get_test_list_model_dir(env):
    #'/home/share/test_list_model'
    return gl.gl_testcasemodel_root


def trans_case_from_txt_to_xml(txt_file_name, xml_file_name,  \
                        testname='NULL', version_num=None):                
    #back_txt_file_name = xml_file_name.replace('.xml','.txt')  
    
    model_list_data = slave_utils.read_file(txt_file_name)
    model_list_data = model_list_data.replace('Save by tool\r\n','')  

    #���ȥ���ո�
    model_list_data = model_list_data.replace(' ','')

    #���ȥ���ո�\t
    model_list_data = model_list_data.replace('\t','')

    #���ͬʱ���б�һ������
    while True:
        nums = model_list_data.count('\r\n\r\n')
        if nums == 0:
            break
        else:
            model_list_data = model_list_data.replace('\r\n\r\n','\r\n')    
            
    #��txt_file_name����һ��ͬ����
    #write_file(back_txt_file_name, model_list_data)  
    
    model_list_data = model_list_data.replace('\n','</case>\n<case>\n') 
    caselist_file_data = '<Task desc="' + testname + '">\n<Cases>\n<case>\n'
    caselist_file_data += model_list_data  
    caselist_file_data += '\r</case>\n</Cases>\n</Task>'  

    #���һ������Ļ���
    caselist_file_data = caselist_file_data.replace('<case>\n</case>\n','')            
    
    caselist_file_data = caselist_file_data.replace('<case>\n\r</case>\n','')  
    slave_utils.write_file(xml_file_name,caselist_file_data)
            

def del_xml_caselist(env, caselist_file):          
    xml_file = get_file_dir(env, get_test_xml_dir(env), caselist_file)
    #env.log.debug('del_xml_caselist: %s',xml_file)
    _remove_file(env, xml_file)



def name_filter_dirty_symbol(env, name):  
    #�����в�Ҫ���ո�,\,/,<,>,|,:����Щ�ַ�
    env.log.error('name_filter_dirty_symbol: name1=%s', name)
    ret_name = makefilter(env, name)
    env.log.error('name_filter_dirty_symbol: name2=%s', ret_name)
    return ret_name

import string 
allchars = string.maketrans('', '')  
keep = string.digits + string.letters + '._'
def makefilter(env, name):
    """ ����һ���������˷��غ�������һ���ַ���Ϊ����  
    �������ַ�����һ�����ֿ������˿���ֻ������  
    keep �е��ַ���ע��keep ������һ����ͨ�ַ���  
    """     
    
    #name = string.maketrans('', '')  
    #���ˡ�0-9a-fA-F._��֮����ַ����ᵥʱitest����Ҫ����    
    
    #env.log.error('makefilter: keep=%s', keep)
    #env.log.error('makefilter: allchars=%s', allchars)
    # ����һ�������в���keep �е��ַ���ɵ��ַ�����keep �Ĳ�����������������Ҫɾ�����ַ�  

    delchar = name.translate(allchars, keep) 
    #delchar = name.translate(keep) 
    #delchar = name.translate(name, keep) 
    env.log.error('makefilter: delchar=%s', delchar)
    # ���ɲ�������Ҫ�Ĺ��˺���

    remain = name.translate(allchars, delchar)
    #remain = name.translate(name, delchar)
    env.log.error('makefilter: remain=%s', remain)
    return remain
    
def checknums(env, a):
    import string
    nums = string.digits
    #env.log.error('checknums: %s, a=%s', nums, a)
    #if type(a) is not str:
    #    env.log.error('checknums1: %s, a=%s', nums, a)
    #    return False
    #else:
    if 1:
        for i in a:
            if i not in nums:
                #env.log.error('checknums2: %s, a=%s', nums, a)
                return False
                
        return True


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
        msg = MIMEText(html, 'html') #实例化为html部分
        #html_part = MIMEText(html, "plain", "utf-8")
        #html2_part = MIMEText(html, "html", "utf-8")
        
        #msg.set_charset('utf-8') #设置编码
        msg['Subject'] = Subject
        msg['From'] = sender #使用国际化编码
        
        
        #html = open('html.tpl').read() #读取HTML模板        
        #html_part = MIMEText(html,'html') 
        #html_part.set_charset('utf-8') #设置编码
        #msg.attach(html_part) #绑定到message里 
        #msg.attach(html2_part)
        try:
            s = smtplib.SMTP('172.16.0.25') #登录SMTP服务器,发信
            for rcpt in rcpts:
                if rcpt != '':
                    rcpt = rcpt+'@spreadtrum.com'
                    msg['To'] = rcpt
                    env.log.error('sendmail rcpt = %s',rcpt)
                    s.sendmail(sender,rcpt,msg.as_string())
        except Exception,e:
            env.log.exception("Failure sending notification "
                               "%s", e) 
           

#递归搜索函数 
def search(env, rootdir,searchdirname): 
    if os.path.isdir(rootdir): 
                #print rootdir 
                #分离路径和文件夹 
                split1 = os.path.split(rootdir) 
                #print split1[1] 

                #判断是否为指定的文件夹 
                if split1[1] == searchdirname: 
                        print "找到文件夹：%s" % (rootdir) 
                        try: 
                                #将文件夹名称改为新的文件夹名称 
                                os.rename(rootdir,split1[0]+"\\"+newdir) 
                                print "文件夹 [%s] 已改名为 [%s]" % (rootdir,newdir) 
                        except: 
                                pass 

                #遍历指定文件夹下的内容（文件和文件夹列表） 
                listnew = os.listdir(rootdir) 

                for l1 in listnew: 
                        path = rootdir + "\\" + l1 
                        #递归调用 
                        search(path,searchdirname) 
    else: 
                #print '不是文件夹：%s' % (rootdir) 
                return 
         
#搜索指定格式的文件           
#if __name__ == '__main__': 
#        root=raw_input("输入搜索目录:") 
#        key=raw_input("输入待搜索的文件夹名称:") 
#        #newdir = raw_input("文件夹改名为：") 
#        #serchDir(root,key) 
#        base="".join([root,key]) 
#        fileName=raw_input("请输入要查找的文件名称或后缀名:") 
#        for result in find_file_by_pattern(fileName,base): 
#                print result


#如果要查找指定名字的文件只需要将以下代码注释即可
#if full_path.endswith(pattern):#不能写成单引号，单引号达不到预期的效果 
#...... 
#...... 
#...... 
#else: 
#                        continue

def find_file_by_pattern(env, pattern, base):     
#pattern: 查找的文件名称或后缀名
#base: 搜索目录 + 待搜索的文件夹名称
    #'''''查找给定文件夹下面所有 '''     
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
        if full_path.endswith(pattern):#不能写成单引号，单引号达不到预期的效果                                         
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

    #多个去掉空格
    model_list_data = model_list_data.replace(' ','')

    #多个去掉空格\t
    model_list_data = model_list_data.replace('\t','')

    #多个同时换行变一个换行
    while True:
        nums = model_list_data.count('\r\n\r\n')
        if nums == 0:
            break
        else:
            model_list_data = model_list_data.replace('\r\n\r\n','\r\n')    
            
    #将txt_file_name备份一个同名的
    #write_file(back_txt_file_name, model_list_data)  
    
    model_list_data = model_list_data.replace('\n','</case>\n<case>\n') 
    caselist_file_data = '<Task desc="' + testname + '">\n<Cases>\n<case>\n'
    caselist_file_data += model_list_data  
    caselist_file_data += '\r</case>\n</Cases>\n</Task>'  

    #最后一个多余的换行
    caselist_file_data = caselist_file_data.replace('<case>\n</case>\n','')            
    
    caselist_file_data = caselist_file_data.replace('<case>\n\r</case>\n','')  
    slave_utils.write_file(xml_file_name,caselist_file_data)
            

def del_xml_caselist(env, caselist_file):          
    xml_file = get_file_dir(env, get_test_xml_dir(env), caselist_file)
    #env.log.debug('del_xml_caselist: %s',xml_file)
    _remove_file(env, xml_file)



def name_filter_dirty_symbol(env, name):  
    #名称中不要含空格,\,/,<,>,|,:等这些字符
    env.log.error('name_filter_dirty_symbol: name1=%s', name)
    ret_name = makefilter(env, name)
    env.log.error('name_filter_dirty_symbol: name2=%s', ret_name)
    return ret_name

import string 
allchars = string.maketrans('', '')  
keep = string.digits + string.letters + '._'
def makefilter(env, name):
    """ 返回一个函数，此返回函数接受一个字符串为参数  
    并返回字符串的一个部分拷贝，此拷贝只包含在  
    keep 中的字符，注意keep 必须是一个普通字符串  
    """     
    
    #name = string.maketrans('', '')  
    #除了【0-9a-fA-F._】之外的字符，提单时itest都需要报错    
    
    #env.log.error('makefilter: keep=%s', keep)
    #env.log.error('makefilter: allchars=%s', allchars)
    # 生成一个由所有不在keep 中的字符组成的字符串：keep 的补集，即所有我们需要删除的字符  

    delchar = name.translate(allchars, keep) 
    #delchar = name.translate(keep) 
    #delchar = name.translate(name, keep) 
    env.log.error('makefilter: delchar=%s', delchar)
    # 生成并返回需要的过滤函数

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


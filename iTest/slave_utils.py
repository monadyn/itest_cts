# -*- coding: utf-8 -*-
#
import gl
import os

import shutil
import calendar
import time

from StringIO import StringIO
from datetime import datetime



def _is_passlisttest(sub_testtype):
    if sub_testtype == gl.gl_PASSLIST_T \
                        or sub_testtype == gl.gl_PASSLIST:
        ret = True
    else:        
        ret = False
    return ret

def _is_fulltest(sub_testtype):
    if sub_testtype == gl.gl_FULL_TEST \
                        or sub_testtype == gl.gl_PASSLIST_T \
                        or sub_testtype == gl.gl_PASSLIST \
                        or sub_testtype == gl.gl_CUSTOM \
                        or sub_testtype == gl.gl_DUAL_L1_PASSLIST \
                        or sub_testtype == gl.gl_DUAL_L2_PASSLIST \
                        or sub_testtype == gl.gl_PASSLIST_CR:
        ret = True
    else:        
        ret = False
    return ret
 

def _is_svn_comm(buildtype):
    if buildtype == gl.gl_SVN_Comm:
        ret = True
    else:        
        ret = False
    return ret  

def read_file(file_name, mode='r'):
    """Read a file and return its content."""

    f = open(file_name, mode)
    try:
        return f.read()
    finally:
        f.close()

def write_file(file_name, data, mode='w'):    
    f = open(file_name, mode)
    try:
        if data:
            f.write(data)
    finally:
        f.close()

def copy_file(src_file, dest_file):    
    if os.path.exists(dest_file):         
        os.unlink(dest_file)        
    #shutil.copy2(src_file, dest_file) 
    shutil.copy(src_file, dest_file)

def check_file(file_path):     
    #if os.path.isfile(file_path)
    if os.path.exists(file_path):   
        ret = True
    else:
        ret = False
    #log.info('ret=%s',ret)  
    return ret


def check_string(string, key):     
    flag = string.count(key)
    if flag == 0:
        ret = False
    else: 
        ret = True
        
    return ret


    

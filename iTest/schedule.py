# -*- coding: utf-8 -*-
#

"""Schedule implementation."""


import os
import struct
import posixpath
import calendar
import re
import time
import socket
import thread
import urllib2

import gl
import utils
import slave_utils

from StringIO import StringIO
from datetime import datetime

from trac.util.translation import _, ngettext, tag_
from trac.util import escape, pretty_timedelta, format_datetime, shorten_line, \
                      Markup
from trac.attachment import Attachment
from trac.config import BoolOption, IntOption, Option
from trac.core import *
from trac.resource import ResourceNotFound
from trac.web import IRequestHandler, RequestDone
                              

class Schedule(object):
    def __init__(self, env):
        self.env = env
        self.log = env.log
        self.mskernel_flag = True
        self.arm_flag = True
        self.svr_env = utils.get_file_dir(self.env, utils.get_itest_log_dir(self.env), gl.gl_init_env) 
        self.t_dailybuild_flag = utils.get_file_dir(self.env, self.svr_env, gl.gl_auto_dailybuild_file_name)

    def condition(self):
        self.log.debug('condition +') 
        polling_time = utils._show_current_time()       
        polling_times1 = polling_time.split(' ',polling_time.count(' '))
        polling_times2 = polling_times1[0].split('/',polling_times1[0].count('/'))     
        #08/04/11 08:16:21
        #polling_times2[2] = 11
        
        cur_day = polling_times2[1]
        if os.path.isfile(self.t_dailybuild_flag):            
            #比较是否过了一天            
            record_day = slave_utils.read_file(self.t_dailybuild_flag)            
            self.log.debug('condition %s,%s', record_day, cur_day) 
            if record_day != cur_day:
                slave_utils.write_file(self.t_dailybuild_flag,cur_day)
                ret = True
            else:
                ret = False
        else:
            #第一次创建文件
            slave_utils.write_file(self.t_dailybuild_flag,cur_day)
            ret = True
        self.log.debug('condition - %s', ret) 
        return ret


    def trigger(self):
        self.log.debug('trigger +') 
        if self.condition() == True:  
            pass
            #thread.start_new_thread(db_backup, (self.env, 'haha'))
            #thread.start_new_thread(clearup_logins, (self.env, 'haha'))
            #thread.start_new_thread(dailybuild, (self.env, 'haha'))             
        self.log.debug('trigger -')

            

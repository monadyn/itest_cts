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
from iTest.model import Report, TManager

import gl
import rpc_server
import utils
import slave_utils
import itest_mmi_data
import test_model
                               


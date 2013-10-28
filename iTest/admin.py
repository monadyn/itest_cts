# -*- coding: utf-8 -*-
#


"""Implementation of the web administration interface."""

from pkg_resources import require, DistributionNotFound
import re
import socket
import thread
import rpc_server
import gl
import slave_utils
import utils

from trac.core import *
from trac.admin import IAdminPanelProvider
from trac.web.chrome import add_stylesheet, add_script, add_warning, add_notice
from genshi.builder import tag


class TestDebug(Component):
    """Web administration panel for configuring iTest."""

    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):        
        if req.perm.has_permission('BUILD_ADMIN'):
            yield ('bitten', 'iTest', 'configs', 'Debug')

    def render_admin_panel(self, req, cat, page, path_info):        
        data = {}

        # Analyze url
        try:
            config_name, platform_id = path_info.split('/', 1)
        except:
            config_name = path_info
            platform_id = None        
        
        if config_name: # Existing build config
            pass            	   
        else: # At the top level build config list
            if req.method == 'POST':                
                if 'debug' in req.args: # debug
                    self._debug(req)  
                    
                req.redirect(req.abs_href.admin(cat, page))
        return 'bitten_admin_configs.html', data

    # Internal methods
    def A_Remove(self, req):
        pass

    def _debug(self, req):
        import xlwt
        import utils
        from datetime import datetime
        import test_action

        utils._get_filesize(self.env, gl.gl_polling_time_file)
        utils._get_filesize(self.env, gl.gl_rpc_svr_polling_time_file)
        utils._get_filesize(self.env, gl.gl_auto_dailybuild_file)
        #import test_model
        #db_conn=test_model.sqldb()
        #a_test_obj = test_model.iTest(None, db_conn)     
        #a_test_obj.reset_field_testtype(db_conn)
        return 
        
        # Create workbook and worksheet
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('temperatures')

# Set up a date format style to use in the
# spreadsheet
        excel_date_fmt = 'M/D/YY h:mm'
        style = xlwt.XFStyle()
        style.num_format_str = excel_date_fmt

# Weather data has no year, so assume it's the current year.
        year = datetime.now().year

# Convert year to a string because we'll be
# building a date string below
        year = str(year)

# The format of the date string we'll be building
        python_str_date_fmt = '%d %b-%H%M-%Y'

        row = 0  # row counter
        col = 0
        f = ["product", "component", "bug_status", \
                        "bug_severity", "reporter", "assigned_to",\
                        "cf_come_from", "cf_base_on_ver", "cf_fix_on_ver", "changeddate"]

        for line in f:
            # Write the data, using the style defined above.
            sheet.write(row,col,line)
            col += 1
            
        sheet.write(row,col,"平台信息".decode('GBK'))
        

        if 0:    
        #for line in f:
            # separate fields by commas
            L = line.rstrip().split(',')

            # skip this line if all fields not present
            if len(L) < 12:
                continue

            # Fields have leading spaces, so strip 'em
            date = L[0].strip()
            time = L[2].strip()

            # Datatypes matter. If we kept this as a string
            # in Python, it would be a string in the Excel sheet.
            temperature = float(L[8])

    # Construct a date string based on the string
    # date format  we specified above
            date_string = date + '-' + time + '-' + year

    # Use the newly constructed string to create a
    # datetime object
            date_object = datetime.strptime(date_string,
                                    python_str_date_fmt)

            # Write the data, using the style defined above.
            sheet.write(row,0,date_object, style)
            sheet.write(row,1,temperature)

            row += 1

        wbk.save('/home/share/data2.xls')
  
        return 
        

            

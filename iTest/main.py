# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2007 Christopher Lenz <cmlenz@gmx.de>
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://bitten.edgewall.org/wiki/License.

import inspect
import os
import textwrap
import thread
import threading


from trac.attachment import ILegacyAttachmentPolicyDelegate
from trac.core import *
from trac.db import DatabaseManager
from trac.env import IEnvironmentSetupParticipant
from trac.perm import IPermissionRequestor
from trac.resource import IResourceManager
from trac.wiki import IWikiSyntaxProvider

#from bitten.api import IBuildListener
from iTest.api import IBuildListener

__all__ = ['iTestSystem']
__docformat__ = 'restructuredtext en'


class iTestSetup(Component):
    implements(IEnvironmentSetupParticipant)

    # IEnvironmentSetupParticipant methods
    def __init__(self):
        #创建文件环境
        #self.log.error('iTestSetup: init')  
        self.iTest_environment_created()
        
    def iTest_environment_created(self):
        import utils
        import gl
        import slave_utils
        
        test_xml_file_path = utils.get_test_xml_dir(self.env)
        if not os.path.exists(test_xml_file_path):  
            os.mkdir(test_xml_file_path) 

        test_list_model_file_path = utils.get_test_list_model_dir(self.env)
        if not os.path.exists(test_list_model_file_path):  
            os.mkdir(test_list_model_file_path) 

        init_env_dir = utils.get_file_dir(self.env, utils.get_itest_log_dir(self.env), gl.gl_init_env) 
        if not os.path.exists(init_env_dir):  
	        os.mkdir(init_env_dir)     
	    
        polling_time_file_name = utils.get_file_dir(self.env, init_env_dir, gl.gl_polling_time_file_name)  
        rpc_polling_time_file_name = utils.get_file_dir(self.env, init_env_dir, gl.gl_rpc_svr_polling_time_file_name) 

        slave_utils.write_file(polling_time_file_name,gl.gl_guardprocess_flag)    
        slave_utils.write_file(rpc_polling_time_file_name,gl.gl_guardprocess_flag) 
        
    def environment_created(self):
        pass
        
        # Create the required tables
        #db = self.env.get_db_cnx()
        #connector, _ = DatabaseManager(self.env)._get_connector()
        #cursor = db.cursor()
        #for table in schema:
        #    self.log.debug('environment_created: table %s', table)
        #    for stmt in connector.to_sql(table):
        #        cursor.execute(stmt)

        # Insert a global version flag
        #cursor.execute("INSERT INTO system (name,value) "
        #               "VALUES ('bitten_version',%s)", (schema_version,))

        # Create the directory for storing snapshot archives
        #snapshots_dir = os.path.join(self.env.path, 'snapshots')
        #os.mkdir(snapshots_dir)

        #db.commit()

    def environment_needs_upgrade(self, db):
        pass
        #cursor = db.cursor()
        #cursor.execute("SELECT value FROM system WHERE name='bitten_version'")
        #row = cursor.fetchone()
        #if not row or int(row[0]) < schema_version:
        #    self.log.debug('BuildSetup upgrade environment')
        #    return True
        #else:
        #    self.log.debug('BuildSetup not need upgrade environment')

    def upgrade_environment(self, db):
        pass
        
        #cursor = db.cursor()
        #cursor.execute("SELECT value FROM system WHERE name='bitten_version'")
        #row = cursor.fetchone()
        #if not row:
        #    self.environment_created()
        #else:
        #    cursor.execute("UPDATE system SET value=%s WHERE "
        #                   "name='bitten_version'", (schema_version,))

class iTestSystem(Component):

    implements(IPermissionRequestor,
               IWikiSyntaxProvider, IResourceManager,
               ILegacyAttachmentPolicyDelegate)

    listeners = ExtensionPoint(IBuildListener)

    # IPermissionRequestor methods
    def __init__(self):
        pass
        
    def get_permission_actions(self):
        actions = ['TEST_HIGHEST', 'TEST_FORMAL_VERSION',
                   'TEST_DAYLI_VERSION', 'MP', 'BASE', 'CR', 'DB']
        return actions + [('BUILD_ADMIN', actions)]

    # IWikiSyntaxProvider methods

    def get_wiki_syntax(self):
        return []

    def get_link_resolvers(self):
        def _format_link(formatter, ns, name, label):
            try:
                name = int(name)
            except ValueError:
                return label
            return label
        yield 'build', _format_link


    # IResourceManager methods
    
    def get_resource_realms(self):
        yield 'build'

    def get_resource_url(self, resource, href, **kwargs):
        config_name, build_id = self._parse_resource(resource.id)
        return href.build(config_name, build_id)


    def _parse_resource(self, resource_id):
        """ Returns a (config_name, build_id) tuple. """
        r = resource_id.split('/', 1)
        if len(r) == 1:
            return r[0], None
        elif len(r) == 2:
            try:
                return r[0], int(r[1])
            except:
                return r[0], None
        return None, None

    # ILegacyAttachmentPolicyDelegate methods

    #def check_attachment_permission(self, action, username, resource, perm):
    #    """ Respond to the various actions into the legacy attachment
    #    permissions used by the Attachment module. """
    #    if resource.parent.realm == 'build':
    #        if action == 'ATTACHMENT_VIEW':
    #            return 'BUILD_VIEW' in perm(resource.parent)
    #        elif action == 'ATTACHMENT_CREATE':
    #            return 'BUILD_MODIFY' in perm(resource.parent) \
    #                    or 'BUILD_CREATE' in perm(resource.parent)
    #        elif action == 'ATTACHMENT_DELETE':
    #            return 'BUILD_DELETE' in perm(resource.parent)

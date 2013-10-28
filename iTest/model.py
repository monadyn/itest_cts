# -*- coding: utf-8 -*-
#


"""Model classes for objects persisted in the database."""

from trac.attachment import Attachment
from trac.db import Table, Column, Index
from trac.resource import Resource
from trac.util.text import to_unicode
import codecs
import os
import shutil

import gl
import MySQLdb
 

__docformat__ = 'restructuredtext en'   

def sqldb():
    #db=MySQLdb.connect(host='172.16.0.230',port=3306,user='ibuildadmin', passwd='SPD#ibuildapp', db='ibuild',charset='utf8')
    db=MySQLdb.connect(host='10.0.0.175',port=3306,user='ilogadmin', passwd='SPD@ilogservice99', db='ilog',charset='utf8')
    return db
      


class Report(object):
    ###################Test###################
#id   build (name)        step      category  generator started   stopped   versionpath 
#3764 xiang.sun_cr118426 xiang.sun TestFinish CR_TEST 1314685113 1314686126 \\...\Version\iTest_center_build4092 

#version_num       tmanager subtmanager   passed failed total 
#DM_BASE_W11.34     HSIT    dspversion    50     1    sub_testtype        

#reserved4       reserved5                reserved6               reserved7  	reserved8 
#special_perity  versionorigins           xmlfile_path            result_path 	platinfo

#ueitreruntimes  

#testtype: waiting time

    db_type = gl.gl_mysql
    _schema = [
        Table('CTSTestSheet', key='id')[
            Column('id', auto_increment=True), Column('build', type='int'),
            Column('step'), Column('category'), Column('generator'), 
            Column('started', type='int'), Column('stopped', type='int'),
            Column('versionpath'), Column('version_num'), Column('testtype', type='int'), 
            Column('tmanager'), Column('subtmanager'), Column('ueitreruntimes'), 
            Column('passed'), Column('failed'), Column('total'), 
            Column('reserved4'), Column('reserved5'), Column('reserved6'), 
            Column('reserved7'), Column('reserved8'),             
            Index(['build', 'step', 'category'])
        ]           
    ]

    # Test status codes
    CREATED = 'TestCreated'
    WAIT_VERSION = 'TestWaitingVersion'
    VERSION_READY = 'TestVersionReady'
    READY = 'TestReady'
    IN_PROGRESS = 'TestInProgress'
    WAIT_STOP = 'TestWaitingStop'
    STOPANDDELETE = 'TestStopAndDelete'
    STOPPED = 'TestStopped'
    DONE = 'TestFinish'
    ERROR = 'TestError'
    
    def __init__(self, env=None, build=None, step=None, category=None,
                 generator=None, versionpath='', caselist=None, version_num='',
                 tmanager = '', subtmanager = '',reserved6=None, reserved4=None,reserved5=None):
        """Initialize a new report with the specified attributes.

        To actually create this build log in the database, the `insert` method
        needs to be called.
        """        
        self.env = env
        self.id = None
        self.build = build
        self.step = step
        self.category = category
        self.generator = generator or ''
        self.items = []          
        self.caselist = caselist  
        
        self.name = ''
        self.creator = ''        
        self.priority = ''
        self.status = ''
        self.versionpath = versionpath
        self.version_num = version_num
        #self.type = ''
        self.started = 0
        self.stopped = 0
        self.waiting_time = 0
        
        self.passed = '0'
        self.failed = '0'
        
        self.total = '' 
        self.tmanager = tmanager 
        self.reserved6 = reserved6
        self.test_type = self.tmanager
        
        self.test_subtype = self.total
        self.xmlfile = self.reserved6
        
        self.subtmanager = subtmanager
        
        self.reserved7 = '' #ower
        self.reserved8 = '' #plan_time

        self.reserved4 = reserved4
        self.reserved5 = reserved5

        self.ueitreruntimes = '' #rerun_times         

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.id)


    new_resource = property(fget=lambda self: Resource('build', '%s' % self.build),
                        doc='test Config resource identification')                        
    
    resource = property(fget=lambda self: Resource('test', '%s' % (self.id)),
                        doc='Test resource identification')

    exists = property(fget=lambda self: self.id is not None,
                      doc='Whether this report exists in the database')                                 
       
    def delete(self, db=None, check_last_flag=False):
        assert self.exists, 'Cannot delete a non-existing report'
        db = sqldb()

        if check_last_flag == True:
            #如果是最后一个，不允许删除，RRM拷贝不能覆盖。
            #last_tests = self.select(self.env, is_run_waiting_queue=True)
            last_tests = self.select()
            for test in last_tests:
                lasttest_id = test.id
                break
            
            if int(lasttest_id) == int(self.id):
                #self.env.log.debug("delete: is last %s",lasttest_id)
                return False
        
        cursor = db.cursor()
        cursor.execute("DELETE FROM CTSTestSheet WHERE id=%s", (self.id,))

        db.commit()
        self.id = None

        return True

    def insert(self, db=None):
        db = sqldb()
        assert self.build and self.step     

        cursor = db.cursor()
        cursor.execute("INSERT INTO CTSTestSheet "
                       "(build,step,category,generator,started,stopped,versionpath,"
                       "version_num,testtype,passed,failed,total,tmanager,subtmanager,"
                       "reserved4,reserved5,reserved6,reserved7,reserved8,ueitreruntimes) "
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                       (self.build, self.step, self.status, self.generator, \
                       self.started,self.stopped,self.versionpath, \
                       self.version_num, self.waiting_time, self.passed,self.failed, \
                       self.total,self.tmanager,self.subtmanager, \
                       self.reserved4, self.reserved5, \
                       self.reserved6,self.reserved7,self.reserved8,self.ueitreruntimes))                        

        #      
        db.commit()
        id = cursor.lastrowid #db.get_last_id(cursor, 'CTSTestSheet') 
        self.name = self.build
        self.id = id


    def fetch(cls, env=None, id=None, name=None, db=None):
        db = sqldb()
        cursor = db.cursor()
        
        if id is not None:  
            cursor.execute("SELECT build,step,category,generator,versionpath,"
                       "version_num,testtype,started,stopped,passed,failed,"
                       "total,tmanager,subtmanager,reserved7,"
                       "reserved8,ueitreruntimes,reserved6,reserved4,reserved5 "
                       "FROM CTSTestSheet WHERE id=%s", (id,))     
        elif name is not None:        
            cursor.execute("SELECT build,step,category,generator,versionpath,"
                       "version_num,testtype,started,stopped,passed,failed,"
                       "total,tmanager,subtmanager,reserved7,"
                       "reserved8,ueitreruntimes,reserved6,reserved4,reserved5,id "
                       "FROM CTSTestSheet WHERE build=%s", (name,))   
        else:
            return None   

        row = cursor.fetchone()
        if not row:
            return None

        report = Report(env=env)

        report.name = row[0]
        report.creator = row[1]
        report.status = row[2]
        report.priority = row[3]  

        report.versionpath = row[4]                     
        report.version_num =  row[5]  
        report.waiting_time = row[6]
        report.started = row[7]  
        report.stopped = row[8] 
        
        report.passed = row[9]
        report.failed = row[10]
        report.total = row[11]
        report.tmanager = row[12]
        report.subtmanager = row[13]
        
        report.reserved7 = row[14]
        report.reserved8 = row[15]
        
        report.ueitreruntimes = row[16]
        report.reserved6 = row[17]
        report.reserved4 = row[18]
        report.reserved5 = row[19]
        
        if id is not None:  
            report.id = id  
        elif name is not None:  
            report.id = row[20]     

        report.build = report.name
        report.step = report.creator
        report.generator = report.priority
        report.category = report.status
        
        report.test_type = report.tmanager
        report.test_subtype = report.total
        report.xmlfile = report.reserved6        

        return report

    fetch = classmethod(fetch)

    def select(cls, env=None, config=None, build=None, step=None, category=None,
               generator=None, tmanager=None, subtmanager=None, total=None, db=None, is_run_waiting_queue=False,
               min_id=None, max_id=None):
        """Retrieve existing reports from the database that match the specified
        criteria.
        """
        where_clauses = []
        joins = []
        if config is not None:
            where_clauses.append(("config=%s", config))
            joins.append("INNER JOIN bitten_build ON (bitten_build.id=build)")
        if build is not None:
            where_clauses.append(("build=%s", build))
        if step is not None:
            where_clauses.append(("step=%s", step))
        if category is not None:
            where_clauses.append(("category=%s", category))
        if generator is not None:
            where_clauses.append(("generator=%s", generator))     
        if tmanager is not None:
            where_clauses.append(("tmanager=%s", tmanager))            
        if subtmanager is not None:
            where_clauses.append(("subtmanager=%s", subtmanager))  
        if total is not None:
            where_clauses.append(("total=%s", total))              
        if min_id is not None:
            where_clauses.append(("id>=%s", min_id ))
        if max_id is not None:
            where_clauses.append(("id<=%s", max_id))


        if where_clauses:
            where = "WHERE " + " AND ".join([wc[0] for wc in where_clauses])
        else:
            where = ""

        db = sqldb()
        cursor = db.cursor()

        if is_run_waiting_queue == True:
            cursor.execute("SELECT CTSTestSheet.id FROM CTSTestSheet %s %s "
                       "ORDER BY id Asc" % (' '.join(joins), where),
                       [wc[1] for wc in where_clauses])   
        else:
            cursor.execute("SELECT CTSTestSheet.id FROM CTSTestSheet %s %s "
                       "ORDER BY id Desc" % (' '.join(joins), where),
                       [wc[1] for wc in where_clauses])              

        for (id, ) in cursor:
            yield Report.fetch(env=env, id=id, db=db)

    select = classmethod(select)


    def update(self, db=None, id=None, name=None):
        db = sqldb()
        cursor = db.cursor() 

        if name is not None:        
            cursor.execute("UPDATE CTSTestSheet SET id=%s, build=%s, step=%s,"
                       "category=%s,generator=%s,started=%s,stopped=%s,"
                       "passed=%s,failed=%s,total=%s,tmanager=%s,"
                       "subtmanager=%s,versionpath=%s,version_num=%s,"
                       "testtype=%s,reserved7=%s,reserved8=%s,"
                       "ueitreruntimes=%s,reserved6=%s,reserved4=%s,reserved5=%s WHERE build=%s",
                       (self.id, self.build, self.step, self.status, self.generator, \
                       self.started, self.stopped,self.passed,self.failed, \
                       self.total,self.tmanager,self.subtmanager, \
                       self.versionpath,self.version_num,self.waiting_time, \
                       self.reserved7,self.reserved8, \
                       self.ueitreruntimes,self.reserved6, \
                       self.reserved4,self.reserved5, \
                       name))    
        else:
            cursor.execute("UPDATE CTSTestSheet SET build=%s, step=%s,"
                       "category=%s,generator=%s,started=%s,stopped=%s,"
                       "passed=%s,failed=%s,total=%s,tmanager=%s,"
                       "subtmanager=%s,versionpath=%s,version_num=%s,"
                       "testtype=%s,reserved7=%s,reserved8=%s,"
                       "ueitreruntimes=%s,reserved6=%s,reserved4=%s,reserved5=%s WHERE id=%s",
                       (self.build, self.step, self.status, self.generator, \
                       self.started, self.stopped,self.passed,self.failed, \
                       self.total,self.tmanager,self.subtmanager, \
                       self.versionpath,self.version_num,self.waiting_time, \
                       self.reserved7,self.reserved8, \
                       self.ueitreruntimes,self.reserved6, \
                       self.reserved4,self.reserved5, \
                       self.id)) 
                       
        db.commit()



class TManager(object):
    """TManager for a test Manager."""
    db_type = gl.gl_mysql
#id   name          type ip            port       active connect_status inprogress_test test_status reserved1 reserved2 reserved3 
#    RDIT_MANAGER1  RDIT 172.16.15.101 1317265935 Yes   reserved                          1                  SINGLE_SIM    0  
#    RDIT_MANAGER1  RDIT 172.16.15.101 1317265935 Yes   mutil_status     mutil_inP_tests  1                  SINGLE_SIM    0  
    _schema = [
            Table('TManager', key=('id', 'name'))[
                Column('id', auto_increment=True),Column('name'),Column('type'),
                Column('ip'),Column('port', type='int'),
                Column('active'),Column('connect_status'),
                Column('inprogress_test'),Column('test_status', type='int'),
                Column('reserved1'),Column('reserved2'),
                Column('reserved3', type='int')
            ]
    ]
    
    def __init__(self, env=None, name=None, type=None, ip=None, \
                    port=0, active=None, connect_status=None, \
                    inprogress_test=None, test_status=0,  \
                    reserved2=None, reserved3=0):        
        self.env = env          
        
        self.id = None
        self.name = name
        self.type = type 
        
        self.ip = ip
        self.port = port
        self.active = active
        
        self.connect_status = connect_status        
        self.inprogress_test = inprogress_test
        self.test_status = test_status 
        
        self.reserved1 = ''
        if reserved2 != None:
            self.reserved2 = reserved2
        else:
            self.reserved2 = 'itest'#默认itest
        self.reserved3 = reserved3               
        
    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.id)

    exists = property(fget=lambda self: self.id is not None,
                      doc='Whether this TManager exists in the database')


    def delete(self, db=None):
        db = sqldb()

        cursor = db.cursor()
        cursor.execute("DELETE FROM TManager WHERE name=%s", (self.name,))

        db.commit()              

    def insert(self, db=None):
        """Insert a new TManager into the database."""
        db = sqldb()

        #assert not self.exists, 'Cannot insert existing target platform'
        #assert self.config, 'Target platform needs to be associated with a ' \
        #                    'configuration'
        #assert self.name, 'Target platform requires a name'

        cursor = db.cursor()       
        cursor.execute("INSERT INTO TManager "
                       "(name,type,ip,port,active,connect_status,inprogress_test,test_status,reserved1,reserved2,reserved3) "
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", 
                       (self.name,self.type,self.ip, \
                       self.port,self.active,self.connect_status, \
                       self.inprogress_test,self.test_status,self.reserved1, \
                       self.reserved2,self.reserved3))
                       
        #self.id = db.get_last_id(cursor, 'TManager')
        db.commit()
    
    def update(self, db=None):
        assert self.name, 'TManager requires a name'
        db = sqldb()

        cursor = db.cursor()
        cursor.execute("UPDATE TManager SET name=%s,type=%s,ip=%s,"
                       "port=%s,active=%s,connect_status=%s,inprogress_test=%s,"
                       "test_status=%s,reserved1=%s,reserved2=%s,reserved3=%s WHERE name=%s",
                       (self.name, self.type, self.ip,int(self.port),
                        self.active, self.connect_status, self.inprogress_test,
                        self.test_status, self.reserved1,self.reserved2,self.reserved3, self.name))                        
        db.commit()
        
        
    def fetch(cls, env=None, name=None, db=None):
        db = sqldb()

        cursor = db.cursor()
        cursor.execute("SELECT type,ip,port,active,connect_status,inprogress_test,test_status,reserved1,reserved2,reserved3"
                       " FROM TManager WHERE name=%s", (name,))
        row = cursor.fetchone()
        if not row:
            return None

        tManager = TManager(env=env)
        #name, type,ip,port,active,connect_status,inprogress_test,test_status,reserved1,reserved2,reserved3
        tManager.name = name
        tManager.type = row[0] or ''
        tManager.ip = row[1] or ''
        tManager.port = int(row[2]) or 0
        tManager.active = row[3] or None
        tManager.connect_status = row[4] or None
        tManager.inprogress_test = row[5] or ''
        tManager.test_status = row[6] or ''
        tManager.reserved1 = row[7] or None
        tManager.reserved2 = row[8]
        tManager.reserved3 = int(row[9]) or 0
        return tManager

    fetch = classmethod(fetch)    

    def select(cls, env=None, name=None, type=None, db=None):
        db = sqldb()

        cursor = db.cursor()
        if name is not None:
            if type is not None:
                cursor.execute("SELECT name, type,ip,port,active,connect_status,inprogress_test,test_status,"
                           "reserved1,reserved2,reserved3 FROM TManager "
                           "WHERE name=%s,type=%s ORDER BY name", (name,type,))                 
            else:
                cursor.execute("SELECT name, type,ip,port,active,connect_status,inprogress_test,test_status,"
                           "reserved1,reserved2,reserved3 FROM TManager "
                           "WHERE name=%s ORDER BY name", (name,))                           
        else:
            if type is not None:
                cursor.execute("SELECT name, type,ip,port,active,connect_status,inprogress_test,test_status,"
                           "reserved1,reserved2,reserved3 FROM TManager "
                           "WHERE type=%s ORDER BY name", (type,))   
            else:
                cursor.execute("SELECT name, type,ip,port,active,connect_status,inprogress_test,test_status,"
                           "reserved1,reserved2,reserved3 FROM TManager "
                           "ORDER BY name")
                               
        #name, type,ip,port,active,connect_status,inprogress_test,test_status,reserved1,reserved2,reserved3
        for name, type,ip,port,active,connect_status,inprogress_test,test_status, \
                reserved1,reserved2,reserved3 in cursor:
            tManager = TManager(env=env, name=name,type=type,ip=ip,port= port,
                                 active=active, connect_status=connect_status,
                                 inprogress_test=inprogress_test,
                                 test_status=test_status, reserved2=reserved2,reserved3=reserved3)
            yield tManager

    select = classmethod(select)




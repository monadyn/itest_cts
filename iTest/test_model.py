import re
import os
import MySQLdb
import shutil
import pickle

import base_model

 

__docformat__ = 'restructuredtext en'   

def sqldb():
    db=MySQLdb.connect(host='172.16.0.230',port=3306,user='ibuildadmin', passwd='SPD#ibuildapp', db='ibuild',charset='utf8')
    return db

class iTest(base_model.base):
    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'build', 'control':'input'})        
        self.fields.append({'name':'step', 'control':'input'})        
        self.fields.append({'name':'category', 'control':'input'})        
        self.fields.append({'name':'generator', 'control':'input'}) 
        
        self.fields.append({'name':'started', 'control':'input'})        
        self.fields.append({'name':'stopped', 'control':'input'})
        
        self.fields.append({'name':'versionpath', 'control':'input'})
        self.fields.append({'name':'version_num', 'control':'input'})        
        self.fields.append({'name':'testtype', 'control':'input'})  
        
        self.fields.append({'name':'tmanager', 'control':'input'})
        self.fields.append({'name':'subtmanager', 'control':'input'})
        self.fields.append({'name':'ueitreruntimes', 'control':'input'})        

        self.fields.append({'name':'passed', 'control':'input'}) 
        self.fields.append({'name':'failed', 'control':'input'}) 
        self.fields.append({'name':'total', 'control':'input'})  

        self.fields.append({'name':'reserved4', 'control':'input'}) 
        self.fields.append({'name':'reserved5', 'control':'input'}) 
        self.fields.append({'name':'reserved6', 'control':'input'}) 
        self.fields.append({'name':'reserved7', 'control':'input'}) 
        self.fields.append({'name':'reserved8', 'control':'input'}) 
        
        base_model.base.__init__(self, id, 'CTSTestSheet',self.fields, db)

    def reset_field_testtype(self, db_conn):
        a_test_obj = iTest(None, db_conn)
        QF = {}   
        rows = a_test_obj.select(QF)
        for Item in rows:
            ID = Item['ID']                    
            b_test_obj = iTest(ID, db_conn)  
            if b_test_obj['testtype'] is None:
                b_test_obj['testtype'] = ''
            if b_test_obj['testtype'] != '':
                b_test_obj['testtype'] = ''                
            b_test_obj.save_changes()




import re
import os
import MySQLdb
import shutil
import pickle

import base_model

__docformat__ = 'restructuredtext en'   

def sqldb():
    #db=MySQLdb.connect(host='172.16.0.230',port=3306,user='ibuildadmin', passwd='SPD#ibuildapp', db='ibuild',charset='utf8')
    db=MySQLdb.connect(host='10.0.0.175',port=3306,user='ilogadmin', passwd='SPD@ilogservice99', db='ilog',charset='utf8')
    return db



class TManager(base_model.base):
#id   name          type ip            port       active connect_status inprogress_test test_status reserved1 reserved2 reserved3 
#    RDIT_MANAGER1  RDIT 172.16.15.101 1317265935 Yes   reserved                          1                  SINGLE_SIM    0  

    def __init__(self, id, db):
        self.fields = []
        self.fields.append({'name':'name', 'control':'input'})
        
        self.fields.append({'name':'type', 'control':'input'})
        self.fields.append({'name':'ip', 'control':'input'})
        self.fields.append({'name':'port', 'control':'input'})        
        self.fields.append({'name':'active', 'control':'input'})
        
        self.fields.append({'name':'connect_status', 'control':'input'})
        self.fields.append({'name':'inprogress_test', 'control':'input'})
        self.fields.append({'name':'test_status', 'control':'input'})        
        self.fields.append({'name':'reserved1', 'control':'input'})  
        
        self.fields.append({'name':'reserved2', 'control':'input'})
        self.fields.append({'name':'reserved3', 'control':'input'})               
        base_model.base.__init__(self, id, 'TManager',self.fields, db)





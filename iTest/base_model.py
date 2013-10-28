# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

from trac.env import Environment
from trac.db import with_transaction

from datetime import datetime
from trac.core import TracError
from trac.resource import Resource, ResourceNotFound
from trac.util import embedded_numbers, partition
from trac.util.text import empty
from trac.util.datefmt import from_utimestamp, to_utimestamp, utc, utcmax
from trac.util.translation import _
from trac.versioncontrol.diff import  unified_diff

class base(object):

    def __init__(self, id, table_name,fieldlist, db):
        self.table_name = table_name
        self.fields = fieldlist
        self.db = db
        self.values={}
        self._old = {}
        self.ID = None
        if id:
            self._fetch(id)
            self.ID = id
            
    def _fetch(self, stc_id):
        row = None
        std_fields = [f['name'] for f in self.fields if f['control'] != 'list'] 
        cursor = self.db.cursor()
        sql = "SELECT %s FROM " % ','.join(std_fields )
        sql = sql + self.table_name + ' '
        sql = sql + ' WHERE ID=' + stc_id
        cursor.execute(sql)
        
        row = cursor.fetchone()
        if not row:
            raise ResourceNotFound(_('%(ID)s does not exist.',  id=stc_id), _('Invalid number'))
        self.ID = stc_id
        for i, field in enumerate(std_fields):
            value = row[i]
            if value is None:
                self.values[field] = empty
            else:
                self.values[field] = value
        self.values['ID'] = stc_id

    def __getitem__(self, name):
        return self.values.get(name)

    def __setitem__(self, name, value):
        if name in self.values  and self.values[name] and self.values[name]== value: 
            return
            
        if name in self.values and unicode(self.values[name]) == unicode(value) : 
            return

        if name not in self._old: # Changed field
            self._old[name] = self.values.get(name)
        elif self._old[name] == value: # Change of field reverted
            del self._old[name]
        self.values[name] = value

    def insert(self, ):
        values = dict(self.values)
        std_fields = []
        for f in self.fields :
            if f['control'] != 'list':
                fname = f['name']
                if fname in values :
                    std_fields.append(fname)
        stc_id = None
        cursor = self.db.cursor()

        cursor.execute("INSERT INTO " +   self.table_name + " (%s) VALUES (%s)"
                            % (','.join(std_fields),
                              ','.join(['%s'] * len(std_fields))),
                           [values[name] for name in std_fields])
        stc_id= str(cursor.lastrowid)
                
        self.db.commit()
        self.ID = stc_id
        self._old = {}
        return self.ID
        
    def save_changes(self, ):

        assert self.ID is not None, 'Cannot update！'

        if not self._old:
            return False # Not modified

        cursor = self.db.cursor()
        for name in self._old.keys():
            cursor.execute("UPDATE " +   self.table_name + " SET %s=%%s WHERE ID=%%s"  % name, (self.values[name], self.ID))
        self.db.commit()
    
        self._old = {}
        return True

    def delete(self, ):

        if self.ID:
            cursor = self.db.cursor()
            cursor.execute("DELETE from " +   self.table_name + "  WHERE ID=%s" , (self.ID, ))
            self.db.commit()
        return True
        
    def select(self, req_dict):
        AllRows=[]
        all_fileds = ['ID'] + [f['name'] for f in self.fields if f['control'] != 'list'] 
        
        where_str=' where 1=1  '

        cursor = self.db.cursor()
            
        for k, v in req_dict.iteritems():
            if k.startswith('field_') and v:
                control=''
                fieldname = k[6:]
                if len(v)>0:
                    if type(v)==type(list()):
                        where_str = where_str + ' and ' + fieldname  + ' in (\'' +  '\',\''.join(v)   + '\')'

                    elif type(v)==type(tuple()):
                        if type(v[0])==type(int()) or type(v[0])==type(float()):
                            where_str = where_str + ' and ' + fieldname  + ">=" + str(v[0]) + " and " + fieldname + "<=" +  str(v[1])
                        else:
                            where_str = where_str + ' and ' + fieldname  + ">='" + v[0] + "' and " + fieldname + "<='" +  v[1] + "'" 
                    else:
                            where_str = where_str + ' and ' + fieldname + "='" +  unicode(v) + "'"
        sql = "SELECT " + ','.join(all_fileds)  +  "  FROM  " +   self.table_name  + where_str + ' order by ID desc'
        assert sql is not None, sql
        cursor.execute(sql)
            
        for row in cursor:
            tmp={}
            if row:
                for i, field in enumerate(all_fileds) : 
                    if row[i]:
                        tmp[field]=unicode(row[i]).strip()
                    else :
                        tmp[field]=''
            AllRows.append(tmp)
        return AllRows

    @classmethod
    def Get_Query_List(self,mydic, my_field_name):
        result = []
        for k, v in mydic.iteritems():
            if k.startswith('field_') and v:
                fieldname = k[6:]
                if fieldname==my_field_name:
                    if type(v)!=type(list()):
                        result=[v]
                    else:
                        result=v
        return result

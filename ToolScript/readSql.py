# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 14:16:47 2022

@author: admin
"""

import re
import pyodbc
import pandas as pd
from tqdm.notebook import trange
from sqlalchemy import create_engine


class sql_tool:
    
    def __init__(self, database_name):
        self.DATABASE = database_name
        self.cnxn = None
        self.cursor = None
        self.server = '127.0.0.1'
        self.user = 'sa'
        self.password = '123456'
        self.engine = create_engine('mssql+pymssql://{}:{}@{}/{}' .format(self.user, self.password, self.server, self.DATABASE))
        
    def connect(self):
        sql = 'DRIVER={SQL Server};SERVER=DESKTOP-4TPSKDV;DATABASE=%s;UID=sa;PWD=123456' % self.DATABASE
        self.cnxn = pyodbc.connect(sql)
        self.cursor = self.cnxn.cursor()
    
    def shudown(self):
        self.cnxn.close()
    
    def get_table(self, table_name, is_show=False):
        self.connect()
        self.cursor.execute("select * from {}" .format(table_name))
        
        data = self.cursor.fetchall()
        columnDes = self.cursor.description
        columnNames = [columnDes[i][0] for i in range(len(columnDes))]
        df = pd.DataFrame([list(i) for i in data],columns=columnNames)
        self.shudown()
        if is_show:
            print('{}表读出成功!' .format(table_name))
        
        return df
    
    def to_sql(self, df, table_name, mothod='replace', is_show=True):
        '''
        数据量大时，不要使用该方法(超过2G的数据使用批量传入)
        '''
        df.to_sql(table_name, self.engine, if_exists=mothod, index=False)
        if is_show:
            print('{}表已存入Sql Server!' .format(table_name))
        pass
    
    def big_to_sql(self, df, table_name, epoch=10000):
        '''
        针对大数据量的table使用该方法存入sql
        '''
        length = df.shape[0]
        
        for start in trange(0, length, epoch):
            end = start + epoch if start + epoch < length else length
            mothod = 'append' if start != 0 else 'replace'            
            tmp_df = df.iloc[start:end, :]
            self.to_sql(tmp_df, table_name, mothod, False)
        pass
        
    def TO_(self, string):
        while True:
            tmp_str = re.search(r"[^A-Za-z_0-9]",string) # 大小写字母、下划线、数字
            if tmp_str == None:
                break
            else:
                string = string.replace(tmp_str.group(),'__')
        return string
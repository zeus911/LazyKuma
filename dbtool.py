#!/usr/bin/env python
# coding:utf-8

import MySQLdb as mysql
from DBUtils.PooledDB import PooledDB
from tools import logstdout     # 导入自定义的logger模块
from conf import config         # 导入db配置文件
import traceback
import sys

logs = logstdout.WriteLog('db')

class DB(object):
    def __init__(self):
        self.host = config.db_host
        self.name = config.db_name
        self.user = config.db_user
        self.passwd = config.db_password
        self.pool = PooledDB \
            (mysql,mincache=4,maxcached=10,\
             host=self.host,db=self.name,user=self.user,passwd=self.passwd,\
             setsession=['SET AUTOCOMMIT=1'],charset="utf-8")

    def connect_db(self):
        self.db = self.pool.connection()
        self.cur = self.db.cursor()

    def close_db(self):
        self.cur.close()
        self.db.close()

    def execute(self,sql):
        self.connect_db()
        return self.cur.execute(sql)

    # 匹配某个字段是否在数据库匹配
    def check(self,table,fields,where):
        self.connect_db()
        '''where以这种格式传递过来：where = {'username':jack,"password":'123456'}
        处理后应该是这样子['username="jack"','password="123456"']'''
        content = ['k="v"' for k,v in where.items()]
        sql = "select %s from %s where %s" % (",".join(fields),table,'AND'.join(content))
        try:
            self.execute(sql)
            result = self.cur.fetchone() # 执行结果只有一条使用fetchone拿出来
        except:
            logs.info("Excute: %s,Error: %s") % (sql,traceback.format_exc())
        finally:
            self.close_db()



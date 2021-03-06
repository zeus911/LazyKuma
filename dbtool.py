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
            (mysql,mincached=4,maxcached=10,
             host=self.host,db=self.name,user=self.user,passwd=self.passwd,
             setsession=['SET AUTOCOMMIT=1'],charset="utf8")

    def connect_db(self):
        self.db = self.pool.connection()
        self.cur = self.db.cursor()

    def close_db(self):
        self.cur.close()
        self.db.close()

    def execute(self,sql):
        self.connect_db()
        return self.cur.execute(sql)

    # 查询 不匹配where操作
    def select_NoWhere(self,table,fields):
        self.connect_db()
        sql = "SELECT %s FROM %s" % (",".join(fields),table)
        try:
            self.execute(sql)
            logs.info("Run sql: %s" % sql)
            return self.cur.fetchall() # 返回执行的所有结果
        except:
            logs.error("Excute: %s,Error: %s" % (sql,traceback.format_exc()))
        finally:
            self.close_db()

    # 查询 匹配WHERE操作
    def check(self,table,fields,where):
        self.connect_db()
        '''where以这种格式传递过来：where = {'name':jack,"password":'123456'}
        处理后应该是这样子['name="jack"','password="123456"']'''
        content = ['%s="%s"' % (k,v) for k,v in where.items()]
        print where
        print content
        sql = "SELECT %s FROM %s WHERE %s" % (",".join(fields),table,"AND".join(content))
        try:
            self.execute(sql)
            logs.info("Run sql: %s" % sql)
            return self.cur.fetchone() # 执行结果只有一条使用fetchone拿出来
        except:
            logs.error("Excute: %s,Error: %s" % (sql,traceback.format_exc()))
        finally:
            self.close_db()

    # 更新操作
    def update(self,table,sets,where):
        self.connect_db()
        content1 = ['%s="%s"' % (k,v) for k,v in where.items()]
        content2 = ['%s="%s"' % (k,v) for k,v in sets.items()] # sets的格式{'name':jack,"name_cn":'123456',...}
        sql = "UPDATE %s SET %s WHERE %s" % (table,",".join(content2),"AND".join(content1))
        try:
            self.execute(sql)
            logs.info("Run sql: %s" % sql)
            return 0
        except:
            logs.error("Excute: %s,Error: %s" % (sql,traceback.format_exc()))
        finally:
            self.close_db()

    # 删除操作
    def delete(self,table,where):
        self.connect_db()
        content = ['%s="%s"' % (k,v) for k,v in where.items()]
        sql = "DELETE FROM %s WHERE %s" % (table,"AND".join(content))
        try:
            self.execute(sql)
            logs.info("Run sql: %s" % sql)
            return 0
        except:
            logs.error("Excute: %s,Error: %s" % (sql,traceback.format_exc()))
        finally:
            self.close_db()

    # 插入操作
    def insert(self,table,fields,values):
        self.connect_db()
        content = ['"%s"' % values[x] for x in fields]
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table,",".join(fields),",".join(content))
        try:
            self.execute(sql)
            logs.info("Run sql: %s" % sql)
            return 0
        except:
            logs.error("Excute: %s,Error: %s" % (sql,traceback.format_exc()))
        finally:
            self.close_db()
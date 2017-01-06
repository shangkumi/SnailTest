# coding:utf-8
import pymysql
import sqlite3
import cx_Oracle
from .Log import Log
import os

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class DBHandle:
    def __init__(self, db, auto_close=True):
        self.DB = db
        self.auto_close = auto_close
        self.connection = None

    def __connect(self):
        try:
            if self.DB['TYPE'].lower() == 'mysql':
                self.conn = pymysql.connect(**self.DB['DBINFO'])
                self.cur = self.conn.cursor()
            elif self.DB['TYPE'].lower() == 'oracle':
                self.conn = cx_Oracle.connect(self.DB['DBINFO'])
                self.cur = self.conn.cursor()
            elif self.DB['TYPE'].lower() == 'sqlite':
                self.conn = sqlite3.connect(self.DB['DBINFO'])
                self.cur = self.conn.cursor()
            else:
                Log.info('%s is Unsupported Type' % self.DB['TYPE'])
        except Exception as err:
            Log.error('数据库接连出错, 错误信息:\n%s' % err)
            assert False

    def execute(self, sql, params=None):
        sql = sql.strip()
        if sql.split()[0].lower() == 'select':
            sql_type = 1
        elif sql.split()[0].lower() in ('update', 'delete', 'insert'):
            sql_type = 2
        else:
            sql_type = 3
        if sql_type == 1:
            if not self.connection:
                self.__connect()
            Log.debug('执行SQL: %s' % sql)
            try:
                if params:
                    self.cur.execute(sql, params)
                else:
                    self.cur.execute(sql)
                field = [i[0] for i in self.cur.description]
                data = self.cur.fetchall()
                n = len(data)
                Log.debug('查询出%s条记录' % n)

                result = [{field[f].lower(): data[i][f] for f in range(len(field))} for i in range(n)]
                if self.auto_close:
                    self.cur.close()
                    self.conn.close()
                return result
            except Exception as err:
                Log.error('查询SQL出错, 错误信息:\n%s' % err)
                if self.auto_close:
                    self.cur.close()
                    self.conn.close()
                assert False
        if sql_type == 2:
            if not self.connection:
                self.__connect()
            Log.debug('执行SQL: %s' % sql)
            try:
                if params:
                    self.cur.execute(sql, params)
                else:
                    self.cur.execute(sql)
                self.conn.commit()
                if self.auto_close:
                    self.cur.close()
                    self.conn.close()
            except Exception as err:
                Log.error('执行SQL出错, 错误信息:\n%s' % err)
                self.conn.rollback()
                if self.auto_close:
                    self.cur.close()
                    self.conn.close()
                assert False
        if sql_type == 3:
            Log.error('不支持的操作,或sql有误:\n%s' % sql)
            assert False

    def executemany(self, sql, params=None):
        if not self.connection:
            self.__connect()
        try:
            self.cur.executemany(sql, params)
            self.conn.commit()
            if self.auto_close:
                self.cur.close()
                self.conn.close()
        except Exception as err:
            Log.error('执行SQL出错, 错误信息:\n %s' % err)
            self.conn.rollback()
            if self.auto_close:
                self.cur.close()
                self.conn.close()
            assert False

    def close(self):
        self.cur.close()
        self.conn.close()
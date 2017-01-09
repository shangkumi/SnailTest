# coding:utf-8
from action.yylg.sql import SQL
from config import DBInfo
from utils.DBHandle import DBHandle


class Duobao:
    DB = DBHandle(DBInfo.DUOBAO_TEST)

    @classmethod
    def query_user_pay_act_by_account(cls, account):
        result = cls.DB.execute(SQL.QUERY_USER_PAY_ACT_BY_ACCOUNT, {'account': account})[0]
        return result

    @classmethod
    def delete_user_pay_act_by_account(cls, account):
        cls.DB.execute(SQL.DELETE_USER_PAY_ACT_BY_ACCOUNT, {'account': account})[0]
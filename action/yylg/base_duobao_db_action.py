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

    @classmethod
    def query_link_config_by_link_type(cls, link_type):
        result = cls.DB.execute(SQL.QUERY_LINK_CONFIG_BY_LINK_TYPE, {'link_type': link_type})
        return result

    @classmethod
    def query_floating_view_setting(cls):
        """tb_duobao_link_config表中, link_type=25的配置为新手浮标配置"""
        result = cls.query_link_config_by_link_type('25')
        return result



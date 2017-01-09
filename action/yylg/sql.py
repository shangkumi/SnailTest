# coding:utf-8

class SQL:
    # TB_DUOBAO_USER_PAY_ACT
    QUERY_USER_PAY_ACT_BY_ACCOUNT = 'select * from TB_DUOBAO_USER_PAY_ACT where account_id = :account'
    DELETE_USER_PAY_ACT_BY_ACCOUNT = 'delete from TB_DUOBAO_USER_PAY_ACT where account_id = :account'

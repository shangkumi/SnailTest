# coding:utf-8

class SQL:
    # TB_DUOBAO_LINK_CONFIG
    QUERY_LINK_CONFIG_BY_LINK_TYPE = 'select * from TB_DUOBAO_LINK_CONFIG where link_type = :link_type and ' \
                                     'sysdate > start_time and sysdate < end_time order by weight desc'
    # TB_DUOBAO_USER_PAY_ACT
    QUERY_USER_PAY_ACT_BY_ACCOUNT = 'select * from TB_DUOBAO_USER_PAY_ACT where account_id = :account'
    DELETE_USER_PAY_ACT_BY_ACCOUNT = 'delete from TB_DUOBAO_USER_PAY_ACT where account_id = :account'

# coding:utf-8
from action.yylg.floating_view_action import FloatingViewAction
from action.yylg.base_duobao_db_action import Duobao
from action.yylg.base_redis_action import RedisAction
from utils.Log import Log


def floating_view_test(channel, account_id):
    query = {
        'product': 'android_cp_hyg',
        'ver': '1.5',
        'apiLevel': '28',
        'channel': channel,
        'deviceId': '351670063004332',
        'apiVer': '1.1',
        'mobileType': 'android',
    }

    data = {
        'userName': account_id,
    }

    r = FloatingViewAction.floating_view(query, data)
    Log.info(r)

if __name__ == '__main__':
    # ACCOUNT_ID = 'urstestzhubo0000@126.com'
    # result = Duobao.query_user_pay_act_by_account(ACCOUNT_ID)
    # Log.info(result)


    # order_num = RedisAction.get_new_user_marketing_order_num(ACCOUNT_ID)
    # Log.info(order_num)

    # floating_view_test('legou', ACCOUNT_ID)
    # floating_view_test('legou', '')

    FloatingViewAction.query_floating_view_setting()
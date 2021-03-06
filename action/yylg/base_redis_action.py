# coding:utf-8
import redis as redis

from config import RedisInfo
from utils.Log import Log


class RedisAction:
    redis_handle = redis.StrictRedis(host=RedisInfo.REDIS_TEST['host'], password=RedisInfo.REDIS_TEST['password'])

    @classmethod
    def get_new_user_marketing_order_num(cls, account_id):
        name = 'new_user_marketing_{0}'.format(account_id)
        key = 'orderNum'
        order_num = cls.redis_handle.hget(name, key)
        if order_num:
            try:
                return int(order_num)
            except ValueError as err:
                Log.error('新用户支付次数获取有误')
                Log.error('ERROR: %s' % err)
        else:
            return order_num

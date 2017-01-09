# coding:utf-8
import json

from action.yylg.url import URL
from utils.HttpHandle import HttpHandle
from utils.Log import Log


class API:
    http = HttpHandle()

    @classmethod
    def floating_view(cls, query, data):
        """
        新手浮标接口
        :param query: 查询字符串
            @product
            @ver
            @apiLevel
            @channel    渠道--关键参数
            @deviceId
            @apiVer
            @mobileType
        :param data:  表单数据
            @userName  用户名--关键参数
        :return: 返回json串
        """
        result = cls.http.post(URL.FLOATING_VIEW_URL, params=query, data=data)
        try:
            result = result.json()
            return result
        except json.decoder.JSONDecodeError:
            Log.error('新手弹窗接口返回有误')
# coding:utf-8
import json

from action.yylg.base_duobao_db_action import Duobao
from action.yylg.url import URL
from utils.HttpHandle import HttpHandle
from utils.Log import Log


class FloatingViewAction:
    """
        新手浮标接口:
            关键参数: channel, userName
            接口逻辑:
                1. 根据userName查出用户支付成功次数(db or redis);
                2. channel为客户端渠道
                3. 根据支付成功次数和渠道查找是否有对应浮标配置(db), 如有配置则返回配置的图片链接和跳转链接
                4. 如没有查到对应配置, 则查找是否有该渠道支付成功次数为-1的配置 (-1代表该渠道所有用户, 优先级低于指定支付成功次数配置), 如查到
                    该渠道支付成功次数-1的配置, 则返回该配置的图片链接和跳转链接
                5. 如没有查到该渠道支付成功次数-1的配置, 则查找默认渠道对应支付成功次数的配置, 如查到默认渠道对应支付成功次数的配置, 则返回该配置的
                    图片链接和跳转链接
                6. 如没有查到默认渠道对应支付成功次数的配置, 则查找默认渠道支付成功次数-1的配置, 如查到认渠道支付成功次数-1的配置, 则返回该配置的
                    图片链接和跳转链接
                7. 如没有查到默认渠道支付成功次数-1的配置, 则返回图片链接和跳转链接都为空

            用户支付成功次数判断逻辑:
                1. 如不传userName参数, 判定用户支付成功次数为0
                2. 如传userName参数, 但TB_DUOBAO_USER_PAY_ACT表中查不到该用户的记录, 判定用户支付成功次数为0
                3. 如传userName参数, TB_DUOBAO_USER_PAY_ACT表中有该用户的记录, 但first_pay_time字段为Null, 判定用户支付成功次数为0
                4. 如传userName参数, TB_DUOBAO_USER_PAY_ACT表中有该用户的记录, first_pay_time字段不为Null, 则去redis中Hash类型
                    的new_user_marketing_+userName中orderNum去查找(userName改为传入的参数)
                5. 如orderNum为nil或空, 则判定用户支付成功次数为0, 如为其它数值, 则判定支付成功次数为orderNum的值
    """
    http = HttpHandle()
    # image_url和click_url不用管是否真实可用, 只要插入数据库中, 接口按业务逻辑正常返回即可
    base_image_url = "https://img.winyylg.cn/hyg/product/images/duobao/newerPopup/1481014242939_1.png"
    base_click_url = "yylgapp://hyg_commodity?id=2016111710PT360704364&showfastparticipant=1"

    @classmethod
    def floating_view(cls, data):
        """
        新手浮标接口
        :param data:
            @userName  用户名
            @channel   渠道
        :return: 返回json串
        """
        result = cls.http.post(URL.FLOATING_VIEW_URL, data=data)
        try:
            result = result.json()
            return result
        except json.decoder.JSONDecodeError:
            Log.error('新手浮标接口返回有误')

    @classmethod
    def query_floating_view_setting(cls):
        """tb_duobao_link_config表中, link_type=25的配置为新手浮标配置"""
        result = Duobao.query_link_config_by_link_type('25')
        cls.__validate_floating_view_setting(result)
        return result

    @classmethod
    def __validate_floating_view_setting(cls, floating_view_setting):
        """验证: 新手浮标不能有渠道相同且支付成功次数相同的配置"""
        validate_dict = {}
        for i in floating_view_setting:
            if not validate_dict.get(i['title']):
                validate_dict[i['title']] = [i['account_type']]
            elif i['account_type'] not in validate_dict[i['title']]:
                validate_dict[i['title']].append(i['account_type'])
            else:
                Log.error('新手浮标有渠道相同且支付成功次数相同的配置, 请检查是否数据有误')
                Log.error('新手浮标配置为: %s' % floating_view_setting)
                assert False
        Log.info(validate_dict)

    @classmethod
    def clear_floating_view_config(cls):
        """清除tb_duobao_link_config表中, link_type=25的配置"""
        # TODO:
        pass

    @classmethod
    def set_floating_view_config(cls, channel, pay_times):
        """设置新手浮标配置"""
        # TODO:
        pass

    @classmethod
    def clear_user_status(cls, account):
        """
        1. 清除用户TB_DUOBAO_USER_PAY_ACT数据
        2. 清除用户reidsr的new_user_marketing_+userName中orderNum数据
        """
        # TODO:
        pass

    @classmethod
    def set_user_status(cls, user_pay_times_type):
        if user_pay_times_type == '1':
            # TODO:
            #       删除TB_DUOBAO_USER_PAY_ACT表用户记录,
            #       删除reidsr的new_user_marketing_+userName中orderNum数据
            return 0
        if user_pay_times_type == '2':
            # TODO:
            #       TB_DUOBAO_USER_PAY_ACT表中插入该用户记录, first_pay_time字段为Null,
            #       删除reidsr的new_user_marketing_+userName中orderNum数据
            return 0
        if user_pay_times_type == '3':
            # TODO:
            #       TB_DUOBAO_USER_PAY_ACT表中插入该用户记录, first_pay_time字段为当前时间,
            #       删除reidsr的new_user_marketing_+userName中orderNum数据
            return 0
        if user_pay_times_type == '4':
            # TODO:
            #       TB_DUOBAO_USER_PAY_ACT表中插入该用户记录, first_pay_time字段为当前时间,
            #       设置reidsr的new_user_marketing_+userName中orderNum数据为2
            return 2
        if user_pay_times_type == '5':
            # TODO:
            #       删除TB_DUOBAO_USER_PAY_ACT表中插入该用户记录
            #       设置reidsr的new_user_marketing_+userName中orderNum数据为2
            return 0
        if user_pay_times_type == '6':
            # TODO:
            #       TB_DUOBAO_USER_PAY_ACT表中插入该用户记录, first_pay_time字段为Null,
            #       设置reidsr的new_user_marketing_+userName中orderNum数据为2
            return 0

    @classmethod
    def expect_config(cls, channel, pay_times):
        """返回预期的配置值"""
        expect_image =  "%s?channel=%s&times=%s" % (cls.base_image_url, channel, pay_times)
        expect_click_url = "%s&channel=%s&times=%s" % (cls.base_click_url, channel, pay_times)
        return {'image': expect_image, 'clickUrl': expect_click_url}
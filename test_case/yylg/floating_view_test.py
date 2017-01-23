# coding:utf-8
from action.yylg.floating_view_action import FloatingViewAction
from utils.Log import Log


class FloatingViewTest:
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

    def __init__(self):
        Log.info('新手浮标接口测试开始...')
        self.test_account = 'urstestzhubo0000@126.com'
        self.test_channel = 'legou'

    def base_assert(self, result):
        """
        1. 验证result字段是否返回100
        2. 验证返回是否有image字段
        3. 验证返回是否有clickUrl字段
        """
        assert result['result'] == 100, '接口返回result字段非100-->' % result['result']
        assert 'image' in result, '接口返回不包含image字段'
        assert 'clickUrl' in result, '接口返回不包含clickUrl字段'

    def abnormal_test(self, user_name, channel):
        """userName, channel参数传异常值时应不报错"""
        data = {
            'userName': user_name,
            'channel': channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)

    def had_channel_and_times_config_test(self, user_pay_times_type):
        """
        :param user_pay_times_type:
            “1”--TB_DUOBAO_USER_PAY_ACT表中查不到该用户记录的情况(应判定pay_times=0)
            “2”--TB_DUOBAO_USER_PAY_ACT表中有该用户记录, 但first_pay_time字段为Null的情况(应判定pay_times=0)
            “3”--TB_DUOBAO_USER_PAY_ACT表中有该用户记录, first_pay_time字段不为Null, redis中
                new_user_marketing_urstestzhubo0000@126.com为空的情况(应判定pay_times=0)
            “4”--TB_DUOBAO_USER_PAY_ACT表中有该用户记录, first_pay_time字段不为Null, redis中
                new_user_marketing_urstestzhubo0000@126.com为2的情况(应判定pay_times=2)
            "5"--TB_DUOBAO_USER_PAY_ACT表中查不到该用户记录, redis中new_user_marketing_urstestzhubo0000@126.com
                为2的情况(应判定pay_times=0)
            "6"--TB_DUOBAO_USER_PAY_ACT表中有该用户记录, 但first_pay_time字段为Null, redis中
                new_user_marketing_urstestzhubo0000@126.com为2的情况(应判定pay_times=0)
        :return:

        用例逻辑:
            1. 清空新手浮标配置
            2. 分别设置默认渠道支付次数为-1, 0, 2次的配置, 和测试渠道支付次数为-1, 0, 2次的配置
            3. 通过入参user_pay_times_type, 设置用户不同状态下支付次数的情况, 并获取当前情况下用户的支付次数pay_times
            4. 调用接口, 先经过base_assert验证返回字段的基本验证
            5. 验证image字段返回值同test_channel渠道,支付pay_times次配置一致(同时也能验证了指定渠道，指定次数的配置优先级
                要高于支付次数-1级默认渠道的配置)
            6. 验证clickUrl字段返回值同test_channel渠道,支付pay_times次配置一致
        """
        FloatingViewAction.clear_floating_view_config()
        FloatingViewAction.set_floating_view_config('default_channel', '-1')
        FloatingViewAction.set_floating_view_config('default_channel', '0')
        FloatingViewAction.set_floating_view_config('default_channel', '2')
        FloatingViewAction.set_floating_view_config(self.test_channel, '-1')
        FloatingViewAction.set_floating_view_config(self.test_channel, '0')
        FloatingViewAction.set_floating_view_config(self.test_channel, '2')

        FloatingViewAction.clear_user_status(self.test_account)
        pay_times = FloatingViewAction.set_user_status(user_pay_times_type)
        data = {
            'userName': self.test_account,
            'channel': self.test_channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == FloatingViewAction.expect_config(self.test_channel, pay_times)['image']
        assert result['clickUrl'] == FloatingViewAction.expect_config(self.test_channel, pay_times)['clickUrl']

    def had_channel_and_no_times_config_test(self, user_pay_times_type):
        """
        :param user_pay_times_type: 同上
        :return:

        用例逻辑:
            1. 清空新手浮标配置
            2. 分别设置默认渠道支付次数为-1, 0, 2次的配置, 和测试渠道支付次数为-1, 1的配置
            3. 通过入参user_pay_times_type, 设置用户不同状态下支付次数的情况, 并获取当前情况下用户的支付次数pay_times
            4. 调用接口, 先经过base_assert验证返回字段的基本验证
            5. 验证image字段返回值同test_channel渠道,支付-1次配置一致(同时也能验证了,如指定渠道没有指定次数的配置,
                不会返回除-1外的非指定次数(1次)的配置, 还验证了, 指定渠道-1次的配置, 优先级高于默认渠道, 指定次数的配置)
            6. 验证clickUrl字段返回值同test_channel渠道,支付-1次配置一致
        """
        FloatingViewAction.clear_floating_view_config()
        FloatingViewAction.set_floating_view_config('default_channel', '-1')
        FloatingViewAction.set_floating_view_config('default_channel', '0')
        FloatingViewAction.set_floating_view_config('default_channel', '2')
        FloatingViewAction.set_floating_view_config(self.test_channel, '-1')
        FloatingViewAction.set_floating_view_config(self.test_channel, '1')

        FloatingViewAction.clear_user_status(self.test_account)
        pay_times = FloatingViewAction.set_user_status(user_pay_times_type)
        data = {
            'userName': self.test_account,
            'channel': self.test_channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == FloatingViewAction.expect_config('default_channel', pay_times)['image']
        assert result['clickUrl'] == FloatingViewAction.expect_config('default_channel', pay_times)['clickUrl']

    def had_default_channel_and_times_config_test(self, user_pay_times_type):
        """
        :param user_pay_times_type: 同上
        :return:

        用例逻辑:
            1. 清空新手浮标配置
            2. 分别设置默认渠道支付次数为-1, 0, 2次的配置, 和测试渠道支付次数为1的配置
            3. 通过入参user_pay_times_type, 设置用户不同状态下支付次数的情况, 并获取当前情况下用户的支付次数pay_times
            4. 调用接口, 先经过base_assert验证返回字段的基本验证
            5. 验证image字段返回值同default_channel渠道,支付pay_times次配置一致(同时也能验证了,如指定渠道没有指定次数及-1次的配置,
                不会返回非指定次数(1次)的配置, 还验证了, 默认渠道指定次数的配置, 优先级高于默认渠道, -1次数的配置)
            6. 验证clickUrl字段返回值同test_channel渠道,支付pay_times次配置一致
        """
        FloatingViewAction.clear_floating_view_config()
        FloatingViewAction.set_floating_view_config('default_channel', '-1')
        FloatingViewAction.set_floating_view_config('default_channel', '0')
        FloatingViewAction.set_floating_view_config('default_channel', '2')
        FloatingViewAction.set_floating_view_config(self.test_channel, '1')

        FloatingViewAction.clear_user_status(self.test_account)
        pay_times = FloatingViewAction.set_user_status(user_pay_times_type)
        data = {
            'userName': self.test_account,
            'channel': self.test_channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == FloatingViewAction.expect_config('default_channel', -1)['image']
        assert result['clickUrl'] == FloatingViewAction.expect_config('default_channel', -1)['clickUrl']

    def had_default_channel_and_no_times_config_test(self, user_pay_times_type):
        """
        :param user_pay_times_type: 同上
        :return:

        用例逻辑:
            1. 清空新手浮标配置
            2. 分别设置默认渠道支付次数为-1, 1次的配置
            3. 通过入参user_pay_times_type, 设置用户不同状态下支付次数的情况, 并获取当前情况下用户的支付次数pay_times
            4. 调用接口, 先经过base_assert验证返回字段的基本验证
            5. 验证image字段返回值同default_channel渠道,支付-1次配置一致(同时也能验证了,如指定渠道没有指定次数及-1次的配置,
                默认渠道也没有指定次数的配置,不会返回默认渠道非指定次数(1次)的配置)
            6. 验证clickUrl字段返回值同test_channel渠道,支付-1次配置一致
        """
        FloatingViewAction.clear_floating_view_config()
        FloatingViewAction.set_floating_view_config('default_channel', '-1')
        FloatingViewAction.set_floating_view_config('default_channel', '1')

        FloatingViewAction.clear_user_status(self.test_account)
        pay_times = FloatingViewAction.set_user_status(user_pay_times_type)
        data = {
            'userName': self.test_account,
            'channel': self.test_channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == FloatingViewAction.expect_config('default_channel', -1)['image']
        assert result['clickUrl'] == FloatingViewAction.expect_config('default_channel', -1)['clickUrl']

    def had_no_config_test(self, user_pay_times_type):
        """
        :param user_pay_times_type: 同上
        :return:

        用例逻辑:
            1. 清空新手浮标配置
            2. 通过入参user_pay_times_type, 设置用户不同状态下支付次数的情况, 并获取当前情况下用户的支付次数pay_times
            3. 调用接口, 先经过base_assert验证返回字段的基本验证
            4. 验证image字段返回值为空""
            5. 验证clickUrl字段返回值为空""
        """
        FloatingViewAction.clear_floating_view_config()

        FloatingViewAction.clear_user_status(self.test_account)
        pay_times = FloatingViewAction.set_user_status(user_pay_times_type)
        data = {
            'userName': self.test_account,
            'channel': self.test_channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == ""
        assert result['clickUrl'] == ""

    def missing_username_test(self):
        """
        不传userName参数, 判定支付次数为0
        :return:
        """
        # 增加测试渠道0次配置
        FloatingViewAction.clear_floating_view_config()
        FloatingViewAction.set_floating_view_config(self.test_channel, '0')
        data = {
            'userName': '',
            'channel': self.test_channel,
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == FloatingViewAction.expect_config(self.test_channel, 0)['image']
        assert result['clickUrl'] == FloatingViewAction.expect_config(self.test_channel, 0)['clickUrl']

    def missing_channel_test(self):
        """
        不传channel参数, 只能判定为默认渠道
        :return:
        """
        # 增加默认渠道2次配置
        FloatingViewAction.clear_floating_view_config()
        FloatingViewAction.set_floating_view_config('default_channel', '2')
        FloatingViewAction.clear_user_status(self.test_account)
        FloatingViewAction.set_user_status("4")    # 设置用户支付次数为2的情况
        data = {
            'userName': self.test_account,
            'channel': "",
        }
        result = FloatingViewAction.floating_view(data)
        self.base_assert(result)
        assert result['image'] == FloatingViewAction.expect_config('default_channel', 2)['image']
        assert result['clickUrl'] == FloatingViewAction.expect_config('default_channel', 2)['clickUrl']


if __name__ == '__main__':
    f = FloatingViewTest()
    f.base_test('urstestzhubo0000@126.com', 'lego')

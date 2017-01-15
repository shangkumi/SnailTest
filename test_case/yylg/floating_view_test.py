# coding:utf-8
from action.yylg.floating_view_action import FloatingViewAction



class Test0:
    pass

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
        pass

    def base_test(self):
        # data = {
        #     'userName': 'urstestzhubo0000@126.com',
        #     'channel': 'legou',
        # }
        data = {
            'userName': 'zbwill',
            'channel': 'test1',
        }
        r = FloatingViewAction.floating_view(data)
        print(r)

class Test1:
    pass

class Test2:
    pass

if __name__ == '__main__':
    f = FloatingViewTest()
    f.base_test()
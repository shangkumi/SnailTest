# coding:utf-8


class ResultCode:
    SUCCESS = {'result': 100, 'resultDesc': '成功'}
    SAME_API_NAME_ERROR = {'result': -100, 'resultDesc': '已有相同文件名'}
    FILE_AND_CLASS_BINDED = {'result': -101, 'resultDesc': '文件的该类已绑定接口'}
    FILE_NOT_FOUND = {'result': -102, 'resultDesc': '未找到该文件'}
    CLASS_NOT_FOUND = {'result': -103, 'resultDesc': '未找到该测试类'}
    DB_ERROR = {'result': -200, 'resultDesc': '数据库报错'}

# coding:utf-8


class ResultCode:
    def __init__(self):
        self.SUCCESS = {'result': 100, 'resultDesc': '成功'}
        self.SAME_API_NAME_ERROR = {'result': -100, 'resultDesc': '已有相同文件名'}
        self.FILE_AND_CLASS_BINDED = {'result': -101, 'resultDesc': '文件的该类已绑定接口'}
        self.FILE_NOT_FOUND = {'result': -102, 'resultDesc': '未找到该文件'}
        self.CLASS_NOT_FOUND = {'result': -103, 'resultDesc': '未找到该测试类'}
        self.API_NOT_FOUND = {'result': -104, 'resultDesc': '未找到该测试接口'}
        self.SAME_TEST_CASE_NAME_ERROR = {'result': -105, 'resultDesc': '该测试接口已有相同的测试用例名'}
        self.FUNC_BINDED = {'result': -106, 'resultDesc': '该方法已绑定用例'}
        self.FUNC_NOT_FOUND = {'result': -107, 'resultDesc': '未找到该测试方法'}
        self.SAME_TEST_DATA_NAME_ERROR = {'result': -108, 'resultDesc': '该用例下已有相同的测试数据名'}
        self.DB_ERROR = {'result': -200, 'resultDesc': '数据库报错'}

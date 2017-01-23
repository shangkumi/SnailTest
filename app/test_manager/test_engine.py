# coding:utf-8
import importlib
import os

import time
import unittest
from io import BytesIO

import HTMLTestRunner
from app.models import Api
from app.test_manager.result_code import ResultCode
from config import BASE_DIR
from utils.Log import Log


class SuiteError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class TestEngine:
    def __init__(self, test_datas):
        self.test_datas = test_datas
        self.test_cases = list({test_data.test_case for test_data in test_datas})
        self.apis = list({test_case.api for test_case in self.test_cases})

    def test_suite_factory(self, api):
        api_info = self.get_test_function(api.id)

        def case_factory(func, test_data, has_error):
            if has_error:
                def function(self):
                    '''%s-%s''' % (test_data.test_case.test_case_name, test_data.test_data_name)
                    raise SuiteError(func['resultDesc'])

                return function
            else:
                def function(self):
                    '''%s-%s''' % (test_data.test_case.test_case_name, test_data.test_data_name)
                    args = test_data.values.split('|')
                    if args == ['']:
                        args = []
                    print('args: %s' % args)
                    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print('start_time: %s\n##############################' % start_time)
                    func(self.instance, *args)
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print('##############################\nend_time: %s' % end_time)

                return function

        class TestCase(unittest.TestCase):
            '''%s''' % api.api_name
            pass

        TestCase.__name__ = api.api_name
        TestCase.__doc__ = api.api_name
        if api_info['result'] == 100:
            @classmethod
            def setUpClass(cls):
                cls.instance = api_info['test_class']()
        else:
            @classmethod
            def setUpClass(cls):
                pass

        @classmethod
        def tearDownClass(cls):
            pass

        n = 0
        for test_case in [test_case for test_case in api.test_cases if test_case in self.test_cases]:
            has_error = True
            if api_info['result'] == 100:
                if test_case.func_name in api_info['func_list']:
                    func = getattr(api_info['test_class'], test_case.func_name)
                    func.__doc__ = test_case.test_case_name
                    has_error = False
                else:
                    func = ResultCode().FUNC_NOT_FOUND
            else:
                func = api_info

            for test_data in [test_data for test_data in test_case.test_datas if test_data in self.test_datas]:
                setattr(TestCase, 'test_%03.f' % n, case_factory(func, test_data, has_error))
                eval('TestCase.test_%03.f' % n).__doc__ = '%s-%s' % (test_case.test_case_name, test_data.test_data_name)
                n += 1
        setattr(TestCase, 'setUpClass', setUpClass)
        setattr(TestCase, 'tearDownClass', tearDownClass)
        return TestCase

    def execute_test(self, tmp=False):
        if tmp:
            fp = BytesIO()
        else:
            now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            report_file_name = 'report_%s.html' % now
            report_file = os.path.join(BASE_DIR, 'report', report_file_name)
            fp = open(report_file, 'wb')
        all_suite = unittest.TestSuite()
        for api in self.apis:
            suite = unittest.TestLoader().loadTestsFromTestCase(self.test_suite_factory(api))
            all_suite.addTest(suite)
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='TestReport', description='用例执行情况:')
        r = runner.run(all_suite)
        result = {'result': runner.getReportAttributes(r)}
        if tmp:
            result['is_tmp'] = True
            result['html'] = fp.getvalue()
        else:
            result['is_tmp'] = False
            result['report_file_name'] = report_file_name
        fp.close()
        return result

    @classmethod
    def get_test_case_file_list(cls):
        test_case_path = os.path.join(BASE_DIR, 'test_case') + os.path.sep
        # apis = Api.query.all()
        file_list = []
        for i in os.walk(test_case_path):
            if i[2]:
                f = [os.path.join(i[0], j).replace(test_case_path, '') for j in i[2] if
                     (j.endswith('.py') and j != '__init__.py')]
                file_list.extend(f)
        file_dict = {'not_binded_file': [], 'binded_api': []}
        for file_path in file_list:
            apis = Api.query.filter_by(file_path=file_path).all()
            if apis:
                file_dict['binded_api'].append(apis)
            else:
                file_dict['not_binded_file'].append(file_path)
        return file_dict

    @classmethod
    def find_test_class(cls, file_path):
        abspath = os.path.join(BASE_DIR, 'test_case', file_path)
        if os.path.exists(abspath) and os.path.isfile(abspath):
            class_list = [i.strip().replace('class ', '').replace(':', '') for i in open(abspath) if
                          i.strip().startswith('class ')]
        else:
            return ResultCode().FILE_NOT_FOUND
        if class_list:
            result = ResultCode().SUCCESS
            result['class_list'] = class_list
            return result
        else:
            return ResultCode().CLASS_NOT_FOUND

    @classmethod
    def get_test_file_code(cls, file_path):
        abspath = os.path.join(BASE_DIR, 'test_case', file_path)
        if os.path.exists(abspath) and os.path.isfile(abspath):
            code = open(abspath).read()
            return code
        else:
            return ResultCode().FILE_NOT_FOUND

    @classmethod
    def get_test_function(cls, api_id):
        api = Api.query.get_or_404(api_id)
        if cls.get_test_file_code(api.file_path) == ResultCode().FILE_NOT_FOUND:
            return ResultCode().FILE_NOT_FOUND
        module_str = 'test_case.' + api.file_path.replace('.py', '').replace(os.path.sep, '.')
        module_str = module_str.replace('..', '.')
        module_str = module_str.replace('\\', '.')
        module_str = module_str.replace('/', '.')
        module = importlib.import_module(module_str)
        try:
            test_class = getattr(module, api.class_name)
            function_list = [i for i in dir(test_class) if not i.startswith('__') and callable(getattr(test_class, i))]
            result = ResultCode().SUCCESS
            result['func_list'] = function_list
            result['test_class'] = test_class
            return result
        except AttributeError as err:
            Log.error(err)
            return ResultCode().CLASS_NOT_FOUND


if __name__ == '__main__':
    # TestEngine.get_test_case_file_list()
    print(TestEngine.find_test_class('yylg/floating_view_test.py'))

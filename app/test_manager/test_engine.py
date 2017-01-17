# coding:utf-8
import importlib
import os

from app.models import Api
from app.test_manager.result_code import ResultCode
from config import BASE_DIR
from utils.Log import Log


class TestEngine:
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
            return ResultCode.FILE_NOT_FOUND
        if class_list:
            result = ResultCode.SUCCESS
            result['class_list'] = class_list
            return result
        else:
            return ResultCode.CLASS_NOT_FOUND

    @classmethod
    def get_test_file_code(cls, file_path):
        abspath = os.path.join(BASE_DIR, 'test_case', file_path)
        Log.info(abspath)
        if os.path.exists(abspath) and os.path.isfile(abspath):
            code = open(abspath).read()
            return code
        else:
            return ResultCode.FILE_NOT_FOUND

    @classmethod
    def get_test_function(cls, api_id):
        api = Api.query.get_or_404(api_id)
        if cls.get_test_file_code(api.file_path) == ResultCode.FILE_NOT_FOUND:
            return ResultCode.FILE_NOT_FOUND
        module_str = 'test_case.' + api.file_path.replace('.py', '').replace(os.path.sep, '.')
        module_str = module_str.replace('..', '.')
        module_str = module_str.replace('\\', '.')
        module_str = module_str.replace('/', '.')
        module = importlib.import_module(module_str)
        try:
            test_class = getattr(module, api.class_name)
            function_list = [i for i in dir(test_class) if not i.startswith('__') and callable(getattr(test_class, i))]
            result = ResultCode.SUCCESS
            result['func_list'] = function_list
            return result
        except AttributeError as err:
            Log.error(err)
            return ResultCode.CLASS_NOT_FOUND

if __name__ == '__main__':
    # TestEngine.get_test_case_file_list()
    print(TestEngine.find_test_class('yylg/floating_view_test.py'))

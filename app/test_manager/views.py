# coding:utf-8
from app import db
from app.models import Api
from app.test_manager import test_manager
from app.test_manager.forms import AddApiForm

from flask import render_template, flash, redirect, url_for, request, jsonify

from app.test_manager.test_engine import TestEngine


@test_manager.route('/test_manager/')
def index():
    return render_template('/test_manager/index.html')


@test_manager.route('/test_manager/add_api/', methods=['GET', 'POST'])
def add_api():
    if request.method == 'GET':
        file_dict = TestEngine.get_test_case_file_list()
        return render_template('/test_manager/add_api.html', file_dict=file_dict)
    if request.method == 'POST':
        api_name = request.form.get('api_name')
        file_path = request.form.get('file_path')
        class_name = request.form.get('class_name')
        remark = request.form.get('remark')

        result = {'result': 100, 'resultDesc': '新增测试接口成功', 'api_id': ''}
        # 验证是否满足条件新建
        if Api.query.filter_by(api_name=api_name).first():
            result['result'] = -100
            result['resultDesc'] = '已有同名接口'
            return jsonify(result)

        api_by_file_path_and_class = Api.query.filter_by(file_path=file_path, class_name=class_name).first()
        if api_by_file_path_and_class:
            result['result'] = -101
            result['resultDesc'] = '文件的该类已绑定测试接口: %s' % api_by_file_path_and_class.api_name
            return jsonify(result)

        try:
            api = Api(api_name=api_name, file_path=file_path, class_name=class_name, remark=remark)
            db.session.add(api)
            db.session.commit()
            result['api_id'] = api.id
            return jsonify(result)
        except Exception as err:
            result['result'] = -200
            result['resultDesc'] = '数据库错误 \n%s' % err
            return jsonify(result)



@test_manager.route('/test_manager/find_test_class/')
def find_test_class():
    test_file_path = request.args.get('file_path')
    class_list = TestEngine.find_test_class(test_file_path)
    if isinstance(class_list, str):
        result = {'result': False, 'des': class_list}
    else:
        result = {'result': True, 'class_list': class_list}
    return jsonify(result)

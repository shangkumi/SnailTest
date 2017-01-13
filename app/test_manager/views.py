# coding:utf-8
from app import db
from app.models import Api, Suite
from app.test_manager import test_manager

from flask import render_template, flash, redirect, url_for, request, jsonify

from app.test_manager.test_engine import TestEngine
from utils.Log import Log


class ResultCode:
    SUCCESS = 100
    SAME_API_NAME_ERROR = -100
    FILE_AND_CLASS_BINDED = -101
    DB_ERROR = -200


@test_manager.route('/test_manager/')
def index():
    return render_template('/test_manager/index.html')


@test_manager.route('/test_manager/api_list/', methods=['GET', 'POST'])
def api_list():
    if request.method == 'GET':
        return render_template('/test_manager/api_list.html')
    if request.method == 'POST':
        key_word = request.form.get('key_word')
        apis = Api.query.all()
        if not key_word.strip():
            result = [{'api_id': i.id, 'api_name': i.api_name, 'file_path': i.file_path, 'class_name': i.class_name} for
                      i in apis]
            return jsonify(result)
        result = [{'api_id': i.id, 'api_name': i.api_name, 'file_path': i.file_path, 'class_name': i.class_name} for i
                  in apis if (key_word in i.api_name) or (key_word in i.file_path) or (key_word in i.class_name)]
        return jsonify(result)
    return render_template('/test_manager/api_list.html')


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

        result = {'result': ResultCode.SUCCESS, 'resultDesc': '新增测试接口成功', 'api_id': ''}
        # 验证是否满足条件新建
        if Api.query.filter_by(api_name=api_name).first():
            result['result'] = ResultCode.SAME_API_NAME_ERROR
            result['resultDesc'] = '已有同名接口'
            return jsonify(result)

        api_by_file_path_and_class = Api.query.filter_by(file_path=file_path, class_name=class_name).first()
        if api_by_file_path_and_class:
            result['result'] = ResultCode.FILE_AND_CLASS_BINDED
            result['resultDesc'] = '文件的该类已绑定测试接口: %s' % api_by_file_path_and_class.api_name
            return jsonify(result)

        try:
            api = Api(api_name=api_name, file_path=file_path, class_name=class_name, remark=remark)
            db.session.add(api)
            db.session.commit()
            result['api_id'] = api.id
            return jsonify(result)
        except Exception as err:
            result['result'] = ResultCode.DB_ERROR
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


@test_manager.route('/test_manager/delete_api/')
def delete_api():
    api_id = request.args.get('api_id')
    api = Api.query.get_or_404(int(api_id))
    for test_case in api.test_cases:
        for test_data in test_case.test_datas:
            for suite in Suite.query.all():
                if test_data in suite.test_datas:
                    suite.test_datas.remove(test_data)
                db.session.add(suite)
            db.session.delete(test_data)
        db.session.delete(test_case)
    db.session.delete(api)
    try:
        db.session.commit()
        Log.info('删除成功')
        return jsonify({'result': ResultCode.SUCCESS, 'resultDesc': '删除成功'})
    except Exception as err:
        db.session.rollback()
        return jsonify({'result': ResultCode.DB_ERROR, 'resultDesc': '删除失败'})

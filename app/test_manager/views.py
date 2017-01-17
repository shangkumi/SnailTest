# coding:utf-8
from app import db
from app.models import Api, Suite
from app.test_manager import test_manager

from flask import render_template, flash, redirect, url_for, request, jsonify

from app.test_manager.result_code import ResultCode
from app.test_manager.test_engine import TestEngine
from utils.Log import Log


@test_manager.route('/test_manager/')
def index():
    return render_template('/test_manager/index.html')


@test_manager.route('/test_manager/api_info/')
def api_info():
    api_id = request.args.get('api_id')
    api = Api.query.get_or_404(api_id)
    code = TestEngine.get_test_file_code(api.file_path)
    return render_template('/test_manager/api_info.html', api=api, code=code)


@test_manager.route('/test_manager/api_list/', methods=['GET', 'POST'])
def api_list():
    if request.method == 'GET':
        return render_template('/test_manager/api_list.html')
    if request.method == 'POST':
        key_word = request.form.get('key_word')
        apis = Api.query.all()
        result = ResultCode.SUCCESS
        if not key_word.strip():
            result['api_list'] = [
                {'api_id': i.id, 'api_name': i.api_name, 'file_path': i.file_path, 'class_name': i.class_name} for i in
                apis]
            return jsonify(result)
        result['api_list'] = [
            {'api_id': i.id, 'api_name': i.api_name, 'file_path': i.file_path, 'class_name': i.class_name} for i
            in apis if (key_word in i.api_name) or (key_word in i.file_path) or (key_word in i.class_name)]
        return jsonify(result)
    return render_template('/test_manager/api_list.html')


@test_manager.route('/test_manager/add_test_case/')
def add_test_case():
    if request.method == 'GET':
        api_id = request.args.get('api_id')
        api = Api.query.get_or_404(api_id)
        result = TestEngine.get_test_function(api_id)
        if result == ResultCode.FILE_NOT_FOUND or result == ResultCode.CLASS_NOT_FOUND:
            flash(result['resultDesc'] + '请修改测试接口')
            return redirect(url_for('test_manager.modify_api', api_id=api_id))

        return render_template('/test_manager/add_test_case.html', api=api, func_list=result['func_list'])


# @test_manager.route('/test_manager/get_test_function/')
# def get_test_function():
#     api_id = request.args.get('api_id')
#     result = TestEngine.get_test_function(api_id)
#     return jsonify(result)


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

        # 验证是否满足条件新建
        if Api.query.filter_by(api_name=api_name).first():
            result = ResultCode.SAME_API_NAME_ERROR
            return jsonify(result)

        api_by_file_path_and_class = Api.query.filter_by(file_path=file_path, class_name=class_name).first()
        if api_by_file_path_and_class:
            result = ResultCode.FILE_AND_CLASS_BINDED
            return jsonify(result)

        try:
            api = Api(api_name=api_name, file_path=file_path, class_name=class_name, remark=remark)
            db.session.add(api)
            db.session.commit()
            result = ResultCode.SUCCESS
            result['api_id'] = api.id
            return jsonify(result)
        except Exception as err:
            result = ResultCode.DB_ERROR
            Log.error('新建测试接口失败\n%s' % err)
            return jsonify(result)


@test_manager.route('/test_manager/modify_api', methods=['GET', 'POST'])
def modify_api():
    if request.method == 'GET':
        api_id = request.args.get('api_id')
        api = Api.query.get_or_404(api_id)
        file_dict = TestEngine.get_test_case_file_list()
        return render_template('/test_manager/modify_api.html', api=api, file_dict=file_dict)
    if request.method == 'POST':
        api_id = request.form.get('api_id')
        api_name = request.form.get('api_name')
        file_path = request.form.get('file_path')
        class_name = request.form.get('class_name')
        remark = request.form.get('remark')

        api = Api.query.get_or_404(api_id)
        # 如api_name修改, 且数据库中有修改后的api_name, 要报错
        if api_name != api.api_name and Api.query.filter_by(api_name=api_name).first():
            result = ResultCode.SAME_API_NAME_ERROR
            return jsonify(result)

        if (file_path != api.file_path
            or class_name != api.class_name
            and Api.query.filter_by(file_path=file_path, class_name=class_name).first()):
            result = ResultCode.FILE_AND_CLASS_BINDED
            return jsonify(result)

        try:
            api.api_name = api_name
            api.file_path = file_path
            api.class_name = class_name
            api.remark = remark
            db.session.add(api)
            db.session.commit()
            result = ResultCode.SUCCESS
            return jsonify(result)
        except Exception as err:
            result = ResultCode.DB_ERROR
            Log.error('修改测试接口失败\n%s' % err)
            return jsonify(result)


@test_manager.route('/test_manager/find_test_class/')
def find_test_class():
    """通过文件路径, 获取文件中的类"""
    test_file_path = request.args.get('file_path')
    result = TestEngine.find_test_class(test_file_path)
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
        return jsonify(ResultCode.SUCCESS)
    except Exception as err:
        db.session.rollback()
        return jsonify(ResultCode.DB_ERROR)

# coding:utf-8
import os

from app import db
from app.models import Api, Suite, TestCase, TestData, TestReport
from app.test_manager import test_manager

from flask import render_template, flash, redirect, url_for, request, jsonify

from app.test_manager.result_code import ResultCode
from app.test_manager.test_engine import TestEngine
from config import BASE_DIR
from utils.Log import Log


@test_manager.route('/')
@test_manager.route('/test_manager/')
def index():
    return render_template('/test_manager/index.html')


#####################
# 测试接口相关
#####################
@test_manager.route('/test_manager/api_list/', methods=['GET', 'POST'])
def api_list():
    if request.method == 'GET':
        return render_template('/test_manager/api_list.html')
    if request.method == 'POST':
        key_word = request.form.get('key_word')
        apis = Api.query.all()
        result = ResultCode().SUCCESS
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


@test_manager.route('/test_manager/api_info/')
def api_info():
    api_id = request.args.get('api_id')
    api = Api.query.get_or_404(api_id)
    code = TestEngine.get_test_file_code(api.file_path)
    if isinstance(code, str):
        return render_template('/test_manager/api_info.html', api=api, code=code)
    else:
        flash(code['resultDesc'])
        return redirect(url_for('test_manager.modify_api', api_id=api_id))


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
            result = ResultCode().SAME_API_NAME_ERROR
            return jsonify(result)

        api_by_file_path_and_class = Api.query.filter_by(file_path=file_path, class_name=class_name).first()
        if api_by_file_path_and_class:
            result = ResultCode().FILE_AND_CLASS_BINDED
            return jsonify(result)

        try:
            api = Api(api_name=api_name, file_path=file_path, class_name=class_name, remark=remark)
            db.session.add(api)
            db.session.commit()
            result = ResultCode().SUCCESS
            result['api_id'] = api.id
            return jsonify(result)
        except Exception as err:
            result = ResultCode().DB_ERROR
            Log.error('新建测试接口失败\n%s' % err)
            return jsonify(result)


@test_manager.route('/test_manager/delete_api/')
def delete_api():
    api_id = request.args.get('api_id')
    api = Api.query.get_or_404(api_id)
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
        return jsonify(ResultCode().SUCCESS)
    except Exception as err:
        db.session.rollback()
        Log.error('删除接口失败')
        return jsonify(ResultCode().DB_ERROR)


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
            result = ResultCode().SAME_API_NAME_ERROR
            return jsonify(result)

        if (file_path != api.file_path
            or class_name != api.class_name
            and Api.query.filter_by(file_path=file_path, class_name=class_name).first()):
            result = ResultCode().FILE_AND_CLASS_BINDED
            return jsonify(result)

        try:
            api.api_name = api_name
            api.file_path = file_path
            api.class_name = class_name
            api.remark = remark
            db.session.add(api)
            db.session.commit()
            result = ResultCode().SUCCESS
            return jsonify(result)
        except Exception as err:
            result = ResultCode().DB_ERROR
            Log.error('修改测试接口失败\n%s' % err)
            return jsonify(result)


#####################
# 测试用例相关
#####################
@test_manager.route('/test_manager/test_case_info/')
def test_case_info():
    test_case_id = request.args.get('test_case_id')
    test_case = TestCase.query.get_or_404(test_case_id)
    code = TestEngine.get_test_file_code(test_case.api.file_path)
    if isinstance(code, str):
        return render_template('/test_manager/test_case_info.html', test_case=test_case, code=code)
    else:
        flash(code['resultDesc'])
        return redirect(url_for('test_manager.modify_api', api_id=test_case.api.id))


@test_manager.route('/test_manager/add_test_case/', methods=['GET', 'POST'])
def add_test_case():
    if request.method == 'GET':
        api_id = request.args.get('api_id')
        api = Api.query.get_or_404(api_id)
        result = TestEngine.get_test_function(api_id)
        if result == ResultCode().FILE_NOT_FOUND or result == ResultCode().CLASS_NOT_FOUND:
            flash(result['resultDesc'] + '请修改测试接口')
            return redirect(url_for('test_manager.modify_api', api_id=api_id))
        return render_template('/test_manager/add_test_case.html', api=api, func_list=result['func_list'])
    if request.method == 'POST':
        api_id = request.form.get('api_id')
        test_case_name = request.form.get('test_case_name')
        func_name = request.form.get('func_name')
        remark = request.form.get('remark')
        api = Api.query.get_or_404(api_id)
        if not api:
            return jsonify(ResultCode().API_NOT_FOUND)
        if test_case_name in [i.test_case_name for i in api.test_cases]:
            return jsonify(ResultCode().SAME_TEST_CASE_NAME_ERROR)
        if func_name in [i.func_name for i in api.test_cases]:
            return jsonify(ResultCode().FUNC_BINDED)
        try:
            test_case = TestCase(test_case_name=test_case_name, func_name=func_name, remark=remark, api_id=api_id)
            db.session.add(test_case)
            db.session.commit()
            result = ResultCode().SUCCESS
            result['test_case_id'] = test_case.id
            return jsonify(result)
        except Exception as err:
            result = ResultCode().DB_ERROR
            Log.error('新建用例失败\n%s' % err)
            return jsonify(result)


@test_manager.route('/test_manager/delete_test_case/')
def delete_test_case():
    test_case_id = request.args.get('test_case_id')
    test_case = TestCase.query.get_or_404(test_case_id)
    for test_data in test_case.test_datas:
        for suite in Suite.query.all():
            if test_data in suite.test_datas:
                suite.test_datas.remove(test_data)
            db.session.add(suite)
        db.session.delete(test_data)
    db.session.delete(test_case)
    try:
        db.session.commit()
        Log.info('用例删除成功')
        return jsonify(ResultCode().SUCCESS)
    except Exception as err:
        db.session.rollback()
        Log.error('删除用例失败')
        return jsonify(ResultCode().DB_ERROR)


@test_manager.route('/test_manager/modify_test_case/', methods=['GET', 'POST'])
def modify_test_case():
    if request.method == 'GET':
        test_case_id = request.args.get('test_case_id')
        test_case = TestCase.query.get_or_404(test_case_id)
        result = TestEngine.get_test_function(test_case.api_id)
        if result == ResultCode().FILE_NOT_FOUND or result == ResultCode().CLASS_NOT_FOUND:
            flash(result['resultDesc'] + '请修改测试接口')
            return redirect(url_for('test_manager.modify_api', api_id=test_case.api_id))
        return render_template('/test_manager/modify_test_case.html', test_case=test_case,
                               func_list=result['func_list'])
    if request.method == 'POST':
        test_case_id = request.form.get('test_case_id')
        test_case_name = request.form.get('test_case_name')
        func_name = request.form.get('func_name')
        remark = request.form.get('remark')

        test_case = TestCase.query.get_or_404(test_case_id)
        if test_case_name != test_case.test_case_name and TestCase.query.filter_by(api_id=test_case.api_id,
                                                                                   test_case_name=test_case_name).first():
            return jsonify(ResultCode().SAME_TEST_CASE_NAME_ERROR)

        if func_name != test_case.func_name and TestCase.query.filter_by(api_id=test_case.api_id,
                                                                         func_name=func_name).first():
            return jsonify(ResultCode().FUNC_BINDED)

        try:
            test_case.test_case_name = test_case_name
            test_case.func_name = func_name
            test_case.remark = remark
            db.session.add(test_case)
            db.session.commit()
            return jsonify(ResultCode().SUCCESS)
        except Exception as err:
            result = ResultCode().DB_ERROR
            Log.error('修改测试用例失败\n%s' % err)
            return jsonify(result)


#####################
# 测试数据相关
#####################
@test_manager.route('/test_manager/test_data_info/')
def test_data_info():
    test_data_id = request.args.get('test_data_id')
    test_data = TestData.query.get_or_404(test_data_id)
    code = TestEngine.get_test_file_code(test_data.test_case.api.file_path)
    if isinstance(code, str):
        return render_template('/test_manager/test_data_info.html', test_data=test_data, code=code)
    else:
        flash(code['resultDesc'])
        return redirect(url_for('test_manager.modify_api', api_id=test_data.test_case.api.id))


@test_manager.route('/test_manager/add_test_data/', methods=['GET', 'POST'])
def add_test_data():
    if request.method == 'GET':
        test_case_id = request.args.get('test_case_id')
        test_case = TestCase.query.get_or_404(test_case_id)
        code = TestEngine.get_test_file_code(test_case.api.file_path)
        if isinstance(code, str):
            return render_template('/test_manager/add_test_data.html', test_case=test_case, code=code)
        else:
            flash(code['resultDesc'])
            return redirect(url_for('test_manager.modify_api', api_id=test_case.api.id))
    if request.method == 'POST':
        test_case_id = request.form.get('test_case_id')
        test_data_name = request.form.get('test_data_name')
        values = request.form.get('values')
        tags = request.form.get('tags')
        remark = request.form.get('remark')
        test_case = TestCase.query.get_or_404(test_case_id)
        result = TestEngine.get_test_function(test_case.api.id)
        if result['result'] != 100:
            return jsonify(result)
        if result['result'] == 100 and test_case.func_name not in result['func_list']:
            return jsonify(ResultCode().FUNC_NOT_FOUND)
        if TestData.query.filter_by(test_case_id=test_case_id, test_data_name=test_data_name).first():
            return jsonify(ResultCode().SAME_TEST_DATA_NAME_ERROR)
        try:
            test_data = TestData(test_data_name=test_data_name, values=values, tags=tags, remark=remark,
                                 test_case_id=test_case.id)
            db.session.add(test_data)
            db.session.commit()
            result = ResultCode().SUCCESS
            result['test_data_id'] = test_data.id
            return jsonify(result)
        except Exception as err:
            result = ResultCode().DB_ERROR
            Log.error('新建测试数据失败\n%s' % err)
            return jsonify(result)


@test_manager.route('/test_manager/delete_test_data/')
def delete_test_data():
    test_data_id = request.args.get('test_data_id')
    test_data = TestData.query.get_or_404(test_data_id)
    for suite in Suite.query.all():
        if test_data in suite.test_datas:
            suite.test_datas.remove(test_data)
        db.session.add(suite)
    db.session.delete(test_data)
    try:
        db.session.commit()
        Log.info('测试数据删除成功')
        return jsonify(ResultCode().SUCCESS)
    except Exception as err:
        db.session.rollback()
        Log.error('删除测试数据失败')
        return jsonify(ResultCode().DB_ERROR)


@test_manager.route('/test_manager/modify_test_data/', methods=['GET', 'POST'])
def modify_test_data():
    if request.method == 'GET':
        test_data_id = request.args.get('test_data_id')
        test_data = TestData.query.get_or_404(test_data_id)
        result = TestEngine.get_test_function(test_data.test_case.api_id)
        if result == ResultCode().FILE_NOT_FOUND or result == ResultCode().CLASS_NOT_FOUND:
            flash(result['resultDesc'] + '请修改测试接口')
            return redirect(url_for('test_manager.modify_api', api_id=test_data.test_case.api_id))
        return render_template('/test_manager/modify_test_data.html', test_data=test_data)
    if request.method == 'POST':
        test_data_id = request.form.get('test_data_id')
        test_data_name = request.form.get('test_data_name')
        values = request.form.get('values')
        tags = request.form.get('tags')
        remark = request.form.get('remark')

        test_data = TestData.query.get_or_404(test_data_id)
        if test_data_name != test_data.test_data_name and TestData.query.filter_by(test_case_id=test_data.test_case_id,
                                                                                   test_data_name=test_data_name).first():
            return jsonify(ResultCode().SAME_TEST_DATA_NAME_ERROR)
        try:
            test_data.test_data_name = test_data_name
            test_data.values = values
            test_data.tags = tags
            test_data.remark = remark
            db.session.add(test_data)
            db.session.commit()
            return jsonify(ResultCode().SUCCESS)
        except Exception as err:
            result = ResultCode().DB_ERROR
            Log.error('修改测试数据失败\n%s' % err)
            return jsonify(result)


#####################
# 测试套件相关
#####################
@test_manager.route('/test_manager/suite_list/')
def suite_list():
    if request.method == 'GET':
        suites = Suite.query.all()
        return render_template('/test_manager/suite_list.html', suites=suites)


@test_manager.route('/test_manager/suite_info/')
def suite_info():
    suite_id = request.args.get('suite_id')
    suite = Suite.query.get_or_404(suite_id)
    test_datas = suite.test_datas
    check_list = ['td_%s' % test_data.id for test_data in test_datas]
    test_cases_list = list({'tc_%s' % test_data.test_case_id for test_data in test_datas})
    apis_list = list({'api_%s' % test_data.test_case.api_id for test_data in test_datas})
    check_list.extend(test_cases_list)
    check_list.extend(apis_list)
    apis = Api.query.all()
    return render_template('/test_manager/suite_info.html', apis=apis, check_list=check_list, suite=suite)


@test_manager.route('/test_manager/add_suite/', methods=['GET', 'POST'])
def add_suite():
    if request.method == 'GET':
        apis = Api.query.all()
        return render_template('/test_manager/add_suite.html', apis=apis)
    if request.method == 'POST':
        suite_name = request.form.get('suite_name')
        remark = request.form.get('remark')
        if not suite_name:
            flash('测试套件名不能为空')
            return redirect(url_for('test_manager.add_suite'))
        if Suite.query.filter_by(suite_name=suite_name).first():
            flash('已有相同名称的测试套件')
            return redirect(url_for('test_manager.add_suite'))
        test_datas = [TestData.query.get(int(i.replace('td_', ''))) for i in request.form.keys() if i.startswith('td_')]
        suite = Suite(suite_name=suite_name, remark=remark)
        suite.test_datas = test_datas
        db.session.add(suite)
        db.session.commit()
        flash('测试套件添加成功')
        return redirect(url_for('test_manager.suite_list'))


@test_manager.route('/test_manager/delete_suite/')
def delete_suite():
    suite_id = request.args.get('suite_id')
    suite = Suite.query.get_or_404(suite_id)
    for test_report in suite.test_reports:
        report_file = os.path.join(BASE_DIR, 'test_case', test_report.report_file)
        if os.path.exists(report_file):
            os.remove(report_file)
        db.session.delete(test_report)
    for test_data in suite.test_datas:
        test_data.suites.remove(suite)
        db.session.add(test_data)
    db.session.delete(suite)
    try:
        db.session.commit()
        Log.info('测试套件已删除成功')
        return jsonify(ResultCode().SUCCESS)
    except Exception as err:
        db.session.rollback()
        Log.error('删除测试套件失败\n%s' % err)
        return jsonify(ResultCode().DB_ERROR)


@test_manager.route('/test_manager/modify_suite/', methods=['GET', 'POST'])
def modify_suite():
    if request.method == 'GET':
        suite_id = request.args.get('suite_id')
        suite = Suite.query.get_or_404(suite_id)
        test_datas = suite.test_datas
        check_list = ['td_%s' % test_data.id for test_data in test_datas]
        test_cases_list = list({'tc_%s' % test_data.test_case_id for test_data in test_datas})
        apis_list = list({'api_%s' % test_data.test_case.api_id for test_data in test_datas})
        check_list.extend(test_cases_list)
        check_list.extend(apis_list)
        apis = Api.query.all()
        return render_template('/test_manager/modify_suite.html', apis=apis, check_list=check_list, suite=suite)
    if request.method == 'POST':
        suite_id = request.form.get('suite_id')
        suite_name = request.form.get('suite_name')
        remark = request.form.get('remark')
        Log.info('id: %s  name: %s  remark: %s ' % (suite_id, suite_name, remark))
        if not suite_name:
            flash('测试套件名不能为空')
            return redirect(url_for('test_manager.modify_suite', suite_id=suite_id))
        suite = Suite.query.get_or_404(suite_id)
        if suite_name != suite.suite_name and Suite.query.filter_by(suite_name=suite_name).first():
            flash('已有相同的测试套件名')
            return redirect(url_for('test_manager.modify_suite', suite_id=suite_id))
        test_datas = [TestData.query.get(int(i.replace('td_', ''))) for i in request.form.keys() if i.startswith('td_')]
        suite.suite_name = suite_name
        suite.remark = remark
        suite.test_datas = test_datas
        try:
            db.session.add(suite)
            db.session.commit()
            Log.info('测试套件修改成功')
            flash('测试套件修改成功')
            return redirect(url_for('test_manager.suite_info', suite_id=suite.id))
        except Exception as err:
            Log.error('测试套件修改失败\n%s' % err)
            flash('测试套件修改失败')
            return redirect(url_for('test_manager.modify_suite', suite_id=suite.id))


#####################
# 测试结果相关
#####################
@test_manager.route('/test_manager/execute_suite/')
def execute_suite():
    suite_id = request.args.get('suite_id')
    suite = Suite.query.get_or_404(suite_id)
    test_engine = TestEngine(suite.test_datas)
    result = test_engine.execute_test()
    report_info = dict(result['result'])
    report_status = report_info['Status'].split(' ')
    r = dict([report_status[i:i + 2] for i in range(0, len(report_status), 2)])
    pass_num = r.get('Pass', 0)
    failed_num = r.get('Failure', 0)
    error_num = r.get('Error', 0)

    test_report = TestReport(report_file=result['report_file_name'], pass_num=int(pass_num), failed_num=int(failed_num),
                             error_num=int(error_num),
                             remark='测试集: %s-->%s' % (suite.suite_name, os.path.basename(result['report_file_name'])),
                             suite_id=suite_id)
    try:
        db.session.add(test_report)
        db.session.commit()
        Log.info('测试套件执行成功')
        Log.info(ResultCode().SUCCESS)
        return jsonify(ResultCode().SUCCESS)
    except Exception as err:
        Log.error('测试套件执行失败\n%s' % err)
        return jsonify(ResultCode().DB_ERROR)


@test_manager.route('/test_manager/get_test_report/')
def get_test_report():
    test_report_id = request.args.get('test_report_id')
    test_report = TestReport.query.get_or_404(test_report_id)
    suite_id = test_report.suite_id
    if os.path.exists(os.path.join(BASE_DIR, 'report', test_report.report_file)):
        report = open(os.path.join(BASE_DIR, 'report', test_report.report_file)).read()
        return report
    else:
        flash('未找到该测试报告, 自动删除该记录')
        db.session.delete(test_report)
        try:
            db.commit()
        except Exception as err:
            Log.error('删除report失败')
            db.rollback()
        return redirect(url_for('test_manager.suite_info', suite_id=suite_id))


@test_manager.route('/test_manager/delete_test_report/')
def delete_test_report():
    test_report_id = request.args.get('test_report_id')
    test_report = TestReport.query.get_or_404(test_report_id)
    db.session.delete(test_report)
    if os.path.exists(os.path.join(BASE_DIR, 'report', test_report.report_file)):
        os.remove(os.path.join(BASE_DIR, 'report', test_report.report_file))
    try:
        db.session.commit()
        Log.info('删除report成功')
        flash('删除report成功')
        return redirect(url_for('test_manager.suite_info', suite_id=test_report.suite_id))
    except Exception as err:
        Log.error('删除report失败')
        db.session.rollback()
        flash('删除report失败')
        return redirect(url_for('test_manager.suite_info', suite_id=test_report.suite_id))


@test_manager.route('/test_manager/execute_test_tmp/')
def execute_test_tmp():
    test_data_id = request.args.get('test_data_id')
    test_data = TestData.query.get_or_404(test_data_id)
    test_engine = TestEngine([test_data])
    result = test_engine.execute_test(tmp=True)
    return result['html']


#####################
# 其它
#####################
@test_manager.route('/test_manager/find_test_class/')
def find_test_class():
    """通过文件路径, 获取文件中的类"""
    test_file_path = request.args.get('file_path')
    result = TestEngine.find_test_class(test_file_path)
    return jsonify(result)


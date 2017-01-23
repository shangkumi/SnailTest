# coding:utf-8
import datetime

from . import db


class Api(db.Model):
    __tablename__ = 'api'
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(64), unique=True, index=True)
    file_path = db.Column(db.String(64))
    class_name = db.Column(db.String(64))
    remark = db.Column(db.Text())

    test_cases = db.relationship('TestCase', backref='api')

    def __repr__(self):
        return '<Api %r>' % self.api_name


class TestCase(db.Model):
    __tablename__ = 'test_case'
    id = db.Column(db.Integer, primary_key=True)
    test_case_name = db.Column(db.String(64), index=True)
    func_name = db.Column(db.String(64))
    remark = db.Column(db.Text())

    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    test_datas = db.relationship('TestData', backref='test_case')

    def __repr__(self):
        return '<TestCase %r>' % self.test_case_name


class TestData(db.Model):
    __tablename__ = 'test_data'
    id = db.Column(db.Integer, primary_key=True)
    test_data_name = db.Column(db.String(64))
    values = db.Column(db.Text())
    tags = db.Column(db.Text())
    remark = db.Column(db.Text())

    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'))


suiteData = db.Table('suiteData',
                     db.Column('suite_id', db.Integer, db.ForeignKey('suite.id')),
                     db.Column('data_id', db.Integer, db.ForeignKey('test_data.id')), )


class Suite(db.Model):
    __tablename__ = 'suite'
    id = db.Column(db.Integer, primary_key=True)
    suite_name = db.Column(db.String(64), unique=True, index=True)
    remark = db.Column(db.Text())

    test_reports = db.relationship('TestReport', backref='suite')
    test_datas = db.relationship('TestData', secondary=suiteData,
                                 backref=db.backref('suites', lazy='dynamic'),
                                 lazy='dynamic')

    def __repr__(self):
        return '<Suite %r>' % self.suite_name


class TestReport(db.Model):
    __tablename__ = 'test_report'
    id = db.Column(db.Integer, primary_key=True)
    report_file = db.Column(db.String(64))
    pass_num = db.Column(db.Integer)
    failed_num = db.Column(db.Integer)
    error_num = db.Column(db.Integer)
    remark = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    suite_id = db.Column(db.Integer, db.ForeignKey('suite.id'))

    def __repr__(self):
        return '<TestReport %r>' % self.id

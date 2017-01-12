# coding:utf-8
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, ValidationError, TextAreaField
from wtforms.validators import DataRequired

from app.models import Api


class ModifyApiForm(FlaskForm):
    api_name = StringField('接口名称', validators=[DataRequired()])
    file_path = StringField('接口测试文件路径', validators=[DataRequired()])
    class_name = StringField('接口测试类名', validators=[DataRequired()])
    remark = TextAreaField('备注')
    submit = SubmitField('提交')


class AddApiForm(ModifyApiForm):
    def validate_api_name(self, field):
        if Api.query.filter_by(api_name=field.data).first():
            raise ValidationError('已有相同的项目名')

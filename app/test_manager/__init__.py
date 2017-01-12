# coding:utf-8
from flask import Blueprint

test_manager = Blueprint('test_manager', __name__)

from . import views, errors

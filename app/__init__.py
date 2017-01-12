# coding:utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import AppConfig

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    AppConfig.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)

    from .test_manager import test_manager as test_manager_blueprint
    app.register_blueprint(test_manager_blueprint)

    return app

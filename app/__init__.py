#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/1 下午11:02
# @Author  : zhuo_hf@foxmail.com
# @Site    :
# @File    : *.py
# @Software: PyCharm
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .logtool import logtool as logtool_blueprint
    app.register_blueprint(logtool_blueprint, url_prefix='/logtool')

    return app

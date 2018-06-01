#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/1 下午11:10
# @Author  : zhuo_hf@foxmail.com
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
from flask import Blueprint

logtool = Blueprint('logtool', __name__)

from . import views

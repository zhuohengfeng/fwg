from flask import render_template, redirect, url_for, abort, flash
from . import logtool



@logtool.route('/')
def index():
    return render_template('log.html')
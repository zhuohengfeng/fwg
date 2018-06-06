#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/6 11:05
# @Author  : zhuo_hf@foxmail.com
# @Site    :
# @File    : xxx.py
# @Software: PyCharm
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, SearchForm, AnalysisForm
from .. import db
from ..models import Permission, Role, User, Post
from ..decorators import admin_required
from werkzeug.utils import secure_filename
from .analysis.utils import pss_chart, wakelock_line_chart_process
import os
import tempfile
import shutil

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


# =============================================================
@main.route('/analysis', methods=['GET', 'POST'])
#@login_required
def analysis():
    form = AnalysisForm()
    if form.validate_on_submit():
        analysisType = int(form.analysisType.data)
        uploadFile = form.uploadFile.data
        # 对文件名进行包装，为了安全,不过对中文的文件名显示有问题
        #filename = secure_filename(uploadFile.filename)

        # Unpack the zipfile into the temporary directory
        url = pss_chart(uploadFile, False, True, False)
        name = url.split("\\")[-1]
        base_dir = os.path.dirname(__file__)
        url = os.path.join(base_dir, name)
        # return render_template('index.html', url=url)
        return "文件上传成功url=".format(url)
    else:
        filename = None
    return render_template('analysis.html', form=form, filename=filename)



@main.route('/search', methods=['GET', 'POST'])
#@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        pass
    return render_template('search.html', form=form)

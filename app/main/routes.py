from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, ChangePasswordForm, \
                           FindUserForm, TaskForm, AddTaskForm
from app.models import User, Task
from app.main import bp
from app.queryes import *


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    tasks = get_user_tasks_and_customers(current_user)
    return render_template('index.html', title='Tasks',
                           tasks=tasks)


@bp.route('/tasks')
@login_required
def tasks():
    tasks = get_tasks()
    return render_template('tasks.html', title='Tasks', tasks=tasks)


@bp.route('/task/<taskid>', methods=['GET', 'POST'])
@login_required
def task(taskid):
    task = Task.query.filter_by(id=taskid).first_or_404()
    if task.executor != -1 and not (task.executor == current_user.id or task.customer == current_user.id):
        return redirect(url_for('main.index'))
    form = TaskForm()
    if task.executor != -1:
        form.submit.label.text = 'Done'
    if form.validate_on_submit():
        if task.customer != current_user.id:
            if task.executor == -1:
                task.executor = current_user.id
            else:
                task.is_end = True    
            db.session.add(task)
            db.session.commit()
            return redirect(url_for('main.index'))
    executor = User.query.get(task.executor)
    customer = User.query.get(task.customer)
    task = {'task': task, 'executor': executor, 'customer': customer}
    return render_template('task.html', title='Task', task=task, form=form)


@bp.route('/create/task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(description=form.description.data, customer=current_user.id)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template("add_task.html", form=form)


@bp.route('/added/tasks')
@login_required
def added_task():
    tasks = get_added_tasks(current_user)
    return render_template("tasks.html", tasks=tasks)


@bp.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)


@bp.route('/edit_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        password_old = form.password_old.data
        password = form.password.data
        password2 = form.password2.data
        current_user.set_password(password)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.change_password'))
    return render_template('change_profile.html', title='Change Password',
                            form=form, label='Change Password')


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.change_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email 
    return render_template('change_profile.html', title='Edit Profile',
                            form=form, label='Edit Profile')


@bp.route('/find', methods=['GET', 'POST'])
@login_required
def find():
    users = User.query.all()
    form = FindUserForm()
    if form.validate_on_submit():
        username = form.username.data
        users = find_users(username)
    return render_template('find.html', title='Find User', 
                           users=users, form=form)

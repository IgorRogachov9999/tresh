from app import db
from app.models import User, Task
from flask_login import current_user

# (task, customer, executor)

def get_user_tasks_and_customers(user):
    all_tasks = Task.query.all()
    return [{'task': task, 'customer': User.query.get(task.customer), 'executor': User.query.get(task.executor)} for task in all_tasks if task.executor == user.id and not task.is_end]


def get_tasks():
    tasks = Task.query.order_by(Task.create_time.desc())
    return [{'task': task, 'customer': User.query.get(task.customer), 'executor': User.query.get(task.executor)} for task in tasks if task.executor == -1]


def get_added_tasks(user):
    tasks = Task.query.order_by(Task.create_time.desc())
    return [{'task': task, 'customer': User.query.get(task.customer), 'executor': User.query.get(task.executor)} for task in tasks if task.customer == user.id and not task.is_end]


def find_users(username):
    all_users = User.query.all()
    return all_users if username == '' else [user for user in all_users if username in user.username]

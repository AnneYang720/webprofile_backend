from flask import Blueprint

user_blue = Blueprint("user", __name__)
task_blue = Blueprint("task", __name__)
worker_blue = Blueprint("worker", __name__)
admin_blue = Blueprint("admin", __name__)

from server.api import user
from server.api import task
from server.api import worker
from server.api import admin
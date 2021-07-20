from flask import Blueprint

user_blue = Blueprint("user", __name__)
task_blue = Blueprint("task", __name__)

from server.api import user
from server.api import task
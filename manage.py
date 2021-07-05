import os

from . import creat_app
from . import models
from flask_script import Manager

app = creat_app()
manager = Manager(app)

if __name__ == "__main__":
    manager.run()


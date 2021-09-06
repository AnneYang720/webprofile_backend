import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request
from flask_cors import *
from server.config import APP_ENV, config  


def setupLogging(level):
    '''创建日志记录'''
    # 设置日志的记录等级
    logging.basicConfig(level=level)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    #TODO: 这里的日志记录可以根据日期命名文件名，方便查看每天的日志记录
    file_log_handler = RotatingFileHandler("server/logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    #为全局添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

def create_app():
    '''
    工厂函数，创建APP实例
    :return app实例
    '''
    setupLogging(config[APP_ENV].LOGGING_LEVEL)

    app = Flask(__name__)
    # CORS(app, supports_credentials=True)
    app.config.from_object(config[APP_ENV])

    # @app.route('/')
    # def index():
    #     return '<h1>Hello World!</h1>'

    # CORS(app, resources=r'/*')

    #注册 api 蓝图
    from server.api import user_blue, task_blue, worker_blue, admin_blue
    app.register_blueprint(user_blue)
    app.register_blueprint(task_blue, url_prefix='/task')
    app.register_blueprint(worker_blue)
    app.register_blueprint(admin_blue, url_prefix='/admin')

    CORS(app, resources=r'/*')
    
    return app
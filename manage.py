import os

from . import creat_app
from flask_script import Manager
from flask_pymongo import PyMongo
from flask_httpauth import HTTPTokenAuth
from flask_jwt_extended import JWTManager
from minio import Minio
from backend.config import APP_ENV, config

app = creat_app()
manager = Manager(app)

# Setup the Flask-JWT-Extended extension
jwt = JWTManager(app)

# Setup the Minio
client = Minio(
    endpoint=config[APP_ENV].M_ENDPOINT,
    access_key=config[APP_ENV].M_ACCESS_KEY,
    secret_key=config[APP_ENV].M_SECRET_KEY,
    region=config[APP_ENV].M_REGION
)

#创建auth
token_auth = HTTPTokenAuth(scheme='Bearer')

# 创建MongoDB数据库连接对象
mongo_conn = PyMongo.MongoClient(host=config[APP_ENV].MONGO_HOST,port=config[APP_ENV].MONGO_PORT, username=config[APP_ENV].MONGO_USERNAME, password=config[APP_ENV].MONGO_PWD)
db = mongo_conn[config[APP_ENV].MONGO_DATABASE] # Select the database

if __name__ == "__main__":
    manager.run()


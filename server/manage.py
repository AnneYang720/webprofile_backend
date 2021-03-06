from server import create_app
from flask_script import Manager
from pymongo import MongoClient
from flask_httpauth import HTTPTokenAuth
# from flask_jwt_extended import JWTManager
from minio import Minio
from server.config import APP_ENV, config
import pika

app = create_app()

manager = Manager(app)

# # Setup the Flask-JWT-Extended extension
# jwt = JWTManager(app)

# Setup the Minio
client = Minio(
    endpoint=config[APP_ENV].M_ENDPOINT,
    access_key=config[APP_ENV].M_ACCESS_KEY,
    secret_key=config[APP_ENV].M_SECRET_KEY,
    region=config[APP_ENV].M_REGION,
    secure=False
)

#创建auth
token_auth = HTTPTokenAuth(scheme='Bearer')

# 创建MongoDB数据库连接对象
mongo_conn = MongoClient(host=config[APP_ENV].MONGO_HOST,port=config[APP_ENV].MONGO_PORT, username=config[APP_ENV].MONGO_USERNAME, password=config[APP_ENV].MONGO_PWD)
db = mongo_conn[config[APP_ENV].MONGO_DATABASE] # Select the database

#创建MQ连接
credentials = pika.PlainCredentials(config[APP_ENV].MQ_USERNAME, config[APP_ENV].MQ_PASSWORD)
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=config[APP_ENV].MQ_HOST, virtual_host='/', credentials=credentials, heartbeat=0))
channel = connection.channel()
channel.exchange_declare(exchange=config[APP_ENV].MQ_EXCHANGE, exchange_type='direct')

if __name__ == "__main__":
    # TODO 插入默认admin
    # print(app.url_map)
    manager.debug = True
    manager.run()


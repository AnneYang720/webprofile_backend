import logging
import os

APP_ENV = "testing"

def getenv(name: str, default=''):
    return os.environ.get('APP_' + name, default)

class BaseConfig:

    '''
    根据业务和场景添加其他相关配置
    '''
    # 配置MongoDB数据库
    MONGO_HOST = getenv('MONGO_HOST', '127.0.0.1')
    MONGO_PORT = getenv('MONGO_PORT', 27017)
    MONGO_USERNAME = getenv('MONGO_USERNAME', '')
    MONGO_PWD = getenv('MONGO_PWD', '')
    MONGO_DATABASE = getenv('MONGO_DATABASE', 'webprofile')
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY', 'super-secret')

    # 配置Minio
    M_ENDPOINT = getenv('M_ENDPOINT', 's3.example.com:9000')
    M_ACCESS_KEY = getenv('M_ACCESS_KEY', 'access_key')
    M_SECRET_KEY = getenv('M_SECRET_KEY', 'secret_key')
    M_REGION = getenv('M_REGION', 'us-east-1')

    # 配置MQ
    MQ_EXCHANGE = getenv('MQ_EXCHANGE', 'meg_tasks')
    MQ_HOST = getenv('MQ_HOST', 'localhost')
    MQ_USERNAME = getenv('MQ_USERNAME', 'webprofile')
    MQ_PASSWORD = getenv('MQ_PASSWORD', 'webprofile')


class TestingConfig(BaseConfig):
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

class DevelopmentConfig(BaseConfig):
    DEBUG = False
    LOGGING_LEVEL = logging.WARNING

config = {
    "testing": TestingConfig,
    "devolopment": DevelopmentConfig,
}

if __name__ == '__main__':
    print(config["testing"])
import logging

APP_ENV = "testing"

class BaseConfig:

    SECRET_KEY = "SECRET_KEY"
    '''
    根据业务和场景添加其他相关配置
    '''
    # 配置MongoDB数据库
    MONGO_HOST = 'MONGO_HOST'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'MONGO_USERNAME'
    MONGO_PWD = 'MONGO_PWD'
    MONGO_DATABASE = 'MONGO_DATABASE'
    JWT_SECRET_KEY = "JWT_SECRET_KEY"

    # 配置Minio
    M_ENDPOINT = 'M_ENDPOINT'
    M_ACCESS_KEY = 'M_ACCESS_KEY'
    M_ACCESS_KEY = 'M_ACCESS_KEY'
    M_REGION = 'M_REGION'


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
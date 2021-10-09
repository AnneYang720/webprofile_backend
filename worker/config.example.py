
class Config:
    # 配置 MQ
    EXCHANGE = 'meg_tasks'  # MQ Exchange 名称，可保持默认

    SERVER_IP = 'YOUR_SERVER_PUBLIC_IP'     # 服务端 IP 地址或域名
    
    BASEURL = f'http://{SERVER_IP}:80/api'  # 服务端 http api 地址，通常无需修改

    MQ_HOST = 'RABBITMQ_HOST_IP'    # RabbitMQ 服务器地址
    MQ_PORT = 5672      # RabbitMQ 端口，默认为 5672

    # worker 基本信息
    NAME = "worker_ex1" # worker命名建议按具体硬件型号
    IP = "10.2.2.2"     # Worker IP，用于前端展示
    PLATFORM = 'x86'
    ID = ''             # ID，注册后自动生成，无需填写
    AUTH = 'public'     # worker 可见性，取值为 public 或 private

    # mge 的版本和路径
    VERS = [
        {'version': '1.4.0', 'path': '/usr/local/megengine', 'args': '--cpu'},
        # {'version': '1.4.0-cuda', 'path': '/usr/local/megengine', 'args': ''}
    ]

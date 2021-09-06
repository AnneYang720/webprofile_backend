from logging import error
import requests
import shlex
import subprocess
import pika
import os
import json
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler

# TODO MQ自己的心跳机制
credentials = pika.PlainCredentials('webprofile', 'webprofile')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost', virtual_host='/', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=Config.NAME, durable=True)
channel.queue_bind(exchange=Config.EXCHANGE, queue=Config.NAME)


def callback(ch, method, properties, body):
    body = json.loads(body.decode())
    print(" [x] Received %r" % body)
    runTask(body['taskId'],body['version'],body['args'])
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


# TODO 区分版本
# TODO MQ runtask失败
def runTask(taskId,version,args): 
    r_geturl = requests.get(Config.BASEURL+'/task/getdownloadurl/'+str(taskId),headers={'content-type':'application/json'})

    result = r_geturl.json()

    if result['flag']:
        mge_url = result['data']['mgeUrl']
        data_url = result['data']['dataUrl']
    else:
        exit()

    r_download_mge = requests.get(mge_url)
    with open("./model.mge", "wb") as mge:
        mge.write(r_download_mge.content)
    mge.close()

    r_download_data = requests.get(data_url)
    with open("./data.npy", "wb") as data:
        data.write(r_download_data.content)
    data.close()

    # 更新状态至running
    formdata = {"taskId":taskId,"state":"running"}
    r_update = requests.post(Config.BASEURL+'/task/updatestate',data = formdata)


    # 运行load and run
    try:
        mge_ver = {}
        for v in Config.VERS:
            if v['version'] == version:
                mge_ver = v
                break
        else:
            raise Exception('unknown version ' + version)

        exec_path = os.path.join(mge_ver['path'], 'bin/load_and_run')
        lib_path = os.path.join(mge_ver['path'], 'lib')
        # TODO: 判断存在性
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = lib_path + ':' + (env['LD_LIBRARY_PATH'] if 'LD_LIBRARY_PATH' in env else '')

        cmd = shlex.split(exec_path + ' model.mge --input data:resnet.npy --profile profile.txt ' + args)
        print(cmd)
        p = subprocess.run(cmd, capture_output=True, env=env)
        
        if p.returncode == 0:
            finalformdata = {"taskId":taskId,"state":"succeeded"}
            output = open('./profile.txt', 'r').read()
            print('load and run succeeded')
            # TODO: stdout里的重要信息保留
        else:
            finalformdata = {"taskId":taskId,"state":"failed"}
            output = p.stderr #p.stdout
            print('load and run has error')
            print(output)

    except Exception as e:
        print("load-and-run failed")
        print(e)

    r_updatestate = requests.post(Config.BASEURL+'/task/updatestate',data = finalformdata)
    result = r_updatestate.json()
    r_uploadoutput = requests.put(result['output_url'],data=output)


# worker注册函数
def workerLogin():
    # 注册worker
    mge_version = [i['version'] for i in Config.VERS]
    formdata = {"name":Config.NAME,"ip":Config.IP,"platform":Config.PLATFORM,"mge_version":mge_version,"auth":Config.AUTH}
    r_login = requests.post(Config.BASEURL+'/worker/add',data = formdata)
    Config.ID = r_login.json()['data']
    print(Config.ID)


# worker更新函数
def workerHeartbeat():
    formdata = {"id":Config.ID}
    r_update = requests.post(Config.BASEURL+'/worker/update',data = formdata)
    print(r_update.json()['message'])


# worker注册（上线）
workerLogin()


# 定时更新状态
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(workerHeartbeat, trigger='cron', second='*/59') # 每10秒运行一次

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=Config.NAME, on_message_callback=callback)

channel.start_consuming()
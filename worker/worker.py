import requests
import shlex
import subprocess
import pika

EXCHANGE = 'meg_tasks'
PLATFORM = 'arm'
BASEURL = 'http://localhost:5000'

credentials = pika.PlainCredentials('webprofile', 'webprofile')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost', virtual_host='/', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=PLATFORM, durable=True)

channel.queue_bind(exchange=EXCHANGE, queue=PLATFORM, routing_key=PLATFORM)

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    runTask(body.decode())
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def runTask(taskId): 
    r_geturl = requests.get(BASEURL+'/task/getdownloadurl/'+str(taskId),headers={'content-type':'application/json'})

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
    r_update = requests.post(BASEURL+'/task/updatestate',data = formdata)


    # 运行load and run
    try:
        cmd = shlex.split('load_and_run model.mge --input data:resnet.npy --profile profile.txt --cpu')
        p = subprocess.run(cmd, capture_output=True)
        
        if p.returncode == 0:
            finalformdata = {"taskId":taskId,"state":"successed"}
            output = open('./profile.txt', 'r').read()
            print('load and run succeeded')
        else:
            finalformdata = {"taskId":taskId,"state":"failed"}
            output = p.stderr #p.stdout
            print('load and run has error')
    except:
        print("load-and-run failed")

    r_updatestate = requests.post(BASEURL+'/task/updatestate',data = finalformdata)
    result = r_updatestate.json()
    r_uploadoutput = requests.put(result['output_url'],data=output)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=PLATFORM, on_message_callback=callback)

channel.start_consuming()
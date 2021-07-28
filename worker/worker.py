import requests
import subprocess
import json

taskId = '6100c8fceaf731e62c42f807'
baseUrl = 'http://localhost:5000'

r_geturl = requests.get(baseUrl+'/task/getdownloadurl/'+str(taskId),headers={'content-type':'application/json'})

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
r_update = requests.post(baseUrl+'/task/updatestate',data = formdata)


# 运行load and run
try:
    p = subprocess.Popen(['load_and_run ./model.mge --input ./resnet.npy --profile ./profile.txt'], shell=True, stdout=subprocess.PIPE, stderr = subprocess.PIPE)

    f1 = open("./output.txt", "wb")
    f2 = open("./error.txt", "wb")
    while True:
        stdout,stderr = p.communicate()
        f1.write(stdout)
        f2.write(stderr)
        if p.returncode == 0:
            finalformdata = {"taskId":taskId,"state":"successed"}
            output = { 'file' : open('./profile.txt', 'r')}
            break
        else:
            finalformdata = {"taskId":taskId,"state":"failed"}
            output = { 'file' : open('./error.txt', 'r')}
            break
except:
    print("load-and-run failed")

r_updatestate = requests.post(baseUrl+'/task/updatestate',data = finalformdata)
result = r_updatestate.json()
r_uploadoutput = requests.put(result['output_url'],files=output)
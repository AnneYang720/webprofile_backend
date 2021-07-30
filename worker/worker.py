import requests
import shlex
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
    cmd = shlex.split('load_and_run model.mge --input data:data.npy --profile profile.txt')
    p = subprocess.run(cmd, capture_output=True)
    
    if p.returncode == 0:
        finalformdata = {"taskId":taskId,"state":"successed"}
        output = open('./profile.txt', 'r').read()
    else:
        finalformdata = {"taskId":taskId,"state":"failed"}
        output = p.stderr #p.stdout
except:
    print("load-and-run failed")

r_updatestate = requests.post(baseUrl+'/task/updatestate',data = finalformdata)
result = r_updatestate.json()
r_uploadoutput = requests.put(result['output_url'],data=output)
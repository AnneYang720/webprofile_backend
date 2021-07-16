import requests
import subprocess

taskId = '12345'
baseUrl = 'http://easy-mock.anneyang.me/mock/60e04f49e235063d5506456a/webprofile/'

r_geturl = requests.get(baseUrl+'task/getdownloadurl/'+taskId)

if r_geturl.flag:
    mge_url = r_geturl.data.mgeUrl
    data_url = r_geturl.data.dataUrl
else:
    exit()

r_download_mge = requests.get(mge_url)
with open("model.mge", "wb") as mge:
    mge.write(r_download_mge.content)

r_download_data = requests.get(data_url)
with open("data.npy", "wb") as data:
    data.write(r_download_data.content)

# 更新状态至running
formdata = {"taskId":taskId,"state":"running"}

# 运行load and run
ret = subprocess.run(['load_and_run',mge,'--input',data,'--profile','profile.txt'], capture_output=True, stderr=subprocess.STDOUT)
#load_and_run resnet50.mge --input resnet.npy --profile profilec.json

# 更新状态，存储结果至对象存储
if ret.returncode == 0:
    finalformdata = {"taskId":taskId,"state":"successed"}
    output = { 'file' : open('./profile.txt', 'r')}
else:
    finalformdata = {"taskId":taskId,"state":"failed"}
    with open("output.txt", "wb") as data:
        data.write(ret.stdout)
    output = { 'file' : open('./output.txt', 'r')}
r_updatestate = requests.post(baseUrl+'task/updatestate',data = finalformdata)
r_uploadoutput = requests.post(r_updatestate.output_url,files=output)
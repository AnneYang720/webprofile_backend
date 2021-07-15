import base64
import time
from flask import Blueprint, g, jsonify, request

from backend.manage import db, jwt, token_auth, client
from backend.utils.response_code import RET
from datetime import timedelta

task = Blueprint('task', __name__)
task_cl = db.tasks # select the collection

# 新建项目
@task.route('/task/createurl', methods=['GET'])
@token_auth.login_required
def createTask():
    platform = request.form.get('platform')
    version = request.form.get('version')
    mge_name = request.form.get('mge_name')
    data_name = request.form.get('data_name')

    # get userid
    userId = g.user['_id']

    # save info into mongodb & create taskid
    taskId = task_cl.insert({
        "userId":userId,
        "mge_name":mge_name,
        "data_name":data_name,
        "mge_key":None,
        "data_key":None,
        "platform":platform,
        "version":version,
        "updateTime":time.time(),
        "state":"initiated",
        "profile_txt":None
    })

    # 对象存储路径
    mge_key = "mge/"+userId+"/"+ taskId
    data_key = "data/"+userId+"/"+ taskId

    # save object to mongodb 
    task_cl.update({"_id":taskId},{"$set":{"mge_key":mge_key,"data_key":data_key}})

    # 设置minio
    mge_url = client.get_presigned_url(
        method="PUT",
        bucket_name="my-bucket",
        object_name=mge_key,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/json"},
    )
    data_url = client.get_presigned_url(
        method="PUT",
        bucket_name="my-bucket",
        object_name=data_key,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/json"},
    )
    
    return jsonify(code=RET.OK, flag=True, message='生成url成功', data={"mgeUrl":mge_url,"dataUrl":data_url,"taskId":taskId})



# mge、data文件上传成功，更新数据库中任务状态
@task.route('/task/savetaskinfo', methods=['POST'])
@token_auth.login_required
def saveTaskInfo():
    taskId = request.form.get('taskId')
    saveFlag = request.form.get('saveFlag')

    if saveFlag:
        # save object to mongodb 
        task_cl.update({"_id":taskId},{"$set":{"updateTime":time.time(), "state":"waiting"}})
    else :
        task_cl.delete_one({"_id":taskId})
    
    return jsonify(code=RET.OK, flag=True, message='任务状态更新成功')

# 获取当前用户的所有task信息
@task.route('/task/getlist/<int:page>/<int:size>', methods=['GET'])
@token_auth.login_required
def getTasksList(page,size):
    page -= 1 # skip page
    userId = g.user['_id'] # get userid
    task_cl.find({"userId":userId},{ "_id": 1, "mge_name": 1, "data_name": 1, "platform": 1, "updateTime": 1, "version": 1, "state": 1 }).skip(page*size).limit(size)

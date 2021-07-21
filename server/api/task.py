import time
from flask import Blueprint, g, jsonify, request

from server.manage import db, token_auth, client
from server.utils.response_code import RET
from server.api import task_blue
from datetime import timedelta
from bson.objectid import ObjectId
import json
from bson import json_util

task_cl = db.tasks # select the collection

# 新建项目
@task_blue.route('/createurl', methods=['GET'])
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
        "output_key":None
    })

    # 对象存储路径
    mge_key = "mge/"+ str(taskId)
    data_key = "data/"+ str(taskId)

    # save object to mongodb 
    task_cl.update({"_id":taskId},{"$set":{"mge_key":mge_key,"data_key":data_key}})

    # 设置minio
    mge_url = client.get_presigned_url(
        method="PUT",
        bucket_name="minio-webprofile",
        object_name=mge_key,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/json"},
    )
    data_url = client.get_presigned_url(
        method="PUT",
        bucket_name="minio-webprofile",
        object_name=data_key,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/json"},
    )
    
    return jsonify(code=RET.OK, flag=True, message='生成上传url成功', data={"mgeUrl":mge_url,"dataUrl":data_url,"taskId":str(taskId)})



# mge、data文件上传成功，更新数据库中任务状态
@task_blue.route('/savetaskinfo', methods=['POST'])
@token_auth.login_required
def saveTaskInfo():
    taskId = request.form.get('taskId')
    saveFlag = request.form.get('saveFlag')

    if saveFlag=="True":
        # save object to mongodb 
        task_cl.update({"_id":ObjectId(taskId)},{"$set":{"updateTime":time.time(), "state":"waiting"}})
    else :
        task_cl.delete_one({"_id":ObjectId(taskId)})
    
    return jsonify(code=RET.OK, flag=True, message='任务状态更新成功')


# 获取当前用户的所有task信息
@task_blue.route('/getlist/<int:page>/<int:size>', methods=['GET'])
@token_auth.login_required
def getTasksList(page,size):
    page -= 1 # skip page
    userId = g.user['_id'] # get userid
    total = task_cl.find({"userId":userId}).count()
    data = task_cl.find({"userId":userId},{ "_id": 1, "mge_name": 1, "data_name": 1, "platform": 1, "updateTime": 1, "version": 1, "state": 1 }).skip(page*size).limit(size)
    docs = list(data)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有任务信息成功', data={"total":total,"rows":docs})

# worker获取task文件的下载url
@task_blue.route('/getdownloadurl/<taskId>', methods=['GET'])
@token_auth.login_required
def getTasksUrl(taskId):
    
    # 对象存储路径
    mge_key = "mge/"+ taskId
    data_key = "data/"+ taskId

    # Get presigned URL string to download 'my-object' in
    # 'my-bucket' with two hours expiry.
    mge_url = client.get_presigned_url(
        method="GET",
        bucket_name="minio-webprofile",
        object_name=mge_key,
        expires=timedelta(hours=2),
    )
    data_url = client.get_presigned_url(
        method="GET",
        bucket_name="minio-webprofile",
        object_name=data_key,
        expires=timedelta(days=1),
    )

    return jsonify(code=RET.OK, flag=True, message='生成下载url成功', data={"mgeUrl":mge_url,"dataUrl":data_url})

# worker上任务运行/完成/失败，更新数据库中任务状态
@task_blue.route('/updatestate', methods=['POST'])
@token_auth.login_required
def saveWorkerTaskInfo():
    taskId = request.form.get('taskId')
    state = request.form.get('state')

    # 如果任务开始运行，更新状态并返回
    if state == "running":
        task_cl.update({"_id":ObjectId(taskId)},{"$set":{"updateTime":time.time(), "state":state}})
        return jsonify(code=RET.OK, flag=True, message='任务状态更新成功')

    # 任务完成（成功or失败）
    output_key = "output/"+ taskId

    output_url = client.get_presigned_url(
        method="PUT",
        bucket_name="minio-webprofile",
        object_name=output_key,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/json"},
    )
    
    task_cl.update({"_id":ObjectId(taskId)},{"$set":{"updateTime":time.time(), "state":state,"output_key":output_key}})

    return jsonify(code=RET.OK, flag=True, message='任务状态更新成功',output_url=output_url)
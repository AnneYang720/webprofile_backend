import time
from flask import g, jsonify, request
import requests
import tempfile
import glob
import os

from server.manage import db, token_auth, client, channel
from server.utils.response_code import RET
from server.utils.network_visualize import visualize
from server.api.models import TaskArgs
from server.api import task_blue
from server.utils.profile_analyze import profile
from server.config import APP_ENV, config
from datetime import timedelta
from bson.objectid import ObjectId
from minio.error import S3Error
import json

task_cl = db.tasks # select the collection

# 新建项目，返回文件上传至MINIO的预签名url
@task_blue.route('/createurl', methods=['POST'])
@token_auth.login_required
def createTask():
    worker = request.form.get('worker')
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
        "worker":worker,
        "version":version,
        "updateTime":int(time.time()*1000),
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
    
    return jsonify(code=RET.OK, flag=True, message='用户创建任务后，生成上传MGE模型和数据文件至MINIO的url成功', data={"mgeUrl":mge_url,"dataUrl":data_url,"taskId":str(taskId)})



# mge、data文件上传成功，更新数据库中任务状态
@task_blue.route('/savetaskinfo', methods=['POST'])
@token_auth.login_required
def saveTaskInfo():
    taskId = request.form.get('taskId')
    saveFlag = request.form.get('saveFlag')
    worker = request.form.get('worker')
    version = request.form.get('version')
    args = request.form.get('args')

    if saveFlag=="true":
        # save object to mongodb 
        task_cl.update({"_id":ObjectId(taskId)},{"$set":{"updateTime":int(time.time()*1000), "state":"waiting"}})
        print("ready to send to mq")
        channel.basic_publish(exchange=config[APP_ENV].MQ_EXCHANGE, routing_key=worker, body=json.dumps({'taskId':taskId,'version':version,'args':args}))
    else :
        task_cl.delete_one({"_id":ObjectId(taskId)})
    
    return jsonify(code=RET.OK, flag=True, message='创建任务后，文件上传成功，任务成功初始化')


# 获取当前用户的所有task信息
@task_blue.route('/getlist/<int:page>/<int:size>', methods=['GET'])
@token_auth.login_required
def getTasksList(page,size):
    page -= 1 # skip page
    userId = g.user['_id'] # get userid
    total = task_cl.find({"userId":userId}).count()
    data = task_cl.find({"userId":userId},{ "_id": 1, "mge_name": 1, "data_name": 1, "worker": 1, "updateTime": 1, "version": 1, "state": 1 }).skip(page*size).limit(size)
    docs = list(data)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有任务信息成功', data={"total":total,"rows":docs})

# 获取当前用户的所有task ID
@task_blue.route('/getidlist', methods=['GET'])
@token_auth.login_required
def getTasksID():
    userId = g.user['_id'] # get userid
    tasks = list(task_cl.find({"userId":userId},{ "_id": 1}))
    data = []
    for task in tasks:
        data.append(str(task["_id"]))
    return jsonify(code=RET.OK, flag=True, message='获取所有任务ID成功', data=data)


# 获得任务Profile
@task_blue.route('/taskprofile', methods=['POST'])
@token_auth.login_required
def taskProfile():
    taskArgs = TaskArgs(request.json)

    # 判断任务是否存在
    tmpTask = task_cl.find_one({"_id":ObjectId(taskArgs.taskId)})
    if not tmpTask:
        return jsonify(code=RET.NODATA, flag=False, message='该任务不存在')
    if tmpTask['userId'] != g.user['_id']: # get userid
        return jsonify(code=RET.NODATA, flag=False, message='您没有该任务的权限')

    # download profile.txt from minio
    output_key = "output/"+ taskArgs.taskId

    with tempfile.NamedTemporaryFile() as profile_tf:
        client.fget_object("minio-webprofile", output_key, profile_tf.name)

        taskArgs.setProfilePath(profile_tf.name)
        tot_dev_time,tot_host_time,deviceList,hostList = profile(taskArgs)

    return jsonify(code=RET.OK, flag=True, message='获得任务Profile信息成功',tot_dev_time=tot_dev_time,tot_host_time=tot_host_time,deviceList=deviceList,hostList=hostList)

# 模型可视化
@task_blue.route('/netvisualize/<taskId>', methods=['GET'])
@token_auth.login_required
def netVisualize(taskId):
    # 对象存储路径
    mge_key = "mge/"+ taskId
    log_key = "log/"+ taskId

    log_url = client.get_presigned_url(
        method="GET",
        bucket_name="minio-webprofile",
        object_name=log_key,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/octet-stream"},
    )

    try:
        client.stat_object("minio-webprofile", log_key)
        return jsonify(code=RET.OK, flag=True, message='模型可视化时，获取log的url成功', data = log_url)

    except S3Error as err:
        pass

    # try:
    with tempfile.NamedTemporaryFile() as mge_tf, tempfile.TemporaryDirectory() as log_td:
        client.fget_object('minio-webprofile', mge_key, mge_tf.name)

        visualize(mge_tf.name, log_td)

        # TODO: 文件找不到
        log_name = glob.glob(log_td+'/*.tfevents*')[0]
        client.fput_object('minio-webprofile', log_key, log_name,
            content_type='application/octet-stream')
    # except Exception as err:
    #     return jsonify(code=RET.THIRDERR, flag=False, message=str(err))
    
    return jsonify(code=RET.OK, flag=True, message='模型可视化时，获取log的url成功', data = log_url)


# 任务失败信息
@task_blue.route('/getfailinfo/<taskId>', methods=['GET'])
@token_auth.login_required
def getFailInfoUrl(taskId):
    # 对象存储路径
    output_key = "output/"+ taskId
    filename = "output_fail_"+taskId
    output_url = client.get_presigned_url(
        method="GET",
        bucket_name="minio-webprofile",
        object_name=output_key,
        expires=timedelta(days=1),
        response_headers={"response-content-disposition": f'attachment; filename={filename}'},
    )

    return jsonify(code=RET.OK, flag=True, message='任务失败，获取失败结果的url成功', data = output_url)


# worker获取task文件的下载url
@task_blue.route('/getdownloadurl/<taskId>', methods=['GET'])
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

    return jsonify(code=RET.OK, flag=True, message='worker获取文件，生成文件下载url成功', data={"mgeUrl":mge_url,"dataUrl":data_url})

# worker上任务运行/完成/失败，更新数据库中任务状态
@task_blue.route('/updatestate', methods=['POST'])
def saveWorkerTaskInfo():
    taskId = request.form.get('taskId')
    state = request.form.get('state')

    # 如果任务开始运行，更新状态并返回
    if state == "running":
        task_cl.update({"_id":ObjectId(taskId)},{"$set":{"updateTime":int(time.time()*1000), "state":state}})
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
    
    task_cl.update({"_id":ObjectId(taskId)},{"$set":{"updateTime":int(time.time()*1000), "state":state,"output_key":output_key}})

    return jsonify(code=RET.OK, flag=True, message='任务状态更新成功',output_url=output_url)

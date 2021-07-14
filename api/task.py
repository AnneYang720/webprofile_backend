import base64
from flask import Blueprint, g, current_app, jsonify, request,make_response

from backend.manage import db, jwt, token_auth, client
from backend.utils.response_code import RET
from datetime import timedelta

task = Blueprint('task', __name__)
task_cl = db.tasks # select the collection

# 新建项目
@task.route('/task/createurl', methods=['GET'])
@token_auth.login_required
def createTask():
    # mgeFile =request.files.get('mgeFile')
    # dataFile =request.files.get('dataFile')
    platform = request.form.get('platform')
    version = request.form.get('version')

    # get userid
    userId = g.user['_id']

    # save info into mongodb & create taskid
    taskId = task_cl.insert({
        "userId":userId,
        "input_mge":None,
        "input_data":None,
        "platform":platform,
        "version":version,
        "state":"initiated",
        "profile_txt":None
    })

    # object_name of two files
    mge_object = "mge/"+userId+"/"+ taskId
    data_object = "data/"+userId+"/"+ taskId

    # save object to mongodb 
    task_cl.update({"_id":taskId},{"$set":{"input_mge":mge_object,"input_data":data_object}})

    # 设置minio
    mge_url = client.get_presigned_url(
        method="PUT",
        bucket_name="my-bucket",
        object_name=mge_object,
        expires=timedelta(days=1),
        response_headers={"response-content-type": "application/json"},
    )
    data_url = client.get_presigned_url(
        method="PUT",
        bucket_name="my-bucket",
        object_name=data_object,
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
        task_cl.update({"_id":taskId},{"$set":{"state":"waiting"}})
    else :
        task_cl.delete_one({"_id":taskId})
    
    return jsonify(code=RET.OK, flag=True, message='任务状态更新成功')

from flask import g, jsonify, request

from server.manage import db, token_auth
from server.utils.response_code import RET
from server.api import admin_blue
from bson.objectid import ObjectId

# select collections
task_cl = db.tasks
worker_cl = db.workers 
user_cl = db.users


# 获取所有worker的信息
@admin_blue.route('/getworkerslist', methods=['GET'])
@token_auth.login_required(role='admin')
def getWorkersList(): 
    data = worker_cl.find()
    workersList = list(data)
    for worker in workersList:
        worker["_id"] = str(worker["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有worker信息成功', data=workersList)


# 获取所有用户的信息
@admin_blue.route('/getuserslist', methods=['GET'])
@token_auth.login_required(role='admin')
def getAllUser(): 
    data = user_cl.find()
    usersList = list(data)
    for user in usersList:
        user["_id"] = str(user["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有worker信息成功', data=usersList)


# 获取所有私有设备的信息
@admin_blue.route('/getprivateworkerslist', methods=['GET'])
@token_auth.login_required(role='admin')
def getPrivateWorkersList(): 
    data = worker_cl.find({"auth":"private"},{ "_id": 1, "name": 1})
    privateWorkersList = list(data)
    for worker in privateWorkersList:
        worker["_id"] = str(worker["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有worker信息成功', data=privateWorkersList)

# TODO 给指定用户增加指定worker
@admin_blue.route('/worker/<userId>', methods=['POST'])
@token_auth.login_required(role='admin')
def addWorker(userId):
    workerId =request.json.get('workerId') 
    workers = user_cl.find({"_id": ObjectId(userId)},{"workers": 1})
    workers.append()
    user_cl.update({"_id":ObjectId(userId)},{"$set":{}})

    # data = worker_cl.find({"auth":"private"},{ "_id": 1, "name": 1})
    # privateWorkersList = list(data)
    # for worker in privateWorkersList:
    #     worker["_id"] = str(worker["_id"])
    return jsonify(code=RET.OK, flag=True, message='成功')
from flask import g, jsonify, request

from server.manage import db, token_auth
from server.utils.response_code import RET
from server.api.models import User
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
    data = user_cl.find({},{"_id": 1, "email": 1, "roles": 1, "workers": 1 })
    usersList = list(data)
    for user in usersList:
        user["_id"] = str(user["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有用户信息成功', data=usersList)


# 获取所有私有设备的信息
@admin_blue.route('/getprivateworkerslist', methods=['GET'])
@token_auth.login_required(role='admin')
def getPrivateWorkersList(): 
    data = worker_cl.find({"auth":"private"},{ "_id": 1, "name": 1})
    privateWorkersList = list(data)
    for worker in privateWorkersList:
        worker["_id"] = str(worker["_id"])
    return jsonify(code=RET.OK, flag=True, message='获取所有私有worker信息成功', data=privateWorkersList)


#  给某用户添加某私有worker
@admin_blue.route('/worker/<userId>', methods=['POST'])
@token_auth.login_required(role='admin')
def addWorker(userId):
    workers = list(user_cl.find({"_id": ObjectId(userId)},{"workers": 1}))[0]['workers']
    worker_add =request.json.get('worker_add')

    if(worker_add in workers):
        return jsonify(code=RET.DATAEXIST, flag=False, message='用户已拥有该worker权限')
    
    workers.append(worker_add)
    print(workers)
    user_cl.update({"_id":ObjectId(userId)},{"$set":{"workers":workers}})
    return jsonify(code=RET.OK, flag=True, message='添加worker成功')


#  删除某用户的某私有worker使用权
@admin_blue.route('/worker/<userId>', methods=['DELETE'])
@token_auth.login_required(role='admin')
def delWorker(userId):
    workers = list(user_cl.find({"_id": ObjectId(userId)},{"workers": 1}))[0]['workers']
    worker_del =request.json.get('worker_del')

    if(worker_del not in workers):
        return jsonify(code=RET.NODATA, flag=False, message='用户没有该worker权限')

    workers.remove(worker_del)
    user_cl.update({"_id":ObjectId(userId)},{"$set":{"workers":workers}})
    return jsonify(code=RET.OK, flag=True, message='删除worker成功')



#  添加某用户为管理员
@admin_blue.route('/add', methods=['POST'])
@token_auth.login_required(role='admin')
def addAdmin():
    admin_add =request.json.get('admin_add')
    roles = list(user_cl.find({"email": admin_add},{"roles": 1}))[0]['roles']

    if("admin" in roles):
        return jsonify(code=RET.DATAEXIST, flag=False, message='用户已拥有admin权限')
    
    roles.append("admin")
    user_cl.update({"email": admin_add},{"$set":{"roles":roles}})
    return jsonify(code=RET.OK, flag=True, message='添加管理员成功')


#  删除某用户管理员权限
@admin_blue.route('/del', methods=['DELETE'])
@token_auth.login_required(role='admin')
def delAdmin():
    admin_del =request.json.get('admin_del')
    roles = list(user_cl.find({"email": admin_del},{"roles": 1}))[0]['roles']

    if("admin" not in roles):
        return jsonify(code=RET.NODATA, flag=False, message='用户没有admin权限')
    
    roles.remove("admin")
    user_cl.update({"email": admin_del},{"$set":{"roles":roles}})
    return jsonify(code=RET.OK, flag=True, message='删除管理员成功')


# 管理员修改用户密码
@admin_blue.route('/changepwd', methods=['POST'])
@token_auth.login_required(role='admin')
def changePwd():
    email =request.json.get('email')
    password =request.json.get('password')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, flag=False, message='参数不完整')

    if user_cl.find_one({"email": email}) is None:
        return jsonify(re_code=RET.NODATA, flag=False, message='用户不存在')

    user_cl.update({"email":email},{"$set":{"password":User.generate_password(password)}})
    
    return jsonify(re_code=RET.OK, flag=True, message='修改密码成功')
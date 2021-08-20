from flask import g, jsonify, request

from server.manage import db, token_auth
from server.utils.response_code import RET
from server.api import worker_blue

# select collections
task_cl = db.tasks
worker_cl = db.workers 
user_cl = db.users


# 新worker注册
@worker_blue.route('/worker/add', methods=['POST'])
def newWorker():    
    name = request.form.get('name')
    ip = request.form.get('ip')
    platform = request.form.get('platform')
    mge_version = request.form.get('mge_version')
    auth = request.form.get('auth')

    if worker_cl.find_one({"name": name}) is not None:
        return jsonify(re_code=RET.DATAEXIST, flag=False, message='worker命名重复')


    # save info into mongodb & create taskid
    workerId = worker_cl.insert({
        "name":name,
        "ip":ip,
        "platform":platform,
        "mge_version":mge_version,
        "platform":platform,
        "auth":auth,
        "state":"Initiated"
    })
    
    return jsonify(code=RET.OK, flag=True, message='新worker注册成功', data=str(workerId))


# 用户获取所有可用的worker列表
@worker_blue.route('/getmyworkerslist', methods=['GET'])
@token_auth.login_required
def getmyworkerslist():
    pub_workers = list(worker_cl.find({"auth":"public"},{"name": 1}))
    # get userid
    userId = g.user['_id']
    pri_workers = list(user_cl.find({"_id":userId},{"workers":1}))[0]['workers']

    my_workers = []
    for worker in pub_workers:
        my_workers.append(worker['name'])
    my_workers.extend(pri_workers)

    return jsonify(code=RET.OK, flag=True, message='获取当前用户的workersList成功', data=my_workers)


# 用户获取选中worker的信息
@worker_blue.route('/getworkinfo/<string:chosenWorker>', methods=['GET'])
@token_auth.login_required
def getWorkerInfo(chosenWorker):
    worker = list(worker_cl.find({"name":chosenWorker},{"platform":1,"mge_version":1}))[0]
    return jsonify(code=RET.OK, flag=True, message='获取当前用户的workersList成功',data={"platform":worker['platform'],"mge_version":worker['mge_version']})
from flask import g, jsonify, request

from server.manage import db
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
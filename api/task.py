import base64
from flask import g, current_app, jsonify, request,make_response
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from backend import db, jwt
from backend.api import api
from backend.models import User
from backend.utils.response_code import RET

task_cl = db.tasks # select the collection

# 新建项目
@api.route('/task/create', methods=['POST'])
def createTask():
    mgeFile =request.files.get('mgeFile')
    dataFile =request.files.get('dataFile')
    platform = request.form.get('platform')
    version = request.form.get('version')

    # get userid
    # create taskid
    # save info into mongodb
    
    



    userId = task_cl.insert({"email":email,"password":User.generate_password(password)})

    if userId:
        return jsonify(re_code=RET.OK, flag=True, message='注册成功')
    else:
        return jsonify(code=RET.SERVERERR, flag=False, message='Internal Error')
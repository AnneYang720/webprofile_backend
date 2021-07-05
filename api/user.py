import base64
import ast
import json
from flask import g, current_app, jsonify, request,make_response
from werkzeug.security import check_password_hash, generate_password_hash
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from backend import db
from backend.api import api
from backend.models import User
from backend.utils.response_code import RET

user_cl = db.users # select the collection

# 用户注册接口
@api.route('/signup', methods=['POST'])
def signup():
    email =request.json.get('email')
    password =request.json.get('password')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, flag=False, message='参数不完整')

    if user_cl.find_one({"email": email}) is not None:
        return jsonify(re_code=RET.DATAEXIST, flag=False, message='用户已存在')

    userId = user_cl.insert({"email":email,"password":generate_password_hash(password)})
    if userId:
        return jsonify(re_code=RET.OK, flag=True, message='注册成功')
    else:
        return jsonify(code=RET.SERVERERR, flag=False, message='Internal Error')

    try:
        try:
            new_user = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            return jsonify(code=RET.REQERR, flag=False, message='Bad Request')
        
        record_created = user_cl.insert(new_user)

        # Signed up successfully
        return jsonify(re_code=RET.OK, flag=True, message='注册成功')
    
    except:
        # Error while trying to create the resource
        return jsonify(code=RET.SERVERERR, flag=False, message='Internal Error')


# 用户登录
@api.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    #解析Authorization
    #email, password = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode().split(':')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, flag=False, message='参数不完整')
    try:
        user = User.query.filter(User.email==email).first()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, flag=False, message='查询用户失败')
    if not user:
        return jsonify(code=RET.NODATA, flag=False, message='用户不存在', data=user)
    if not user.verify_password(password):
        return jsonify(code=RET.PARAMERR, flag=False, message='帐户名或密码错误')

    #更新最后一次登录时间
    user.update_last_seen()
    token = user.generate_user_token()
    return jsonify(code=RET.OK, flag=True, message='登录成功', token=token)



@auth.verify_password
def verify_password(email_or_token, password):
    if request.path == '/login':
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_user_token(email_or_token)
        if not user:
            return False
    g.user = user
    return True



@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)



@api.route('/')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.email})

# # -*- coding: utf-8 -*-
# # @Author: Dima Sumaroka
# # @Date:   2017-01-23 13:08:19
# # @Last Modified by:   Dima Sumaroka
# # @Last Modified time: 2017-02-08 14:15:54

# from app import app, lm
# from flask import request, session
# from flask_login import login_user, logout_user, login_required
# from .user import User
# from bson import json_util, ObjectId
# import json
# import base64

# @app.route('/login', methods=['POST'])
# def login():
#     response = {
#         "success": False,
#         "response": " "
#     }
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if username and password:
#         user = app.mongo.db.user.find_one({"username": username})
#         if user and User.validate_login(user["password_hash"], password):
#             user_obj = User.build_user(user)
#             if login_user(user_obj):
#                 userSession = {
#                     'userId': user['_id'],
#                     'session_id': session["_id"],
#                     'success': True
#                 }
#                 app.mongo.db.session.insert(userSession)
#                 app.mongo.db.session.update({
#                     "userId" : ObjectId(user['_id'])
#                 },
#                 {
#                     "$set": {
#                         "session_id": session['_id']
#                     }
#                 }, upsert=True)
#                 return json_util.dumps(userSession)
#         else:
#             response["response"] = "Worng password"
#             return json.dumps(response)
#     else:
#         response["response"] = "Username or password not entered"
#         return json.dumps(response)

# @app.route('/logout')
# def logout():
#     response = {
#         "success": False,
#         "response": " "
#     }
#     api_key = request.headers.get('Authorization')
#     if api_key:
#         api_key = api_key.replace('Basic ', '', 1)
#         try:
#             api_key = base64.b64decode(api_key)
#         except TypeError:
#             pass
#         userFromSession = app.mongo.db.session.find_one({"session_id": api_key})
#         if userFromSession:
#             deleteUser = app.mongo.db.session.remove({'_id': userFromSession['_id']}, True)
#             if deleteUser:
#                 response['success'] = True
#                 response['response'] = "User Logged out"
#             else:
#                 response['response'] = "Something went wrong"
#         else:
#             response['success'] = True
#             response['response'] = "User Logged out"
#         logout_user()
#     return json.dumps(response)

# @app.route('/write', methods=['GET'])
# @login_required
# def write():
#     return json.dumps({"success": True})

# @lm.request_loader
# def load_user_from_request(request):
#     api_key = request.headers.get('Authorization')
#     if api_key:
#         api_key = api_key.replace('Basic ', '', 1)
#         try:
#             api_key = base64.b64decode(api_key)
#         except TypeError:
#             pass
#         userFromSession = app.mongo.db.session.find_one(
#             {
#                 "session_id": api_key
#             })
#         if userFromSession:
#             user = app.mongo.db.user.find_one(
#                 {
#                     "_id": ObjectId(userFromSession['userId'])
#                 })

#             user_obj = User.build_user(user)
#             if user_obj:
#                 return user_obj
#             else:
#                 return None
#         else:
#             return None

# @app.route('/register', methods=['POST'])
# def new_user():
#     response = {
#         "success": False,
#         "response": " "
#     }
#     username = request.json.get('username')
#     password = request.json.get('password')
#     email = request.json.get('email')

#     if username is None or password is None:
#         response["response"] = "username or pass not provided"
#         return json.dumps(response)

#     if app.mongo.db.user.find_one({"username": username}) is not None:
#         response["response"] = "username taken"
#         return json.dumps(response)

#     user = User("")
#     user.username = username
#     user.hash_password(password = password)
#     user.set_email(email = email)

#     if user.save():
#         response["success"] = True
#         response["response"] = "User saved"
#         response["userId"] = user.id
#         response = json.dumps(response, default=json_util.default)
#     return json.dumps(response)

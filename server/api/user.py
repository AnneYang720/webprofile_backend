from flask import g, current_app, jsonify, request,make_response

from server.manage import db, token_auth
from server.api.models import User
from server.utils.response_code import RET
from server.api import user_blue

user_cl = db.users # select the collection

# 用户注册接口
@user_blue.route('/signup', methods=['POST'])
def signup():
    email =request.json.get('email')
    password =request.json.get('password')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, flag=False, message='参数不完整')

    if user_cl.find_one({"email": email}) is not None:
        return jsonify(re_code=RET.DATAEXIST, flag=False, message='用户已存在')

    userId = user_cl.insert({"email":email,"password":User.generate_password(password), "workers":[], "roles":['user']})
    if userId:
        return jsonify(re_code=RET.OK, flag=True, message='注册成功')
    else:
        return jsonify(code=RET.SERVERERR, flag=False, message='Internal Error')


# 用户登录
@user_blue.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, flag=False, message='参数不完整')

    try:
        user = user_cl.find_one({"email": email})
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, flag=False, message='查询用户失败')

    if not user:
        return jsonify(code=RET.NODATA, flag=False, message='用户不存在', data=user)
    if not User.verify_password(user['password'], password):
        return jsonify(code=RET.PARAMERR, flag=False, message='帐户名或密码错误')
    
    #更新最后一次登录时间
    token = User.generate_user_token(user['_id'])
    return jsonify(code=RET.OK, flag=True, message='登录成功', token=token)


@token_auth.verify_token
def verify_token(token):
    user = User.verify_auth_token(token)
    if not user:
        return False
    g.user = user
    return user

@token_auth.get_user_roles
def get_user_roles(user):
    return user['roles']



@token_auth.error_handler
def tokenUnauthorized():
    return jsonify(code=RET.USERERR, flag=False, message='登录错误')

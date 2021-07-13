import base64
from flask import g, current_app, jsonify, request,make_response
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from backend import db, jwt
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

    userId = user_cl.insert({"email":email,"password":User.generate_password(password)})
    if userId:
        return jsonify(re_code=RET.OK, flag=True, message='注册成功')
    else:
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
        user = user_cl.find_one({"email": email})
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, flag=False, message='查询用户失败')

    if not user:
        return jsonify(code=RET.NODATA, flag=False, message='用户不存在', data=user)
    if not User.verify_password(user['password'], password):
        return jsonify(code=RET.PARAMERR, flag=False, message='帐户名或密码错误')

    #更新最后一次登录时间
    token = User.generate_user_token()
    return jsonify(code=RET.OK, flag=True, message='登录成功', token=token)

# 登录后的首页
@api.route('/')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.email})


@auth.verify_password
def verify_password(email_or_token, password):
    if request.path == '/login':
        user = user_cl.find_one({"email": email_or_token})
        if not user or not User.verify_password(user['password'], password):
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


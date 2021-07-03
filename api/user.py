import base64
from flask import g, current_app, jsonify, request,make_response
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from app import db
from app.api_v1 import api
from backend.models import User
from backend.utils.response_code import RET

# 用户注册接口
@api.route('/signup', methods=['POST'])
def signup():
    email =request.json.get('email')
    password =request.json.get('password')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, flag=False, message='参数不完整')

    user = User()
    user.email = email
    user.password = password    #利用user model中的类属性方法加密用户的密码并存入数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(code=RET.DBERR, flag=False, message='注册失败')
    # 响应结果
    return jsonify(re_code=RET.OK, flag=True, message='注册成功')

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
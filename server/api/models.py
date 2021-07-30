from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from flask import jsonify, current_app
from functools import wraps
from bson.objectid import ObjectId
import json

from server.manage import db

#用户模型
class User():
    def __init__(self, id):
        self.id = id
        self.email = None
        self.password_hash = None

    # 禁止读取密码
    @property
    def password(self):
        raise AttributeError('密码不可访问')

    def generate_password(password):
        return generate_password_hash(password)

    # 密码验证，验证成功返回True,否则返回False
    def verify_password(password_hash, password):
        return check_password_hash(password_hash, password)

    # 生成确认身份的Token(密令)
    def generate_user_token(id, expiration=43200):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': str(id)}).decode('utf-8')
 
    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = db.users.find_one({"_id": ObjectId(data['id'])})
        return user

    # 更新最后一次登录时间
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 返回用户信息
    def to_json(self):
        return {
            'user_id': self.id,
            'email': self.email,
        }

    def __repr__(self):
        return '<User %r>' % self.email


class TaskArgs():
    def __init__(self, form):
        self.taskId = form.get('taskId')
        self.top = 3 if form.get('top')=="" else form.get('top')
        self.type = None if form.get('type')=="[]" else json.loads(form.get('type'))
        self.aggregateBy = None if form.get('aggregateBy')=="" else form.get('aggregateBy')
        self.oprName = None if form.get('oprName')=="" else form.get('oprName')
        self.inputDtype = None if form.get('inputDtype')=="" else form.get('inputDtype')
        self.topEndKey = "end" if form.get('topEndKey')=="" else form.get('topEndKey')
        self.aggregate = None if form.get('aggregate')=="" else form.get('aggregate')
        self.orderBy = "time" if form.get('orderBy')=="" else form.get('orderBy')
        self.copyTime = False if form.get('copyTime')=="false" else True
        self.minTime = float("-inf") if form.get('minTime')=="" else form.get('minTime')
        self.maxTime = float("inf") if form.get('maxTime')=="" else form.get('maxTime')
        self.showHost = False if form.get('showHost')=="false" else True
        self.profilePath = None

    
    def setProfilePath(self, profilePath):
        self.profilePath = profilePath


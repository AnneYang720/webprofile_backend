from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from flask import jsonify, current_app, g, request
from functools import wraps
from server.utils.response_code import RET

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

    def generate_password(self, password):
        return generate_password_hash(password)

    # 密码验证，验证成功返回True,否则返回False
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成确认身份的Token(密令)
    def generate_user_token(self, expiration=43200):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')
 
    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_user_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = db.users.find_one({"_id": data['id']})
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
    
    def save(self):
        self.id = app.mongo.db.user.insert({
                "password_hash": self.password_hash,
                "email": self.email,
                "createtedAt": datetime.now()
            })
        if self.id:
            return True
        else:
            return False

    def __repr__(self):
        return '<User %r>' % self.email





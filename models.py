from flask_login import UserMixin
from werkzeug.security import check_password_hash


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = str(id)  # id를 문자열로 변환 (Flask-Login 요구 사항)
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.constants import ROLE_ADMIN, ROLE_USER
from utils.helpers import utc_now

# Hash MD5 legado (hex de 32 caracteres) gravado pela versão anterior; migrado no próximo login.
_LEGACY_MD5 = re.compile(r'^[0-9a-f]{32}$')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def password_needs_rehash(self):
        return bool(self.password and _LEGACY_MD5.match(self.password))

    def check_password(self, raw_password):
        if self.password_needs_rehash():
            legacy = hashlib.md5(raw_password.encode()).hexdigest()
            return hmac.compare_digest(self.password, legacy)
        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == ROLE_ADMIN

    # ---------- acesso a dados ----------

    @classmethod
    def get(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def count_all(cls):
        return cls.query.count()

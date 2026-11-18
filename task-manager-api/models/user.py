import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from models.constants import ROLE_ADMIN, ROLE_USER, STAFF_ROLES
from utils.clock import utcnow

FORMATO_MD5_LEGADO = re.compile(r'[0-9a-f]{32}')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        """Confere a senha; hash MD5 legado é substituído pelo KDF na primeira conferência válida."""
        if FORMATO_MD5_LEGADO.fullmatch(self.password):
            legado = hashlib.md5(pwd.encode(), usedforsecurity=False).hexdigest()
            if not hmac.compare_digest(legado, self.password):
                return False
            self.set_password(pwd)
            return True
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def is_staff(self):
        return self.role in STAFF_ROLES

    @classmethod
    def find(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def list_page(cls, limit, offset):
        return cls.query.order_by(cls.id).limit(limit).offset(offset).all()

    @classmethod
    def count_all(cls):
        return cls.query.count()

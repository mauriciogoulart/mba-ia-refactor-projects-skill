from database import db
from utils.constants import DEFAULT_COLOR
from utils.helpers import utc_now


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utc_now)

    # ---------- acesso a dados ----------

    @classmethod
    def get(cls, category_id):
        return db.session.get(cls, category_id)

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def count_all(cls):
        return cls.query.count()

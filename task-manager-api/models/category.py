from database import db, get_by_id
from models.constants import DEFAULT_COLOR
from utils.clock import utcnow


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utcnow)

    @classmethod
    def find(cls, category_id):
        return get_by_id(cls, category_id)

    @classmethod
    def list_page(cls, limit, offset):
        return cls.query.order_by(cls.id).limit(limit).offset(offset).all()

    @classmethod
    def count_all(cls):
        return cls.query.count()

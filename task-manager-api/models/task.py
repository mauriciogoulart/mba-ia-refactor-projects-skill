from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from utils.constants import CLOSED_STATUSES, DEFAULT_PRIORITY, DEFAULT_STATUS, STATUS_DONE
from utils.helpers import utc_now


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    @property
    def tag_list(self):
        return self.tags.split(',') if self.tags else []

    def is_overdue(self, now=None):
        """Regra única de atraso: tem prazo vencido e não está concluída/cancelada."""
        now = now or utc_now()
        return bool(self.due_date) and self.due_date < now and self.status not in CLOSED_STATUSES

    # ---------- acesso a dados ----------

    @classmethod
    def get(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_with_relations(cls):
        return (cls.query.options(joinedload(cls.user), joinedload(cls.category))
                .order_by(cls.id).all())

    @classmethod
    def list_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        query = cls.query
        if text:
            query = query.filter(or_(cls.title.like(f'%{text}%'), cls.description.like(f'%{text}%')))
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.order_by(cls.id).all()

    @classmethod
    def count_all(cls):
        return db.session.query(func.count(cls.id)).scalar()

    @classmethod
    def count_by(cls, column):
        return dict(db.session.query(column, func.count(cls.id)).group_by(column).all())

    @classmethod
    def count_by_status(cls):
        return cls.count_by(cls.status)

    @classmethod
    def count_by_priority(cls):
        return cls.count_by(cls.priority)

    @classmethod
    def count_by_user(cls):
        return cls.count_by(cls.user_id)

    @classmethod
    def count_by_category(cls):
        return cls.count_by(cls.category_id)

    @classmethod
    def count_done_by_user(cls):
        return dict(db.session.query(cls.user_id, func.count(cls.id))
                    .filter(cls.status == STATUS_DONE).group_by(cls.user_id).all())

    @classmethod
    def _overdue_query(cls, now):
        return cls.query.filter(cls.due_date.isnot(None), cls.due_date < now,
                                cls.status.notin_(CLOSED_STATUSES))

    @classmethod
    def count_overdue(cls, now):
        return cls._overdue_query(now).count()

    @classmethod
    def list_overdue(cls, now):
        return cls._overdue_query(now).order_by(cls.id).all()

    @classmethod
    def count_created_since(cls, since):
        return cls.query.filter(cls.created_at >= since).count()

    @classmethod
    def count_done_since(cls, since):
        return cls.query.filter(cls.status == STATUS_DONE, cls.updated_at >= since).count()

    @classmethod
    def detach_category(cls, category_id):
        cls.query.filter_by(category_id=category_id).update({cls.category_id: None},
                                                            synchronize_session=False)

from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from database import db
from models.constants import DEFAULT_PRIORITY, FINISHED_STATUSES, STATUS_DONE, STATUS_PENDING
from utils.clock import utcnow


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def is_overdue(self):
        if not self.due_date or self.status in FINISHED_STATUSES:
            return False
        return self.due_date < utcnow()

    @classmethod
    def find(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_page(cls, limit, offset):
        return (cls.query.options(joinedload(cls.user), joinedload(cls.category))
                .order_by(cls.id).limit(limit).offset(offset).all())

    @classmethod
    def search(cls, term, status, priority, user_id, limit, offset):
        query = cls.query
        if term:
            query = query.filter(db.or_(cls.title.like(f'%{term}%'), cls.description.like(f'%{term}%')))
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.order_by(cls.id).limit(limit).offset(offset).all()

    @classmethod
    def list_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id).all()

    @classmethod
    def list_overdue(cls):
        return (cls.query.filter(cls.due_date.isnot(None), cls.due_date < utcnow(),
                                 cls.status.notin_(FINISHED_STATUSES))
                .order_by(cls.id).all())

    @classmethod
    def count_all(cls):
        return cls.query.count()

    @classmethod
    def count_by_status(cls):
        return dict(db.session.query(cls.status, func.count(cls.id)).group_by(cls.status).all())

    @classmethod
    def count_by_priority(cls):
        return dict(db.session.query(cls.priority, func.count(cls.id)).group_by(cls.priority).all())

    @classmethod
    def count_by_category(cls):
        return dict(db.session.query(cls.category_id, func.count(cls.id)).group_by(cls.category_id).all())

    @classmethod
    def totals_by_user(cls):
        """Devolve {user_id: (total de tasks, tasks concluídas)}."""
        done = func.sum(case((cls.status == STATUS_DONE, 1), else_=0))
        rows = db.session.query(cls.user_id, func.count(cls.id), done).group_by(cls.user_id).all()
        return {user_id: (total, completed) for user_id, total, completed in rows}

    @classmethod
    def count_created_since(cls, moment):
        return cls.query.filter(cls.created_at >= moment).count()

    @classmethod
    def count_done_since(cls, moment):
        return cls.query.filter(cls.status == STATUS_DONE, cls.updated_at >= moment).count()

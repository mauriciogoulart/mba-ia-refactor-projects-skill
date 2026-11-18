from datetime import timedelta

from models.category import Category
from models.constants import (
    HIGH_PRIORITY_LIMIT,
    RECENT_ACTIVITY_DAYS,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
)
from models.task import Task
from models.user import User
from services.task_service import completion_rate
from services.user_service import get_user
from utils.clock import utcnow

PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}


def _overdue_summary():
    now = utcnow()
    tasks = Task.list_overdue()
    return {
        'count': len(tasks),
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (now - task.due_date).days,
            }
            for task in tasks
        ],
    }


def _user_productivity():
    totals = Task.totals_by_user()
    productivity = []
    for user in User.list_all():
        total, completed = totals.get(user.id, (0, 0))
        productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': completion_rate(completed, total),
        })
    return productivity


def build_summary():
    by_status = Task.count_by_status()
    by_priority = Task.count_by_priority()
    recent_limit = utcnow() - timedelta(days=RECENT_ACTIVITY_DAYS)
    return {
        'generated_at': str(utcnow()),
        'overview': {
            'total_tasks': Task.count_all(),
            'total_users': User.count_all(),
            'total_categories': Category.count_all(),
        },
        'tasks_by_status': {
            status: by_status.get(status, 0)
            for status in (STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_CANCELLED)
        },
        'tasks_by_priority': {label: by_priority.get(level, 0) for level, label in PRIORITY_LABELS.items()},
        'overdue': _overdue_summary(),
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(recent_limit),
            'tasks_completed_last_7_days': Task.count_done_since(recent_limit),
        },
        'user_productivity': _user_productivity(),
    }


def build_user_report(user_id):
    user = get_user(user_id)
    tasks = Task.list_by_user(user_id)
    total = len(tasks)
    done = sum(1 for task in tasks if task.status == STATUS_DONE)
    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': sum(1 for task in tasks if task.status == STATUS_PENDING),
            'in_progress': sum(1 for task in tasks if task.status == STATUS_IN_PROGRESS),
            'cancelled': sum(1 for task in tasks if task.status == STATUS_CANCELLED),
            'overdue': sum(1 for task in tasks if task.is_overdue()),
            'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_LIMIT),
            'completion_rate': completion_rate(done, total),
        },
    }

from datetime import timedelta

from models.category import Category
from models.task import Task
from models.user import User
from services.exceptions import AppError
from utils.constants import (HIGH_PRIORITY_MAX, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS,
                             STATUS_DONE, VALID_STATUSES)
from utils.helpers import calculate_percentage, utc_now


def summary_report():
    now = utc_now()
    total_tasks = Task.count_all()
    by_status = Task.count_by_status()
    by_priority = Task.count_by_priority()
    overdue_tasks = Task.list_overdue(now)
    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    totals_by_user = Task.count_by_user()
    done_by_user = Task.count_done_by_user()
    productivity = []
    for user in User.list_all():
        total = totals_by_user.get(user.id, 0)
        completed = done_by_user.get(user.id, 0)
        productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(utc_now()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': User.count_all(),
            'total_categories': Category.count_all(),
        },
        'tasks_by_status': {status: by_status.get(status, 0) for status in VALID_STATUSES},
        'tasks_by_priority': {label: by_priority.get(priority, 0)
                              for priority, label in PRIORITY_LABELS.items()},
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [{
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (utc_now() - task.due_date).days,
            } for task in overdue_tasks],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(since),
            'tasks_completed_last_7_days': Task.count_done_since(since),
        },
        'user_productivity': productivity,
    }


def user_report(user_id):
    user = User.get(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    tasks = Task.list_by_user(user_id)
    now = utc_now()
    counts = {status: 0 for status in VALID_STATUSES}
    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
    total = len(tasks)

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            **counts,
            'overdue': sum(1 for task in tasks if task.is_overdue(now)),
            'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_MAX),
            'completion_rate': calculate_percentage(counts[STATUS_DONE], total),
        },
    }

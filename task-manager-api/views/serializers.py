"""Serialização de saída (DTOs). Campos sensíveis (senha/hash) nunca são expostos."""
from utils.helpers import format_date


def task_to_dict(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'user_id': task.user_id,
        'category_id': task.category_id,
        'created_at': str(task.created_at),
        'updated_at': str(task.updated_at),
        'due_date': format_date(task.due_date),
        'tags': task.tag_list,
    }


def task_with_overdue(task, now):
    data = task_to_dict(task)
    data['overdue'] = task.is_overdue(now)
    return data


def task_list_item(task, now):
    data = task_with_overdue(task, now)
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def user_task_item(task, now):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': format_date(task.due_date),
        'overdue': task.is_overdue(now),
    }


def user_to_public(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'active': user.active,
        'created_at': str(user.created_at),
    }


def user_list_item(user, task_count):
    data = user_to_public(user)
    data['task_count'] = task_count
    return data


def category_to_dict(category, task_count=None):
    data = {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_at': str(category.created_at),
    }
    if task_count is not None:
        data['task_count'] = task_count
    return data

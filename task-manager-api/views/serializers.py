"""Serialização de saída: somente os campos públicos de cada entidade."""


def _optional_date(value):
    return str(value) if value else None


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
        'due_date': _optional_date(task.due_date),
        'tags': task.tags.split(',') if task.tags else [],
    }


def task_detail(task):
    return {**task_to_dict(task), 'overdue': task.is_overdue()}


def task_list_item(task):
    return {
        **task_detail(task),
        'user_name': task.user.name if task.user else None,
        'category_name': task.category.name if task.category else None,
    }


def user_task_item(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': _optional_date(task.due_date),
        'overdue': task.is_overdue(),
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


def category_to_dict(category):
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_at': str(category.created_at),
    }

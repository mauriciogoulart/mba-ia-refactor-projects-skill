"""Script para popular o banco com dados iniciais.

ATENÇÃO: apaga todas as tasks, usuários e categorias existentes antes de recriá-los.
As senhas dos usuários de demonstração vêm de SEED_ADMIN_PASSWORD, SEED_MANAGER_PASSWORD
e SEED_USER_PASSWORD (ver .env.example).
"""
import sys
from datetime import timedelta

from app import create_app
from config.settings import Settings
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import utc_now

SEED_PASSWORD_VARS = ('SEED_ADMIN_PASSWORD', 'SEED_MANAGER_PASSWORD', 'SEED_USER_PASSWORD')


def _user(name, email, password, role):
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    return user


def _category(name, description, color):
    return Category(name=name, description=description, color=color)


def seed_data(settings):
    missing = [name for name in SEED_PASSWORD_VARS if not getattr(settings, name)]
    if missing:
        print(f"Seed não executado: defina {', '.join(missing)}.", file=sys.stderr)
        return 1

    app = create_app(settings)
    with app.app_context():
        Task.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        joao = _user('João Silva', 'joao@email.com', settings.SEED_ADMIN_PASSWORD, 'admin')
        maria = _user('Maria Santos', 'maria@email.com', settings.SEED_USER_PASSWORD, 'user')
        pedro = _user('Pedro Oliveira', 'pedro@email.com', settings.SEED_MANAGER_PASSWORD, 'manager')
        db.session.add_all([joao, maria, pedro])
        db.session.commit()

        backend = _category('Backend', 'Tarefas de backend', '#3498db')
        frontend = _category('Frontend', 'Tarefas de frontend', '#2ecc71')
        devops = _category('DevOps', 'Tarefas de infraestrutura', '#e74c3c')
        bug = _category('Bug', 'Correção de bugs', '#e67e22')
        db.session.add_all([backend, frontend, devops, bug])
        db.session.commit()

        now = utc_now()
        tasks_data = [
            {'title': 'Implementar autenticação JWT', 'description': 'Adicionar autenticação real com JWT', 'status': 'pending', 'priority': 1, 'user_id': joao.id, 'category_id': backend.id, 'due_date': now - timedelta(days=3)},
            {'title': 'Criar tela de login', 'description': 'Tela de login responsiva', 'status': 'in_progress', 'priority': 2, 'user_id': maria.id, 'category_id': frontend.id, 'due_date': now + timedelta(days=5)},
            {'title': 'Configurar CI/CD', 'description': 'Pipeline com GitHub Actions', 'status': 'done', 'priority': 2, 'user_id': pedro.id, 'category_id': devops.id, 'tags': 'devops,ci,github'},
            {'title': 'Corrigir bug no filtro de busca', 'description': 'Filtro não funciona com caracteres especiais', 'status': 'pending', 'priority': 1, 'user_id': joao.id, 'category_id': bug.id, 'due_date': now - timedelta(days=1)},
            {'title': 'Adicionar paginação na API', 'description': 'Endpoints retornam todos os registros', 'status': 'pending', 'priority': 3, 'user_id': joao.id, 'category_id': backend.id, 'due_date': now + timedelta(days=10)},
            {'title': 'Escrever testes unitários', 'description': 'Cobertura mínima de 80%', 'status': 'pending', 'priority': 2, 'user_id': maria.id, 'category_id': backend.id},
            {'title': 'Documentar API com Swagger', 'description': 'Gerar documentação automática', 'status': 'cancelled', 'priority': 4, 'user_id': pedro.id, 'category_id': backend.id},
            {'title': 'Refatorar models', 'description': 'Melhorar organização dos models', 'status': 'in_progress', 'priority': 3, 'user_id': maria.id, 'category_id': backend.id, 'tags': 'refactor,tech-debt'},
            {'title': 'Configurar monitoramento', 'description': 'Prometheus + Grafana', 'status': 'pending', 'priority': 4, 'user_id': pedro.id, 'category_id': devops.id, 'due_date': now + timedelta(days=20)},
            {'title': 'Melhorar validações de input', 'description': 'Usar marshmallow ou pydantic', 'status': 'pending', 'priority': 3, 'user_id': joao.id, 'category_id': backend.id, 'tags': 'improvement,validation'},
        ]
        db.session.add_all([Task(**task_data) for task_data in tasks_data])
        db.session.commit()

        print("Seed concluído com sucesso!")
        print(f"  {User.count_all()} usuários")
        print(f"  {Category.count_all()} categorias")
        print(f"  {Task.count_all()} tasks")
    return 0


if __name__ == '__main__':
    sys.exit(seed_data(Settings.from_env()))

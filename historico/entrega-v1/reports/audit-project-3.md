================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Path:    task-manager-api
Run:     2026-11-06T14:07:15-03:00          Run id: 20261106-140715
Stack:   Python 3.14.0 + Flask 3.0.0 (confiança: alta)
Files:   15 analyzed | ~1158 lines of code
Architecture: parcialmente-em-camadas
Skill:   refactor-arch 1.1 | Catalog 1.0
Evidence: reports/evidence/project-3/20261106-140715/

## Summary
CRITICAL: 7 | HIGH: 4 | MEDIUM: 11 | LOW: 6
Total: 28 findings (189 ocorrências)
Por categoria: Segurança 12 | Arquitetura 8 | Deprecated 2 | Testes 1 | Qualidade 5 | Outro 0
Cobertura: 15/15 arquivos-fonte lidos integralmente (+ 2 arquivos de teste lidos); 0 inspecionados só por busca

## Estrutura ANTES
```
task-manager-api/
├── app.py                         (34)   entrypoint + config literal + rotas / e /health + create_all no import
├── database.py                    (3)    instância SQLAlchemy
├── seed.py                        (99)   seed destrutivo com senhas literais
├── models/
│   ├── __init__.py                (3)
│   ├── category.py                (21)
│   ├── task.py                    (60)   model + validações/regra de atraso não usadas
│   └── user.py                    (38)   model + hash MD5 + to_dict com senha
├── routes/
│   ├── __init__.py                (1)
│   ├── report_routes.py           (223)  rotas + controller + agregações + CRUD de categorias
│   ├── task_routes.py             (299)  rotas + controller + validação + regra + acesso a dados + serialização
│   └── user_routes.py             (211)  rotas + controller + validação + login + acesso a dados
├── services/
│   ├── __init__.py                (1)
│   └── notification_service.py    (48)   SMTP com credenciais literais; nunca usado
├── utils/
│   ├── __init__.py                (1)
│   └── helpers.py                 (116)  helpers e constantes; nenhum usado
├── tests/
│   ├── conftest.py                (103)
│   └── test_api.py                (283)
├── instance/tasks.db              (ignorado pelo git; não lido)
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

| Métrica | Valor |
|---|---|
| Arquivos-fonte | 15 |
| Linhas de código (aprox.) | ~1158 |
| Camadas presentes (papéis) | entrypoint, config (misturada no entrypoint), rotas+controllers (misturados), models, services (só notificação, sem uso), utils (sem uso); **ausentes**: controllers dedicados, services de domínio, middleware (auth/erros), config dedicada |
| Maior arquivo | routes/task_routes.py (299) |
| Arquivos com 3+ papéis | 4 (app.py, routes/task_routes.py, routes/user_routes.py, routes/report_routes.py) |

## Superfície de ataque
| Método | Rota | Handler (arquivo:linha) | Autenticação | Administrativa/destrutiva |
|---|---|---|---|---|
| GET | / | app.py:26 | não | não |
| GET | /health | app.py:22 | não | não |
| GET | /tasks | routes/task_routes.py:11 | não | não |
| GET | /tasks/<int:task_id> | routes/task_routes.py:65 | não | não |
| POST | /tasks | routes/task_routes.py:85 | não | não |
| PUT | /tasks/<int:task_id> | routes/task_routes.py:156 | não | não |
| DELETE | /tasks/<int:task_id> | routes/task_routes.py:225 | não | não |
| GET | /tasks/search | routes/task_routes.py:240 | não | não |
| GET | /tasks/stats | routes/task_routes.py:273 | não | não |
| GET | /users | routes/user_routes.py:10 | não | não (expõe e-mails) |
| GET | /users/<int:user_id> | routes/user_routes.py:27 | não | não (expõe hash de senha) |
| POST | /users | routes/user_routes.py:42 | não | não (aceita `role` do cliente; devolve hash) |
| PUT | /users/<int:user_id> | routes/user_routes.py:92 | não | **sim** (altera `role`/`active`) |
| DELETE | /users/<int:user_id> | routes/user_routes.py:134 | não | **sim** (remove usuário e suas tasks) |
| GET | /users/<int:user_id>/tasks | routes/user_routes.py:153 | não | não |
| POST | /login | routes/user_routes.py:185 | não | não (token falso; devolve hash) |
| GET | /reports/summary | routes/report_routes.py:12 | não | não (nomes e produtividade de todos os usuários) |
| GET | /reports/user/<int:user_id> | routes/report_routes.py:103 | não | não (expõe e-mail) |
| GET | /categories | routes/report_routes.py:157 | não | não |
| POST | /categories | routes/report_routes.py:167 | não | não |
| PUT | /categories/<int:cat_id> | routes/report_routes.py:190 | não | não |
| DELETE | /categories/<int:cat_id> | routes/report_routes.py:211 | não | não |

Entradas: corpo JSON (tasks, usuários, login, categorias), query string de `/tasks/search` (`q`, `status`, `priority`, `user_id`), parâmetros de rota inteiros. Segredos: literais no fonte (app.py:13; services/notification_service.py:9-10; seed.py:19, 26, 33). Integrações externas: SMTP em services/notification_service.py (nunca chamado). Banco: SQLite local `instance/tasks.db` (existe, 20 KB, com dados; não lido).

## Findings

### [CRITICAL] F-001 · SEC-02 Segredos e credenciais hardcoded
File: app.py:13; services/notification_service.py:9-10; seed.py:19, 26, 33
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `app.config['SECRET_KEY'] = 'supe***'` · `self.email_user = 'task***'` / `self.email_password = 'senh***'` · `u1.set_password('****')` (admin; senhas de seed de 4 caracteres mascaradas integralmente)
Description: a `SECRET_KEY` do Flask, o usuário/senha SMTP e as senhas dos três usuários de seed (incluindo o `admin` João) estão em literais versionados; nenhuma configuração é lida do ambiente.
Impact: quem lê o repositório obtém a chave de assinatura da aplicação, a credencial do e-mail e a senha do administrador de demonstração; os valores permanecem no histórico git.
Recommendation: módulo de configuração por variáveis de ambiente, `.env.example` só com nomes, senhas de seed por variável (fixture de teste define); rotacionar os valores já expostos (Playbook P-01).

### [CRITICAL] F-002 · SEC-09 Autenticação/autorização ausente ou falsa
File: app.py:15; routes/user_routes.py:210
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / CWE-862 / A01:2021, A07:2021
Evidência: `'token': 'fake-jwt-token-' + str(user.id)` · `CORS(app)`
Description: o login devolve um token previsível que nenhuma rota verifica; **nenhuma** das 22 rotas checa identidade, inclusive as que leem/escrevem dados pessoais; CORS liberado para qualquer origem.
Impact: qualquer cliente remoto lê, altera e apaga tasks, usuários e categorias; qualquer site pode chamar a API pelo navegador da vítima.
Recommendation: emitir credencial verificável (token assinado com `SECRET_KEY` e expiração), decorador único de autenticação/perfil nas rotas de dados e CORS por lista de origens (Playbook P-05, P-19) — **exige contrato** (CT-01, CT-02, CT-06).

### [CRITICAL] F-003 · SEC-05 Modo debug ativo e bind público
File: app.py:34
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-489 / A05:2021
Evidência: `app.run(debug=True, host='0.0.0.0', port=5000)`
Description: o boot documentado (`python app.py`) liga o depurador Werkzeug e escuta em todas as interfaces, sem controle por ambiente.
Impact: tracebacks com código-fonte expostos a qualquer host da rede e console de depuração interativo acessível (protegido apenas por PIN).
Recommendation: `APP_DEBUG` (padrão desligado) e `APP_HOST` (padrão `127.0.0.1`) lidos da configuração (Playbook P-01).

### [CRITICAL] F-004 · SEC-07 Dados sensíveis expostos em respostas
File: models/user.py:21; routes/user_routes.py:33, 85, 129, 209
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-200 / CWE-201 / A02:2021
Evidência: `'password': self.password,` (em `User.to_dict`), usado por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`
Description: o serializador do usuário inclui o hash da senha, devolvido por quatro rotas públicas.
Impact: combinado com F-005 (MD5 sem salt), o hash é revertido por tabela/força bruta em segundos para senhas curtas.
Recommendation: serializador com lista branca de campos (Opção 1: chave `password` mantida com `null`; Opção 2: campo omitido) (Playbook P-04) — CT-05.

### [CRITICAL] F-005 · SEC-06 Armazenamento inseguro de senha
File: models/user.py:29, 32
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-327 / CWE-916 / A02:2021
Evidência: `self.password = hashlib.md5(pwd.encode()).hexdigest()` · `return self.password == hashlib.md5(pwd.encode()).hexdigest()`
Description: senha protegida por MD5 sem salt e comparada por igualdade direta.
Impact: hashes vazados (ver F-004) são revertidos trivialmente; senhas iguais geram hashes iguais.
Recommendation: KDF adequado (`werkzeug.security`, já dependência do Flask) com rehash transparente do MD5 legado no login (Playbook P-03).

### [CRITICAL] F-006 · SEC-10 Escalação de privilégio / mass assignment
File: routes/user_routes.py:52, 71-78, 119-125
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-915 / CWE-269 / A01:2021
Evidência: `role = data.get('role', 'user')` … `user.role = role` · `user.role = data['role']` · `user.active = data['active']`
Description: `POST /users` aceita `role` do corpo (inclusive `admin`) e `PUT /users/<id>` altera `role` e `active` de qualquer usuário, sem autenticação.
Impact: qualquer cliente anônimo cria administradores, promove/rebaixa usuários e desativa contas (bloqueia login de terceiros).
Recommendation: só administrador autenticado define `role`/`active`; cadastro anônimo fixa `role='user'` (Playbook P-05, P-07) — **exige contrato** (CT-03, CT-04).

### [CRITICAL] F-007 · SEC-03 Endpoint destrutivo sem autenticação
File: routes/user_routes.py:134
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021
Evidência: `@user_bp.route('/users/<int:user_id>', methods=['DELETE'])` → `db.session.delete(t)` para cada task e `db.session.delete(user)`
Description: remoção de usuário (com exclusão em cascata das suas tasks) sem nenhuma verificação de identidade ou perfil.
Impact: atacante remoto apaga todos os usuários e tasks iterando ids.
Recommendation: exigir token de administrador (Playbook P-05) — **exige contrato** (CT-03).

### [HIGH] F-008 · SEC-08 Dados sensíveis em logs
File: routes/user_routes.py:83, 89; services/notification_service.py:21
Ocorrências: 3 · Confiança: LIKELY · Categoria: Segurança
CWE/OWASP: CWE-532 / A09:2021
Evidência: `print(f"Usuário criado: {user.id} - {user.name}")` · `print(f"ERRO: {str(e)}")` · `print(f"Email enviado para {to}")`
Description: nome e e-mail (PII) vão para a saída padrão; o texto de exceções do SQLAlchemy (`IntegrityError` etc.) inclui os parâmetros ligados do INSERT (nome, e-mail, hash da senha). LIKELY: depende de uma falha de banco ocorrer (p. ex. corrida no e-mail único).
Impact: PII e hash de senha persistidos em logs sem mascaramento.
Recommendation: `logging` configurado, mascarar e-mail e não registrar `str(e)` de erros de banco com parâmetros (Playbook P-15).

### [HIGH] F-009 · ARC-04 Acoplamento forte sem composition root
File: app.py:9-31; seed.py:2; routes/task_routes.py:147-148; routes/user_routes.py:81-82; routes/report_routes.py:183-184
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `app = Flask(__name__)` no nível do módulo · `with app.app_context(): db.create_all()` no import · `from app import app, db` (seed) · `db.session.add(...)`/`commit()` nos handlers
Description: não há app factory; importar `app.py` cria a aplicação com configuração fixa e já toca o banco; o seed depende desse efeito colateral; os handlers usam a sessão global diretamente.
Impact: impossível criar a app com outra configuração (teste, produção) sem editar código; importar o módulo altera o banco.
Recommendation: `create_app()` como composition root, `create_all` dentro do factory, seed usando o factory, persistência só em services (Playbook P-13).

### [HIGH] F-010 · ARC-02 Lógica de negócio nos handlers de rota
File: routes/report_routes.py:12-155; routes/task_routes.py:11-299; routes/user_routes.py:42-211
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `if t.due_date < datetime.utcnow(): if t.status != 'done' and t.status != 'cancelled': ...` (regra de atraso em handler) · cascata manual `for t in tasks: db.session.delete(t)` · agregações de relatório inteiras no handler
Description: as três blueprints validam, aplicam regra de negócio (atraso, estatísticas, produtividade, cascata), consultam e persistem; `services/` não tem nenhum serviço de domínio.
Impact: regras não testáveis isoladamente e duplicadas (F-017); qualquer mudança de regra exige editar vários handlers.
Recommendation: camada `services/` por domínio e controllers finos (Playbook P-09).

### [HIGH] F-011 · ARC-06 Responsabilidade fora do lugar
File: routes/report_routes.py:157-223
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `@report_bp.route('/categories', methods=['POST'])` (e GET, PUT, DELETE) no módulo de relatórios
Description: o CRUD completo de categorias (4 handlers) está no blueprint `reports`.
Impact: domínio de categorias difícil de localizar e evoluir; acoplamento indevido com relatórios.
Recommendation: módulo próprio de rotas/controller/service de categorias, mantendo as URLs (Playbook P-08).

### [MEDIUM] F-012 · SEC-17 Falta de proteções HTTP básicas
File: app.py:15; routes/user_routes.py:185
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-770 / CWE-693 / A05:2021
Evidência: `CORS(app)` sem origens; nenhum limitador ou cabeçalho de segurança registrado; `POST /login` sem limitação de tentativas
Description: sem rate limit no login, sem cabeçalhos de segurança (`X-Content-Type-Options`, `X-Frame-Options` etc.) e CORS aberto.
Impact: força bruta de senha sem custo (agravada por senhas de 4 caracteres aceitas); respostas sem proteções de navegador.
Recommendation: cabeçalhos de segurança aditivos; CORS restrito (CT-06); rate limit exige dependência nova (recomendação manual) (Playbook P-19).

### [MEDIUM] F-013 · SEC-13 Vazamento de detalhes internos em erros
File: app.py:34; routes/report_routes.py:197; routes/task_routes.py:113, 182, 261, 264
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-209 / A05:2021
Evidência: `if priority < 1 or priority > 5:` com `priority` vindo do JSON (`"5"` ⇒ `TypeError`) · `int(priority)` sem tratamento · `if 'name' in data:` com `data = None`
Description: não há handler central de erros; entradas com tipo inválido levantam exceções não tratadas que, com `debug=True`, devolvem a página de traceback do Werkzeug (código-fonte e caminhos).
Impact: exposição de código e estrutura interna a partir de uma requisição malformada.
Recommendation: handler global que registra o detalhe e devolve JSON genérico; validação de tipos (Playbook P-06, P-07).

### [MEDIUM] F-014 · SEC-12 Validação de entrada ausente ou frágil
File: routes/report_routes.py:180, 196-197; routes/task_routes.py:96-100, 113, 182, 261, 264; routes/user_routes.py:61, 102-103, 124-125
Ocorrências: 10 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-20 / A03:2021
Evidência: `len(title)` sem checar tipo · `priority < 1` sem `int` · `int(request.args.get('priority'))` sem `try` · `category.color = data.get('color', '#000000')` (sem formato) · `user.name = data['name']` (vazio aceito) · `user.active = data['active']` (qualquer tipo) · regex `^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$` (aceita `a@b`)
Description: tipos, formatos e obrigatoriedade não são verificados de forma consistente entre criar e atualizar; `PUT /categories/<id>` não trata corpo ausente.
Impact: erros 500 (ver F-013) e dados inválidos persistidos (cor inválida, nome vazio, `active` não booleano).
Recommendation: validação na borda com as mesmas regras em criar/atualizar (Playbook P-07); a troca 500 → 400 para tipos inválidos **exige contrato** (CT-07).

### [MEDIUM] F-015 · SEC-16 Dependências antigas e não usadas
File: requirements.txt:1-6
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-1104 / A06:2021
Evidência: `marshmallow==3.20.1`, `python-dotenv==1.0.0` (nunca importados); `requests==2.31.0` (só usado em tests/); `flask==3.0.0`, `flask-cors==4.0.0` fixados em versões de 2023
Description: pacotes declarados sem uso na aplicação, dependência de teste no manifesto de produção e versões fixadas antigas; versão de Python não declarada.
Impact: superfície de ataque e de manutenção maior; possíveis CVEs conhecidas nas versões fixadas (não consultado: rede).
Recommendation: remover não usados, mover `requests` para `requirements-dev.txt`; rodar `pip-audit` (classe C) e atualizar conforme resultado (Playbook P-18).

### [MEDIUM] F-016 · ARC-10 Integridade referencial ausente
File: models/task.py:13-14; routes/report_routes.py:211-223
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)` (sem `ondelete`; SQLite sem `PRAGMA foreign_keys`) · `db.session.delete(cat)` sem tratar tasks
Description: excluir uma categoria deixa tasks com `category_id` apontando para registro inexistente.
Impact: dados órfãos; `category_id` inconsistente nas respostas de tasks.
Recommendation: anular `category_id` das tasks na exclusão (service) e declarar `ondelete='SET NULL'` (Playbook P-10).

### [MEDIUM] F-017 · ARC-08 Código duplicado
File: models/task.py:23-36, 50-60; routes/report_routes.py:33-43, 132-135; routes/task_routes.py:17-28, 30-39, 71-80, 92-114, 166-184, 283-287; routes/user_routes.py:61, 106, 162-169, 171-180; utils/helpers.py:21, 57-108
Ocorrências: 15 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: regra "atrasada" (`due_date < utcnow()` e status ≠ done/cancelled) repetida 7 vezes; serialização de task repetida em 3 lugares; validação de task em 3 lugares; regex de e-mail em 3 lugares
Description: a mesma regra e a mesma serialização são reimplementadas em vários handlers, enquanto `Task.is_overdue()` e `process_task_data()` existem e não são usados.
Impact: correções precisam ser replicadas; divergências já existentes (helpers aceita `dd/mm/aaaa`, rotas não).
Recommendation: regra única no model/service, serializador único, validador único (Playbook P-16).

### [MEDIUM] F-018 · ARC-11 Sem paginação / carga total / várias COUNT
File: routes/report_routes.py:15-30, 53; routes/task_routes.py:14, 249-266, 275-281; routes/user_routes.py:12
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `Task.query.all()` em listagens e para contar atrasadas · 12 `count()` separados + `Task.query.all()` em `/reports/summary`
Description: listagens e estatísticas carregam tabelas inteiras e fazem uma consulta por contagem.
Impact: tempo e memória crescem linearmente com os dados.
Recommendation: agregação `GROUP BY` e contagem de atrasadas no banco; paginação só com parâmetro opcional (contrato) (Playbook P-11).

### [MEDIUM] F-019 · ARC-07 Queries N+1
File: routes/report_routes.py:56, 163; routes/task_routes.py:42, 51; routes/user_routes.py:22
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` dentro do loop de tasks · `len(u.tasks)` por usuário · `Task.query.filter_by(user_id=u.id).all()` por usuário · `count()` por categoria
Description: consultas executadas dentro de loops sobre o resultado de outra consulta.
Impact: `GET /tasks` faz até 2N+1 consultas; relatórios e listagens degradam com o volume.
Recommendation: `joinedload`/`selectinload` e agregações por grupo (Playbook P-11).

### [MEDIUM] F-020 · ARC-09 Tratamento de erro ruim
File: routes/report_routes.py:186, 207, 221; routes/task_routes.py:13-63, 137, 204, 236; routes/user_routes.py:130, 149; utils/helpers.py:46, 49, 88
Ocorrências: 13 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `except:` nu (12 ocorrências) · `GET /tasks` inteiro dentro de `try/except:` que devolve `{'error': 'Erro interno'}`
Description: capturas genéricas descartam o erro (inclusive `KeyboardInterrupt`/`SystemExit`); exceções não previstas viram HTML (sem handler) enquanto outras viram JSON.
Impact: falhas silenciosas e respostas de erro inconsistentes.
Recommendation: exceções de domínio e handler central com formato único `{'error': ...}` (Playbook P-06).

### [MEDIUM] F-021 · DEP-01 `datetime.utcnow()` deprecated (Python ≥ 3.12)
File: models/category.py:11; models/task.py:15-16, 52; models/user.py:14; routes/report_routes.py:35, 42, 45, 71, 133; routes/task_routes.py:31, 72, 215, 285; routes/user_routes.py:172; seed.py:66, 67, 69, 70, 74; services/notification_service.py:35; utils/helpers.py:38
Ocorrências: 22 · Confiança: CONFIRMED · Categoria: Deprecated
CWE/OWASP: n/a
Evidência: `created_at = db.Column(db.DateTime, default=datetime.utcnow)` · `if t.due_date < datetime.utcnow():`
Description: `datetime.utcnow()` é deprecated desde Python 3.12; o projeto não restringe a versão e roda em 3.14.0. Equivalente moderno: `datetime.now(timezone.utc)` (aqui sem `tzinfo` ao gravar/comparar, porque as colunas `DateTime` do SQLite são ingênuas e o formato de `str()` faz parte das respostas).
Impact: `DeprecationWarning` hoje e remoção futura.
Recommendation: helper único de "agora em UTC" (Playbook P-14).

### [MEDIUM] F-022 · DEP-02 SQLAlchemy `Model.query.get(id)` legado
File: routes/report_routes.py:105, 192, 213; routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227; routes/user_routes.py:29, 94, 136, 155
Ocorrências: 16 · Confiança: CONFIRMED · Categoria: Deprecated
CWE/OWASP: n/a
Evidência: `task = Task.query.get(task_id)`
Description: com Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.x, `Query.get()` é API legada (`LegacyAPIWarning`). Equivalente moderno: `db.session.get(Model, id)`.
Impact: avisos e remoção prevista em versões futuras.
Recommendation: substituir por `db.session.get` (Playbook P-14).

### [LOW] F-023 · TST-02 Instruções de validação incompletas
File: README.md:5-11
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Testes
CWE/OWASP: n/a
Evidência: README cita só `pip install -r requirements.txt`, `python seed.py`, `python app.py`
Description: não documenta `requirements-dev.txt` nem como rodar `pytest`; não alerta que `seed.py` apaga todos os dados; cita `tasks.db` quando o arquivo real fica em `instance/tasks.db`. (Testes existem: 25 testes de integração — TST-01 não se aplica.)
Impact: quem chega ao projeto não sabe validar mudanças e pode apagar dados ao seguir o README.
Recommendation: documentar instalação de dev, `python -m pytest` e o efeito do seed (recomendação manual).

### [LOW] F-024 · QLT-03 Imports, funções e serviço mortos
File: app.py:7; models/task.py:3, 38-48; models/user.py:34-38; routes/report_routes.py:7-8; routes/task_routes.py:7; routes/user_routes.py:6; services/notification_service.py:4-48; utils/helpers.py:3-7, 9-108, 110-116
Ocorrências: 11 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `import os, sys, json, datetime` (só `datetime` usado) · `import json, os, sys, time` · `from utils.helpers import format_date, calculate_percentage` (não usados) · `NotificationService` nunca instanciado · `VALID_STATUSES`, `validate_status`, `is_admin` sem referências
Description: busca por nome em todo o projeto não encontra uso desses imports, funções, constantes e da classe de notificação.
Impact: ruído, falsa impressão de que existem validação/notificação/constantes em uso.
Recommendation: remover ou passar a usar (constantes e validação consolidadas); `NotificationService` mantido com configuração por ambiente, decisão de integrar/remover fica com o usuário (Playbook P-16).

### [LOW] F-025 · QLT-01 Magic numbers e strings soltas
File: models/task.py:39, 46; routes/report_routes.py:180; routes/task_routes.py:96, 99, 110, 113, 167, 169, 177, 182; routes/user_routes.py:64, 71, 115, 120; utils/helpers.py:75
Ocorrências: 16 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `['pending', 'in_progress', 'done', 'cancelled']` repetida; `len(title) < 3`, `> 200`; `len(password) < 4`; `['user', 'admin', 'manager']`; `'#000000'`
Description: limites e enumerações de regra repetidos como literais, embora `utils/helpers.py:110-116` declare as constantes.
Impact: alteração de regra exige caçar literais.
Recommendation: constantes de domínio únicas (Playbook P-16).

### [LOW] F-026 · QLT-05 Estilo inconsistente
File: models/task.py:40-43, 46-48, 51-60; models/user.py:35-38; routes/task_routes.py:141, 210; utils/helpers.py:21-23, 53-55, 103
Ocorrências: 9 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `if type(tags) == list:` · `if self.role == 'admin': return True else: return False`
Description: `type(x) == list` em vez de `isinstance`; `if/else` que devolve booleano; `if` aninhados triplos.
Impact: legibilidade.
Recommendation: `isinstance`, retorno direto da expressão (Playbook P-16).

### [LOW] F-027 · QLT-02 Nomes pouco descritivos
File: models/category.py:14; routes/report_routes.py:24-28; routes/task_routes.py:16; routes/user_routes.py:14; seed.py:78; utils/helpers.py:83
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `p1 = Task.query.filter_by(priority=1).count()` … `p5` · `for t in tasks` · `for u in users` · `td`, `d`, `p`
Description: variáveis de uma letra/abreviações em lógica de negócio.
Impact: legibilidade.
Recommendation: nomes descritivos (Playbook P-16).

### [LOW] F-028 · QLT-04 `print` no lugar de logger
File: routes/task_routes.py:149, 153, 219, 234; routes/user_routes.py:83, 89, 147; services/notification_service.py:21, 24; utils/helpers.py:39-41
Ocorrências: 10 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `print(f"Task criada: {task.id} - {task.title}")`
Description: saída por `print` como mecanismo de log, sem nível nem formato.
Impact: logs não filtráveis nem configuráveis.
Recommendation: `logging` configurado na composition root (Playbook P-15).

## Descartados / falsos positivos
- SEC-01 em routes/task_routes.py:252-253 — descartado porque `Task.title.like(f'%{query}%')` passa o valor como parâmetro ligado do ORM (não é SQL concatenado); curingas `%`/`_` só afetam o resultado da busca.
- ARC-01 em routes/task_routes.py (299 linhas) — descartado porque os models estão em `models/` e o arquivo não concentra todas as camadas; o problema real é ARC-02 (F-010).
- SEC-15 em routes/user_routes.py:140-146 — descartado porque a exclusão das tasks e do usuário ocorre num único `commit` (atômico, com `rollback` em falha).
- SEC-11 (IDOR) — descartado porque não existe identidade no fluxo; coberto por SEC-09 (F-002).
- ARC-03 em services/notification_service.py:6 — descartado porque a lista é por instância (não global) e a classe nunca é instanciada.
- SEC-04 em services/notification_service.py:1 — `smtplib` não executa comando nem código.
- SEC-02 em tests/test_api.py:152 — valor de teste dentro do diretório de testes.
- QLT-04 em seed.py:93-96 — saída de script de linha de comando, não log de aplicação.

## Correções que exigem mudança de contrato
| ID | Rota/campo | Mudança | Sev. | Motivo (Finding) | Impacto para clientes | Resolvido na Opção 1? | Prova prevista na Opção 2 |
|---|---|---|---|---|---|---|---|
| CT-01 | POST /login · `token` | `fake-jwt-token-<id>` → token assinado (itsdangerous, `SECRET_KEY`, expiração); chave `token` mantida | CRITICAL | F-002 | usar o token recebido em `Authorization: Bearer`; não montar token | não (fica residual) | T2 em `test_login_sucesso` (token aceito em rota protegida) + teste novo: token forjado ⇒ 401 |
| CT-02 | /tasks*, /categories*, /reports/*, GET /users, GET /users/<id>, GET /users/<id>/tasks | exigir token válido (sem/ inválido ⇒ 401) | CRITICAL | F-002 | enviar `Authorization` após `POST /login`; `/`, `/health`, `/login` e `POST /users` seguem abertos | não (fica residual) | teste novo: sem token 401, token inválido 401, com token 200 |
| CT-03 | PUT /users/<id>, DELETE /users/<id> | exigir token; DELETE e alteração de `role`/`active` só admin (403); demais campos: o próprio usuário ou admin | CRITICAL | F-006, F-007 | apenas admin remove usuários e altera perfil/estado | não (fica residual) | teste novo: 401 / 403 (não admin) / 200 (admin) |
| CT-04 | POST /users · `role` | `role` ≠ `user` exige token admin (403); cadastro anônimo com `role` `user` mantido (201) | CRITICAL | F-006 | cadastro público não escolhe perfil privilegiado | não (fica residual) | teste novo: anônimo `role=admin` ⇒ 403; admin ⇒ 201 |
| CT-05 | `password` em GET /users/<id>, POST /users, PUT /users/<id>, POST /login (`user`) | omitir o campo | CRITICAL | F-004 | deixa de receber o hash | sim (chave mantida com `null`) | teste novo: `password` ausente nas 4 rotas |
| CT-06 | CORS (todas as rotas) | origens restritas por `CORS_ORIGINS` | CRITICAL | F-002, F-012 | origens não configuradas deixam de receber `Access-Control-Allow-Origin` | não (fica residual) | teste novo: `Origin` não permitida ⇒ sem cabeçalho; permitida ⇒ com cabeçalho |
| CT-07 | POST/PUT /tasks (`title`/`priority` com tipo inválido), GET /tasks/search (`priority`/`user_id` não inteiros), PUT /categories/<id> sem JSON | 500 (traceback HTML) → 400 `{'error': ...}` | MEDIUM | F-013, F-014 | tratar 400 em vez de 500 | parcial (status 500 mantido, corpo JSON genérico sem traceback) | teste novo: cada entrada inválida ⇒ 400 |

Resumo para a pergunta: 7 correções exigem contrato; na Opção 1 ficam residuais 3 CRITICAL (F-002, F-006, F-007) e 0 HIGH (além de parciais MEDIUM em F-012 e F-014).

## Testes afetados
| Teste | Motivo (C-xx/CT-xx) | Classe (T1/T2/T4) | Ajuste previsto |
|---|---|---|---|
| tests/conftest.py::api | C-01 (senhas de seed por variável de ambiente) | T1 | definir `SEED_ADMIN_PASSWORD`/`SEED_MANAGER_PASSWORD`/`SEED_USER_PASSWORD` no `env` dos processos `seed.py`/`app.py` com os mesmos valores atuais; asserções inalteradas |
| tests/conftest.py::api (Opção 2) | CT-02, CT-03, CT-04 | T1 | após `/health`, login como admin do seed e envio de `Authorization` pelo `Cliente`; fixture adicional de cliente anônimo |
| tests/test_api.py (todos exceto `test_raiz`, `test_health`, `test_login_*`) (Opção 2) | CT-02, CT-03, CT-04 | T1 | só autenticação via fixture; asserções idênticas |
| tests/test_api.py::test_login_sucesso (Opção 2) | CT-01 | T2 | `token == "fake-jwt-token-<id>"` → token não previsível **e** aceito em `GET /users/<id>` (200); demais asserções mantidas |
| tests/test_contratos.py (novo, Opção 2) | CT-01…CT-07 | T4 | provas 401/403/400/campo ausente/CORS, com execução vermelha no checkpoint |

## Plano de mudanças
| ID | Mudança | Sev. | Resolve | Arquivos | Padrão | Afeta contrato | Depende de |
|---|---|---|---|---|---|---|---|
| C-01 | Módulo de config por ambiente (`SECRET_KEY` — chave aleatória por processo se ausente, `APP_DEBUG`, `APP_HOST`, `APP_PORT`, `DATABASE_URL`, `CORS_ORIGINS`, `SMTP_*`, senhas de seed); debug desligado e bind `127.0.0.1` por padrão; seed e notificação sem literais; `.env.example` | CRITICAL | F-001, F-003 | app.py, config/settings.py (novo), seed.py, services/notification_service.py, .env.example (novo), tests/conftest.py (T1) | P-01 | não | — |
| C-02 | Remover `marshmallow` e `python-dotenv` (não usados) e mover `requests` para `requirements-dev.txt` | MEDIUM | F-015 (parcial) | requirements.txt, requirements-dev.txt | P-18 | não | — |
| C-03 | Models: `ondelete='SET NULL'` em `tasks.category_id` e anulação das tasks na exclusão de categoria; regra de atraso única em `Task.is_overdue()`; CRUD de categorias em módulo próprio (mesmas URLs) | HIGH | F-011, F-016 | models/, routes/category_routes.py (novo), routes/report_routes.py | P-08, P-10 | não | C-01 |
| C-04 | Hash de senha com `werkzeug.security`; rehash do MD5 legado no login; seed com hash | CRITICAL | F-005 | models/user.py, services/auth_service.py (novo), seed.py | P-03 | não | C-03 |
| C-05 | Camada `services/` (tasks, usuários, categorias, relatórios) e `controllers/` finos; rotas só registram blueprints | HIGH | F-010, F-017 (parcial) | services/, controllers/ (novo), routes/ | P-09 | não | C-03 |
| C-06 | Validação na borda: tipos e faixas (`title` texto, `priority` inteiro 1–5, ids inteiros, query params inteiros), JSON ausente ⇒ 400 em todas as rotas de escrita, cor `#RRGGBB`, nome não vazio, `active` booleano, mesmas regras em criar/atualizar | MEDIUM | F-014 | validators (novo, consolida `process_task_data`), controllers/ | P-07 | CT-07 | C-05 |
| C-07 | Serializadores públicos sem senha (Opção 1: `password: null`; Opção 2: campo omitido) | CRITICAL | F-004 | models/user.py, controllers/ | P-04 | CT-05 | C-03 |
| C-08 | Autenticação por token assinado (`itsdangerous`, já dependência do Flask), decoradores `require_auth`/`require_role`, propriedade em `PUT /users/<id>`, `role` restrito no cadastro (**só Opção 2**) | CRITICAL | F-002, F-006, F-007 | middlewares/auth.py (novo), services/auth_service.py, routes/, controllers/ | P-05 | CT-01, CT-02, CT-03, CT-04 | C-01, C-04, C-07 |
| C-09 | Handler central de erros (`AppError` + `Exception`), formato único `{'error': ...}`, fim dos `except:` nus | MEDIUM | F-013, F-020 | middlewares/error_handler.py (novo), controllers/, utils/ | P-06 | CT-07 (Opção 1: status mantido) | C-05 |
| C-10 | `logging` configurado na composition root; e-mail mascarado; fim dos `print` na aplicação | HIGH | F-008, F-028 | config/logging_config.py (novo), controllers/, services/ | P-15 | não | C-05 |
| C-11 | `joinedload`/`selectinload` nas listagens, contagens por `GROUP BY`, atrasadas contadas no banco | MEDIUM | F-019, F-018 (parcial: sem paginação) | services/ | P-11 | não | C-05 |
| C-12 | `create_app()` como composition root, `create_all` no factory, seed via factory; `python app.py` mantido | HIGH | F-009 | app.py, seed.py, database.py | P-13 | não | C-03, C-05 |
| C-13 | Cabeçalhos de segurança aditivos; CORS restrito por `CORS_ORIGINS` (**só Opção 2**) | CRITICAL | F-012 (parcial), F-002 (parte CORS) | middlewares/security.py (novo), app.py | P-19 | CT-06 | C-01, C-12 |
| C-14 | `datetime.utcnow()` → helper `utc_now()` baseado em `datetime.now(timezone.utc)` (sem `tzinfo` para manter colunas e formato); `Query.get` → `db.session.get` | MEDIUM | F-021, F-022 | models/, services/, seed.py, utils/ | P-14 | não | C-05 |
| C-15 | Constantes de domínio, remoção de imports/funções mortos, `isinstance`, retornos diretos, nomes descritivos | MEDIUM | F-017, F-024, F-025, F-026, F-027 | todos os módulos | P-16 | não | C-01…C-14 |

Ordem de aplicação: C-01 → C-02 → C-03 → C-04 → C-05 → C-06 → C-07 → C-08 → C-09 → C-10 → C-11 → C-12 → C-13 → C-14 → C-15.

Recomendações manuais (sem `C-xx`):
- F-001: rotacionar `SECRET_KEY`, senha SMTP e senhas de seed já presentes no histórico git.
- F-012 (parcial): rate limit no `/login` exige dependência nova (ex.: `flask-limiter`, classe C).
- F-015: rodar `pip-audit -r requirements.txt` (classe C) e atualizar `flask`/`flask-cors` conforme o resultado; declarar a versão de Python suportada.
- F-018 (parcial): paginação com limite padrão muda o contrato das listagens.
- F-023: documentar no README instalação de dev, `python -m pytest`, o efeito destrutivo do `seed.py` e o caminho `instance/tasks.db`.
- F-024 (parcial): decidir se `NotificationService` será integrado ao fluxo de atribuição de tasks ou removido.
- F-016 (parcial): o `instance/tasks.db` existente mantém o schema antigo; habilitar FKs com enforcement exige migração (classe D).

## Plano de comandos
| ID | Comando | Finalidade | Origem | Classe | Efeitos colaterais |
|---|---|---|---|---|---|
| K-00 | `git branch refactor-arch/checkpoint-20261106-140715` | checkpoint do código original (árvore limpa exceto `.claude/` não rastreado; HEAD 489ae25) | 07 §2.2 | C | cria ref de branch local; sem commit |
| K-01 | `git worktree add "<scratchpad>/checkpoint-original" refactor-arch/checkpoint-20261106-140715` | cópia do código original para a prova vermelha (só Opção 2) | 06 §8.9 | C | diretório fora do projeto + metadados em `.git/worktrees` |
| K-02 | `python -m venv .venv` | ambiente isolado (Python 3.14.0 do sistema não tem flask/flask-sqlalchemy/flask-cors/pytest) | README.md:6 (implícito); pip list | C | cria `task-manager-api/.venv` (ignorado pelo `.gitignore`) |
| K-03 | `.venv/Scripts/python.exe -m pip install -r requirements-dev.txt` | instalar dependências do projeto e de teste | README.md:6; requirements-dev.txt:1-2 | C | rede (PyPI); escreve em `.venv` |
| K-04 | `.venv/Scripts/python.exe -m pytest -v -p no:cacheprovider` | baseline V1 e validação final (a fixture copia o projeto para diretório temporário, roda `seed.py` e `app.py` lá, porta 5000) | pytest.ini:1-3; tests/conftest.py:73-100 | B | `__pycache__`, cópia em diretório temporário do pytest |
| K-05 | `.venv/Scripts/python.exe -m compileall -q <arquivos/pacotes>` | V5 após cada bloco | toolchain Python | B | `__pycache__` |
| K-06 | `.venv/Scripts/python.exe -c "from app import create_app; ..."` (listar `url_map`) | V5: rotas registram (após C-12 o import não toca o banco) | app.py | B | nenhum |
| K-07 | `netstat -ano \| findstr :5000` | porta livre antes/depois | 06 §5 | A | nenhum |
| K-08 | `.venv/Scripts/python.exe -m pytest tests/test_contratos.py` na cópia do checkpoint | prova vermelha (só Opção 2) | 06 §8.9 | B (na cópia) | copia o teste novo para a cópia do checkpoint |
| K-09 | `git worktree remove "<scratchpad>/checkpoint-original"` | limpeza da cópia (só Opção 2) | — | C | remove a cópia |
| — | `python seed.py` no diretório do projeto | seed documentado | README.md:7 | D | apaga users/tasks/categories de `instance/tasks.db`; **nunca** executado automaticamente (os testes o rodam só na cópia temporária) |
| — | `pip-audit -r requirements.txt` | auditoria de dependências (F-015) | catálogo SEC-16 | C | rede + instalação de ferramenta; **não planejado** (recomendação) |

## Plano de validação
| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim (após K-02/K-03) | `.venv/Scripts/python.exe -m pytest -v -p no:cacheprovider` (pytest.ini:1-3, B) | 25 testes de integração caixa-preta via HTTP; sobem a aplicação real numa cópia temporária |
| V2 Script de verificação do projeto | não | — | sem lint/check/CI no repositório |
| V3 Boot + requisições existentes | parcial | boot `python app.py` coberto pela fixture de V1 (conftest.py:82-99, espera `/health`) | não há coleção/`curl` versionados |
| V4 Sondagem ad hoc | não aplicável | — | V1 cobre as 22 rotas (P4 não será perguntada) |
| V5 Estático | sempre | K-05, K-06 (B) | compilar e listar rotas |
| Pré-requisitos | | K-02, K-03 (C) | dependências ausentes no Python do sistema; se recusados, V1 não roda e o veredito cai para V5 |
| Testes afetados previstos | | conftest.py (T1, C-01); Opção 2: T1 de autenticação, T2 em `test_login_sucesso`, T4 em tests/test_contratos.py | seção "Testes afetados" |
| Prova prevista por `CT-xx` (Opção 2) | | teste novo para CT-01…CT-07 | vermelho no checkpoint (K-01/K-08) |
| Não exercitável | | `python seed.py` no banco real (destrutivo) | `DELETE /users/<id>` e `DELETE /categories/<id>` são exercitados só na cópia temporária, com dados criados pelos próprios testes |

## Decisões do usuário
- P1 Escopo: "Sim, aplicar todas" (C-01…C-15)
- P2 Modo de comandos: "Completo" (classe C sem perguntar; classe D individual)
- P3 Contrato: "Atualizar contrato" — Opção 2 (CT-01…CT-07 aplicados com testes que comprovem)
- P4 Sondagem ad hoc: não aplicável (V1 cobre as 22 rotas)

================================
Total: 28 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---
# ANEXO — FASE 3 (Run id: 20261106-140715)

## Decisões do usuário (registro)
- Escopo: todas (C-01…C-15)
- Modo de comandos: Completo (classe C executada sem pergunta: K-00, K-01, K-02, K-03, K-09; nenhum comando classe D executado)
- Contrato: Opção 2 — atualizar (CT-01, CT-02, CT-03, CT-04, CT-05, CT-06, CT-07 aplicados)
- Sondagem ad hoc: não aplicável (V1 cobre as 22 rotas)

## Estrutura DEPOIS
```
task-manager-api/
├── app.py                 (41)  composition root: create_app(), injeção do TokenSigner, boot `python app.py`
├── database.py            (3)   instância SQLAlchemy
├── seed.py                (81)  seed via create_app(); senhas por ambiente; hash KDF
├── .env.example                 nomes das variáveis (valores fictícios)
├── config/        settings.py (55) · logging_config.py (16)
├── models/        task.py (117) · user.py (57) · category.py (27) · __init__.py (3)     entidades + consultas
├── services/      task_service.py (78) · user_service.py (68) · category_service.py (42) · report_service.py (83)
│                  auth_service.py (48) · persistence.py (19) · exceptions.py (7) · notification_service.py (53)
├── controllers/   task_controller.py (44) · user_controller.py (69) · category_controller.py (28)
│                  report_controller.py (11) · system_controller.py (11) · validators.py (244)
├── views/         serializers.py (74)                                                  DTOs sem senha
├── middlewares/   auth.py (40) · error_handler.py (24) · security.py (18)
├── routes/        __init__.py (10) · task_routes.py (14) · user_routes.py (17) · category_routes.py (13)
│                  report_routes.py (10) · system_routes.py (8)                         só mapeamento
├── utils/         constants.py (26) · helpers.py (22)
└── tests/         conftest.py · test_api.py · test_contratos.py (novo)
```

| Métrica | ANTES | DEPOIS |
|---|---|---|
| Arquivos-fonte | 15 | 41 (inclui 7 `__init__.py`) |
| Linhas de código (aprox.) | ~1158 | ~1483 |
| Camadas presentes | entrypoint, config misturada, rotas+controllers misturados, models, services/utils sem uso | config, models (dados), services, controllers (+ validação), views (serializadores), routes, middlewares (auth, erros, segurança), composition root |
| Maior arquivo | routes/task_routes.py (299) | controllers/validators.py (244) |
| Arquivos com 3+ papéis | 4 | 0 |

Método de contagem igual ao da Fase 1 (`wc -l`, sem tests/, .venv/, __pycache__/, .claude/).

### Mapa antigo → novo
| Arquivo original | Destino(s) |
|---|---|
| app.py | app.py (`create_app`), config/settings.py, config/logging_config.py, routes/system_routes.py + controllers/system_controller.py (`/`, `/health`), middlewares/security.py |
| routes/task_routes.py | routes/task_routes.py (mapeamento), controllers/task_controller.py, controllers/validators.py, services/task_service.py, views/serializers.py, models/task.py (consultas) |
| routes/user_routes.py | routes/user_routes.py, controllers/user_controller.py, services/user_service.py, services/auth_service.py, middlewares/auth.py |
| routes/report_routes.py | routes/report_routes.py + controllers/report_controller.py + services/report_service.py; CRUD de categorias → routes/category_routes.py + controllers/category_controller.py + services/category_service.py |
| models/task.py, user.py, category.py | mesmos arquivos (sem `to_dict` → views/serializers.py; `validate_*` removidos; `is_overdue` passa a ser a regra única; consultas `get/list/count`); hash em models/user.py com `werkzeug.security` |
| services/notification_service.py | mesmo arquivo (configuração injetada, logger com e-mail mascarado, timeout no SMTP) |
| utils/helpers.py | utils/helpers.py (`utc_now`, `format_date`, `calculate_percentage`, `is_valid_color`, todos usados) + utils/constants.py; `process_task_data` → controllers/validators.py |
| seed.py | seed.py (via `create_app`, senhas `SEED_*`) |
| — (novo) | services/exceptions.py, services/persistence.py, middlewares/error_handler.py, .env.example |

## Mudanças aplicadas
| ID | Status | Observação |
|---|---|---|
| C-01 | aplicada | config/settings.py lê tudo do ambiente; sem `SECRET_KEY` gera chave aleatória por processo (aviso no log); `APP_DEBUG` padrão `false`, `APP_HOST` padrão `127.0.0.1`; seed exige `SEED_*_PASSWORD`; SMTP por `SMTP_*`; `.env.example` |
| C-02 | aplicada (parcial em F-015) | removidos `marshmallow` e `python-dotenv`; `requests` movido para requirements-dev.txt; versões não atualizadas (exige `pip-audit`) |
| C-03 | aplicada | `ondelete='SET NULL'` (bancos novos) + `Task.detach_category` na exclusão; CRUD de categorias em módulo próprio, mesmas URLs (parâmetro interno `cat_id` → `category_id`) |
| C-04 | aplicada | `generate_password_hash`/`check_password_hash`; hash MD5 legado verificado com `hmac.compare_digest` e regravado no login (services/auth_service.py:38-41) |
| C-05 | aplicada | services por domínio; controllers só validam, chamam service e serializam |
| C-06 | aplicada | controllers/validators.py: tipos, faixas, JSON não-objeto ⇒ 400, cor `#xxxxxx`, nome não vazio, `active` booleano, e-mail com domínio pontuado, mesmas regras em criar/atualizar |
| C-07 | aplicada | views/serializers.py: `user_to_public` sem `password` (Opção 2: campo omitido) |
| C-08 | aplicada | middlewares/auth.py (`require_auth`, `require_role`), `TokenSigner` (itsdangerous, `SECRET_KEY`, `TOKEN_MAX_AGE`); propriedade em `PUT /users/<id>`; `role` privilegiado só por admin |
| C-09 | aplicada | middlewares/error_handler.py: `AppError` + handler genérico JSON `{'error': 'Erro interno'}`; `HTTPException` preservada; mensagens 500 do contrato mantidas via services/persistence.py |
| C-10 | aplicada | `logging` configurado no factory; logs só com ids; e-mail mascarado; falhas de banco registram só o tipo da exceção |
| C-11 | aplicada (parcial em F-018) | `joinedload` em `GET /tasks`; contagens por `GROUP BY`; atrasadas filtradas no banco; sem paginação (contrato) |
| C-12 | aplicada | `create_app()`; `create_all` dentro do factory; seed usa o factory; importar `app` não toca o banco |
| C-13 | aplicada (parcial em F-012) | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`; CORS por `CORS_ORIGINS` (padrão: nenhuma origem); rate limit não aplicado (dependência nova) |
| C-14 | aplicada | `utc_now()` (`datetime.now(timezone.utc)` sem tzinfo, mesmo formato de `str()`); `db.session.get` |
| C-15 | aplicada (parcial em F-024) | constantes em utils/constants.py; imports/funções mortos removidos; `isinstance`; retornos diretos; nomes descritivos; `NotificationService` mantido sem uso (decisão de produto) |

## Contratos — resultado
**Opção 2 (atualizar):**

| CT | Rota/campo | Antes → Depois | Por que (F-xxx, CWE/OWASP) | Impacto e como adaptar o cliente | Prova (E-nn) |
|---|---|---|---|---|---|
| CT-01 | POST /login · `token` | `fake-jwt-token-<id>` → token assinado com expiração (8 h padrão) | F-002, CWE-306/A07 | usar o `token` recebido em `Authorization: Bearer <token>` | E-03 verde (`test_ct01_token_forjado_e_rejeitado`, `test_login_sucesso`); E-04 vermelho |
| CT-02 | /tasks*, /categories*, /reports/*, GET /users, GET /users/<id>, GET /users/<id>/tasks | abertas → exigem token válido (401 sem/ inválido) | F-002, CWE-306/CWE-862/A01 | autenticar via `POST /login`; `/`, `/health`, `/login`, `POST /users` seguem abertos | E-03 verde (`test_ct02_*`); E-04 vermelho |
| CT-03 | PUT /users/<id>, DELETE /users/<id> | abertas → token; DELETE e `role`/`active` só admin (403); demais campos só o próprio usuário ou admin | F-006, F-007, CWE-915/CWE-306/A01 | operações administrativas com token de admin | E-03 verde (`test_ct03_*`); E-04 vermelho |
| CT-04 | POST /users · `role` | qualquer `role` aceito → `role` ≠ `user` exige token admin (403) | F-006, CWE-269/A01 | cadastro público sem `role` ou com `user` | E-03 verde (`test_ct04_*`); E-04 vermelho |
| CT-05 | `password` em GET /users/<id>, POST /users, PUT /users/<id>, POST /login | hash MD5 exposto → campo omitido | F-004, CWE-200/A02 | não ler `password` das respostas | E-03 verde (`test_ct05_*`); E-04 vermelho |
| CT-06 | CORS (todas as rotas) | `*` → apenas `CORS_ORIGINS` | F-002, F-012, CWE-942/A05 | configurar `CORS_ORIGINS` com a origem do front | E-03 verde (`test_ct06_*`); E-04 vermelho |
| CT-07 | POST/PUT /tasks, GET /tasks/search, PUT /categories/<id>, POST /users, POST /login (tipos inválidos) + regras C-06 (nome vazio, `active` não booleano, cor inválida, e-mail sem domínio pontuado) | 500 (traceback/HTML) ou 200/201 com dado inválido → 400 `{'error': ...}` | F-013, F-014, CWE-20/CWE-209/A03 | tratar 400 | E-03 verde (`test_ct07_*`, `test_c06_*`); E-04 vermelho |

**Texto-base para o README (seção Resultados):**
> A refatoração `refactor-arch` (Run id 20261106-140715) alterou o contrato de 20 das 22 rotas, aprovado pelo usuário na rodada de perguntas (Opção 2). Motivo: a API não tinha autenticação real (token `fake-jwt-token-<id>`), expunha o hash MD5 das senhas e deixava qualquer cliente criar administradores e excluir usuários (F-002, F-004, F-006, F-007). Agora `POST /login` emite token assinado, as rotas de dados exigem `Authorization: Bearer <token>`, alterar perfil e excluir usuários exige admin, `password` não aparece nas respostas, o CORS segue `CORS_ORIGINS` e entradas com tipo inválido devolvem 400. `/`, `/health`, `/login` e `POST /users` (perfil `user`) continuam públicos. O seed exige `SEED_ADMIN_PASSWORD`, `SEED_MANAGER_PASSWORD` e `SEED_USER_PASSWORD` (ver `.env.example`). Justificativa e provas (testes verdes no código novo e vermelhos no original) em `reports/audit-project-3.md` e `reports/evidence/project-3/20261106-140715/`.

## Alterações em testes
| Teste | Motivo | Classe | Antes/Depois (trecho do diff) | Asserções | Reexecução | Snapshot |
|---|---|---|---|---|---|---|
| tests/conftest.py::servidor / api / anonimo | C-01 (senhas de seed por ambiente), CT-02/03/04 (autenticação) | T1 | `env = {**os.environ, "PYTHONIOENCODING": "utf-8"}` → `+ **AMBIENTE_TESTE` (`SEED_*`, `CORS_ORIGINS`); fixture `api` → login do admin do seed e `Authorization: Bearer`; nova fixture `anonimo` sem credencial; `Cliente` aceita token | mantidas (setup; + 1 asserção de login na fixture) | E-03 | `tests-before/tests/conftest.py` |
| tests/test_api.py::test_login_sucesso | CT-01 | T2 | `assert corpo["token"] == "fake-jwt-token-" + id` → `assert corpo["token"] != "fake-jwt-token-" + id` + token aceito em `GET /users/<id>` (200) | reforçadas (3 → 4) | E-03 verde; E-04 vermelho | `tests-before/tests/test_api.py` |

Demais 24 testes de tests/test_api.py: sem alteração de código (passam a autenticar via fixture `api`). Contagem de `assert` em test_api.py: 83 → 84. Diff completo: `E-06-diff-testes.patch`. Integridade: `git diff --stat -- tests/` = conftest.py e test_api.py (os 2 registrados) + tests/test_contratos.py (novo, registrado); snapshot `tests-before/` idêntico ao HEAD (ignorando CRLF).

## Testes adicionados (Opção 2)
| Teste | CT/F | O que comprova | Verde (código refatorado) | Vermelho (checkpoint original) |
|---|---|---|---|---|
| tests/test_contratos.py::test_ct01_token_forjado_e_rejeitado | CT-01 / F-002 | token previsível ⇒ 401 | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_ct02_rotas_de_dados_exigem_token | CT-02 / F-002 | 16 rotas: sem token e token inválido ⇒ 401 | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_ct02_rotas_publicas_continuam_abertas | CT-02 | `/` e `/health` seguem 200 sem token (guarda de regressão) | E-03 | E-04 (PASSED — esperado: comportamento inalterado) |
| tests/test_contratos.py::test_ct02_token_valido_libera_acesso | CT-02 | com token ⇒ 200 (guarda de regressão) | E-03 | E-04 (PASSED — esperado) |
| tests/test_contratos.py::test_ct03_alterar_e_excluir_usuario_exige_permissao | CT-03 / F-006, F-007 | 401 anônimo; 403 não admin (outro usuário, `role`, `active`, DELETE); 200 no próprio nome; admin exclui | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_ct04_cadastro_anonimo_nao_define_role_privilegiado | CT-04 / F-006 | anônimo `admin`/`manager` ⇒ 403; anônimo `user` ⇒ 201; admin `manager` ⇒ 201 | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_ct05_password_ausente_nas_respostas | CT-05 / F-004 | `password` ausente em POST/GET/PUT de usuário e no login | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_ct06_cors_somente_para_origens_configuradas | CT-06 / F-002, F-012 | origem não permitida sem `Access-Control-Allow-Origin`; permitida com o cabeçalho | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_ct07_tipo_invalido_retorna_400 | CT-07 / F-013, F-014 | 10 entradas com tipo inválido ⇒ 400 JSON | E-03 | E-04 (FAILED) |
| tests/test_contratos.py::test_c06_validacoes_adicionais | CT-07 (C-06) / F-014 | nome vazio, `active` texto, cor inválida, e-mail sem domínio ⇒ 400 | E-03 | E-04 (FAILED) |

## Evidências de execução
(`E-00` — Fase 1 — foi gravado na Fase 2; ver `06-protocolo-validacao.md`, seção 7.)

### E-01 · Suíte pytest (baseline)
Comando:      `.venv/Scripts/python.exe -m pytest -v -p no:cacheprovider`      Diretório: task-manager-api
Origem:       K-04 · pytest.ini:1-3 · Classe B · Autorização: automática (classe B)
Início/Fim:   2026-11-06T14:19:02-03:00 → 2026-11-06T14:19:10-03:00 (duração 8 s)        Exit code: 0
Ambiente:     Python 3.14.0, pytest 9.2.0, Flask 3.0.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.8, Flask-Cors 4.0.0 (.venv criado por K-02/K-03)
Resultado:    passed 25 | failed 0 | skipped 0
Saída (início e fim):
  platform win32 -- Python 3.14.0, pytest-9.2.0, pluggy-1.7.0
  collecting ... collected 25 items
  tests/test_api.py::test_raiz PASSED [  4%]
  [...]
  tests/test_api.py::test_relatorio_por_usuario PASSED [100%]
  ============================= 25 passed in 6.78s ==============================
Bruto:        reports/evidence/project-3/20261106-140715/E-01-baseline-pytest.log
Integridade:  testes alterados/adicionados: 0 (código original)

### E-02 · Rotas registradas (baseline, V5)
Comando:      `<.venv>/python.exe -B -c "from app import app; ...url_map"`      Diretório: worktree do checkpoint (`refactor-arch/checkpoint-20261106-140715`, HEAD 489ae25)
Origem:       K-01 + K-06 · Classe B (na cópia) · Autorização: automática
Exit code:    0
Resultado:    22 combinações método+rota
Bruto:        reports/evidence/project-3/20261106-140715/E-02-baseline-rotas.log

### E-03 · Suíte pytest (após refatoração)
Comando:      `.venv/Scripts/python.exe -m pytest -v -p no:cacheprovider`      Diretório: task-manager-api
Origem:       K-04 · pytest.ini:1-3 · Classe B · Autorização: automática (classe B)
Início/Fim:   2026-11-06T14:29:01-03:00 → 2026-11-06T14:29:11-03:00 (duração 10 s)        Exit code: 0
Ambiente:     idem E-01
Resultado:    passed 35 | failed 0 | skipped 0   (baseline E-01: passed 25 | failed 0 | skipped 0; os 25 originais seguem presentes e passando + 10 novos)
Saída (fim):
  tests/test_contratos.py::test_c06_validacoes_adicionais PASSED
  ============================= 35 passed in 8.43s ==============================
Bruto:        reports/evidence/project-3/20261106-140715/E-03-final-pytest.log
Integridade:  testes alterados/adicionados: 2 alterados + 1 arquivo novo (10 testes) — ver "Alterações em testes" / "Testes adicionados" (verificado por git diff e tests-before/)

### E-04 · Prova de sensibilidade (testes novos/T2 no código original)
Comando:      `<.venv>/python.exe -m pytest tests/test_contratos.py "tests/test_api.py::test_login_sucesso" -v -p no:cacheprovider --tb=line`      Diretório: worktree do checkpoint (HEAD 489ae25) com conftest.py, test_api.py e test_contratos.py novos copiados
Origem:       K-08 · 06 §8.9 · Classe B (na cópia fora do projeto) · Autorização: automática
Início/Fim:   2026-11-06T14:28:07-03:00 → 2026-11-06T14:28:13-03:00 (duração 6 s)        Exit code: 1
Resultado:    failed 9 | passed 2 (as 2 guardas de regressão, esperado)
Saída (fim):
  FAILED tests/test_api.py::test_login_sucesso - AssertionError: assert 'fake-j...
  ========================= 9 failed, 2 passed in 5.22s =========================
Bruto:        reports/evidence/project-3/20261106-140715/E-04-vermelho-checkpoint.log

### E-05 · Compilação e rotas (após refatoração, V5)
Comando:      `.venv/Scripts/python.exe -m compileall -q ...` + `.venv/Scripts/python.exe -B -W error::DeprecationWarning -c "create_app(... DATABASE_URL='sqlite://') ... url_map"`      Diretório: task-manager-api
Origem:       K-05, K-06 · Classe B · Autorização: automática
Início/Fim:   2026-11-06T14:29:11-03:00 → 2026-11-06T14:29:12-03:00        Exit code: 0
Resultado:    compileall OK; 22 combinações método+rota, idênticas a E-02; nenhum `DeprecationWarning` (promovido a erro)
Bruto:        reports/evidence/project-3/20261106-140715/E-05-final-v5-rotas.log

### E-06 · Diff dos testes
Comando:      `git diff -- tests/` + `diff -u /dev/null tests/test_contratos.py`
Resultado:    299 linhas; conftest.py e test_api.py alterados, test_contratos.py novo
Bruto:        reports/evidence/project-3/20261106-140715/E-06-diff-testes.patch

### Comparação antes/depois (rotas)
| Método | Rota | ANTES | DEPOIS | Resultado | Prova |
|---|---|---|---|---|---|
| GET | / | 200 {message, version} | 200 {message, version} | igual | E-01, E-03 |
| GET | /health | 200 {status, timestamp} | 200 {status, timestamp} | igual | E-01, E-03 |
| POST | /login | 200 {message, user(+password), token falso}; 400/401/403 | 200 {message, user(sem password), token assinado}; 400/401/403 | ALTERADO (aprovado CT-01, CT-05) | E-03, E-04 |
| GET | /users | 200 sem token | 401 sem token; 200 com token (mesmas chaves) | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /users/<id> | 200 {..., password, tasks}; 404 | 401 sem token; 200 {..., tasks} sem password; 404 | ALTERADO (aprovado CT-02, CT-05) | E-03, E-04 |
| POST | /users | 201 (+password; qualquer role); 400/409 | 201 sem password; role ≠ user ⇒ 403 sem admin; 400/409 | ALTERADO (aprovado CT-04, CT-05, CT-07) | E-03, E-04 |
| PUT | /users/<id> | 200 sem token (+password); 400/404/409 | 401/403 conforme CT-03; 200 sem password; 400/404/409 | ALTERADO (aprovado CT-03, CT-05, CT-07) | E-03, E-04 |
| DELETE | /users/<id> | 200 sem token; 404 | 401/403 (não admin); 200 admin; 404 | ALTERADO (aprovado CT-03) | E-03, E-04 |
| GET | /users/<id>/tasks | 200; 404 | 401 sem token; 200; 404 | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /tasks | 200 (lista com overdue/user_name/category_name) | 401 sem token; 200 mesmas chaves | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /tasks/<id> | 200 (+overdue); 404 | 401 sem token; 200; 404 | ALTERADO (aprovado CT-02) | E-03, E-04 |
| POST | /tasks | 201; 400/404; 500 em tipo inválido | 401 sem token; 201; 400/404; 400 em tipo inválido | ALTERADO (aprovado CT-02, CT-07) | E-03, E-04 |
| PUT | /tasks/<id> | 200; 400/404; 500 em tipo inválido | 401 sem token; 200; 400/404 | ALTERADO (aprovado CT-02, CT-07) | E-03, E-04 |
| DELETE | /tasks/<id> | 200; 404 | 401 sem token; 200; 404 | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /tasks/search | 200; 500 em parâmetro não inteiro | 401 sem token; 200; 400 | ALTERADO (aprovado CT-02, CT-07) | E-03, E-04 |
| GET | /tasks/stats | 200 {total, pending, in_progress, done, cancelled, overdue, completion_rate} | 401 sem token; 200 mesmas chaves | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /reports/summary | 200 {overview, tasks_by_status, tasks_by_priority, overdue, recent_activity, user_productivity, generated_at} | 401 sem token; 200 mesmas chaves | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /reports/user/<id> | 200 {user, statistics}; 404 | 401 sem token; 200; 404 | ALTERADO (aprovado CT-02) | E-03, E-04 |
| GET | /categories | 200 (+task_count) | 401 sem token; 200 mesmas chaves | ALTERADO (aprovado CT-02) | E-03, E-04 |
| POST | /categories | 201; 400 | 401 sem token; 201; 400 (+ cor inválida) | ALTERADO (aprovado CT-02, CT-07) | E-03, E-04 |
| PUT | /categories/<id> | 200; 404; 500 com corpo `null` | 401 sem token; 200; 404; 400 | ALTERADO (aprovado CT-02, CT-07) | E-03, E-04 |
| DELETE | /categories/<id> | 200; 404 (tasks órfãs) | 401 sem token; 200 (tasks desvinculadas); 404 | ALTERADO (aprovado CT-02) | E-03, E-04 |

CORS (CT-06) vale para todas as rotas. Nenhuma rota `DIVERGENTE`: todas as asserções originais de test_api.py (status e chaves) continuam passando com token (E-03).

### Resumo da validação
| Degrau | Comando | Resultado | Evidência |
|---|---|---|---|
| V1 (baseline) | `.venv/Scripts/python.exe -m pytest -v -p no:cacheprovider` | passed 25 / failed 0 / skipped 0 | E-01 |
| V5 (baseline) | listagem do `url_map` no checkpoint | 22 rotas | E-02 |
| V1 (final) | `.venv/Scripts/python.exe -m pytest -v -p no:cacheprovider` | passed 35 / failed 0 / skipped 0 | E-03 |
| Prova vermelha | testes novos + T2 no checkpoint original | failed 9 / passed 2 (guardas) | E-04 |
| V5 (final) | `compileall` + `url_map` com `-W error::DeprecationWarning` | OK; 22 rotas idênticas | E-05 |
Veredito: VALIDADO (V1) — boot real coberto pela fixture (seed + `python app.py` + `/health`); sem coleção de requisições no projeto (V3 parcial).

## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python; pytest relata Python 3.14.0 (E-00, E-01)
- [x] Framework detectado corretamente — Flask 3.0.0 em requirements.txt:1, `Flask(__name__)`; instalado Flask 3.0.0 (E-00, E-01)
- [x] Domínio da aplicação descrito corretamente — tasks/usuários/categorias/relatórios confirmados nas 22 rotas (E-00, E-02)
- [x] Número de arquivos analisados condiz com a realidade — 15 arquivos / 1158 linhas por `wc -l` (E-00)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — seções na ordem do `03-template-relatorio.md` (este arquivo)
- [x] Cada finding tem arquivo e linhas exatos — linhas confirmadas por `grep -n` e releitura antes da gravação
- [x] Findings ordenados por severidade (CRITICAL → LOW) — F-001…F-007 CRITICAL, F-008…F-011 HIGH, F-012…F-022 MEDIUM, F-023…F-028 LOW
- [x] Mínimo de 5 findings identificados — 28
- [x] Detecção de APIs deprecated incluída (se aplicável) — F-021 (DEP-01), F-022 (DEP-02)
- [x] Skill pausa e pede confirmação antes da Fase 3 — rodada P1/P2/P3 registrada em "Decisões do usuário"

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — config/, models/, services/, controllers/, views/, routes/, middlewares/, app.py; 0 arquivos com 3+ papéis (Estrutura DEPOIS)
- [~] Configuração extraída para módulo de config (sem hardcoded) — config/settings.py; busca por literais de segredo/debug = vazio (reauditoria); valores antigos seguem no histórico git (F-001: rotacionar)
- [x] Models criados para abstrair dados — consultas em models/*.py (`get`, `list_*`, `count_*`, `search`); controllers sem `db`
- [x] Views/Routes separadas para visualização ou roteamento — routes/*.py só `add_url_rule`; views/serializers.py
- [x] Controllers concentram o fluxo da aplicação — controllers/*.py validam, chamam services e serializam
- [x] Error handling centralizado — middlewares/error_handler.py; nenhum `except:` nu nem `str(e)` (reauditoria)
- [x] Entry point claro — app.py `create_app()` + `python app.py` (E-03: fixture sobe por esse comando)
- [x] Aplicação inicia sem erros — fixture sobe `python app.py` e responde `/health` (E-03)
- [x] Endpoints originais respondem corretamente — 2 de 22 rotas iguais; 20 alteradas por contrato aprovado (CT-01…CT-07) com prova E-03/E-04; asserções originais de todas as 22 passam com token (E-03)

## Itens residuais (reauditoria)
- F-001 (parcial, CRITICAL no histórico): o código não tem mais segredos, mas `SECRET_KEY`, senha SMTP e senhas de seed antigas continuam no histórico git — rotacionar (ação manual).
- F-005 (dados legados): hashes MD5 já gravados em `instance/tasks.db` permanecem até o próximo login de cada usuário (migração automática); a verificação MD5 existe só para isso (models/user.py:32-35).
- F-012 (parcial, MEDIUM): sem rate limit no `/login` — exige dependência nova (ex.: `flask-limiter`, classe C).
- F-015 (parcial, MEDIUM): versões fixadas de 2023 (`flask==3.0.0`, `flask-cors==4.0.0`, `requests==2.31.0`) não auditadas — rodar `pip-audit` (classe C); versão de Python não declarada.
- F-018 (parcial, MEDIUM): listagens sem paginação — mudaria o contrato.
- F-023 (LOW): README não documenta testes nem as variáveis `SEED_*` agora exigidas por `python seed.py` (texto-base acima; edição do README não estava no plano).
- F-024 (parcial, LOW): `NotificationService` continua sem uso — decidir integrar ou remover.
- F-016 (observação): `instance/tasks.db` existente mantém o schema antigo (sem `ondelete`); a desvinculação é feita no service. Migrar o schema é classe D.

## Observações da execução
- Stack detectada e confiança: Python 3.14.0 + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1 (alta). SQLAlchemy 2.1.8 instalado como dependência transitiva não fixada.
- Dicas específicas usadas × derivadas do sinal abstrato: todas as dicas Python/Flask/SQLAlchemy do catálogo; nenhum item derivado.
- Nível de organização encontrado e como a Fase 3 se adaptou: `parcialmente-em-camadas` ⇒ mantidos `models/`, `routes/`, `services/`, `utils/`, `database.py`, `app.py`, `seed.py`; regra saiu das rotas para services/controllers; categorias ganharam módulo próprio; criados config/, controllers/, views/, middlewares/.
- Aplicação: C-01/C-02 isoladas; C-03…C-15 aplicadas numa passada estrutural única (a reescrita dos 3 módulos de rotas toca todos os padrões), seguida de V5 (E-05) e V1. A primeira execução da suíte completa já passou (35/35); nenhuma reversão.
- Precedência de erros: a validação de formato (C-06) roda antes das checagens de existência/unicidade. Uma entrada com dois problemas ao mesmo tempo (ex.: `due_date` inválida + `user_id` inexistente; e-mail duplicado + `role` inválido) pode receber outro dos erros esperados (400 em vez de 404/409). Entradas com um único problema mantêm status e mensagem originais.
- `SECRET_KEY` ausente ⇒ chave aleatória por processo, com aviso no log; defina-a em produção para que os tokens sobrevivam a reinícios.
- Falsos positivos descartados: 8 (ver "Descartados / falsos positivos").
- Limitações da validação: sem coleção de requisições (V3 parcial pela fixture); rate limit e auditoria de dependências não executados; `python seed.py` no banco real (classe D) não executado — `instance/tasks.db` intacto (mtime 2026-11-04).
- Arquivos criados pela execução fora do código-fonte: `task-manager-api/.venv/` (ignorado pelo git), `__pycache__/`, branch `refactor-arch/checkpoint-20261106-140715` (mantida para o usuário decidir), worktree em scratchpad (removida por K-09). Nenhum commit feito.
- Logs do Windows exibem acentos com a codificação do console (cp1252); sem efeito funcional.

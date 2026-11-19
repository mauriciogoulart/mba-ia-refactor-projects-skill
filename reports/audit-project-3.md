================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Path:    task-manager-api
Run:     2026-11-16T21:45:49-03:00          Run id: 20261116-214549
Stack:   Python 3.14 + Flask 3.0.0 (confiança: alta)
Files:   15 analyzed | ~1158 lines of code
Architecture: parcialmente-em-camadas
Skill:   refactor-arch 1.2 | Catalog 1.2
Evidence: reports/evidence/project-3/20261116-214549/

## Summary
CRITICAL: 7 | HIGH: 4 | MEDIUM: 11 | LOW: 6
Total: 28 findings (181 ocorrências)
Por categoria: Segurança 13 | Arquitetura 7 | Deprecated 2 | Testes 1 | Qualidade 5 | Outro 0
Cobertura: 15/15 arquivos-fonte lidos integralmente; testes (2) também lidos integralmente

## Estrutura ANTES
```
task-manager-api/
├── app.py
├── database.py
├── seed.py
├── models/
│   ├── __init__.py
│   ├── category.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── __init__.py
│   ├── report_routes.py
│   ├── task_routes.py
│   └── user_routes.py
├── services/
│   ├── __init__.py
│   └── notification_service.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── tests/
    ├── conftest.py
    └── test_api.py
```

| Métrica | Valor |
|---|---|
| Arquivos-fonte | 15 |
| Linhas de código (aprox.) | ~1158 |
| Camadas presentes (papéis) | entrypoint/config (app.py), rotas+controllers (routes/), models (models/), service (não usado), util (não usado) |
| Maior arquivo | routes/task_routes.py (299) |
| Arquivos com 3+ papéis | 4 (app.py, routes/task_routes.py, routes/user_routes.py, routes/report_routes.py) |

## Superfície de ataque
| Método | Rota | Handler (arquivo:linha) | Autenticação | Administrativa/destrutiva |
|---|---|---|---|---|
| GET | / | app.py:27 | não | não |
| GET | /health | app.py:23 | não | não |
| GET | /tasks | routes/task_routes.py:12 | não | não |
| GET | /tasks/<id> | routes/task_routes.py:66 | não | não |
| POST | /tasks | routes/task_routes.py:86 | não | não |
| PUT | /tasks/<id> | routes/task_routes.py:157 | não | não |
| DELETE | /tasks/<id> | routes/task_routes.py:226 | não | sim |
| GET | /tasks/search | routes/task_routes.py:241 | não | não |
| GET | /tasks/stats | routes/task_routes.py:274 | não | não |
| GET | /users | routes/user_routes.py:11 | não | não |
| GET | /users/<id> | routes/user_routes.py:28 | não | não |
| POST | /users | routes/user_routes.py:43 | não | sim (aceita `role`) |
| PUT | /users/<id> | routes/user_routes.py:93 | não | sim (altera `role`/`active`) |
| DELETE | /users/<id> | routes/user_routes.py:135 | não | sim (apaga tasks em cascata) |
| GET | /users/<id>/tasks | routes/user_routes.py:154 | não | não |
| POST | /login | routes/user_routes.py:186 | n/a (emite token falso) | não |
| GET | /reports/summary | routes/report_routes.py:13 | não | não |
| GET | /reports/user/<id> | routes/report_routes.py:104 | não | não |
| GET | /categories | routes/report_routes.py:158 | não | não |
| POST | /categories | routes/report_routes.py:168 | não | não |
| PUT | /categories/<id> | routes/report_routes.py:191 | não | não |
| DELETE | /categories/<id> | routes/report_routes.py:212 | não | sim |

## Findings

### [CRITICAL] F-001 · SEC-02 Segredos e credenciais hardcoded
File: app.py:13; services/notification_service.py:9-10
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `app.config['SECRET_KEY'] = 'supe***'` · `self.email_password = 'senh***'`
Description: a `SECRET_KEY` do Flask é literal no código versionado e carregada em runtime; a credencial SMTP (usuário e senha da conta `task***`) também é literal no serviço de notificação. Toda a configuração (URI do banco, chave) está fixa em `app.py:11-13`, sem módulo de config nem leitura de ambiente.
Impact: qualquer pessoa com acesso ao repositório conhece a chave de assinatura (sessões/tokens assinados) e a senha SMTP; trocar o valor exige alterar código.
Recommendation: extrair configuração para módulo de config lido do ambiente, sem valor secreto padrão (chave efêmera aleatória quando ausente); remover a credencial SMTP do fonte. Segredos já publicados no histórico git devem ser rotacionados (ação manual). (Playbook P-01)

### [CRITICAL] F-002 · SEC-09 Autenticação ausente/falsa e CORS aberto
File: app.py:15; routes/user_routes.py:186-211 (e as demais 19 rotas de dados)
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / CWE-862 / A01:2021, A07:2021
Evidência: `'token': 'fake-jwt-token-' + str(user.id)` · `CORS(app)`
Description: nenhuma rota verifica identidade; o login devolve um token previsível (`fake-jwt-token-<id>`) que nunca é validado; `CORS(app)` libera qualquer origem. Há dados pessoais (nome, e-mail) e escrita em todas as entidades. Severidade CRITICAL porque **nenhuma** rota verifica identidade e há PII e escrita (regra do catálogo).
Impact: qualquer cliente remoto lê e altera tasks, usuários e categorias; qualquer site pode chamar a API pelo navegador da vítima.
Recommendation: token assinado com expiração emitido no login, verificação obrigatória nas rotas de dados, CORS restrito a origens configuradas. (Playbook P-05, P-19)

### [CRITICAL] F-003 · SEC-05 Modo debug ativo com bind público
File: app.py:34
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-489 / A05:2021
Evidência: `app.run(debug=True, host='0.0.0.0', port=5000)`
Description: debug fixo no código de inicialização, escutando em todas as interfaces.
Impact: o depurador interativo do Werkzeug fica exposto na rede (stack traces e console), além do reloader em produção.
Recommendation: debug e host lidos da configuração, desligado e `127.0.0.1` por padrão. (Playbook P-01)

### [CRITICAL] F-004 · SEC-07 Hash de senha exposto nas respostas
File: models/user.py:21; routes/user_routes.py:33, 85, 129, 209
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-200 / CWE-201 / A02:2021
Evidência: `'password': self.password,` (em `User.to_dict()`)
Description: `User.to_dict()` inclui o hash da senha e é devolvido por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`, todas sem autenticação.
Impact: qualquer cliente obtém o hash MD5 sem salt (F-005) de qualquer usuário, inclusive do administrador, e o quebra offline trivialmente.
Recommendation: serializar usuários sem o campo `password` (DTO de saída). (Playbook P-04)

### [CRITICAL] F-005 · SEC-06 Senha armazenada com MD5 sem salt
File: models/user.py:29, 32
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-327 / CWE-916 / A02:2021
Evidência: `self.password = hashlib.md5(pwd.encode()).hexdigest()`
Description: a senha é derivada por MD5 sem salt e comparada por igualdade direta (`check_password`).
Impact: hashes vazados (F-004) são revertidos por tabela/força bruta em segundos; senhas iguais têm hash igual.
Recommendation: KDF adequado (`werkzeug.security`, já instalado com o Flask) e migração transparente dos hashes MD5 legados no login. (Playbook P-03)

### [CRITICAL] F-006 · SEC-03 Rotas destrutivas sem autenticação
File: routes/report_routes.py:211-223; routes/task_routes.py:225-238; routes/user_routes.py:134-151
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021
Evidência: `@user_bp.route('/users/<int:user_id>', methods=['DELETE'])` → `db.session.delete(t)` para cada task e `db.session.delete(user)`
Description: remoção de usuário (com exclusão em cascata das tasks dele), de categoria e de task sem nenhuma verificação de identidade ou perfil.
Impact: qualquer cliente remoto destrói dados por enumeração de IDs.
Recommendation: exigir autenticação em todas e perfil administrador para remover usuário e categoria. (Playbook P-05)

### [CRITICAL] F-007 · SEC-10 Escalação de privilégio por mass assignment
File: routes/user_routes.py:52, 71-78, 119-125
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-915 / CWE-269 / A01:2021
Evidência: `role = data.get('role', 'user')` … `user.role = role` · `user.role = data['role']` · `user.active = data['active']`
Description: `POST /users` aceita `role` do corpo (inclusive `admin`) e `PUT /users/<id>` grava `role` e `active` de qualquer usuário, sem autenticação.
Impact: qualquer pessoa cria uma conta administradora ou promove/desativa contas de terceiros.
Recommendation: `role`/`active` só alteráveis por administrador autenticado; cadastro público cria apenas `user`; edição de usuário só pelo próprio ou por admin. (Playbook P-05, P-07)

### [HIGH] F-008 · SEC-08 Dados pessoais em logs
File: routes/user_routes.py:83; services/notification_service.py:21
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-532 / A09:2021
Evidência: `print(f"Usuário criado: {user.id} - {user.name}")` · `print(f"Email enviado para {to}")`
Description: nome do usuário (e e-mail, no serviço de notificação) gravados na saída padrão como log, sem mascaramento.
Impact: PII persiste em logs de servidor/agregadores sem controle de acesso.
Recommendation: logger estruturado registrando apenas identificadores. (Playbook P-15)

### [HIGH] F-009 · SEC-02 Credenciais de seed em texto no fonte (administrador)
File: seed.py:19, 26, 33
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `u1.set_password('****')` (4 caracteres; usuário `role='admin'`)
Description: as senhas dos três usuários de demonstração, incluindo o administrador `joao@email.com`, estão literais no seed versionado.
Impact: qualquer instância semeada tem um administrador com senha pública.
Recommendation: senhas de seed lidas de variáveis de ambiente (aleatórias quando ausentes, nunca impressas) e fixture dos testes adaptada. (Playbook P-01 — credenciais de seed)

### [HIGH] F-010 · ARC-02 Lógica de negócio e persistência nas rotas
File: routes/report_routes.py:12-155; routes/task_routes.py:11-299; routes/user_routes.py:10-211
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `if t.due_date < datetime.utcnow(): if t.status != 'done' and t.status != 'cancelled': ...` dentro de `get_tasks()`; `db.session.add(task)` / `db.session.commit()` nos handlers
Description: os handlers validam, aplicam regras (atraso, estatísticas, cascata de exclusão, agregações de relatório), consultam e persistem diretamente; não há camada de service (services/ contém só um serviço não usado) nem controllers separados das rotas.
Impact: regras não testáveis isoladamente, duplicadas entre rotas (F-017) e acopladas ao HTTP.
Recommendation: extrair services por domínio, controllers finos e rotas só de roteamento. (Playbook P-09, P-08)

### [HIGH] F-011 · ARC-06 CRUD de categorias no módulo de relatórios
File: routes/report_routes.py:157-223
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `@report_bp.route('/categories', methods=['POST'])`
Description: os quatro handlers de categorias (listar, criar, atualizar, remover) estão no blueprint `reports`.
Impact: responsabilidade fora do lugar dificulta localizar e proteger o domínio de categorias.
Recommendation: módulo próprio de categorias (rota/controller/service), mantendo os mesmos caminhos. (Playbook P-08)

### [MEDIUM] F-012 · SEC-17 Falta de proteções HTTP básicas
File: app.py:15; routes/user_routes.py:186
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-770 / CWE-693 / A05:2021
Evidência: `CORS(app)` · `def login():` sem limite de tentativas
Description: nenhum limite de tentativas em `/login`, nenhum cabeçalho de segurança (`X-Content-Type-Options`, `X-Frame-Options` etc.), CORS irrestrito.
Impact: força bruta de senha sem barreira; respostas sem endurecimento básico.
Recommendation: limite de falhas de login, cabeçalhos de segurança aditivos, CORS restrito. (Playbook P-19)

### [MEDIUM] F-013 · SEC-16 Dependências não usadas e sem lockfile
File: requirements.txt:4-6
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-1104 / A06:2021
Evidência: `marshmallow==3.20.1`, `requests==2.31.0`, `python-dotenv==1.0.0`
Description: `marshmallow` e `python-dotenv` nunca são importados; `requests` só é usado pelos testes (`tests/conftest.py:18`) mas está nas dependências de runtime; não há lockfile. As versões fixadas (flask 3.0.0, flask-cors 4.0.0) são antigas; não consultei CVEs (rede = classe C).
Impact: superfície de ataque e de atualização maior que o necessário.
Recommendation: remover/realocar as não usadas e rodar `pip-audit` (classe C, sugerido). (Playbook P-18)

### [MEDIUM] F-014 · SEC-12 Validação de entrada ausente ou frágil
File: routes/report_routes.py:180, 196-202; routes/task_routes.py:96-100, 113, 167-170, 182, 261, 264; routes/user_routes.py:61, 102-103, 124-125
Ocorrências: 11 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-20 / A03:2021
Evidência: `if priority < 1 or priority > 5:` (sem checar tipo) · `tasks.filter(Task.priority == int(priority))`
Description: tipos não são verificados (prioridade texto, título numérico, `int()` em query string) e geram exceção não tratada; `PUT /categories` usa `data` sem checar `None`; cor da categoria não é validada (`is_valid_color` existe e não é usado); nome vazio e `active` não booleano aceitos em `PUT /users`; regex de e-mail aceita domínio sem ponto.
Impact: erros 500/traceback para entradas triviais e dados inconsistentes gravados.
Recommendation: validação na borda com tipos e faixas, resposta 400 padronizada. (Playbook P-07)

### [MEDIUM] F-015 · SEC-13 Exceções não tratadas chegam ao cliente
File: routes/task_routes.py:113, 182, 261, 264; routes/report_routes.py:197
Ocorrências: 5 · Confiança: LIKELY · Categoria: Segurança
CWE/OWASP: CWE-209 / A05:2021
Evidência: `tasks = tasks.filter(Task.user_id == int(user_id))` (ValueError sem tratamento) + `debug=True` (app.py:34)
Description: não há `errorhandler` central; as exceções acima sobem até o Werkzeug, que com `debug=True` devolve a página de depuração com stack trace. Não executado na Fase 2 (somente leitura), por isso LIKELY.
Impact: vazamento de caminhos, código e variáveis internas.
Recommendation: handler central de erros com corpo JSON genérico. (Playbook P-06)

### [MEDIUM] F-016 · ARC-10 Integridade referencial ausente
File: models/task.py:13-14; routes/report_routes.py:217-219
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)` · `db.session.delete(cat)`
Description: remover uma categoria deixa tasks com `category_id` apontando para registro inexistente (SQLite não aplica FK sem `PRAGMA foreign_keys`); nenhuma regra `ondelete`/tratamento no código.
Impact: dados órfãos e contagens incoerentes.
Recommendation: desvincular (`category_id = NULL`) as tasks ao remover a categoria, na mesma transação. (Playbook P-10)

### [MEDIUM] F-017 · ARC-08 Código duplicado
File: models/task.py:50-60; routes/report_routes.py:34-36, 132-135; routes/task_routes.py:17-39, 71-80, 92-114, 166-184, 283-287; routes/user_routes.py:162-180; utils/helpers.py:57-108
Ocorrências: 11 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `if t.status != 'done' and t.status != 'cancelled':` (regra "atrasada" repetida 7 vezes; `Task.is_overdue` existe e não é usado)
Description: regra de atraso repetida em 7 lugares; serialização de task refeita à mão em 2 rotas apesar de `Task.to_dict`; validações de criar/atualizar task duplicadas e uma terceira versão em `process_task_data` (não usada).
Impact: correções precisam ser replicadas; divergências já existem (formatos de data aceitos diferentes).
Recommendation: regra única no model/service, serialização e validação centralizadas. (Playbook P-16)

### [MEDIUM] F-018 · ARC-11 Sem paginação e contagens repetidas
File: routes/report_routes.py:15-30, 53, 159; routes/task_routes.py:14, 266, 275-281; routes/user_routes.py:12
Ocorrências: 7 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `tasks = Task.query.all()` · 12 `count()` separados em `summary_report`
Description: listagens carregam a tabela inteira; relatórios fazem uma consulta `COUNT` por status/prioridade onde uma agregação resolve.
Impact: tempo e memória crescem linearmente com os dados.
Recommendation: agregação com `GROUP BY` e paginação (`limit`/`offset`). (Playbook P-11)

### [MEDIUM] F-019 · ARC-07 Queries N+1
File: routes/report_routes.py:56, 163; routes/task_routes.py:42, 51; routes/user_routes.py:22
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `user = User.query.get(t.user_id)` dentro de `for t in tasks:`
Description: uma consulta por item em listagens de tasks (usuário e categoria), usuários (`len(u.tasks)`), relatório de produtividade e categorias (`count` por categoria).
Impact: 2N+1 consultas por requisição.
Recommendation: carregamento antecipado/agregação. (Playbook P-11)

### [MEDIUM] F-020 · ARC-09 Tratamento de erro ruim
File: routes/report_routes.py:186, 207, 221; routes/task_routes.py:62, 137, 151, 204, 221, 236; routes/user_routes.py:87, 130, 149; services/notification_service.py:23; utils/helpers.py:46, 49, 88
Ocorrências: 16 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `except:` → `return jsonify({'error': 'Erro interno'}), 500`
Description: 12 `except:` genéricos e 4 `except Exception` que descartam o erro (só `print`); sem handler central (`errorhandler` ausente).
Impact: falhas silenciosas e diagnóstico impossível.
Recommendation: handler central, exceções específicas e log da causa. (Playbook P-06)

### [MEDIUM] F-021 · DEP-01 `datetime.utcnow()` deprecated (Python 3.12+)
File: models/category.py:11; models/task.py:15, 16, 52; models/user.py:14; routes/report_routes.py:35, 42, 45, 71, 133; routes/task_routes.py:31, 72, 215, 285; routes/user_routes.py:172; seed.py:66, 67, 69, 70, 74; services/notification_service.py:35; utils/helpers.py:38
Ocorrências: 22 · Confiança: CONFIRMED · Categoria: Deprecated
CWE/OWASP: n/a
Evidência: `created_at = db.Column(db.DateTime, default=datetime.utcnow)`
Description: o runtime em uso é Python 3.14 (.venv) e não há restrição de versão; `datetime.utcnow()` é deprecated desde 3.12.
Impact: DeprecationWarning hoje, remoção futura.
Recommendation: `datetime.now(timezone.utc)` (mantendo valores UTC sem fuso no banco, para preservar o formato). (Playbook P-14)

### [MEDIUM] F-022 · DEP-02 SQLAlchemy `Query.get()` legado
File: routes/report_routes.py:105, 192, 213; routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227; routes/user_routes.py:29, 94, 136, 155
Ocorrências: 16 · Confiança: CONFIRMED · Categoria: Deprecated
CWE/OWASP: n/a
Evidência: `task = Task.query.get(task_id)`
Description: flask-sqlalchemy 3.1.1 com SQLAlchemy 2.1.8 instalado; `Query.get()` é legado na série 2.x.
Impact: LegacyAPIWarning e remoção futura.
Recommendation: `db.session.get(Model, id)`. (Playbook P-14)

DEP: nenhuma API deprecated de Flask (DEP-04) encontrada para Flask 3.0.0.

### [LOW] F-023 · TST-02 Instruções de teste ausentes
File: README.md:5-11
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Testes
CWE/OWASP: n/a
Evidência: seção "Como rodar" só com `pip install`, `python seed.py`, `python app.py`
Description: há suíte pytest (`pytest.ini`, `requirements-dev.txt`), mas o README não diz como instalá-la nem rodá-la e não há CI. (Finding de ausência; referência: README.md.)
Impact: validação depende de descoberta manual.
Recommendation: documentar `pip install -r requirements-dev.txt` e `python -m pytest` (recomendação manual).

### [LOW] F-024 · QLT-03 Imports e código mortos
File: app.py:7; models/task.py:3, 38-60; models/user.py:34-38; routes/report_routes.py:7-8; routes/task_routes.py:7; routes/user_routes.py:6; services/notification_service.py:4-48; utils/helpers.py:3-7, 9-108
Ocorrências: 11 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `import os, sys, json, datetime` (só `datetime` é usado)
Description: imports sem uso em 6 arquivos; `NotificationService` nunca instanciado; helpers e constantes de `utils/helpers.py` sem chamadas (`format_date`/`calculate_percentage` são importados e não usados); `Task.validate_*`, `Task.is_overdue` e `User.is_admin` sem uso (busca por nome em todo o projeto).
Impact: ruído e falsa impressão de camadas existentes.
Recommendation: remover ou integrar. (Playbook P-16)

### [LOW] F-025 · QLT-05 Estilo inconsistente
File: models/task.py:40-43, 46-48; models/user.py:35-38; routes/task_routes.py:30-39, 141, 210; utils/helpers.py:21-23, 103
Ocorrências: 8 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `if type(tags) == list:`
Description: `type(x) == list` em vez de `isinstance`; `if/else` que devolve booleano; `if` aninhados em vez de expressão.
Impact: legibilidade.
Recommendation: padronizar. (Playbook P-16)

### [LOW] F-026 · QLT-02 Nomes ruins
File: routes/report_routes.py:24-28, 161; routes/task_routes.py:16, 151; routes/user_routes.py:14
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `p1 = Task.query.filter_by(priority=1).count()`
Description: variáveis `p1…p5`, `t`, `u`, `c`, `e` sem significado.
Impact: legibilidade.
Recommendation: nomes descritivos. (Playbook P-16)

### [LOW] F-027 · QLT-01 Magic numbers e strings soltas
File: routes/task_routes.py:96, 99, 110, 113, 167, 169, 177, 182; routes/user_routes.py:64, 71, 115, 120
Ocorrências: 12 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `if status not in ['pending', 'in_progress', 'done', 'cancelled']:`
Description: listas de status/papéis e limites (título 3–200, prioridade 1–5, senha ≥ 4) repetidos como literais; as constantes de `utils/helpers.py:110-116` não são usadas.
Impact: regra espalhada.
Recommendation: constantes nomeadas únicas. (Playbook P-16)

### [LOW] F-028 · QLT-04 `print` no lugar de logger
File: routes/task_routes.py:149, 153, 219, 234; routes/user_routes.py:83, 89, 147; services/notification_service.py:21, 24; utils/helpers.py:39, 41
Ocorrências: 11 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `print(f"Task criada: {task.id} - {task.title}")`
Description: saída por `print` como mecanismo de log (seed.py, script de CLI, fica fora).
Impact: sem nível, sem destino configurável.
Recommendation: `logging`. (Playbook P-15)

## Descartados / falsos positivos
- ARC-01 em routes/task_routes.py, routes/user_routes.py, routes/report_routes.py, app.py — descartado porque models e banco estão em módulos próprios; nenhum arquivo concentra todas as camadas (rubrica CRITICAL). A mistura rota+regra+dados é reportada como ARC-02 (F-010).
- SEC-01 em routes/task_routes.py:252-253 — descartado: `Task.title.like(f'%{query}%')` usa filtro do ORM com parâmetro ligado, não SQL montado.
- SEC-11 (IDOR) em routes/user_routes.py:93, 154 — descartado: não existe identidade no fluxo; reportado como SEC-09 (F-002), conforme o catálogo.
- SEC-15 em routes/user_routes.py:140-146 — descartado: exclusão das tasks e do usuário ocorre num único `commit` (atômico).
- ARC-03 em services/notification_service.py:6 — descartado: lista de instância (não global) e a classe nunca é instanciada (coberto por F-024).
- ARC-04 — descartado: acesso direto ao ORM nos handlers já coberto por F-010; não há instanciação de infraestrutura fora do composition root além do serviço morto.
- TST-01/TST-03 — descartados: existe suíte de integração (25 testes) com dependências declaradas e instaladas no .venv.

## Correções que exigem mudança de contrato

| ID | Rota/campo | Mudança | Sev. | Motivo (Finding) | Impacto para clientes | Refatorar | Manter contrato\* | Híbrido | Prova prevista |
|---|---|---|---|---|---|---|---|---|---|
| CT-01 | todas as rotas de dados (exceto `GET /`, `GET /health`, `POST /login`, `POST /users`) | exigir `Authorization: Bearer <token>` (401 sem/ com token inválido) | CRITICAL | F-002, F-006 | enviar o token obtido em `POST /login` | aplica | não (fica sem correção) | aplica — variante mínima (mesmas rotas, payloads e respostas para o cliente autenticado) | teste novo (integração) + execução local autenticada |
| CT-02 | `POST /login` → campo `token` | token assinado com expiração no lugar de `fake-jwt-token-<id>` | CRITICAL | F-002 | o valor do token muda de formato (chave mantida) | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração: token forjado ⇒ 401) + execução local autenticada |
| CT-03 | campo `password` em `GET /users/<id>`, `POST /users`, `PUT /users/<id>`, `POST /login` | omitir campo | CRITICAL | F-004 | deixa de receber o hash | aplica | sim (valor neutralizado, chave mantida) | aplica — variante mínima (omite) | teste novo (integração: campo ausente) + execução local autenticada |
| CT-04 | `POST /users` (`role`/`active`), `PUT /users/<id>` | `role`≠`user`/`active` só por admin (403); editar usuário só o próprio ou admin (403) | CRITICAL | F-007 | cadastro público cria só `user`; promoções exigem token de admin | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-05 | `DELETE /users/<id>`, `DELETE /categories/<id>` | exigir perfil admin (403 para não-admin) | CRITICAL | F-006 | só administradores removem usuários/categorias | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-06 | CORS (todas as rotas) | origens permitidas só as configuradas (`CORS_ORIGINS`; padrão: nenhuma origem cruzada) | CRITICAL | F-002, F-012 | front-ends em outra origem precisam ser configurados | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração: `Origin` não permitida sem `Access-Control-Allow-Origin`) |
| CT-07 | `PUT /users/<id>` (`name`, `active`, `email`), `POST/PUT /categories` (`name`, `color`) | rejeitar com 400 valores antes aceitos (nome vazio, `active` não booleano, e-mail sem ponto no domínio, cor fora de `#RRGGBB`) | MEDIUM | F-014 | payloads inválidos que antes eram gravados passam a 400 | aplica | não (só a parte retrocompatível: tipo inválido ⇒ 400) | não aplica (MEDIUM/LOW) | teste novo (integração) |
| CT-08 | `GET /tasks`, `GET /tasks/search`, `GET /users`, `GET /categories` | limite padrão de 100 itens + `limit`/`offset` (formato array mantido) | MEDIUM | F-018 | listas com mais de 100 itens passam a exigir paginação | aplica | não (só parâmetros opcionais, sem limite padrão) | não aplica (MEDIUM/LOW; só parâmetros opcionais) | teste novo (integração) |

("parcial" em CRITICAL/HIGH conta como sem correção no resumo abaixo e na segunda confirmação.)

Resumo para a pergunta: 8 correções exigem contrato. Refatorar: corrige todas. Manter contrato\*: ficam sem correção 3 CRITICAL (F-002, F-006, F-007) e 0 HIGH, exige segunda confirmação. Híbrido: aplica 6 (CT-01 a CT-06, CRITICAL/HIGH); ficam sem correção 2 MEDIUM/LOW (CT-07, CT-08 — só a parte retrocompatível).

## Testes afetados
| Teste | Motivo (C-xx/CT-xx) | Classe (T1/T2/T4) | Ajuste previsto |
|---|---|---|---|
| tests/conftest.py (fixture `api`, classe `Cliente`) | C-02 (seed por ambiente), CT-01/CT-04/CT-05 (autenticação) | T1 | gerar `SECRET_KEY` e senhas `SEED_*` aleatórias no ambiente do subprocesso; logar como admin e enviar `Authorization` por padrão; expor clientes anônimo e de usuário comum e o caminho do log do servidor para os testes de prova; `PYTHONUNBUFFERED=1` |
| tests/test_api.py::test_login_sucesso | C-02, CT-02 | T1 + T2 | senha do admin vinda da fixture; asserção do formato `fake-jwt-token-<id>` substituída por: token presente, diferente do formato previsível e aceito em rota protegida (200) |
| tests/test_api.py (demais 24 testes) | CT-01/CT-04/CT-05 | T1 (sem alteração textual) | autenticação de admin fornecida pela fixture; asserções inalteradas |
| pytest.ini | testes de unidade novos importam módulos do projeto | T1 | `pythonpath = .` |
| tests/test_seguranca.py (novo) | CT-01…CT-08, F-004, F-006, F-007, F-008, F-009 | T4 (integração) | sem token ⇒ 401, token forjado ⇒ 401, não-admin ⇒ 403, campo `password` ausente, CORS, log sem PII, senha antiga do seed rejeitada, validação e paginação |
| tests/test_unidade.py (novo) | F-001, F-003, F-005, F-010, F-011 | T4 (unidade) | config lida do ambiente (debug off/127.0.0.1), hash KDF + migração MD5, regra de atraso/estatística no service, módulo de categorias |

## Plano de mudanças
| ID | Mudança | Sev. | Resolve | Arquivos | Padrão | Afeta contrato | Depende de |
|---|---|---|---|---|---|---|---|
| C-01 | módulo de config lido do ambiente (SECRET_KEY efêmera se ausente, DATABASE_URL, DEBUG off, HOST 127.0.0.1, PORT, CORS_ORIGINS; `.env` via python-dotenv); `create_app()` | CRITICAL | F-001, F-003 | config/settings.py, app.py | P-01 | não | — |
| C-02 | senhas do seed lidas de `SEED_*_PASSWORD` (aleatórias e não impressas se ausentes); fixture de testes adaptada | HIGH | F-009 | seed.py, tests/conftest.py | P-01 | não | C-01 |
| C-03 | remover `marshmallow` e mover `requests` para requirements-dev (python-dotenv passa a ser usado em C-01) | MEDIUM | F-013 | requirements.txt, requirements-dev.txt | P-18 | não | C-01 |
| C-04 | models com constantes de domínio, `is_overdue` único e desvinculação de tasks ao remover categoria (mesma transação) | MEDIUM | F-016, F-017 | models/*.py | P-08, P-10 | não | — |
| C-05 | hash de senha com `werkzeug.security` + migração transparente de MD5 legado no login | CRITICAL | F-005 | models/user.py | P-03 | não | C-04 |
| C-06 | services por domínio (task, user, category, report, auth) e controllers finos; rotas só roteamento; categorias em módulo próprio (mesmos caminhos) | HIGH | F-010, F-011, F-017 | services/, controllers/, routes/ | P-09, P-08 | não | C-04 |
| C-07 | validação na borda: tipos inválidos ⇒ 400 (compatível) + valores estritos (CT-07) | MEDIUM | F-014 | validators/ (ou services), controllers/ | P-07 | CT-07 | C-06 |
| C-08 | serialização de usuário sem `password` | CRITICAL | F-004 | models/user.py | P-04 | CT-03 | C-06 |
| C-09 | token assinado (itsdangerous, já instalado com o Flask) com expiração; decoradores `login_required`/`admin_required`; regras de role/active e de edição própria; DELETE de usuário/categoria só admin | CRITICAL | F-002, F-006, F-007 | middleware/auth.py, services/auth_service.py, routes/, controllers/ | P-05 | CT-01, CT-02, CT-04, CT-05 | C-01, C-08 |
| C-10 | handlers centrais de erro JSON (400/401/403/404/405/415/500), fim dos `except:` genéricos | MEDIUM | F-015, F-020 | middleware/errors.py, controllers/ | P-06 | não | C-06 |
| C-11 | `logging` com identificadores apenas (sem nome/e-mail) | HIGH | F-008, F-028 | services/, app.py | P-15 | não | C-06 |
| C-12 | eliminar N+1 (eager load/agregações `GROUP BY`) e paginação `limit`/`offset` | MEDIUM | F-018, F-019 | services/ | P-11 | CT-08 | C-06 |
| C-13 | composition root: `create_app()` registra extensões, blueprints, handlers; `db.create_all()` só no factory | HIGH | F-010 | app.py | P-13 | não | C-06 |
| C-14 | cabeçalhos de segurança, limite de falhas de login em memória (sem nova dependência), CORS restrito | MEDIUM | F-012, F-002 | app.py, middleware/ | P-19 | CT-06 | C-01 |
| C-15 | `datetime.utcnow()` → `datetime.now(timezone.utc)` (UTC sem fuso no banco) e `Query.get` → `db.session.get` | MEDIUM | F-021, F-022 | models/, services/, seed.py | P-14 | não | C-06 |
| C-16 | limpeza: imports/helpers mortos, `NotificationService` (nunca instanciado; remove a credencial SMTP), `isinstance`, nomes, constantes | LOW | F-001, F-024, F-025, F-026, F-027 | utils/, services/notification_service.py, models/ | P-16 | não | C-06 |

Recomendações manuais (sem `C-xx`):
- F-023 (TST-02): documentar testes no README (`pip install -r requirements-dev.txt`, `python -m pytest`) e o uso de `SECRET_KEY`/`SEED_*` — o texto-base sai no anexo da Fase 3.
- F-001: rotacionar `SECRET_KEY` e a senha SMTP publicadas no histórico git (ação manual externa).
- F-013: rodar `pip-audit` (classe C, rede) e avaliar atualização de flask/flask-cors.

## Plano de comandos
| ID | Comando | Finalidade | Origem | Classe | Efeitos colaterais |
|---|---|---|---|---|---|
| K-00 | `git worktree add --detach <tmp>/exec-p3/checkpoint HEAD` | checkpoint do código original fora do projeto (baseline V4 e provas vermelhas) | política 07 §2.2 | C | cria worktree fora do repositório e metadado em `.git/worktrees` |
| K-01 | `.venv/Scripts/python -m pytest` | testes do projeto (baseline e final) | pytest.ini; tests/conftest.py | B | copia o projeto para tmp do pytest, roda seed na cópia, porta 5000 |
| K-02 | `.venv/Scripts/python -B -c "<import/compilação dos módulos>"` | verificação rápida (V5) após cada bloco | toolchain Python | B | nenhum (sem bytecode) |
| K-03 | `python app.py` (na cópia em `<tmp>/exec-p3`) | boot (V3/V4) com banco descartável | README.md:10 | B | porta 5000 |
| K-04 | `python seed.py` | seed | README.md:9 | D sobre `instance/tasks.db` do projeto (apaga as 3 tabelas) — **não será executado no projeto**; B apenas em cópias descartáveis (fixture de testes, V4) | apaga dados |
| K-05 | `pip install -r requirements-dev.txt` | instalar dependências | README.md:8 | C | **não necessário**: pacotes já presentes no .venv |
| K-06 | `.venv/Scripts/python -m pytest <testes novos> -o pythonpath=.` no checkpoint | prova de sensibilidade (vermelho no original) | 06 §8.9 | B (na cópia) | porta 5000 |
| K-07 | scripts de requisição em `<tmp>/exec-p3` (python + requests do .venv) | execução local autenticada baseline/final | 06 §5.1 | B (banco descartável) | porta 5000 |
| K-08 | encerrar processos iniciados (`taskkill /PID`), `git worktree remove <tmp>/exec-p3/checkpoint` | limpeza | 06 §4 | B / C | remove worktree criado pela execução |
| K-09 | `pip-audit` | auditoria de CVEs | catálogo SEC-16 | C (rede) | **não será executado** (só recomendado) |

## Plano de validação
| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim | `.venv/Scripts/python -m pytest` (pytest.ini, B) | integração caixa-preta via HTTP, 25 testes |
| V2 Script de verificação do projeto | não | — | sem lint/CI/Makefile |
| V3 Boot + requisições existentes | parcial | boot `python app.py` (README.md:10) | sem coleção de requisições; o boot é exercitado pela fixture do V1 |
| V4 Execução local autenticada | depende de P4 | boot da cópia em `<tmp>/exec-p3` com `DATABASE_URL` temporário + seed próprio + requisições com token do `POST /login` | 22 rotas; baseline no checkpoint e final |
| V5 Estático | sempre | import/compilação dos módulos (B) | — |
| Pré-requisitos | | `pip install -r requirements-dev.txt` (C) | já satisfeitos no .venv |
| Testes afetados previstos | | conftest.py (T1), test_login_sucesso (T1+T2), demais (T1 via fixture) | seção "Testes afetados" |
| Prova prevista (`CT-xx` aplicados e correções CRITICAL/HIGH) | | tests/test_seguranca.py (integração) + tests/test_unidade.py (unidade) + V4; vermelho no checkpoint | F-008 por inspeção do log do servidor da fixture |
| Não exercitável | | envio real de e-mail (serviço morto, removido); banco do projeto `instance/tasks.db` (nunca tocado) | — |

## Decisões do usuário
Resposta da rodada de perguntas: `1A 2A 3A 4A`
- P1 (escopo): Sim, aplicar todas as mudanças do plano
- P2 (modo de comandos): Equilibrado (recomendado)
- P3 (contrato): Refatorar (recomendado) — CT-01 a CT-08
- P4 (execução local autenticada): Sim, incluindo escrita em banco descartável (recomendado)

================================
Total: 28 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---
# ANEXO — FASE 3 (Run id: 20261116-214549)

## Decisões do usuário (registro)
- Escopo: todas (`1A`), mais C-17 incluída na reauditoria (`Q3A`)
- Modo de comandos: Equilibrado (`2A`); lote classe C K-00 e K-08 aprovado (`Q1A`)
- Contrato: Refatorar (`3A`) — CT-01 a CT-08 aplicados; CT-09 aprovado na reauditoria (`Q3A`)
- Execução local autenticada (P4): incluindo escrita em banco descartável (`4A`)
- Mecanismo de identidade (P-05): token assinado com expiração emitido por `POST /login`, com `itsdangerous` e perfis (`Q2A`)
- Correção pós-validação independente: a validação independente reprovou a primeira versão do F-029 por correção parcial; a conclusão foi aplicada dentro da C-17 / CT-09 já aprovada, com evidências novas E-10 a E-17
- Segunda correção pós-validação independente: a segunda validação (commit `5ba4f4b`) reprovou porque o token de uma conta excluída passava a valer para a conta nova que herdava o mesmo id. A correção vincula o token à credencial e inclui os ajustes 2 a 4 da validação. Segundo o coordenador da execução, a ampliação do CT-09 foi aprovada pelo usuário ao autorizar a conclusão das correções. Evidências: E-18 a E-27

### Finding surgido na reauditoria (aprovado na pergunta Q3)

### [HIGH] F-029 · SEC-11 IDOR / falta de checagem de propriedade
File (código antes da correção): routes/user_routes.py, routes/report_routes.py, services/task_service.py (rotas `GET /users`, `GET /users/<id>`, `GET /users/<id>/tasks`, `GET /reports/summary`, `GET /reports/user/<id>`, `PUT /tasks/<id>`, `DELETE /tasks/<id>`)
Ocorrências: 7 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-639 / A01:2021
Evidência: usuário recém-cadastrado por `POST /users` (público, perfil `user`) recebeu 200 ao ler dados e ao alterar e remover tasks de outra pessoa.
Description: na Fase 2 o SEC-11 foi descartado porque não havia identidade no fluxo. A autenticação introduzida por C-09 criou essa identidade, e a reauditoria mostrou que faltava confrontá-la com o dono do recurso.
Impact: qualquer pessoa podia se cadastrar, obter token e ler e-mails de terceiros, além de alterar ou remover tasks alheias.
Recommendation: aplicada em C-17 / CT-09 (Playbook P-05, autorização de propriedade).
Complemento da validação independente: a primeira versão protegia `GET /users/<id>/tasks`, mas as mesmas tasks seguiam acessíveis por `GET /tasks`, `GET /tasks/<id>` e `GET /tasks/search?user_id=<id>`, e um usuário comum podia atribuir ou transferir tasks a terceiros. Todas as leituras e atribuições foram corrigidas (E-11 a E-15).
Complemento da segunda validação independente: o token só carregava o id; excluída a conta A, um novo cadastro B herdava o id e o token de A voltava a valer, lendo os dados de B e trocando a senha dele. No original isso foi reproduzido: B não conseguiu mais entrar (E-18). O token agora carrega uma impressão HMAC do hash de senha atual e responde 401 quando ela não confere (E-19 a E-23).

## Estrutura DEPOIS
```
task-manager-api/
├── app.py                  # composition root: create_app()
├── database.py
├── seed.py
├── .env.example
├── config/settings.py
├── models/                 # constants, task, user, category
├── views/serializers.py    # DTOs de saída
├── validators/             # common, task, user, category
├── services/               # auth, token, task, user, category, report, persistence
├── controllers/            # auth, task, user, category, report
├── routes/                 # task, user, category, report, system
├── middleware/             # auth, error_handler, security
├── utils/                  # clock, errors, limits
└── tests/                  # conftest, test_api, test_seguranca, test_unidade
```

| Métrica | ANTES | DEPOIS |
|---|---|---|
| Arquivos-fonte | 15 | 45 |
| Linhas de código (aprox.) | ~1158 | ~1588 |
| Camadas presentes | entrypoint/config, rotas+controllers, models, service e util não usados | config, models, views, validators, services, controllers, routes, middleware, composition root |
| Maior arquivo | routes/task_routes.py (299) | validators/task_validator.py (136) |
| Arquivos com 3+ papéis | 4 | 0 |

### Mapa antigo → novo
| Arquivo original | Destino(s) |
|---|---|
| app.py | app.py (composition root), config/settings.py, routes/system_routes.py, middleware/error_handler.py, middleware/security.py |
| models/task.py | models/task.py (dados e regra de atraso), views/serializers.py, models/constants.py |
| models/user.py | models/user.py (dados e hash), views/serializers.py |
| models/category.py | models/category.py, views/serializers.py |
| routes/task_routes.py | routes/task_routes.py, controllers/task_controller.py, services/task_service.py, validators/task_validator.py |
| routes/user_routes.py | routes/user_routes.py, controllers/user_controller.py, controllers/auth_controller.py, services/user_service.py, services/auth_service.py, services/token_service.py, validators/user_validator.py |
| routes/report_routes.py (relatórios) | routes/report_routes.py, controllers/report_controller.py, services/report_service.py |
| routes/report_routes.py (categorias) | routes/category_routes.py, controllers/category_controller.py, services/category_service.py, validators/category_validator.py |
| utils/helpers.py | removido; partes úteis em utils/clock.py, utils/errors.py, models/constants.py e validators/ |
| services/notification_service.py | removido (nunca instanciado; continha a credencial SMTP) |

## Mudanças aplicadas
| ID | Status | Observação |
|---|---|---|
| C-01 | aplicada | config/settings.py; chave efêmera fora de produção; `APP_ENV=production` exige `SECRET_KEY` e proíbe debug |
| C-02 | aplicada | senhas de seed via `SEED_*_PASSWORD`; aleatórias e não exibidas quando ausentes |
| C-03 | aplicada | `marshmallow` removido; `requests` movido para requirements-dev.txt; `sqlalchemy`, `werkzeug` e `itsdangerous`, importados diretamente, declarados nas versões já instaladas no .venv (validação independente); nada foi instalado |
| C-04 | aplicada | constantes, `Task.is_overdue` único, consultas nos models |
| C-05 | aplicada | `werkzeug.security` e migração de MD5 legado na primeira conferência válida |
| C-06 | aplicada | services, controllers finos e categorias em módulo próprio |
| C-07 | aplicada | validators/ com tipos, faixas e CT-07; após a segunda validação, prioridade só inteira (rejeita `2.5` e `true`) e textos com surrogate isolado ⇒ 400 em qualquer campo do corpo |
| C-08 | aplicada | views/serializers.py sem `password` |
| C-09 | aplicada | middleware/auth.py e services/token_service.py; após a segunda validação, o token carrega uma impressão HMAC truncada do hash de senha atual, nunca o hash, e é recusado (401) após troca de senha, exclusão da conta ou reaproveitamento do id |
| C-10 | aplicada | handler central em middleware/error_handler.py; nenhum `except:` genérico |
| C-11 | aplicada | `logging` apenas com identificadores |
| C-12 | aplicada | eager load, agregações `GROUP BY`, `limit`/`offset` |
| C-13 | aplicada | `create_app()` como composition root |
| C-14 | aplicada | cabeçalhos de segurança, limite de falhas de login (429) e CORS restrito |
| C-15 | aplicada | utils/clock.py e `db.session.get` |
| C-16 | aplicada | código morto removido |
| C-17 | aplicada (incluída na reauditoria, `Q3A`; concluída após a validação independente) | leituras e alterações de tasks restritas ao responsável e à gestão; listagem, busca, estatísticas e `task_count` de categorias limitados ao próprio usuário; atribuição a terceiros só pela gestão; `user_id`/`category_id` malformados ou fora da faixa ⇒ 400; ids gigantes na URL ⇒ 404; após a segunda validação, `user_id`/`category_id` igual a 0 ⇒ 404, como qualquer id inexistente, e usuário comum não atribui ao id 0 (403) |

## Contratos — resultado
| CT | Rota/campo | Antes → Depois | Por que (F-xxx, CWE/OWASP) | Impacto e como adaptar o cliente | Prova (E-nn) |
|---|---|---|---|---|---|
| CT-01 | rotas de dados | abertas → exigem `Authorization: Bearer <token>` (401) | F-002, F-006, CWE-306/A01 | enviar o token obtido em `POST /login` | E-19 verde; E-20 vermelho; E-21 |
| CT-02 | `POST /login`, campo `token` | `fake-jwt-token-<id>` → token assinado, validade padrão de 1 h, vinculado à credencial: deixa de valer após troca de senha, exclusão da conta ou reaproveitamento do id | F-002, CWE-306/A07 | tratar o token como valor opaco; renovar após expirar ou após trocar a senha | E-19; E-20; E-21 |
| CT-03 | campo `password` | hash devolvido → campo omitido | F-004, CWE-200/A02 | deixar de ler o campo | E-19; E-20; E-21 |
| CT-04 | `POST /users`, `PUT /users/<id>` | `role`/`active` livres → só admin (403); edição só pelo próprio ou admin | F-007, CWE-915/A01 | promoções exigem token de admin | E-19; E-20; E-21 |
| CT-05 | `DELETE /users/<id>`, `DELETE /categories/<id>` | abertas → só admin (403) | F-006, CWE-306/A01 | usar token de admin | E-19; E-20; E-21 |
| CT-06 | CORS | qualquer origem → só `CORS_ORIGINS` (padrão: nenhuma) | F-002, F-012, CWE-942/A05 | configurar as origens dos front-ends | E-19; E-20; E-21 |
| CT-07 | `PUT /users/<id>`, `POST`/`PUT /categories` | valores inválidos gravados → 400 | F-014, CWE-20/A03 | enviar nome não vazio, `active` booleano, e-mail com domínio completo e cor `#RRGGBB`; `priority` inteiro de 1 a 5 em tasks | E-19; E-20; E-21 |
| CT-08 | `GET /tasks`, `/tasks/search`, `/users`, `/categories` | carga total → até 100 itens, com `limit`/`offset` | F-018, CWE-770/A05 | paginar listas com mais de 100 itens | E-19; E-20; E-21 |
| CT-09 | `GET`/`PUT`/`DELETE /tasks/<id>`; `GET /tasks`, `/tasks/search`, `/tasks/stats`; `POST /tasks`; `GET /categories` (`task_count`); `GET /users/<id>`, `/users/<id>/tasks`, `/reports/user/<id>`; `GET /users`, `/reports/summary` | qualquer autenticado → responsável, próprio usuário ou gestão, conforme a rota: acesso direto alheio ⇒ 403; listagem, busca e contagens só com as próprias tasks; atribuir ou transferir a terceiro sem gestão ⇒ 403; task criada por usuário comum fica sob sua responsabilidade; referência malformada ⇒ 400 | F-029, CWE-639/A01 | usar a conta do responsável ou perfil `admin`/`manager` para visão geral e atribuição | E-19; E-20; E-21 |

**Texto-base para o README (seção Resultados):** a refatoração alterou o acesso às rotas de dados, o formato do token de login, a resposta de usuários, o CORS, a validação e a paginação das listagens (CT-01 a CT-09). As mudanças corrigem falhas de autenticação, autorização e exposição de dados e foram aprovadas na rodada de perguntas do Run 20261116-214549; o CT-09 foi aprovado depois da reauditoria. Para usar a API, defina `SECRET_KEY` e `SEED_*_PASSWORD` (ver `.env.example`), rode `python seed.py`, obtenha o token em `POST /login` e envie `Authorization: Bearer <token>`. Testes: `pip install -r requirements-dev.txt` e `python -m pytest`. Justificativas e provas estão em `reports/audit-project-3.md` e `reports/evidence/project-3/20261116-214549/`.

## Alterações em testes
| Teste | Motivo | Classe | Antes/Depois (trecho do diff) | Asserções | Reexecução | Snapshot |
|---|---|---|---|---|---|---|
| tests/conftest.py (fixture `api`, `Cliente`) | C-02, CT-01, CT-04, CT-05, CT-09 | T1 | senhas `SEED_*` e `SECRET_KEY` no ambiente; login de admin, usuário e gerente; `Authorization` por padrão | sem asserções de teste alteradas | E-11 | `tests-before/tests/conftest.py` |
| tests/test_api.py::test_login_sucesso | C-02, CT-02 | T1 + T2 | `"1234"` → `api.senha_admin`; token previsível → token presente, diferente do previsível e aceito em rota protegida | reforçadas (de 3 para 5) | E-11 | `tests-before/tests/test_api.py` |
| pytest.ini | testes de unidade importam módulos do projeto | T1 | `pythonpath = .` | n/a | E-11 | `tests-before/pytest.ini` |

| tests/test_unidade.py::test_listagem_limita_a_100_itens_por_padrao | CT-09 (tasks só visíveis ao responsável) | T1 | as 101 tasks do cenário passam a ter o usuário do teste como responsável | mantidas | E-11 | `tests-before-validacao/tests/test_unidade.py` |

| tests/test_unidade.py::test_token_assinado_valida_adulteracao_e_expiracao | C-09 (token vinculado à credencial) | T1 | `issue(7)`/`verify(token)` → `issue(usuario)`/`verify(token, carregar)` | mantidas (4 cenários iguais, agora conferindo o usuário devolvido) | E-19 | `tests-before-validacao-2/tests/test_unidade.py` |
| tests/test_unidade.py::test_listagem_limita_a_100_itens_por_padrao | C-09 | T1 | `issue(usuario.id)` → `issue(usuario)` | mantidas | E-19 | `tests-before-validacao-2/tests/test_unidade.py` |

Diffs unificados: `E-09-diff-testes.patch` (primeira rodada), `E-17-diff-testes.patch` (primeira validação independente) e `E-25-diff-testes.patch` (segunda validação independente). Os outros 24 testes de `test_api.py` não foram editados; nenhum teste foi removido, pulado ou enfraquecido.

## Testes adicionados (provas)
| Teste | Tipo | CT/F | O que comprova | Verde (código refatorado) | Vermelho (checkpoint original) |
|---|---|---|---|---|---|
| test_seguranca.py::test_rota_sem_token_retorna_401 (18 casos) | integração | CT-01 / F-002, F-006 | sem token ⇒ 401 | E-19 | E-20 |
| test_seguranca.py::test_token_invalido_ou_forjado_retorna_401 (2) | integração | CT-02 / F-002 | token inválido ou forjado ⇒ 401 | E-19 | E-20 |
| test_seguranca.py::test_token_valido_acessa_rota_protegida | integração | CT-01 | token válido ⇒ 200 | E-19 | controle positivo: passa no original |
| test_seguranca.py::test_rotas_publicas_continuam_abertas | integração | CT-01 | `/` e `/health` seguem públicas | E-19 | controle positivo: passa no original |
| test_seguranca.py::test_respostas_de_usuario_nao_trazem_password | integração | CT-03 / F-004 | campo ausente | E-19 | E-20 |
| test_seguranca.py::test_cadastro_publico_cria_apenas_usuario_comum | integração | CT-04 / F-007 | `role=admin` sem admin ⇒ 403 | E-19 | E-20 |
| test_seguranca.py::test_usuario_nao_altera_outro_usuario | integração | CT-04 / F-007 | edição de terceiro ⇒ 403 | E-19 | E-20 |
| test_seguranca.py::test_usuario_edita_a_si_mesmo_sem_mudar_privilegio | integração | CT-04 / F-007 | autoedição ok; `role`/`active` ⇒ 403 | E-19 | E-20 |
| test_seguranca.py::test_admin_altera_privilegio | integração | CT-04 | admin altera perfil | E-19 | controle positivo: passa no original |
| test_seguranca.py::test_remover_usuario_exige_admin | integração | CT-05 / F-006 | 401, 403 e 200 por perfil | E-19 | E-20 |
| test_seguranca.py::test_remover_categoria_exige_admin | integração | CT-05 / F-006 | 401, 403 e 200 por perfil | E-19 | E-20 |
| test_seguranca.py::test_remover_task_exige_autenticacao | integração | CT-01 / F-006 | sem token ⇒ 401 | E-19 | E-20 |
| test_seguranca.py::test_task_de_terceiro_nao_pode_ser_alterada_nem_removida | integração | CT-09 / F-029 | terceiro ⇒ 403 e task intacta | E-19 | E-20 |
| test_seguranca.py::test_responsavel_e_gestao_alteram_a_task | integração | CT-09 | responsável e gerente ⇒ 200 | E-19 | controle positivo: passa no original |
| test_seguranca.py::test_dados_de_usuario_so_para_o_proprio_ou_gestao (3) | integração | CT-09 / F-029 | terceiro ⇒ 403; próprio e gestão ⇒ 200 | E-19 | E-20 |
| test_seguranca.py::test_visoes_gerais_so_para_gestao (2) | integração | CT-09 / F-029 | usuário comum ⇒ 403; gestão ⇒ 200 | E-19 | E-20 |
| test_seguranca.py::test_cors_nao_libera_origem_externa | integração | CT-06 / F-002 | origem externa sem liberação | E-19 | E-20 |
| test_seguranca.py::test_cabecalhos_de_seguranca_presentes | integração | F-012 | cabeçalhos presentes | E-19 | E-20 |
| test_seguranca.py::test_login_bloqueia_apos_falhas_repetidas | integração | F-012 | 5 falhas ⇒ 429 | E-19 | E-20 |
| test_seguranca.py::test_atualizar_usuario_rejeita_valor_invalido (3) | integração | CT-07 / F-014 | valores inválidos ⇒ 400 | E-19 | E-20 |
| test_seguranca.py::test_categoria_rejeita_cor_e_nome_invalidos | integração | CT-07 / F-014 | valores inválidos ⇒ 400 | E-19 | E-20 |
| test_seguranca.py::test_tipos_invalidos_retornam_400 | integração | F-014, F-015 | tipo inválido ⇒ 400 | E-19 | E-20 |
| test_seguranca.py::test_paginacao_das_listagens | integração | CT-08 / F-018 | `limit`/`offset` | E-19 | E-20 |
| test_seguranca.py::test_log_do_servidor_nao_registra_dados_pessoais | integração | F-008 | nome e e-mail fora do log | E-19 | E-20 |
| test_seguranca.py::test_senha_literal_antiga_do_seed_nao_funciona | integração | F-009 | senha antiga ⇒ 401 | E-19 | E-20 |
| test_unidade.py (configuração, 4 testes) | unidade | F-001, F-003 | padrões seguros e segredos fora do fonte | E-19 | E-20 |
| test_unidade.py (senha, 2 testes) | unidade | F-005 | KDF com salt e migração de MD5 | E-19 | E-20 |
| test_unidade.py (token e limite, 2 testes) | unidade | F-002, F-012 | adulteração, expiração e janela de bloqueio | E-19 | E-20 |
| test_unidade.py (camadas e paginação, 4 testes) | unidade | F-010, F-011, F-016, CT-08 | regra no service, módulo próprio, vínculo e limite de 100 | E-19 | E-20 (erro de fixture: `create_app` não existe no original) |
| test_seguranca.py::test_listagem_mostra_somente_as_proprias_tasks | integração | CT-09 / F-029 | `GET /tasks` só com as próprias tasks | E-19 | E-20 |
| test_seguranca.py::test_acesso_direto_a_task_alheia_retorna_403 | integração | CT-09 / F-029 | alheia ⇒ 403; própria e gestão ⇒ 200; inexistente ⇒ 404 | E-19 | E-20 |
| test_seguranca.py::test_busca_filtra_pelo_proprio_usuario | integração | CT-09 / F-029 | busca por termo e `user_id` alheios vazia; gestão encontra | E-19 | E-20 |
| test_seguranca.py::test_estatisticas_consideram_somente_as_proprias_tasks | integração | CT-09 / F-029 | totais limitados ao usuário | E-19 | E-20 |
| test_seguranca.py::test_contagem_por_categoria_nao_revela_tasks_alheias | integração | CT-09 / F-029 | `task_count` sem tasks alheias | E-19 | E-20 |
| test_seguranca.py::test_usuario_comum_nao_atribui_task_a_terceiro | integração | CT-09 / F-029 | criar, transferir ou remover responsável ⇒ 403 | E-19 | E-20 |
| test_seguranca.py::test_gestao_atribui_task_a_terceiro | integração | CT-09 | gerente atribui e transfere | E-19 | controle positivo: passa no original |
| test_seguranca.py::test_task_criada_por_usuario_comum_fica_sob_sua_responsabilidade | integração | CT-09 / F-029 | criador vira responsável | E-19 | E-20 |
| test_seguranca.py::test_referencia_invalida_retorna_400 (6) | integração | CT-09 / F-014 | `[]`, `{}` e inteiro gigante ⇒ 400 | E-19 | E-20 |
| test_seguranca.py::test_inteiros_gigantes_na_url_e_na_busca_nao_geram_500 | integração | F-014 | URL ⇒ 404; busca e paginação ⇒ 400 | E-19 | E-20 |
| test_unidade.py (escopo, estatísticas e id fora da faixa, 3 testes) | unidade | CT-09 / F-029 | escopo por perfil e consultas limitadas | E-19 | E-20 |
| test_unidade.py::test_referencia_invalida_e_rejeitada (16) | unidade | CT-09 / F-014 | referências malformadas ⇒ 400 | E-19 | E-20 |
| test_unidade.py::test_referencia_numerica_em_texto_e_normalizada | unidade | CT-09 | `"5"` vira `5`, sem burlar a comparação de responsável | E-19 | E-20 |
| test_unidade.py::test_dependencias_diretas_fixadas_na_versao_instalada | unidade | F-013 | dependências diretas declaradas na versão instalada | E-19 | E-20 |
| test_seguranca.py::test_token_de_conta_excluida_nao_assume_a_conta_que_herda_o_id | integração | CT-02 / F-002 | conta B herda o id; o token de A responde 401 ao ler, trocar a senha e listar | E-19 | E-20 |
| test_seguranca.py::test_token_antigo_deixa_de_valer_apos_troca_de_senha | integração | CT-02 / F-002 | token anterior à troca ⇒ 401; novo login funciona | E-19 | E-20 |
| test_seguranca.py::test_titulo_com_surrogate_isolado_retorna_400 | integração | F-014 | surrogate isolado ⇒ 400 (antes 500) | E-19 | E-20 |
| test_seguranca.py::test_prioridade_nao_inteira_retorna_400 (2) | integração | CT-07 / F-014 | `2.5` e `true` ⇒ 400 | E-19 | E-20 |
| test_seguranca.py::test_referencia_zero_ou_inexistente_retorna_404 (4) | integração | CT-09 | id 0 ⇒ 404; inexistente ⇒ 404 | E-19 | E-20 (os 2 casos com 999999 já davam 404 no original: controle) |
| test_seguranca.py::test_usuario_comum_nao_atribui_task_ao_id_zero | integração | CT-09 / F-029 | `user_id: 0` ⇒ 403 | E-19 | E-20 |
| test_seguranca.py::test_estatisticas_por_status_e_atraso_no_escopo_do_usuario | integração | CT-09 / F-029 | contagens por status e de atraso só do usuário | E-19 | E-20 |
| test_unidade.py::test_token_vinculado_a_credencial_da_conta | unidade | CT-02 / F-002 | troca de hash, outra conta e token sem impressão ⇒ None; o hash não vai para o payload | E-19 | E-20 |
| test_unidade.py::test_contagens_por_status_e_atraso_respeitam_o_responsavel | unidade | CT-09 / F-029 | contagens exatas por status e atraso no escopo; mata os 2 mutantes (E-26) | E-19 | E-20 |
| test_unidade.py::test_prioridade_aceita_somente_inteiro_na_faixa (6) | unidade | CT-07 / F-014 | `2.5`, `2.0`, `true`, `false`, texto e nulo ⇒ 400 | E-19 | E-20 |
| test_unidade.py::test_texto_com_surrogate_isolado_e_rejeitado | unidade | F-014 | surrogate em task, tags, categoria e credenciais ⇒ 400 | E-19 | E-20 |

Totais: 116 testes novos (74 de integração, 42 de unidade): 60 na primeira rodada, 36 após a primeira validação independente e 20 após a segunda. No checkpoint, com `test_login_sucesso`, foram 117 execuções: 103 falhas, 7 erros de fixture e 7 aprovações (controles positivos e os 2 casos de referência inexistente que já davam 404 no original).

## Evidências de execução
(`E-00` — Fase 1 — foi gravado na Fase 2.) Arquivos brutos em `reports/evidence/project-3/20261116-214549/`. E-01 a E-17 são de rodadas anteriores e foram preservados; **os resultados finais são os de E-18 a E-27**, gerados após a segunda validação independente.

### E-01 · Testes do projeto (baseline)
Comando: `.venv\Scripts\python.exe -m pytest -v` · Diretório: task-manager-api · Origem: K-01 · Classe B · Autorização: automática
Exit code: 0 · Resultado: passed 25 | failed 0 | skipped 0 · Bruto: `E-01-baseline-pytest.log`

### E-02 · Execução local autenticada (baseline)
Comando: `python v4_bateria.py baseline <cópia do checkpoint>` (script temporário fora do projeto) · Origem: K-07 · Classe B
Exit code: 0 · Resultado: 117 requisições em banco descartável · Bruto: `E-02-baseline-execucao-local.log`
Observação: reexecutada no código original depois do CT-09, com a bateria estendida de 104 para 117 requisições, para manter a mesma bateria nos dois lados.

### E-03 · Testes do projeto (após refatoração)
Comando: `.venv\Scripts\python.exe -m pytest -v` · Origem: K-01 · Classe B
Exit code: 0 · Resultado: passed 85 | failed 0 | skipped 0 (baseline E-01: passed 25) · Bruto: `E-03-final-pytest.log`
Integridade: 3 arquivos alterados e 2 adicionados, conferidos com `git diff` e `tests-before/`.

### E-04 · Prova de sensibilidade (checkpoint original)
Comando: `python -m pytest tests/test_seguranca.py tests/test_unidade.py tests/test_api.py::test_login_sucesso -q --tb=no -rA -p no:cacheprovider` · Origem: K-06 · Classe B na cópia
Exit code: 1 (esperado) · Resultado: failed 53 | errors 4 | passed 4 · Bruto: `E-04-prova-vermelha-checkpoint.log`

### E-05 · Execução local autenticada (após refatoração)
Comando: `python v4_bateria.py final <cópia do projeto>` · Origem: K-07 · Classe B
Exit code: 0 · Resultado: 117 requisições em banco descartável · Bruto: `E-05-final-execucao-local.log`

### E-06 · Comparação antes/depois
Resultado: 50 iguais, 65 alteradas por contrato aprovado, 2 por correção sem contrato, 0 divergentes · Bruto: `E-06-comparacao-rotas.log`

### E-07 · Reauditoria
Comando: `python -B reauditoria.py` (script temporário fora do projeto) · Exit code: 0 · Bruto: `E-07-reauditoria.log`

### E-08 · Boot (após refatoração)
Resultado: `Debug mode: off`, `Running on http://127.0.0.1:5000` · Bruto: `E-08-boot-final.log`

### E-09 · Diff dos testes
Bruto: `E-09-diff-testes.patch`; originais em `tests-before/`.

### E-10 · Execução local autenticada (baseline, bateria ampliada)
Comando: `python v4_bateria.py baseline <cópia do checkpoint bb765d3>` · Origem: K-07 · Classe B · Autorização: automática
Exit code: 0 · Resultado: 150 requisições em banco descartável (as 117 de E-02 + 33 casos novos) · Bruto: `E-10-baseline-execucao-local.log`, `E-10-baseline-execucao-local-requisicoes.log`

### E-11 · Testes do projeto (final)
Comando: `.venv\Scripts\python.exe -m pytest -q --tb=short` · Origem: K-01 · Classe B · Autorização: automática
Exit code: 0 · Resultado: passed 121 | failed 0 | skipped 0 (baseline E-01: passed 25) · Bruto: `E-11-final-pytest.log`
Integridade: nenhum teste removido, pulado ou com asserção enfraquecida; diff em `E-17-diff-testes.patch`.

### E-12 · Prova de sensibilidade (checkpoint original)
Comando: `python -m pytest tests/test_seguranca.py tests/test_unidade.py tests/test_api.py::test_login_sucesso -q --tb=no -rA -p no:cacheprovider` · Origem: K-06 · Classe B na cópia
Exit code: 1 (esperado) · Resultado: failed 86 | errors 6 | passed 5 · Bruto: `E-12-prova-vermelha-checkpoint.log`

### E-13 · Execução local autenticada (final)
Comando: `python v4_bateria.py final <cópia do projeto>` · Origem: K-07 · Classe B · Autorização: automática
Exit code: 0 · Resultado: 150 requisições em banco descartável · Bruto: `E-13-final-execucao-local.log`, `E-13-final-execucao-local-requisicoes.log`

### E-14 · Comparação antes/depois
Exit code: 0 · Resultado: 61 iguais, 83 alteradas por contrato aprovado, 6 por correção sem contrato, 0 divergentes · Bruto: `E-14-comparacao-rotas.log`, `E-14-comparacao-rotas-detalhe.log`

### E-15 · Reauditoria do catálogo e matriz de acesso
Comando: `python -B reauditoria.py` (script temporário fora do projeto) · Classe B
Exit code: 0 · Resultado: 19 verificações de acesso entre usuários sem falha; 5 verificações adicionais confirmam os residuais R-01, R-02, R-04 e R-05 · Bruto: `E-15-reauditoria.log`

### E-16 · Boot (final)
Resultado: `Debug mode: off`, `Running on http://127.0.0.1:5000` · Bruto: `E-16-boot-final.log`

### E-17 · Diff dos testes (validação independente)
Bruto: `E-17-diff-testes.patch`; arquivos anteriores em `tests-before-validacao/`.

### E-18 · Execução local autenticada (baseline, bateria ampliada)
Comando: `python v4_bateria.py baseline <cópia do checkpoint bb765d3>` · Origem: K-07 · Classe B · Autorização: automática
Exit code: 0 · Resultado: 171 requisições em banco descartável (as 150 de E-10 + 21 casos novos); no original, o token da conta excluída A trocou a senha da conta B, que herdou o id · Bruto: `E-18-baseline-execucao-local.log`, `E-18-baseline-execucao-local-requisicoes.log`

### E-19 · Testes do projeto (final)
Comando: `.venv\Scripts\python.exe -m pytest -q --tb=short` · Origem: K-01 · Classe B · Autorização: automática
Exit code: 0 · Resultado: passed 141 | failed 0 | skipped 0 (baseline E-01: passed 25) · Bruto: `E-19-final-pytest.log`
Integridade: nenhum teste removido, pulado ou com asserção enfraquecida; diff em `E-25-diff-testes.patch`.

### E-20 · Prova de sensibilidade (checkpoint original)
Comando: `python -m pytest tests/test_seguranca.py tests/test_unidade.py tests/test_api.py::test_login_sucesso -q --tb=no -rA -p no:cacheprovider` · Origem: K-06 · Classe B na cópia
Exit code: 1 (esperado) · Resultado: failed 103 | errors 7 | passed 7 · Bruto: `E-20-prova-vermelha-checkpoint.log`

### E-21 · Execução local autenticada (final)
Comando: `python v4_bateria.py final <cópia do projeto>` · Origem: K-07 · Classe B · Autorização: automática
Exit code: 0 · Resultado: 171 requisições em banco descartável; token de A ⇒ 401 depois da exclusão e da troca de senha; B mantém o acesso · Bruto: `E-21-final-execucao-local.log`, `E-21-final-execucao-local-requisicoes.log`

### E-22 · Comparação antes/depois (primeira classificação)
Exit code: 0 · Resultado: 3 linhas marcadas DIVERGENTE por falta de regra no classificador, todas explicadas em E-27 (login de B, que só falhava no original porque o ataque teve sucesso, e dois 405 que só mudaram o corpo para JSON) · Bruto: `E-22-comparacao-rotas.log`, `E-22-comparacao-rotas-detalhe.log`

### E-23 · Reauditoria do catálogo, matriz de acesso e usos do token
Comando: `python -B reauditoria.py` (script temporário fora do projeto) · Classe B
Exit code: 0 · Resultado: 19 verificações de acesso entre usuários e 12 de token e identidade (id reaproveitado, troca de senha, desativação, rebaixamento de perfil, identificação opcional em `POST /users`), todas sem falha; 21 pontos de uso de token e identidade inspecionados; residuais confirmados · Bruto: `E-23-reauditoria.log`

### E-24 · Boot (final)
Resultado: `Debug mode: off`, `Running on http://127.0.0.1:5000` · Bruto: `E-24-boot-final.log`

### E-25 · Diff dos testes (segunda validação independente)
Bruto: `E-25-diff-testes.patch`; arquivos anteriores em `tests-before-validacao-2/`.

### E-26 · Mutantes do escopo de `/tasks/stats`
Comando: `python -B mutantes.py` (cópias temporárias fora do projeto) · Classe B
Exit code: 0 · Resultado: M1 (contagem por status sem escopo) e M2 (atraso sem escopo) mortos pelos testes novos · Bruto: `E-26-mutantes-estatisticas.log`

### E-27 · Comparação antes/depois (classificação final)
Comando: `python v4_comparar.py` sobre os mesmos JSON de E-18 e E-21 · Classe B
Exit code: 0 · Resultado: 68 iguais (2 apenas com o corpo de erro em JSON), 96 alteradas por contrato aprovado, 7 por correção sem contrato, 0 divergentes · Bruto: `E-27-comparacao-rotas-reclassificada.log`, `E-27-comparacao-rotas-detalhe.log`

### Execução local autenticada (V4)
Credenciais: geradas por execução nas variáveis `SEED_*_PASSWORD` + `POST /login` (no código original, dados do seed versionado); valores mascarados. Integrações: nenhuma. Banco: arquivo SQLite descartável em cópia fora do projeto.

| Método | Rota | Credencial | ANTES (status) | DEPOIS (status) | Resultado | Qtde | Prova |
|---|---|---|---|---|---|---|---|
| GET | `/` | sem | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/health` | sem | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| POST | `/login` | sem | 200 | 200 | igual | 6 | E-18, E-21, E-27 |
| POST | `/login` | sem | 401 | 401 | igual | 1 | E-18, E-21, E-27 |
| POST | `/login` | sem | 400 | 400 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks` | user | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| GET | `/tasks` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 2 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | admin | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=a` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=a` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=a` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=a` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=a` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/stats` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/stats` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/stats` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/stats` | user | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| GET | `/tasks/stats` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/users` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/users` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | admin | 200 | 200 | ALTERADO (aprovado CT-03) | 2 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/reports/summary` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/reports/summary` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/reports/summary` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/reports/summary` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/reports/summary` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/categories` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/categories` | invalida | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/categories` | forjada | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| GET | `/categories` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/categories` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| POST | `/tasks` | sem | 201 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| POST | `/tasks` | user | 201 | 201 | igual | 1 | E-18, E-21, E-27 |
| POST | `/tasks` | admin | 201 | 201 | igual | 9 | E-18, E-21, E-27 |
| POST | `/tasks` | admin | 500 | 400 | ALTERADO (correção F-014, sem contrato) | 2 | E-18, E-21, E-27 |
| GET | `/tasks/search?priority=abc` | admin | 500 | 400 | ALTERADO (correção F-014, sem contrato) | 1 | E-18, E-21, E-27 |
| PUT | `/tasks/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| PUT | `/tasks/<id>` | user | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| PUT | `/tasks/<id>` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| DELETE | `/tasks/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| DELETE | `/tasks/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| DELETE | `/tasks/<id>` | admin | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| POST | `/users` | sem | 201 | 201 | ALTERADO (aprovado CT-03) | 4 | E-18, E-21, E-27 |
| POST | `/users` | sem | 201 | 403 | ALTERADO (aprovado CT-04/CT-05) | 1 | E-18, E-21, E-27 |
| POST | `/users` | user | 201 | 403 | ALTERADO (aprovado CT-04/CT-05) | 1 | E-18, E-21, E-27 |
| POST | `/users` | admin | 201 | 201 | ALTERADO (aprovado CT-03) | 4 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-04/CT-05) | 2 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | user | 200 | 200 | ALTERADO (aprovado CT-03) | 1 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | admin | 200 | 200 | ALTERADO (aprovado CT-03) | 1 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | admin | 200 | 400 | ALTERADO (aprovado CT-07) | 1 | E-18, E-21, E-27 |
| DELETE | `/users/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| DELETE | `/users/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-04/CT-05) | 1 | E-18, E-21, E-27 |
| DELETE | `/users/<id>` | admin | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| POST | `/categories` | sem | 201 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| POST | `/categories` | user | 201 | 201 | igual | 1 | E-18, E-21, E-27 |
| POST | `/categories` | admin | 201 | 400 | ALTERADO (aprovado CT-07) | 1 | E-18, E-21, E-27 |
| PUT | `/categories/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| PUT | `/categories/<id>` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| POST | `/categories` | admin | 201 | 201 | igual | 4 | E-18, E-21, E-27 |
| DELETE | `/categories/<id>` | sem | 200 | 401 | ALTERADO (aprovado CT-01/CT-02) | 1 | E-18, E-21, E-27 |
| DELETE | `/categories/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-04/CT-05) | 1 | E-18, E-21, E-27 |
| DELETE | `/categories/<id>` | admin | 200 | 200 | igual | 2 | E-18, E-21, E-27 |
| GET | `/users` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/reports/summary` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | manager | 200 | 200 | ALTERADO (aprovado CT-03) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | user | 200 | 200 | ALTERADO (aprovado CT-03) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>/tasks` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/reports/user/<id>` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| PUT | `/tasks/<id>` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| DELETE | `/tasks/<id>` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks?limit=2` | admin | 200 | 200 | ALTERADO (aprovado CT-08) | 1 | E-18, E-21, E-27 |
| GET | `/tasks` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | user | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/<id>` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?user_id=1` | user | 200 | 200 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=sigiloso` | user | 200 | 200 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?q=sigiloso` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| GET | `/tasks/stats` | manager | 200 | 200 | igual | 1 | E-18, E-21, E-27 |
| POST | `/tasks` | user | 201 | 403 | ALTERADO (aprovado CT-09) | 1 | E-18, E-21, E-27 |
| PUT | `/tasks/<id>` | user | 200 | 403 | ALTERADO (aprovado CT-09) | 2 | E-18, E-21, E-27 |
| POST | `/tasks` | manager | 201 | 201 | igual | 1 | E-18, E-21, E-27 |
| POST | `/tasks` | admin | 500 | 400 | ALTERADO (aprovado CT-09) | 6 | E-18, E-21, E-27 |
| PUT | `/tasks/<id>` | admin | 500 | 400 | ALTERADO (aprovado CT-09) | 6 | E-18, E-21, E-27 |
| GET | `/tasks/<gigante>` | admin | 500 | 404 | ALTERADO (correção F-014, sem contrato) | 1 | E-18, E-21, E-27 |
| GET | `/users/<gigante>` | admin | 500 | 404 | ALTERADO (correção F-014, sem contrato) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?user_id=<gigante>` | admin | 500 | 400 | ALTERADO (correção F-014, sem contrato) | 1 | E-18, E-21, E-27 |
| GET | `/tasks/search?priority=<gigante>` | admin | 500 | 400 | ALTERADO (correção F-014, sem contrato) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | conta_a | 200 | 200 | ALTERADO (aprovado CT-03) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | conta_a | 200 | 401 | ALTERADO (aprovado CT-02, token vinculado à conta) | 1 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | conta_a | 200 | 401 | ALTERADO (aprovado CT-02, token vinculado à conta) | 1 | E-18, E-21, E-27 |
| POST | `/login` | sem | 401 | 200 | ALTERADO (aprovado CT-02: no original o token de A trocou a senha de B) | 1 | E-18, E-21, E-27 |
| PUT | `/users/<id>` | conta_c | 200 | 200 | ALTERADO (aprovado CT-03) | 1 | E-18, E-21, E-27 |
| GET | `/users/<id>` | conta_c | 200 | 401 | ALTERADO (aprovado CT-02, token vinculado à conta) | 1 | E-18, E-21, E-27 |
| POST | `/tasks` | admin | 201 | 400 | ALTERADO (aprovado CT-07/CT-09) | 2 | E-18, E-21, E-27 |
| POST | `/tasks` | admin | 201 | 404 | ALTERADO (aprovado CT-07/CT-09) | 2 | E-18, E-21, E-27 |
| POST | `/tasks` | admin | 404 | 404 | igual | 1 | E-18, E-21, E-27 |
| PUT | `/tasks/<gigante>` | admin | 405 | 405 | igual (status; corpo de erro em JSON pelo handler central, C-10) | 1 | E-18, E-21, E-27 |
| DELETE | `/tasks/<gigante>` | admin | 405 | 405 | igual (status; corpo de erro em JSON pelo handler central, C-10) | 1 | E-18, E-21, E-27 |

### Comparação antes/depois (rotas)
| Método | Rota | ANTES | DEPOIS | Resultado | Prova |
|---|---|---|---|---|---|
| GET | / | 200 | 200 | igual | E-27 |
| GET | /health | 200 | 200 | igual | E-27 |
| POST | /login | 200, token previsível, `password` | 200, token assinado e vinculado à credencial, sem `password` | ALTERADO (aprovado CT-02, CT-03) | E-27 |
| GET | /tasks | 200 aberta, todas as tasks | 401; usuário comum só as próprias; gestão todas | ALTERADO (aprovado CT-01, CT-08, CT-09) | E-27 |
| GET | /tasks/<id> | 200 aberta | 401; 403 alheia; 200 responsável e gestão; 404 id gigante | ALTERADO (aprovado CT-01, CT-09; correção F-014) | E-27 |
| POST | /tasks | 201 aberta; 500 com tipo inválido | 401; 201 com o criador comum como responsável; 403 atribuição a terceiro; 400 tipo, referência, prioridade não inteira ou texto inválido; 404 `user_id`/`category_id` 0 ou inexistente | ALTERADO (aprovado CT-01, CT-07, CT-09; correção F-014) | E-27 |
| PUT | /tasks/<id> | 200 aberta | 401; 403 terceiro ou transferência sem gestão; 200 responsável e gestão; 400 referência inválida | ALTERADO (aprovado CT-01, CT-09) | E-27 |
| DELETE | /tasks/<id> | 200 aberta | 401; 403 terceiro; 200 responsável e gestão | ALTERADO (aprovado CT-01, CT-09) | E-27 |
| GET | /tasks/search | 200 aberta; 500 com filtro inválido | 401; usuário comum só as próprias; gestão todas; 400 filtro inválido | ALTERADO (aprovado CT-01, CT-08, CT-09; correção F-014) | E-27 |
| GET | /tasks/stats | 200 aberta, totais gerais | 401; usuário comum só os próprios totais; gestão totais gerais | ALTERADO (aprovado CT-01, CT-09) | E-27 |
| GET | /users | 200 aberta | 401; 403 usuário comum; 200 gestão | ALTERADO (aprovado CT-01, CT-08, CT-09) | E-27 |
| GET | /users/<id> | 200 com `password` | 401; 403 terceiro; 200 próprio e gestão, sem `password`; 404 id gigante | ALTERADO (aprovado CT-01, CT-03, CT-09; correção F-014) | E-27 |
| POST | /users | 201 com qualquer `role` | 201 só `user`; 403 para outro perfil sem admin | ALTERADO (aprovado CT-03, CT-04) | E-27 |
| PUT | /users/<id> | 200 aberta; token de conta excluída trocava a senha da conta que herdou o id | 401 (inclusive token de conta excluída ou anterior à troca de senha); 403 terceiro; 200 próprio ou admin; 400 valor inválido | ALTERADO (aprovado CT-01, CT-03, CT-04, CT-07) | E-27 |
| DELETE | /users/<id> | 200 aberta | 401; 403; 200 admin | ALTERADO (aprovado CT-01, CT-05) | E-27 |
| GET | /users/<id>/tasks | 200 aberta | 401; 403 terceiro; 200 próprio e gestão | ALTERADO (aprovado CT-01, CT-09) | E-27 |
| GET | /reports/summary | 200 aberta | 401; 403 usuário comum; 200 gestão | ALTERADO (aprovado CT-01, CT-09) | E-27 |
| GET | /reports/user/<id> | 200 aberta | 401; 403 terceiro; 200 próprio e gestão | ALTERADO (aprovado CT-01, CT-09) | E-27 |
| GET | /categories | 200 aberta, contagem geral | 401; `task_count` só das próprias tasks para usuário comum | ALTERADO (aprovado CT-01, CT-08, CT-09) | E-27 |
| POST | /categories | 201 aberta | 401; 201 autenticado; 400 cor inválida | ALTERADO (aprovado CT-01, CT-07) | E-27 |
| PUT | /categories/<id> | 200 aberta | 401; 200 autenticado | ALTERADO (aprovado CT-01) | E-27 |
| DELETE | /categories/<id> | 200 aberta | 401; 403; 200 admin | ALTERADO (aprovado CT-01, CT-05) | E-27 |

### Resumo da validação
| Degrau | Comando | Resultado | Evidência |
|---|---|---|---|
| V1 | `.venv\Scripts\python.exe -m pytest -q --tb=short` | passed 141 / failed 0 / skipped 0 (baseline 25) | E-01, E-19 |
| V2 | não disponível | sem lint, CI ou Makefile no projeto | — |
| V3 | boot `python app.py` | sobe em 127.0.0.1:5000 sem debug; sem coleção de requisições no projeto | E-24 |
| V4 | bateria de 171 requisições | 68 iguais, 96 por contrato aprovado, 7 por correção sem contrato, 0 divergentes | E-18, E-21, E-27 |
| V5 | importação da aplicação | coberta pelo boot e pela suíte | E-19, E-24 |
| Mutantes | 2 mutantes do escopo de `/tasks/stats` | 2 mortos | E-26 |

Veredito: VALIDADO (V1+V4)

## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python 3.14.0 em `.venv/pyvenv.cfg` (E-00)
- [x] Framework detectado corretamente — Flask 3.0.0 em manifesto, import e instância (E-00)
- [x] Domínio da aplicação descrito corretamente — tasks, usuários, categorias e relatórios (E-00)
- [x] Número de arquivos analisados condiz com a realidade — 15 arquivos por `wc -l` (E-00)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — seções e ordem de `03-template-relatorio.md`
- [x] Cada finding tem arquivo e linhas exatos — linhas relidas; quatro imprecisões de contagem e linha corrigidas antes da pausa
- [x] Findings ordenados por severidade (CRITICAL → LOW) — F-001 a F-028
- [x] Mínimo de 5 findings identificados — 28, mais F-029 na reauditoria (concluído após duas validações independentes)
- [x] Detecção de APIs deprecated incluída (se aplicável) — F-021 e F-022
- [x] Skill pausa e pede confirmação antes da Fase 3 — resposta `1A 2A 3A 4A`

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — config, models, views, controllers, routes e entry point separados (E-23)
- [x] Configuração extraída para módulo de config (sem hardcoded) — config/settings.py; busca por segredos sem ocorrências (E-23)
- [x] Models criados para abstrair dados — consultas somente em models/; `db.session` só em services/persistence.py para a transação (E-23)
- [x] Views/Routes separadas para visualização ou roteamento — routes/ e views/serializers.py
- [x] Controllers concentram o fluxo da aplicação — controllers/ chamam validators, services e views
- [x] Error handling centralizado — middleware/error_handler.py; zero `except:` genérico (E-23)
- [x] Entry point claro — app.py com `create_app()`; comando `python app.py` (E-24)
- [x] Aplicação inicia sem erros — E-24
- [x] Endpoints originais respondem corretamente — 22 de 22 rotas presentes; 2 iguais e 20 alteradas por contratos aprovados CT-01 a CT-09, com prova (E-19, E-21, E-27)

## Itens residuais (reauditoria)
CRITICAL/HIGH sem correção: Nenhum
Corrigidos no código com ação manual pendente: F-001 e F-009 — rotacionar `SECRET_KEY`, senha SMTP e senhas de seed publicadas no histórico git
Demais findings ainda presentes, total ou parcialmente:
- F-013 (MEDIUM, parcial): sem lockfile e versões de flask e flask-cors não atualizadas; atualizar exige instalação e `pip-audit` (classe C), fora do plano
- F-014 (MEDIUM, parcial): senha mínima de 4 caracteres mantida; elevá-la mudaria o contrato e não foi aprovado
- F-016 (MEDIUM, parcial): a parte de registros órfãos era falso positivo (ver observações); o schema segue sem `ondelete`, pois alterá-lo é migração (classe D)
- F-018 (MEDIUM, parcial): `GET /users/<id>`, `GET /users/<id>/tasks` e os relatórios continuam sem paginação
- F-023 (LOW): README não atualizado (recomendação manual; texto-base acima)
- F-025 (LOW, parcial): datas seguem serializadas com `str()` para preservar o formato das respostas

Pontos não corrigidos, declarados após a validação independente (nenhum foi aprovado para correção nesta execução):
- R-01 (MEDIUM): categorias podem ser criadas e renomeadas por qualquer usuário autenticado (E-23)
- R-03 (LOW): possível enumeração de e-mail pelo tempo de resposta do login, pois o hash só é calculado para conta existente; não medido nesta execução
- R-04 (LOW): e-mail com caixa diferente cria conta separada (E-23)
- R-05 (LOW): `POST /users` responde 409 para e-mail já cadastrado, o que revela a existência da conta; comportamento original mantido, identificado na reauditoria (E-23)
- R-06 (LOW): 403 para task alheia × 404 para task inexistente permite a um usuário autenticado descobrir quais ids existem (E-23)
- R-07 (LOW): URL com id de milhares de dígitos responde 405 em `PUT`/`DELETE /tasks/<id>`, porque o conversor de inteiros do Werkzeug não casa a rota; não há erro interno nem vazamento (E-23)
- R-02 (token antigo válido após troca de senha) foi **corrigido** na segunda validação independente e saiu desta lista (E-19, E-21, E-23)

## Observações da execução
- Stack detectada e confiança: Python 3.14 + Flask 3.0.0, confiança alta.
- Dicas específicas usadas × derivadas do sinal abstrato: dicas do catálogo para Python/Flask; nada derivado.
- Nível de organização encontrado e como a Fase 3 se adaptou: `parcialmente-em-camadas`; models e blueprints mantidos, regra e dados movidos para as camadas corretas.
- Falsos positivos descartados: 7 na Fase 2. **Correção da auditoria:** F-016 afirmou que remover categoria deixava tasks órfãs, mas E-02 mostra `category_id` nulo já no código original, porque o SQLAlchemy desvincula os filhos. A regra agora é explícita em services/category_service.py.
- Limitações da validação: V2 indisponível; envio de e-mail não exercitado porque o serviço foi removido; o limite de login fica em memória, por processo.
- Mudanças de comportamento sem `CT-xx` próprio: erros 404/405 e de JSON malformado passam a ter corpo JSON, com o mesmo status; `POST /login` pode responder 429 após 5 falhas; quando um payload tem dois erros simultâneos, a mensagem devolvida pode ser outra, pois a validação de formato ocorre antes da checagem de referências.
- `active` em `POST /users` já era ignorado no original e continua ignorado.
- Hashes MD5 existentes em `instance/tasks.db` só migram no próximo login de cada usuário. O banco do projeto não foi alterado nesta execução.
- Tentativas/iterações na Fase 3 e reversões: uma iteração para incluir C-17 / CT-09 e duas para concluí-la após as reprovações das validações independentes; nenhuma reversão. O classificador da comparação V4 ganhou duas regras depois de E-22, e a classificação final está em E-27, sobre os mesmos dados. A verificação rápida foi feita ao fim do bloco de mudanças, e não após cada padrão do playbook.
- Arquivos criados pela execução fora do código-fonte: `reports/audit-project-3.md`, `reports/evidence/project-3/20261116-214549/`; worktree do checkpoint e cópias temporárias em `exec-p3`, recriados na segunda rodada e removidos na limpeza. Nenhuma branch criada.

# Relatório de Issues — Análise de Código Legado

Projetos analisados: `code-smells-project` (Flask), `ecommerce-api-legacy` (Express), `task-manager-api` (Flask).
Formato de cada item: **ID — Título** · local · **Problema** (o que é) · **Por que é um problema** (impacto).

## Resumo

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| code-smells-project | 6 | 5 | 8 | 6 | 25 |
| ecommerce-api-legacy | 6 | 6 | 6 | 5 | 23 |
| task-manager-api | 5 | 4 | 9 | 5 | 23 |

---

# 1. code-smells-project (Python/Flask — API de E-commerce)

## CRITICAL

**CS-C1 — SQL Injection generalizado** · `models.py` (linhas 28, 48-50, 58-61, 92, 110, 127-128, 140-166, 280, 291-297)
- **Problema:** todas as queries são montadas por concatenação de strings com dados vindos do request (nome, email, senha, termo de busca, categoria, status).
- **Por que é problema:** permite bypass de login (`' OR '1'='1`), leitura, alteração e exclusão arbitrária de dados.

**CS-C2 — Endpoint que executa SQL arbitrário** · `app.py:59-78` (`POST /admin/query`)
- **Problema:** recebe `sql` no body e executa direto no banco, sem autenticação nem restrição.
- **Por que é problema:** qualquer cliente pode ler, alterar ou destruir todo o banco, tornando o item C1 irrelevante para um atacante.

**CS-C3 — Reset de banco sem autenticação** · `app.py:47-57` (`POST /admin/reset-db`)
- **Problema:** apaga itens, pedidos, produtos e usuários com uma única chamada pública.
- **Por que é problema:** perda total de dados por qualquer pessoa com acesso à rede; não há confirmação, perfil admin ou ambiente restrito.

**CS-C4 — Segredos hardcoded e expostos pela API** · `app.py:7`, `controllers.py:285-289`, `database.py:76`
- **Problema:** `SECRET_KEY` fixa no código e devolvida em `/health` (junto com `debug`, `db_path`); credenciais de seed (`admin123`) no fonte.
- **Por que é problema:** vazamento de credenciais pelo repositório e por endpoint público; a chave permite forjar sessões assinadas.

**CS-C5 — Senhas em texto puro e retornadas nas respostas** · `models.py:83, 99, 110, 128`, `database.py:75-79`
- **Problema:** senhas são gravadas e comparadas sem hash; `GET /usuarios` e `/usuarios/<id>` devolvem o campo `senha`.
- **Por que é problema:** qualquer vazamento ou consulta expõe credenciais reais dos usuários (e do admin).

**CS-C6 — Modo debug ativo e bind em 0.0.0.0** · `app.py:8, 88`
- **Problema:** `DEBUG=True` e `app.run(host="0.0.0.0", debug=True)` fixos no código.
- **Por que é problema:** o debugger interativo do Werkzeug permite execução remota de código e vaza stack traces.

## HIGH

**CS-H1 — Regras de negócio em models e controllers (MVC violado)** · `models.py:133-169, 235-273`, `controllers.py:208-210, 247-250`
- **Problema:** cálculo de desconto, validação de estoque, criação de pedido e disparo de "notificações" vivem em model/controller; `app.py` também contém rotas e acesso a banco.
- **Por que é problema:** não há camada de serviço; a lógica não é testável isoladamente e qualquer mudança afeta várias camadas.

**CS-H2 — Conexão global mutável e compartilhada** · `database.py:4-12`
- **Problema:** `db_connection` global única, com `check_same_thread=False`, reutilizada por todas as requisições; o schema e o seed são criados dentro de `get_db()`.
- **Por que é problema:** não é thread-safe sob concorrência, dificulta testes (sem isolamento) e mistura criação de schema com acesso a dados.

**CS-H3 — Criação de pedido sem transação e com race condition** · `models.py:133-169`
- **Problema:** verifica estoque num loop e só depois insere/atualiza em outro, sem `BEGIN`/rollback em caso de erro.
- **Por que é problema:** requisições concorrentes podem vender além do estoque; falha no meio deixa pedido parcial e estoque inconsistente.

**CS-H4 — Ausência de autenticação e autorização** · `controllers.py:167-186`, `app.py` (todas as rotas), `app.py:9`
- **Problema:** `/login` devolve dados do usuário sem token/sessão; nenhuma rota valida identidade ou perfil; `CORS(app)` aberto a qualquer origem.
- **Por que é problema:** qualquer um cria/edita/deleta produtos, vê pedidos de todos os usuários e consulta o relatório de vendas.

**CS-H5 — Acoplamento forte sem injeção de dependência** · `controllers.py:1-3, 264-275`, `models.py:1`
- **Problema:** controllers e models importam `get_db` diretamente; `health_check` executa SQL no controller.
- **Por que é problema:** impossível trocar o banco ou mockar dependências em testes; camadas não têm fronteira clara.

## MEDIUM

**CS-M1 — Queries N+1 em pedidos** · `models.py:171-233`
- **Problema:** para cada pedido consulta itens, e para cada item consulta o produto (3 níveis de loop com queries).
- **Por que é problema:** o número de consultas cresce com o volume de dados; resolvível com JOIN.

**CS-M2 — Código duplicado** · `models.py:12-21, 31-40, 304-313` (produto), `171-233` (pedidos), `controllers.py:24-96`
- **Problema:** serialização `row → dict` repetida 5×, listagem de pedidos copiada em duas funções, validação de produto duplicada entre criar e atualizar.
- **Por que é problema:** correções precisam ser replicadas; já há divergência (atualizar não valida tamanho do nome nem categoria).

**CS-M3 — Validações ausentes nas rotas** · `controllers.py:43-46, 118-121, 157-160, 198-203, 237-245`
- **Problema:** não valida tipos (`preco` string gera `TypeError`), `quantidade` ≤ 0 (quantidade negativa aumenta estoque), formato/unicidade de e-mail, existência do usuário e do pedido, nem `float()` de filtros.
- **Por que é problema:** gera erros 500, dados inválidos e permite manipulação de estoque/preço.

**CS-M4 — Detalhes internos expostos nos erros** · `controllers.py` (`str(e)` em ~20 respostas)
- **Problema:** `except Exception as e` retorna a mensagem da exceção ao cliente; sem handler global de erros.
- **Por que é problema:** vaza detalhes de SQL/estrutura do banco e retorna 500 para erros de entrada.

**CS-M5 — Dinheiro armazenado como float** · `database.py:19, 41, 51`; `models.py:146, 257-272`
- **Problema:** `preco`, `total` e `preco_unitario` usam `REAL`/float.
- **Por que é problema:** erros de arredondamento em totais e relatórios financeiros.

**CS-M6 — Schema sem constraints** · `database.py:14-53`
- **Problema:** sem `UNIQUE` em `usuarios.email`, sem `NOT NULL`, sem chaves estrangeiras entre pedidos/itens/produtos/usuários.
- **Por que é problema:** permite e-mails duplicados e registros órfãos; a integridade depende só do código.

**CS-M7 — Fluxo de cancelamento incompleto** · `controllers.py:237-255`
- **Problema:** status é atualizado sem verificar se o pedido existe nem a transição válida; "cancelado" só imprime "Devolver estoque".
- **Por que é problema:** estoque nunca é devolvido e pedidos entregues podem voltar para pendente.

**CS-M8 — Listagens sem paginação e `SELECT *`** · `models.py:7, 75, 206`; relatório com 6 queries em `models.py:239-254`
- **Problema:** retorna todos os registros e usa várias consultas `COUNT` onde uma agregação resolveria.
- **Por que é problema:** degrada com o crescimento da base.

## LOW

**CS-L1 — Magic numbers e valores soltos** · `models.py:257-262`, `controllers.py:47-52, 242`
- **Problema:** faixas de desconto (10000/5000/1000 → 10%/5%/2%), tamanhos de nome, categorias e status hardcoded.
- **Por que é problema:** regra de negócio escondida em literais; difícil de ajustar e reutilizar.

**CS-L2 — Nomes que sombreiam builtins ou pouco descritivos** · `controllers.py:14, 56, 64`, `models.py:187-191`
- **Problema:** parâmetro `id`, variáveis `cursor2`/`cursor3`, `dados`.
- **Por que é problema:** reduz legibilidade e sombreia a função embutida `id`.

**CS-L3 — Imports não utilizados** · `models.py:2` (`sqlite3`), `database.py:2` (`os`)
- **Problema:** dependências importadas sem uso.
- **Por que é problema:** ruído e confusão sobre o que o módulo realmente depende.

**CS-L4 — `print()` no lugar de logging** · `controllers.py` (8, 57, 106, 161, 179, 208-210, 248-250), `app.py:56`
- **Problema:** logs via `print`, incluindo e-mail do usuário em login.
- **Por que é problema:** sem níveis, formato ou destino configurável; mistura dados pessoais em stdout.

**CS-L5 — Valores de ambiente hardcoded no health check** · `controllers.py:285-288`
- **Problema:** `"ambiente": "producao"`, `"db_path": "loja.db"`, `"debug": True` são literais.
- **Por que é problema:** informação enganosa e acoplada ao código em vez de configuração.

**CS-L6 — Concatenação de strings e checagem por truthiness** · `controllers.py:8, 57`, `models.py:294-297`
- **Problema:** `"..." + str(x)` em vez de f-string; `if preco_min:` ignora o valor `0`.
- **Por que é problema:** menor legibilidade e bug sutil de filtro.

> Dependências (`flask==3.1.1`, `flask-cors==5.0.1`): recentes, sem libs depreciadas identificadas.

---

# 2. ecommerce-api-legacy (Node.js/Express — LMS API)

## CRITICAL

**EC-C1 — Credenciais e chaves hardcoded** · `utils.js:1-7`, `AppManager.js:18`
- **Problema:** senha de banco, chave de gateway `pk_live_...` e usuário SMTP no fonte; usuário seed com senha `123`.
- **Por que é problema:** segredos versionados no repositório; uma chave "live" exposta permite uso indevido do gateway.

**EC-C2 — Dados de cartão registrados em log** · `AppManager.js:45`
- **Problema:** `console.log` imprime o número completo do cartão junto com a chave do gateway.
- **Por que é problema:** violação de PCI-DSS e LGPD; logs passam a conter dados financeiros e segredos.

**EC-C3 — Aprovação de pagamento simulada de forma insegura** · `AppManager.js:46-48`
- **Problema:** `cc.startsWith("4") ? "PAID" : "DENIED"` decide o status; não há gateway real, validação nem tokenização.
- **Por que é problema:** qualquer cartão iniciado em 4 matricula o aluno sem pagar; não impede fraude nem reflete cobrança real.

**EC-C4 — Hash de senha inválido** · `utils.js:17-23`, `AppManager.js:68`
- **Problema:** `badCrypto` repete 2 caracteres de base64 e trunca em 10 caracteres (previsível e reversível); senha padrão `"123456"` se não informada.
- **Por que é problema:** não protege credenciais; ainda bloqueia o event loop com 10.000 concatenações por cadastro.

**EC-C5 — Rotas administrativas e destrutivas sem autenticação** · `AppManager.js:80, 131`
- **Problema:** `/api/admin/financial-report` e `DELETE /api/users/:id` são públicos.
- **Por que é problema:** exposição de receita e dados de alunos e exclusão de qualquer usuário por terceiros.

**EC-C6 — God Class `AppManager`** · `AppManager.js:4-139`
- **Problema:** uma única classe cria o banco, define o schema, popula seeds, registra rotas e implementa checkout, pagamento, relatório e exclusão.
- **Por que é problema:** quebra total de separação de responsabilidades; nada é testável ou reutilizável isoladamente.

## HIGH

**EC-H1 — Lógica de negócio dentro das rotas** · `AppManager.js:28-78`
- **Problema:** o handler do checkout valida, consulta curso/usuário, cria usuário, "cobra", matricula e audita.
- **Por que é problema:** controller gordo, sem services/repositories, impede reutilização e testes unitários.

**EC-H2 — Checkout sem transação** · `AppManager.js:50-63, 69-71`
- **Problema:** usuário, matrícula, pagamento e auditoria são `INSERT`s independentes; o erro da auditoria é ignorado.
- **Por que é problema:** falha no meio deixa usuário/matrícula sem pagamento e dados inconsistentes.

**EC-H3 — Callback hell** · `AppManager.js:37-78, 83-128`
- **Problema:** até 6 níveis de callbacks aninhados, contadores manuais (`coursesPending`, `enrPending`).
- **Por que é problema:** código difícil de ler, propenso a erros de fluxo; deveria usar Promises/`async-await`.

**EC-H4 — Estado global mutável** · `utils.js:9-10, 12-15, 25`
- **Problema:** `globalCache` cresce sem limite e nunca é lido; `totalRevenue` global não utilizado; `logAndCache` mistura log e cache.
- **Por que é problema:** vazamento de memória, estado compartilhado entre requisições e responsabilidades confusas.

**EC-H5 — Acoplamento forte e banco volátil** · `AppManager.js:6-8`, `app.js:8-10`
- **Problema:** `AppManager` instancia `sqlite3.Database(':memory:')` e importa `config` global diretamente, sem injeção de dependência.
- **Por que é problema:** dados somem a cada restart; impossível trocar banco ou mockar em testes.

**EC-H6 — Exclusão de usuário deixa dados órfãos** · `AppManager.js:131-137`
- **Problema:** apaga só o usuário; a resposta admite que matrículas e pagamentos "ficaram sujos" e ignora o `err`.
- **Por que é problema:** inconsistência financeira e relatório com "Unknown"; responde sucesso mesmo em falha.

## MEDIUM

**EC-M1 — Queries N+1 no relatório financeiro** · `AppManager.js:83-126`
- **Problema:** para cada curso busca matrículas e, para cada matrícula, 2 consultas (usuário e pagamento).
- **Por que é problema:** quantidade de queries cresce linearmente com os dados; substituível por um JOIN.

**EC-M2 — Ordem não determinística e erros ignorados no relatório** · `AppManager.js:92, 104, 106`
- **Problema:** `report.push` ocorre em callbacks assíncronos (ordem varia); `err` não é verificado — `enrollments.length` quebra se a query falhar.
- **Por que é problema:** resposta instável e risco de crash do processo por exceção não tratada.

**EC-M3 — Validações ausentes no checkout** · `AppManager.js:29-35`
- **Problema:** só checa presença; não valida formato de e-mail, tipo de `c_id`, formato do cartão (Luhn), nem exige senha.
- **Por que é problema:** aceita dados malformados e cria usuários com senha padrão.

**EC-M4 — Sem middlewares e tratamento de erro central** · `app.js:5-10`
- **Problema:** apenas `express.json()`; sem handler de erros, rate limit, `helmet`, CORS configurado ou logging estruturado.
- **Por que é problema:** exceções derrubam rotas e não há proteção contra abuso (por exemplo, tentativas de cartão).

**EC-M5 — Schema sem constraints** · `AppManager.js:12-16`
- **Problema:** `users.email` sem `UNIQUE`, sem `NOT NULL` e sem chaves estrangeiras.
- **Por que é problema:** checkouts concorrentes podem duplicar usuários; integridade depende só do código.

**EC-M6 — Respostas inconsistentes** · `AppManager.js:35, 38, 41, 48, 135`
- **Problema:** mistura `send("texto")` e `json(...)`, com mensagens em PT/EN e códigos genéricos.
- **Por que é problema:** contrato de API imprevisível para clientes.

## LOW

**EC-L1 — Nomes crípticos** · `AppManager.js:29-33`, `api.http:8-12`
- **Problema:** `u`, `e`, `p`, `cid`, `cc` e payload `usr`/`eml`/`pwd`/`c_id`.
- **Por que é problema:** reduz legibilidade e documentação implícita da API.

**EC-L2 — Magic numbers e strings soltas** · `utils.js:19-22`, `AppManager.js:46, 68`
- **Problema:** `10000`, `substring(0, 10)`, `"4"`, `"PAID"`/`"DENIED"`, `"123456"`.
- **Por que é problema:** significado oculto; deveriam ser constantes/enums nomeadas.

**EC-L3 — Código morto e imports sem uso** · `AppManager.js:2` (`totalRevenue`), `utils.js` (`dbUser`, `smtpUser`, `totalRevenue`)
- **Problema:** variáveis importadas/definidas e nunca usadas.
- **Por que é problema:** ruído e falsa impressão de funcionalidades.

**EC-L4 — Estilo inconsistente** · `AppManager.js:26, 50-54`
- **Problema:** mistura `this` e `self`, `let` onde caberia `const`, nomes de projeto "Frankenstein LMS" (`app.js:13`).
- **Por que é problema:** inconsistência e confusão sobre escopo de `this`.

**EC-L5 — Dependências e metadados** · `package.json`
- **Problema:** `express ^4.18.2` (a linha 4.x está em modo de manutenção; o Express 5 é a versão atual), sem script de teste/lint; nome e descrição de boilerplate.
- **Por que é problema:** atualização futura mais custosa; recomenda-se rodar `npm audit` (não executado nesta análise).

---

# 3. task-manager-api (Python/Flask — Task Manager)

## CRITICAL

**TM-C1 — Segredos hardcoded e debug ativo** · `app.py:13, 34`, `services/notification_service.py:9-10`
- **Problema:** `SECRET_KEY`, usuário/senha SMTP no código; `app.run(debug=True, host='0.0.0.0')`.
- **Por que é problema:** credenciais versionadas; o debugger do Werkzeug exposto na rede permite execução remota de código.

**TM-C2 — Hash de senha com MD5 sem salt** · `models/user.py:27-32`
- **Problema:** `hashlib.md5(pwd.encode())` para armazenar e verificar senha.
- **Por que é problema:** MD5 é rápido e quebrável por rainbow tables; deveria usar `bcrypt`/`argon2`/`werkzeug.security`.

**TM-C3 — Hash da senha devolvido pela API** · `models/user.py:21`; `routes/user_routes.py:33, 85, 129, 209`
- **Problema:** `User.to_dict()` inclui `password` e é usado em respostas de criar, buscar, atualizar e login.
- **Por que é problema:** expõe o hash (MD5, trivial de quebrar) de qualquer usuário a qualquer cliente.

**TM-C4 — Sem autenticação real; token falso** · `routes/user_routes.py:207-211` e todas as rotas
- **Problema:** `/login` devolve `'fake-jwt-token-<id>'`; nenhum endpoint valida token ou perfil.
- **Por que é problema:** qualquer pessoa lista/apaga usuários, tarefas e vê relatórios; o login não protege nada.

**TM-C5 — Escalação de privilégio** · `routes/user_routes.py:52, 71-78, 119-125`
- **Problema:** `POST /users` aceita `role: "admin"` enviado pelo cliente; `PUT /users/<id>` altera `role` e `active` sem autorização.
- **Por que é problema:** qualquer visitante se torna admin ou reativa/desativa contas.

## HIGH

**TM-H1 — Lógica de negócio nas rotas, sem camada de serviço** · `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`
- **Problema:** regras (atraso, estatísticas, relatórios, cascata de exclusão) estão nos handlers; `services/` contém só um serviço nunca usado.
- **Por que é problema:** controllers gordos, difíceis de testar e reaproveitar.

**TM-H2 — Responsabilidades misturadas em `report_routes.py`** · `routes/report_routes.py:157-223`
- **Problema:** o CRUD de categorias (`/categories`) está no blueprint de relatórios.
- **Por que é problema:** viola SRP/MVC e dificulta encontrar e manter rotas.

**TM-H3 — Integridade referencial manual e incompleta** · `routes/user_routes.py:140-145`, `routes/report_routes.py:217-218`
- **Problema:** `delete_user` apaga as tarefas do usuário em loop; `delete_category` deixa tasks com `category_id` órfão; sem `cascade`/`ondelete` nos relacionamentos.
- **Por que é problema:** exclusão silenciosa de dados de outros fluxos e registros apontando para entidades inexistentes.

**TM-H4 — Acoplamento direto rota → model/`db.session` e serviço morto** · `routes/*.py`, `services/notification_service.py`
- **Problema:** rotas usam `Model.query` e `db.session` diretamente, sem repositório ou injeção; `NotificationService` (com estado em memória) nunca é instanciado.
- **Por que é problema:** impossível testar sem banco real; código morto cria falsa expectativa de envio de e-mail.

## MEDIUM

**TM-M1 — Queries N+1** · `routes/task_routes.py:41-57`, `user_routes.py:22`, `report_routes.py:55-56, 163`
- **Problema:** `User.query.get`/`Category.query.get` por tarefa, `len(u.tasks)` por usuário, consulta por usuário no resumo e `count` por categoria.
- **Por que é problema:** o número de queries cresce com os dados; usar `joinedload` ou agregações.

**TM-M2 — Carga total em memória e sem paginação** · `routes/task_routes.py:14, 266, 281`; `user_routes.py:12`; `report_routes.py:30, 53`
- **Problema:** `.all()` em tabelas inteiras, inclusive para só contar atrasadas.
- **Por que é problema:** consumo de memória e latência crescem com a base; um `COUNT` filtrado resolveria.

**TM-M3 — Validações ausentes ou frágeis** · `task_routes.py:113, 182, 261-264`; `user_routes.py:103, 125`; `report_routes.py:196-202`
- **Problema:** `priority` sem checagem de tipo (string gera `TypeError`), `int()` de query string sem tratamento, `request.get_json()` nulo em `update_category`, `name`/`active`/`color` sem validação, regex de e-mail permissiva, tags não-string.
- **Por que é problema:** retornam 500 e aceitam dados inconsistentes.

**TM-M4 — `except:` genérico** · `task_routes.py:62, 137, 204, 236`; `user_routes.py:130, 149`; `report_routes.py:186, 207, 221`
- **Problema:** captura qualquer exceção (inclusive `KeyboardInterrupt`) e descarta o erro, às vezes sem log.
- **Por que é problema:** oculta bugs e dificulta diagnóstico.

**TM-M5 — Duplicação da regra de "atrasada" e da serialização** · `models/task.py:50-60`; `task_routes.py:30-39, 71-80, 284-287`; `user_routes.py:161-181`; `report_routes.py:35-36, 132-135`
- **Problema:** a mesma lógica é reescrita ≥ 6 vezes e `to_dict` é duplicado manualmente em `get_tasks` e `get_user_tasks`, embora `Task.is_overdue()` exista.
- **Por que é problema:** correções precisam ser replicadas e as versões já divergem.

**TM-M6 — Helpers e validadores mortos/duplicados** · `utils/helpers.py:19-116`, `models/task.py:38-48`
- **Problema:** `process_task_data`, `validate_email`, `parse_date` (aceita `d/m/Y`), constantes e `validate_status/priority` não são usados; as rotas reimplementam as mesmas validações.
- **Por que é problema:** regras divergentes (formatos de data diferentes) e código morto.

**TM-M7 — APIs depreciadas** · `Model.query.get()` (rotas), `datetime.utcnow()` (`models/*.py`, rotas)
- **Problema:** `Query.get()` é legado no SQLAlchemy 2.x (usar `db.session.get`); `datetime.utcnow()` é depreciado desde o Python 3.12.
- **Por que é problema:** gera warnings hoje e quebra em versões futuras.

**TM-M8 — Dependências desatualizadas e não usadas** · `requirements.txt`
- **Problema:** `marshmallow`, `requests` e `python-dotenv` não são importados; `flask==3.0.0` e `flask-cors==4.0.0` estão fixados em versões antigas.
- **Por que é problema:** superfície de ataque maior e risco de CVEs conhecidos (recomenda-se `pip-audit`, não executado nesta análise).

**TM-M9 — CORS aberto e schema criado no import** · `app.py:15, 30-31`
- **Problema:** `CORS(app)` libera todas as origens; `db.create_all()` roda no import, sem migrations.
- **Por que é problema:** exposição desnecessária a qualquer origem e evolução de schema não controlada.

## LOW

**TM-L1 — Imports não utilizados** · `app.py:7`, `task_routes.py:7`, `user_routes.py:6`, `report_routes.py:7-8`, `helpers.py:2-7`
- **Problema:** `os`, `sys`, `json`, `time`, `hashlib`, `math`, `format_date`, `calculate_percentage` etc. sem uso.
- **Por que é problema:** ruído e dependências falsas entre módulos.

**TM-L2 — Magic numbers e strings repetidas** · `task_routes.py:96-113`, `user_routes.py:64, 71`
- **Problema:** listas de status/roles, limites 3/200/1-5/4 repetidos; as constantes de `helpers.py:110-116` existem mas não são usadas.
- **Por que é problema:** alterar uma regra exige editar vários pontos.

**TM-L3 — Estilo e nomes** · `report_routes.py:24-28`, `task_routes.py:141, 210`
- **Problema:** variáveis `p1…p5`, `cat`, `t`; `type(x) == list` em vez de `isinstance`; `if/else` aninhados que retornam booleanos (`is_overdue`, `is_admin`).
- **Por que é problema:** reduz legibilidade; idiomas não-Pythonicos.

**TM-L4 — Logs com `print` e datas não ISO** · `task_routes.py:149, 219, 234`; `models/*.py` (`str(datetime)`)
- **Problema:** sem `logging`; datas serializadas por `str()` em vez de ISO 8601.
- **Por que é problema:** sem níveis de log e formato de data ambíguo para clientes.

**TM-L5 — Tags em string CSV e seed frágil** · `models/task.py:18`, `seed.py:11-14, 19-34`
- **Problema:** tags guardadas como texto separado por vírgula (quebra se a tag contiver vírgula); o seed apaga todas as tabelas sem confirmação e usa senhas fracas.
- **Por que é problema:** modelagem limitada e risco de perda de dados se executado por engano.

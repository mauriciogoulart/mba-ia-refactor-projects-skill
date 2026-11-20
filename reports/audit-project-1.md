================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Path:    code-smells-project
Run:     2026-11-16T19:55:23-03:00          Run id: 20261116-195523
Stack:   Python + Flask 3.1.1 (confiança: alta)
Files:   4 analyzed | ~780 lines of code
Architecture: monolito-sem-camadas
Skill:   refactor-arch 1.2 | Catalog 1.2
Evidence: reports/evidence/project-1/20261116-195523/

## Summary
CRITICAL: 9 | HIGH: 6 | MEDIUM: 10 | LOW: 6
Total: 31 findings (146 ocorrências)
Por categoria: Segurança 15 | Arquitetura 10 | Deprecated 0 | Testes 1 | Qualidade 5 | Outro 1
Cobertura: 4/4 lidos integralmente; 0 inspecionados por busca (testes, manifestos e README também lidos integralmente)

DEP: nenhuma encontrada para Flask 3.1.1 / flask-cors 5.0.1 / Python 3.14 (runtime do .venv; versão não declarada). Buscados: `datetime.utcnow`, `before_first_request`, `JSONEncoder`, `flask.escape`, `imp`, `distutils`, adaptadores de datetime do sqlite3 (não usados: sem `detect_types`).

## Estrutura ANTES
```
code-smells-project/
├── app.py            (88)  config + rotas + handlers admin com SQL + entrypoint
├── controllers.py    (292) handlers HTTP + validação + regras/notificações + SQL no health
├── database.py       (86)  conexão global + schema + seed
├── models.py         (314) SQL + regra de negócio + serialização
├── requirements.txt / requirements-dev.txt / pytest.ini / README.md
└── tests/
    ├── conftest.py
    └── test_api.py
```

| Métrica | Valor |
|---|---|
| Arquivos-fonte | 4 |
| Linhas de código (aprox.) | ~780 |
| Camadas presentes (papéis) | entrypoint, config (inline), rotas, controllers, models/dados; ausentes: services, middleware, módulo de config |
| Maior arquivo | models.py (314) |
| Arquivos com 3+ papéis | 3 (app.py, controllers.py, models.py) |

## Superfície de ataque
| Método | Rota | Handler (arquivo:linha) | Autenticação | Administrativa/destrutiva |
|---|---|---|---|---|
| GET | / | app.py:32 | não | não |
| GET | /produtos | controllers.py:5 | não | não |
| GET | /produtos/busca | controllers.py:111 | não | não |
| GET | /produtos/<int:id> | controllers.py:14 | não | não |
| POST | /produtos | controllers.py:24 | não | não (escrita) |
| PUT | /produtos/<int:id> | controllers.py:64 | não | não (escrita) |
| DELETE | /produtos/<int:id> | controllers.py:98 | não | sim (exclusão) |
| GET | /usuarios | controllers.py:128 | não | não (PII + senhas) |
| GET | /usuarios/<int:id> | controllers.py:136 | não | não (PII + senha) |
| POST | /usuarios | controllers.py:146 | não | não (cadastro público) |
| POST | /login | controllers.py:167 | não | não |
| POST | /pedidos | controllers.py:188 | não | não (escrita) |
| GET | /pedidos | controllers.py:229 | não | não (todos os pedidos) |
| GET | /pedidos/usuario/<int:usuario_id> | controllers.py:222 | não | não |
| PUT | /pedidos/<int:pedido_id>/status | controllers.py:237 | não | não (escrita) |
| GET | /relatorios/vendas | controllers.py:257 | não | sim (relatório financeiro) |
| GET | /health | controllers.py:264 | não | não (expõe configuração/segredo) |
| POST | /admin/reset-db | app.py:47 | não | sim (apaga todas as tabelas) |
| POST | /admin/query | app.py:59 | não | sim (SQL arbitrário) |

Entradas: JSON body (produtos, usuários, login, pedidos, status, `sql`), query string (`q`, `categoria`, `preco_min`, `preco_max`), parâmetros de rota inteiros. Segredos: literais em app.py:7, controllers.py:289, database.py:76-78. Integrações externas: nenhuma real (e-mail/SMS/push apenas `print`, controllers.py:208-210). Identidade: inexistente — `/login` só devolve os dados do usuário, sem token/sessão.

## Findings

### [CRITICAL] F-001 · SEC-02 Segredos e credenciais hardcoded
File: app.py:7; controllers.py:289; database.py:75-79
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `app.config["SECRET_KEY"] = "minh***"` · `"secret_key": "minh***"` · `("Admin", "admin@loja.com", "admi***", "admin")`
Description: a `SECRET_KEY` do Flask é literal no código versionado e repetida no handler de health; o seed cria o administrador e dois clientes com senhas literais no fonte (database.py:76-78).
Impact: qualquer pessoa com acesso ao repositório conhece a chave de assinatura e a senha do administrador; a chave já está no histórico git.
Recommendation: ler `SECRET_KEY` e credenciais de seed de variáveis de ambiente (com geração aleatória quando ausentes), remover os literais e rotacionar a chave publicada (Playbook P-01).

### [CRITICAL] F-002 · SEC-05 Modo debug ativo e bind público
File: app.py:8, 88
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-489 / A05:2021
Evidência: `app.config["DEBUG"] = True` · `app.run(host="0.0.0.0", port=5000, debug=True)`
Description: debug fixo no código de inicialização com escuta em todas as interfaces.
Impact: o depurador interativo do Werkzeug fica acessível na rede, permitindo execução de código e exposição de stack traces.
Recommendation: `DEBUG` e `HOST` por variável de ambiente com padrão desligado/`127.0.0.1` (Playbook P-01).

### [CRITICAL] F-003 · SEC-09 Autenticação/autorização ausente
File: app.py:11-26; controllers.py:167-186
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306, CWE-862 / A01:2021, A07:2021
Evidência: `app.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])` · `return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200`
Description: nenhuma rota verifica identidade; `/login` valida a senha mas não emite token/sessão, logo não existe identidade para proteger rotas. Escrita de produtos, listagem de usuários (PII), todos os pedidos, pedidos de qualquer usuário (IDOR implícito) e mudança de status ficam abertos. CRITICAL porque nenhuma rota verifica identidade e há dados pessoais e escrita.
Impact: qualquer cliente remoto altera catálogo e preços, lê dados de todos os usuários/pedidos e aprova/cancela pedidos.
Recommendation: emitir token assinado no login e exigir `Authorization: Bearer` com checagem de perfil/propriedade nas rotas de dados (Playbook P-05).

### [CRITICAL] F-004 · SEC-03 Endpoint administrativo/destrutivo sem autenticação
File: app.py:28, 47-57, 59-78
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021
Evidência: `@app.route("/admin/reset-db", methods=["POST"])` … `cursor.execute("DELETE FROM usuarios")`
Description: `/admin/reset-db` apaga todas as tabelas, `/admin/query` executa SQL e `/relatorios/vendas` expõe faturamento, todos sem qualquer verificação de identidade ou perfil.
Impact: destruição total dos dados e vazamento de informação financeira por requisição anônima.
Recommendation: exigir token de administrador em `/admin/reset-db` e `/relatorios/vendas`; remover `/admin/query` (ver F-005) (Playbook P-05).

### [CRITICAL] F-005 · SEC-04 Execução arbitrária de SQL
File: app.py:59-78
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-94 / A03:2021
Evidência: `query = dados.get("sql", "")` … `cursor.execute(query)`
Description: o campo `sql` do corpo é executado diretamente no banco, com `commit` para comandos que não são SELECT.
Impact: leitura (incluindo senhas), alteração e destruição arbitrária do banco por qualquer cliente.
Recommendation: remover a rota; não há variante segura de execução de SQL vindo do cliente (Playbook P-05, P-02).

### [CRITICAL] F-006 · SEC-07 Dados sensíveis expostos em respostas
File: controllers.py:286-289; models.py:83, 99
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-200, CWE-201 / A02:2021
Evidência: `"db_path": "loja.db", "debug": True, "secret_key": "minh***"` · `"senha": row["senha"]`
Description: `GET /health` (pública) devolve a chave secreta, caminho do banco e flag de debug; `GET /usuarios` e `GET /usuarios/<id>` serializam a coluna `senha` (texto puro, F-007).
Impact: vazamento da chave de assinatura e das senhas de todos os usuários, incluindo o administrador, por requisição anônima.
Recommendation: DTO de saída sem `senha`; health apenas com status/contagens (Playbook P-04).

### [CRITICAL] F-007 · SEC-06 Armazenamento inseguro de senha
File: database.py:75-83; models.py:109-111, 126-129
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-256 / A02:2021
Evidência: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
Description: senhas são gravadas em texto puro (seed e cadastro) e comparadas por igualdade dentro do SQL.
Impact: qualquer leitura do banco (F-005, F-006, backup) expõe todas as senhas reutilizáveis.
Recommendation: hash com KDF (`werkzeug.security`, já instalado com o Flask) e verificação em código (Playbook P-03).

### [CRITICAL] F-008 · SEC-01 SQL Injection
File: models.py:47-50, 57-61, 109-111, 126-129, 140, 148-151, 155, 157-161, 163-166, 289-299
Ocorrências: 10 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-89 / A03:2021
Evidência: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` · `query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"`
Description: strings do body (nome, descricao, categoria, email, senha, produto_id, quantidade, usuario_id) e da query string (`q`, `categoria`) são concatenadas no SQL. O login aceita `' OR '1'='1` e devolve o primeiro usuário (admin). As demais concatenações com `id` vindos de `<int:...>` (models.py:28, 68, 92, 174, 280) não são exploráveis isoladamente, mas serão parametrizadas na mesma mudança.
Impact: bypass de login, leitura/alteração arbitrária de dados por requisição anônima.
Recommendation: placeholders `?` em todas as consultas (Playbook P-02).

### [CRITICAL] F-009 · ARC-01 God File
File: app.py:1-88; models.py:1-314
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `app.config["SECRET_KEY"] = ...` / `app.add_url_rule(...)` / `cursor.execute("DELETE FROM itens_pedido")` / `app.run(...)` no mesmo arquivo
Description: app.py reúne config, registro de rotas, handlers com SQL direto e entrypoint (4 papéis); models.py reúne acesso a dados, regra de negócio (desconto por faixa em models.py:256-262, validação de estoque em 139-146) e serialização em 314 linhas, para três domínios.
Impact: impossível testar regras isoladamente; qualquer mudança toca arquivos que concentram todas as responsabilidades.
Recommendation: separar config, rotas, controllers, services e models por domínio; app.py vira composition root (Playbook P-08, P-09, P-13).

### [HIGH] F-010 · SEC-12 Validação de entrada ausente ou frágil (regra de estoque/financeira)
File: controllers.py:39-46, 81-90, 169-170, 195-203, 239-240; models.py:144-146
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-20 / A03:2021
Evidência: `itens = dados.get("itens", [])` … `total = total + (produto["preco"] * item["quantidade"])`
Description: `quantidade` não é validada (negativa ou texto); `preco`/`estoque` não têm checagem de tipo (string causa `TypeError` → 500); PUT de produto não valida nome/categoria; `/login` e `PUT .../status` chamam `.get` em corpo possivelmente `None` (500). HIGH porque chega à regra de estoque e ao total do pedido.
Impact: pedido com quantidade negativa gera total negativo e aumenta o estoque; dados inválidos persistidos.
Recommendation: validar presença, tipo e faixa na borda, respondendo 400 no formato de erro já existente (Playbook P-07).

### [HIGH] F-011 · SEC-08 Dados sensíveis (PII) em logs
File: controllers.py:161, 179, 182
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-532 / A09:2021
Evidência: `print("Login falhou: " + email)`
Description: e-mail do usuário é escrito em claro no stdout em cadastro e em login (sucesso e falha).
Impact: PII em logs; logs de falha de login revelam e-mails tentados.
Recommendation: logger com mascaramento de e-mail (Playbook P-15).

### [HIGH] F-012 · SEC-15 Fluxo crítico sem transação / condição de corrida
File: models.py:139-169
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-362 / A04:2021
Evidência: `if produto["estoque"] < item["quantidade"]:` … (outro loop) `"UPDATE produtos SET estoque = estoque - " + str(item["quantidade"])`
Description: o estoque é verificado num loop e baixado em outro, sem transação explícita nem `rollback`; o `UPDATE` não condiciona a `estoque >= quantidade`. Falha no meio (ex.: produto removido) deixa pedido e itens parciais na conexão global compartilhada.
Impact: venda acima do estoque sob concorrência e pedidos inconsistentes.
Recommendation: transação única com `UPDATE ... WHERE estoque >= ?` verificando `rowcount` e rollback em erro (Playbook P-10).

### [HIGH] F-013 · ARC-04 Acoplamento forte sem injeção de dependência
File: app.py:4, 49-50, 66-67; controllers.py:3, 266-274
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `db = get_db()` / `cursor.execute("SELECT COUNT(*) FROM produtos")` dentro de handlers
Description: handlers HTTP (admin em app.py e health em controllers.py) importam e usam a conexão diretamente, fora da camada de dados.
Impact: lógica de dados espalhada pela camada HTTP; impossível substituir o banco em testes.
Recommendation: acesso a dados só em models/repositórios; conexão provida pelo composition root (Playbook P-13, P-08).

### [HIGH] F-014 · ARC-02 Lógica de negócio em controller/model sem camada de serviço
File: controllers.py:52-54, 208-210, 242-250; models.py:256-262
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `if novo_status == "aprovado": print("NOTIFICAÇÃO: ...")` · `if faturamento > 10000: desconto = faturamento * 0.1`
Description: regras de domínio (categorias válidas, transições de status, notificações de pedido, faixas de desconto do relatório) estão nos handlers e no módulo de acesso a dados; não existe camada de serviço.
Impact: regra duplicável e não testável isoladamente; mudança de regra exige mexer em HTTP ou SQL.
Recommendation: extrair services por domínio (Playbook P-09).

### [HIGH] F-015 · ARC-03 Conexão global mutável compartilhada
File: database.py:4-11
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `global db_connection` … `sqlite3.connect(db_path, check_same_thread=False)`
Description: uma única conexão SQLite de módulo é compartilhada por todas as requisições e threads, com `check_same_thread=False`.
Impact: transações de requisições concorrentes se misturam (commit/rollback de uma afeta outra); agrava F-012.
Recommendation: conexão por requisição (`g` + `teardown_appcontext`) criada no composition root (Playbook P-13).

### [MEDIUM] F-016 · SEC-17 Falta de proteções HTTP básicas
File: app.py:9, 21
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-770, CWE-693 / A05:2021
Evidência: `CORS(app)` · `app.add_url_rule("/login", ...)`
Description: CORS liberado para qualquer origem, sem cabeçalhos de segurança e sem limite de tentativas em `/login`.
Impact: força bruta de senha sem barreira; qualquer site pode chamar a API pelo navegador.
Recommendation: CORS restrito por configuração, cabeçalhos de segurança e limite de tentativas de login (Playbook P-19).

### [MEDIUM] F-017 · SEC-13 Vazamento de detalhes internos em erros
File: app.py:77-78; controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
Ocorrências: 17 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-209 / A05:2021
Evidência: `return jsonify({"erro": str(e)}), 500`
Description: o texto da exceção (mensagens do sqlite, `TypeError` etc.) é devolvido ao cliente em todos os handlers.
Impact: revela estrutura de tabelas/SQL e facilita a exploração de F-008.
Recommendation: handler central de erros com mensagem genérica e log interno, mantendo status 500 e formato `{"erro": ...}` (Playbook P-06).

### [MEDIUM] F-018 · SEC-16 Dependências sem lockfile
File: requirements.txt:1-2
Ocorrências: 1 · Confiança: LIKELY · Categoria: Segurança
CWE/OWASP: CWE-1104 / A06:2021
Evidência: `flask==3.1.1` / `flask-cors==5.0.1`
Description: diretas fixadas e importadas, mas dependências transitivas (Werkzeug, Jinja2, itsdangerous…) não são fixadas e não há lockfile; vulnerabilidades não foram consultadas (sem rede, por política).
Impact: builds não reprodutíveis; versão vulnerável de transitiva pode entrar sem aviso.
Recommendation: rodar `pip-audit` e gerar lock/constraints (classe C; recomendação manual) (Playbook P-18).

### [MEDIUM] F-019 · ARC-09 Tratamento de erro ruim / respostas inconsistentes
File: controllers.py:10, 21, 60, 95, 108, 125, 133, 143, 164, 185, 218, 226, 234, 254, 261, 291; controllers.py:20, 142
Ocorrências: 18 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `except Exception as e:` (16×) · 404 de produto com `"sucesso": False` (linha 20) × 404 de usuário sem `sucesso` (linha 142)
Description: captura genérica em todos os handlers convertendo qualquer erro (inclusive de validação) em 500; formato de erro inconsistente.
Impact: erros de cliente aparecem como 500; clientes não conseguem tratar erros de forma uniforme.
Recommendation: handler central de erros e exceções de domínio (Playbook P-06).

### [MEDIUM] F-020 · ARC-08 Código duplicado
File: controllers.py:28-46, 72-90; models.py:12-21, 31-40, 304-313, 178-199, 211-231
Ocorrências: 7 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: bloco `"id": row["id"], "nome": row["nome"], ...` repetido 3× para produtos; montagem de pedido+itens repetida 2×; validação criar/atualizar repetida
Description: serialização row→dict de produto (3×), de pedido com itens (2×) e validação de produto (2×, já divergente: PUT não valida nome/categoria).
Impact: correções aplicadas em um lugar e esquecidas em outro (a divergência de validação já existe).
Recommendation: funções únicas de serialização e validação (Playbook P-16).

### [MEDIUM] F-021 · ARC-10 Integridade referencial ausente
File: database.py:14-53; models.py:148-151
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `email TEXT,` (sem UNIQUE/NOT NULL) · `usuario_id INTEGER,` (sem FOREIGN KEY)
Description: schema sem NOT NULL, UNIQUE em e-mail ou FK; pedido é criado para `usuario_id` inexistente; e-mails duplicados são aceitos (login devolve o primeiro).
Impact: dados órfãos e contas ambíguas.
Recommendation: validar existência do usuário e unicidade do e-mail no serviço; restrições no schema de bancos novos (Playbook P-10).

### [MEDIUM] F-022 · ARC-12 Dinheiro em ponto flutuante
File: database.py:19, 41, 51; models.py:146
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `preco REAL,` · `total = total + (produto["preco"] * item["quantidade"])`
Description: preço, total e preço unitário em `REAL`/`float`, somados sem arredondamento.
Impact: erros de arredondamento acumulados em totais e no relatório.
Recommendation: cálculo em `Decimal` com quantização a 2 casas; migração do armazenamento para tipo exato (Playbook P-17).

### [MEDIUM] F-023 · ARC-11 Carga total / `SELECT *` / múltiplos COUNT
File: models.py:7, 75, 206, 239-254
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `cursor.execute("SELECT * FROM pedidos")` · cinco consultas `COUNT`/`SUM` separadas no relatório
Description: listagens carregam tabelas inteiras com `SELECT *`; o relatório faz 5 consultas onde uma agregação resolve.
Impact: degradação com volume; colunas sensíveis trafegam sem necessidade.
Recommendation: colunas explícitas, agregação única e paginação opcional (Playbook P-11).

### [MEDIUM] F-024 · ARC-07 Queries N+1
File: models.py:187-199, 219-231
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `for item in itens: cursor3.execute("SELECT nome FROM produtos WHERE id = " + ...)`
Description: para cada pedido, uma consulta de itens e, para cada item, uma consulta de produto.
Impact: 1 + P + I consultas por listagem.
Recommendation: JOIN de itens com produtos e agrupamento em memória (Playbook P-11).

### [MEDIUM] F-025 · OUTRO-01 Atualização de status de pedido inexistente responde sucesso
File: controllers.py:245-252; models.py:275-283
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Outro
CWE/OWASP: n/a
Evidência: `models.atualizar_status_pedido(pedido_id, novo_status)` … `return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200`
Description: o `UPDATE` não verifica `rowcount`; `PUT /pedidos/999999/status` responde 200 "Status atualizado" sem alterar nada.
Impact: cliente acredita ter aprovado/cancelado pedido inexistente.
Recommendation: retornar 404 quando o pedido não existir (padrão equivalente: P-09/P-06).

### [LOW] F-026 · TST-02 Instruções de teste ausentes
File: README.md:5-12
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Testes
CWE/OWASP: n/a
Evidência: `pip install -r requirements.txt` / `python app.py` (nenhuma menção a testes)
Description: o README explica como rodar mas não como testar; `requirements-dev.txt` e `pytest.ini` existem sem documentação; não há CI.
Impact: novos desenvolvedores não sabem que a suíte exige a porta 5000 livre e as dependências de dev.
Recommendation: documentar `pip install -r requirements-dev.txt` e `python -m pytest` (recomendação manual).

### [LOW] F-027 · QLT-04 `print` no lugar de logger
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Ocorrências: 19 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + ...)`
Description: toda a saída operacional é `print`, sem nível nem formato.
Impact: logs não filtráveis; mistura com saída do servidor.
Recommendation: módulo `logging` (Playbook P-15).

### [LOW] F-028 · QLT-05 Estilo inconsistente
File: controllers.py:8, 54, 57, 200
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `if not itens or len(itens) == 0:` · `"Listando " + str(len(produtos)) + " produtos"`
Description: checagem redundante e concatenação com `str()` em vez de f-strings.
Impact: legibilidade.
Recommendation: simplificar (Playbook P-16).

### [LOW] F-029 · QLT-02 Nomes que sombreiam builtins / pouco descritivos
File: controllers.py:14, 56, 64, 98, 136, 160; models.py:24, 54, 65, 89, 187, 191
Ocorrências: 12 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `def buscar_produto(id):` · `cursor2 = db.cursor()` / `cursor3 = db.cursor()`
Description: `id` sombreia o builtin; `cursor2`/`cursor3` não descrevem o propósito.
Impact: legibilidade e risco de bug ao usar `id()`.
Recommendation: renomear (`produto_id`, `itens_cursor`) (Playbook P-16).

### [LOW] F-030 · QLT-01 Magic numbers e strings soltas
File: controllers.py:52, 242; models.py:257-262
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `["pendente", "aprovado", "enviado", "entregue", "cancelado"]` · `if faturamento > 10000: desconto = faturamento * 0.1`
Description: categorias, status e faixas de desconto como literais soltos.
Impact: regra espalhada; mudança exige caçar literais.
Recommendation: constantes nomeadas no domínio (Playbook P-16).

### [LOW] F-031 · QLT-03 Imports sem uso
File: database.py:2; models.py:2
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `import os` · `import sqlite3`
Description: `os` em database.py e `sqlite3` em models.py nunca são usados (busca por `os.` e `sqlite3.` nos arquivos).
Impact: ruído.
Recommendation: remover (Playbook P-16).

## Descartados / falsos positivos
- SEC-01 em models.py:28, 68, 92, 174, 280 — `id`/`usuario_id`/`pedido_id` chegam pelo conversor `<int:...>` do Flask; não exploráveis isoladamente (parametrizados mesmo assim em C-03).
- SEC-10 em controllers.py:160 / models.py:122 — `tipo` não é lido do corpo (padrão `cliente`); escalada só via F-008.
- SEC-11 — sem identidade no fluxo, reportado como SEC-09 (F-003), conforme catálogo.
- SEC-14 — total calculado no servidor (models.py:146); não há pagamento; notificações são apenas `print`.
- SEC-08 para senha — nenhuma senha é logada; apenas e-mail (F-011).
- TST-01 / TST-03 — há 23 testes de integração com pytest e dependências declaradas (requirements-dev.txt) e instaladas no .venv.
- DEP-01…05 — nenhuma ocorrência (ver Summary).

## Correções que exigem mudança de contrato
| ID | Rota/campo | Mudança | Sev. | Motivo (Finding) | Impacto para clientes | Refatorar | Manter contrato\* | Híbrido | Prova prevista |
|---|---|---|---|---|---|---|---|---|---|
| CT-01 | POST /admin/query | remover | CRITICAL | F-005, F-004 | rota deixa de existir (404) | aplica | não (fica sem correção) | aplica — variante mínima: remoção (não há variante segura) | teste novo (integração) + execução local autenticada |
| CT-02 | POST /admin/reset-db | exigir token de admin (401 sem token, 403 não-admin) | CRITICAL | F-004 | enviar `Authorization: Bearer <token admin>` | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-03 | GET /relatorios/vendas | exigir token de admin | CRITICAL | F-004 | enviar token de admin | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-04 | POST/PUT/DELETE /produtos | exigir token de admin | CRITICAL | F-003 | enviar token de admin; GET de produtos segue público | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-05 | GET /usuarios, GET /usuarios/<id> | exigir token (lista: admin; por id: o próprio usuário ou admin) | CRITICAL | F-003 | enviar token; POST /usuarios segue público | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-06 | POST /pedidos, GET /pedidos, GET /pedidos/usuario/<id>, PUT /pedidos/<id>/status | exigir token (criar: o próprio `usuario_id` ou admin; listar todos e mudar status: admin; por usuário: o próprio ou admin) | CRITICAL | F-003 | enviar token; 403 para pedido/listagem de outro usuário | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) + execução local autenticada |
| CT-07 | POST /login → `dados.token` | adicionar campo `token` (aditivo; mecanismo de CT-02…06) | CRITICAL | F-003 | passa a receber token; campos atuais mantidos | aplica | não (fica sem correção) | aplica — variante mínima | teste novo (integração) |
| CT-08 | GET /usuarios, GET /usuarios/<id> → `senha` | omitir campo | CRITICAL | F-006 | deixa de receber `senha` | aplica | sim (valor neutralizado, chave mantida) | aplica — variante mínima (omite) | teste novo (integração) |
| CT-09 | GET /health → `secret_key`, `db_path`, `debug` | omitir campos | CRITICAL | F-006 | deixa de receber esses 3 campos; `status`, `database`, `counts` mantidos | aplica | sim (valor neutralizado, chave mantida) | aplica — variante mínima (omite) | teste novo (integração) |
| CT-10 | CORS (todas as rotas) | restringir origens por configuração | MEDIUM | F-016 | navegadores de origens não configuradas deixam de receber `Access-Control-Allow-Origin` | aplica | não (fica sem correção) | não aplica (MEDIUM/LOW) | teste novo (integração) |
| CT-11 | PUT /pedidos/<id>/status (pedido inexistente) | 200 → 404 | MEDIUM | F-025 | tratar 404 | aplica | não (fica sem correção) | não aplica (MEDIUM/LOW) | teste novo (integração) |
| CT-12 | POST /usuarios (e-mail duplicado), POST /pedidos (usuário inexistente) | 201 → 400 (formato de erro existente) | MEDIUM | F-021 | tratar 400 | aplica | não (fica sem correção) | não aplica (MEDIUM/LOW) | teste novo (integração) |

Resumo para a pergunta: 12 correções exigem contrato. Refatorar: corrige todas. Manter contrato\*: ficam sem correção 3 CRITICAL e 0 HIGH (F-003, F-004, F-005), exige segunda confirmação. Híbrido: aplica 9 (CRITICAL/HIGH: CT-01…CT-09); ficam sem correção 3 MEDIUM/LOW (CT-10, CT-11, CT-12).

## Testes afetados
| Teste | Motivo (C-xx/CT-xx) | Classe (T1/T2/T4) | Ajuste previsto |
|---|---|---|---|
| tests/conftest.py (fixture `api`) | C-01 (seed/SECRET_KEY/DB por ambiente) | T1 | definir variáveis de ambiente de teste (senhas de seed aleatórias, SECRET_KEY) e expor credenciais/token para os testes |
| tests/test_api.py::test_login_sucesso | C-01 (senha de seed por ambiente) | T1 | usar a senha de seed da fixture em vez do literal |
| tests/test_api.py::_criar_produto, test_crud_produto, test_atualizar_e_deletar_produto_inexistente, test_criar_produto_validacoes | CT-04 | T2 | enviar token de admin |
| tests/test_api.py::test_listar_usuarios_seed, test_buscar_usuario, test_criar_usuario | CT-05 | T2 | token de admin / do próprio usuário |
| tests/test_api.py::_criar_usuario, test_criar_pedido_*, test_atualizar_status_pedido | CT-06 | T2 | login do usuário criado e token; status com token de admin |
| tests/test_api.py::test_relatorio_vendas | CT-03 | T2 | token de admin |
| novos em tests/ (provas) | CT-01…CT-12; F-001, F-002, F-006, F-007, F-008, F-010, F-011, F-012 | T4 | integração (HTTP, mesma fixture) e unidade quando a prova não é observável via HTTP |

## Plano de mudanças
| ID | Mudança | Sev. | Resolve | Arquivos | Padrão | Afeta contrato | Depende de |
|---|---|---|---|---|---|---|---|
| C-01 | Módulo de configuração por ambiente (SECRET_KEY, DEBUG off, HOST 127.0.0.1, PORT, DB_PATH, CORS, credenciais de seed aleatórias se ausentes) | CRITICAL | F-001, F-002 | app.py, database.py, config/ (novo) | P-01 | não | — |
| C-02 | Extrair camada de dados por domínio (database/ conexão+schema+seed; models/ produto, usuario, pedido) | CRITICAL | F-009 | models.py, database.py → models/, database/ | P-08 | não | C-01 |
| C-03 | Parametrizar todas as consultas | CRITICAL | F-008 | models/ | P-02 | não | C-02 |
| C-04 | Hash de senha com KDF (werkzeug.security) e verificação em código, com rehash transparente de senhas legadas | CRITICAL | F-007 | models/usuario, database/seed, services | P-03 | não | C-02 |
| C-05 | Transação atômica na criação de pedido (`UPDATE ... WHERE estoque >= ?`, rollback) e integridade (usuário existente, e-mail único, NOT NULL em bancos novos) | HIGH | F-012, F-021 | models/pedido, services, database/schema | P-10 | CT-12 | C-02 |
| C-06 | Cálculo monetário com Decimal quantizado (armazenamento REAL mantido) | MEDIUM | F-022 (parcial) | services/pedido, services/relatorio | P-17 | não | C-02 |
| C-07 | Extrair services (produto, usuario, pedido, relatorio) com regras, status, notificações e 404 de pedido inexistente | HIGH | F-014, F-009, F-025 | controllers.py, models.py → services/ | P-09 | CT-11 | C-02 |
| C-08 | Validação de entrada na borda (tipos, faixas, quantidade > 0, corpo ausente) com 400 no formato existente | HIGH | F-010 | controllers/, validators | P-07 | não | C-07 |
| C-09 | Serialização sem campos sensíveis (usuário sem `senha`; health sem segredo/config) | CRITICAL | F-006 | models/, controllers/health | P-04 | CT-08, CT-09 | C-07 |
| C-10 | Autenticação por token assinado no login, decoradores de perfil/propriedade, proteção de admin e remoção de /admin/query | CRITICAL | F-003, F-004, F-005 | controllers/, routes/, auth (novo) | P-05 | CT-01…CT-07 | C-09 |
| C-11 | Tratamento de erros centralizado (sem `str(e)` ao cliente; status/formato mantidos) | MEDIUM | F-017, F-019 | app factory, controllers/ | P-06 | não | C-07 |
| C-12 | Logging com `logging` e mascaramento de e-mail | HIGH | F-011, F-027 | controllers/, services/, app.py | P-15 | não | C-07 |
| C-13 | Eliminar N+1 (JOIN), colunas explícitas, agregação única no relatório, paginação opcional retrocompatível | MEDIUM | F-024, F-023 | models/ | P-11 | não | C-03 |
| C-14 | Composition root (app factory), conexão por requisição, sem estado global | HIGH | F-013, F-015, F-009 | app.py, database/ | P-13 | não | C-07 |
| C-15 | Cabeçalhos de segurança, limite de tentativas em /login, CORS restrito por config | MEDIUM | F-016 | app factory, config | P-19 | CT-10 | C-14 |
| C-16 | Limpeza: constantes, deduplicação, nomes, imports mortos, estilo | LOW | F-020, F-028, F-029, F-030, F-031 | todos | P-16 | não | C-14 |

Recomendações manuais (sem `C-xx`):
- F-001: rotacionar a `SECRET_KEY` e a senha de admin já publicadas no histórico git (ação externa ao código).
- F-018: rodar `pip-audit -r requirements.txt` e gerar lock/constraints das transitivas (classe C, rede).
- F-026: documentar no README a execução dos testes (`pip install -r requirements-dev.txt`, `python -m pytest`, porta 5000 livre).
- F-022: migração do armazenamento monetário para inteiro em centavos/`NUMERIC` exige migração do `loja.db` existente — fora do escopo automático.

## Plano de comandos
| ID | Comando | Finalidade | Origem | Classe | Efeitos colaterais |
|---|---|---|---|---|---|
| K-00 | `git branch refactor-arch/checkpoint-20261116-195523 HEAD` + `git worktree add <tmp>\exec-p1\checkpoint refactor-arch/checkpoint-20261116-195523` | checkpoint do código original e cópia para provas vermelhas/baseline V4 | política 07 §2.2 | C | cria branch e worktree fora do projeto (sem commit) |
| K-01 | `.venv\Scripts\python.exe -m pytest` | baseline e validação final (V1) | pytest.ini:1-3; requirements-dev.txt:1-3 | B | sobe a app em cópia temporária na porta 5000; cria `.pytest_cache` |
| K-02 | `.venv\Scripts\python.exe -m py_compile <arquivos>` / import da app | verificação rápida após cada bloco (V5) | toolchain Python | B | `__pycache__` |
| K-03 | `.venv\Scripts\python.exe app.py` (cwd e banco em `<tmp>\exec-p1`) | boot (V3/V4) | README.md:9; app.py:80-88 | B | porta 5000; banco descartável no diretório temporário |
| K-04 | script de requisições em `<tmp>\exec-p1` contra `http://127.0.0.1:5000` | execução local autenticada (V4), baseline (checkpoint) e final | 06 §5.1 | B (banco descartável) | nenhum no projeto |
| K-05 | `.venv\Scripts\python.exe -m pytest <testes novos>` com a cópia do checkpoint | prova vermelha no código original | 06 §8.9 | B | `.pytest_cache` na cópia |
| K-06 | `taskkill /F /T /PID <pid>`; `git worktree remove <tmp>\exec-p1\checkpoint`; remover scripts temporários | limpeza | 07 §2 | B/C | remove apenas o que a execução criou |
| — | `pip install -r requirements.txt` / `-r requirements-dev.txt` | instalação | README.md:8 | C | **não necessário**: dependências já instaladas no .venv |
| — | `pip-audit` | auditoria de dependências | recomendação F-018 | C | **não será executado** (rede) |
| — | `POST /admin/reset-db` | rota destrutiva | app.py:47-57 | D | só no banco descartável da V4 (B); nunca contra `loja.db` |

## Plano de validação
| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim | `.venv\Scripts\python.exe -m pytest` (pytest.ini:1-3, B) | 23 testes de integração (HTTP caixa-preta contra `python app.py` em cópia temporária) |
| V2 Script de verificação do projeto | não | — | sem lint/CI/scripts |
| V3 Boot + requisições existentes | parcial | boot `python app.py` (README.md:9) | não há coleção nem `curl` versionados; só o boot é exercitado |
| V4 Execução local autenticada | depende de P4 | boot com variáveis de teste e banco em `<tmp>\exec-p1` + requisições geradas por script temporário | baseline na cópia do checkpoint (credenciais do seed versionado) e final (credenciais aleatórias por ambiente + token do /login) |
| V5 Estático | sempre | `python -m py_compile` / import (B) | — |
| Pré-requisitos | | nenhum (deps instaladas) | — |
| Testes afetados previstos | | ver "Testes afetados" | T1: conftest, test_login_sucesso; T2: produtos/usuários/pedidos/relatório |
| Prova prevista (`CT-xx` aplicados e correções CRITICAL/HIGH) | | testes novos de integração em tests/ (+ unidade para hash/log) e V4 | vermelho no checkpoint, verde no refatorado |
| Não exercitável | | POST /admin/reset-db fora do banco descartável; concorrência real de F-012 (prova por teste de atomicidade, não de carga) | — |

## Decisões do usuário
- P1: Sim, aplicar todas as mudanças do plano (1A)
- P2: Equilibrado (recomendado) (2A)
- P3: Refatorar (recomendado) — CT-01…CT-12 aplicados (3A)
- P4: Sim, incluindo escrita em banco descartável (recomendado) (4A)
- Segunda confirmação: não aplicável (nenhum CRITICAL/HIGH sem correção)
- Fase 3 — lote classe C (K-00a, K-00b, K-06): Executar todos (1A); decisão de design P-05: token assinado emitido pelo POST /login com itsdangerous e SECRET_KEY da config (2A)

================================
Total: 31 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---
# ANEXO — FASE 3 (Run id: 20261116-195523)

## Decisões do usuário (registro)
- Escopo: todas (P1 = "Sim, aplicar todas as mudanças do plano")
- Modo de comandos: Equilibrado (lote classe C K-00a/K-00b/K-06: "Executar todos")
- Contrato: Refatorar (CT-01…CT-12 aplicados)
- Execução local autenticada (P4): incluindo escrita (banco descartável)
- Decisão de design (P-05, passo 1): token assinado emitido pelo `POST /login` (itsdangerous, já instalado com o Flask; chave `SECRET_KEY` da config; expiração `TOKEN_MAX_AGE`)

## Estrutura DEPOIS
```
code-smells-project/
├── app.py                      composition root: create_app() + python app.py
├── .env.example                nomes das variáveis (valores fictícios)
├── config/      settings.py (ambiente), logging_config.py
├── database/    connection.py (conexão por requisição), schema.py (DDL + seed por variável de ambiente)
├── models/      produto_model.py, usuario_model.py, pedido_model.py, admin_model.py
├── services/    produto_service.py, usuario_service.py, pedido_service.py, relatorio_service.py,
│                sistema_service.py, auth_service.py, regras.py, dinheiro.py, erros.py
├── controllers/ produto_controller.py, usuario_controller.py, pedido_controller.py,
│                sistema_controller.py, validators.py
├── routes/      __init__.py (blueprints + proteção por rota)
├── views/       serializers.py (DTO por lista branca)
├── middlewares/ auth.py, errors.py, security.py
└── tests/       conftest.py, test_api.py, test_seguranca.py (novo), test_unidade.py (novo)
```

| Métrica | ANTES | DEPOIS |
|---|---|---|
| Arquivos-fonte | 4 | 35 (28 com código + 7 `__init__.py` vazios) |
| Linhas de código (aprox.) | ~780 | ~1220 |
| Camadas presentes | entrypoint, config inline, rotas, controllers, models | config, database, models, services, controllers, routes, views, middlewares, composition root |
| Maior arquivo | models.py (314) | controllers/validators.py (121) |
| Arquivos com 3+ papéis | 3 (app.py, controllers.py, models.py) | 0 |

(Mesmo método de contagem da Fase 1: `wc -l` nos `.py` do código-fonte, sem tests/.venv/.claude.)

### Mapa antigo → novo
| Arquivo original | Destino(s) |
|---|---|
| app.py | app.py (composition root), config/settings.py, routes/__init__.py, controllers/sistema_controller.py (index, reset), middlewares/security.py (CORS); `/admin/query` removida (CT-01) |
| controllers.py | controllers/produto_controller.py, usuario_controller.py, pedido_controller.py, sistema_controller.py, controllers/validators.py; regras → services/*; notificações → logging em services/pedido_service.py |
| models.py | models/produto_model.py, usuario_model.py, pedido_model.py; desconto/relatório → services/relatorio_service.py; serialização → views/serializers.py |
| database.py | database/connection.py, database/schema.py |

## Mudanças aplicadas
| ID | Status | Observação |
|---|---|---|
| C-01 | aplicada | config/settings.py lê SECRET_KEY (aleatória por processo se ausente), APP_DEBUG (padrão off), APP_HOST (127.0.0.1), APP_PORT, DB_PATH, CORS_ORIGINS, SEED_*; seed de usuários só com SEED_ADMIN_PASSWORD/SEED_CLIENTE_PASSWORD (padrão do playbook P-01; o plano citava "senhas aleatórias se ausentes" — sem variável o usuário simplesmente não é criado, com aviso no log); `.env.example` criado |
| C-02 | aplicada | camada de dados por domínio (models/, database/) |
| C-03 | aplicada | todas as consultas com `?`; f-strings restantes só interpolam constantes internas (lista de colunas, fragmentos fixos, marcadores `?`, tabelas em lista branca) |
| C-04 | aplicada | `werkzeug.security` (scrypt); seed com hash; senha legada em texto puro migra para hash no primeiro login correto |
| C-05 | aplicada | `BEGIN IMMEDIATE` + `UPDATE ... WHERE estoque >= ?` + rollback; e-mail único e usuário existente validados no serviço (CT-12); NOT NULL/UNIQUE/FK no DDL de bancos novos; `PRAGMA foreign_keys = ON` |
| C-06 | aplicada (parcial) | totais e relatório em Decimal com ROUND_HALF_UP; coluna REAL mantida (migração fora do escopo) |
| C-07 | aplicada | services por domínio; PUT status de pedido inexistente ⇒ 404 (CT-11) |
| C-08 | aplicada | controllers/validators.py: tipos, faixas, quantidade inteira > 0, corpo ausente ⇒ 400 no formato de erro existente |
| C-09 | aplicada | DTO sem `senha`; health sem `secret_key`/`db_path`/`debug` (CT-08, CT-09) |
| C-10 | aplicada | `exigir_autenticacao(perfis)` + `garantir_proprio_ou_admin`; login devolve `dados.token`; `/admin/query` removida (CT-01…CT-07) |
| C-11 | aplicada | handler central (`AppError`, `Exception` ⇒ `{"erro": "Erro interno", "sucesso": false}` 500); todas as respostas de erro passam a ter `sucesso: false` (chave aditiva) |
| C-12 | aplicada | `logging`; logs com ids, sem e-mail/senha/token |
| C-13 | aplicada (parcial) | JOIN único para itens; colunas explícitas; relatório em 1 consulta; paginação opcional `limite`/`offset` (sem parâmetros a resposta é igual à original) |
| C-14 | aplicada | `create_app()`; conexão por requisição (`g` + teardown); dependências injetadas; `python app.py` mantido |
| C-15 | aplicada | cabeçalhos de segurança; limite de 5 falhas de login por IP+e-mail em 300 s (429); CORS só para `CORS_ORIGINS` (CT-10) |
| C-16 | aplicada | constantes em services/regras.py; serialização/validação únicas; sem `id`/`cursor2`; imports mortos removidos |

## Contratos — resultado
| CT | Rota/campo | Antes → Depois | Por que (F-xxx, CWE/OWASP) | Impacto e como adaptar o cliente | Prova (E-nn) |
|---|---|---|---|---|---|
| CT-01 | POST /admin/query | 200 (executa SQL) → 404 (removida) | F-005/F-004, CWE-94/A03 | não há substituto; operação deixa de existir | E-05 verde; E-08 vermelho; E-03/E-07 #43-44 |
| CT-02 | POST /admin/reset-db | aberta → 401 sem/inválido, 403 cliente, 200 admin | F-004, CWE-306/A01 | enviar `Authorization: Bearer <token admin>` | E-05; E-08; E-07 #49-51 |
| CT-03 | GET /relatorios/vendas | aberta → 401/403/200 admin | F-004, CWE-306/A01 | token de admin | E-05; E-08; E-07 #39-42 |
| CT-04 | POST/PUT/DELETE /produtos | aberta → exige admin (GET público) | F-003, CWE-862/A01 | token de admin | E-05; E-08; E-07 #10-15, 46-48 |
| CT-05 | GET /usuarios, /usuarios/<id> | aberta → lista admin; por id próprio ou admin | F-003, CWE-862/A01 | token; cliente só lê o próprio registro | E-05; E-08; E-07 #16-22 |
| CT-06 | POST /pedidos, GET /pedidos, GET /pedidos/usuario/<id>, PUT status | aberta → token + propriedade/admin | F-003, CWE-639/A01 | token; `usuario_id` do pedido = usuário do token (ou admin) | E-05; E-08; E-07 #23-37 |
| CT-07 | POST /login → `dados.token` | sem token → token assinado (aditivo) | F-003, CWE-306/A07 | ler `dados.token` e enviar como Bearer | E-05; E-08; E-07 #06, #09 |
| CT-08 | `senha` em /usuarios | presente → omitida | F-006, CWE-200/A02 | campo deixa de existir | E-05; E-08; E-07 #18, #20 |
| CT-09 | /health `secret_key`, `db_path`, `debug` | presentes → omitidos | F-006, CWE-200/A02 | usar só `status`, `database`, `counts` | E-05; E-08; E-07 #02 |
| CT-10 | CORS | `*` → só `CORS_ORIGINS` | F-016, CWE-693/A05 | configurar `CORS_ORIGINS` com a origem do front | E-05; E-08 |
| CT-11 | PUT /pedidos/<id>/status inexistente | 200 → 404 | F-025 | tratar 404 | E-05; E-08; E-07 #38 |
| CT-12 | POST /usuarios e-mail duplicado; POST /pedidos usuário inexistente | 201 → 400 | F-021 | tratar 400 | E-05; E-08; E-07 #27, #45 |

**Texto-base para o README (seção Resultados):** A auditoria `refactor-arch` (Run id 20261116-195523) mudou o contrato de 12 pontos da API, todos por segurança ou integridade, e o usuário aprovou essas mudanças na rodada de perguntas (opção "Refatorar"). `POST /admin/query` foi removida. Rotas administrativas, de escrita de produtos, de usuários e de pedidos passam a exigir o token emitido por `POST /login` (`Authorization: Bearer`), com checagem de perfil e de propriedade. `senha` e configuração interna saíram das respostas, o CORS ficou restrito e três casos inválidos passaram a responder 404/400. A justificativa de cada mudança está em `reports/audit-project-1.md` ("Contratos — resultado") e as provas em `reports/evidence/project-1/20261116-195523/`. Para rodar: defina `SEED_ADMIN_PASSWORD`/`SEED_CLIENTE_PASSWORD` (ver `.env.example`) antes de `python app.py`.

## Alterações em testes
| Teste | Motivo | Classe | Antes/Depois (trecho do diff) | Asserções | Reexecução | Snapshot |
|---|---|---|---|---|---|---|
| tests/conftest.py (fixtures `credenciais`, `ambiente_app`, `admin_headers`, `caminho_banco`, `log_servidor`; env da app) | C-01 (seed/SECRET_KEY/DB por ambiente), CT-07 | T1 | `env = {**os.environ, "PYTHONIOENCODING": "utf-8"}` → `+ "PYTHONUNBUFFERED", "SECRET_KEY", "SEED_ADMIN_PASSWORD", "SEED_CLIENTE_PASSWORD", "DB_PATH"` | sem asserções novas; lógica de boot/encerramento mantida | E-05 | `tests-before/tests/conftest.py` |
| tests/test_api.py::test_login_sucesso | C-01 | T1 | `"senha": "admi***"` → `"senha": credenciais["admin"]` | mantidas (idênticas) | E-05 | `tests-before/tests/test_api.py` |
| tests/test_api.py: test_crud_produto, test_atualizar_e_deletar_produto_inexistente, test_criar_produto_validacoes, test_listar_usuarios_seed, test_buscar_usuario, test_criar_usuario, test_criar_pedido_calcula_total_e_baixa_estoque, test_criar_pedido_estoque_insuficiente, test_criar_pedido_produto_inexistente, test_criar_pedido_validacoes, test_atualizar_status_pedido, test_relatorio_vendas (+ helpers `_criar_produto`, `_criar_usuario` → `_criar_usuario_com_token`) | CT-03, CT-04, CT-05, CT-06 (autenticação necessária) | T1 | `api.get("/usuarios")` → `api.get("/usuarios", headers=admin_headers)`; `_criar_usuario(api)` → `_criar_usuario_com_token(api)` | mantidas (67 `assert` antes e depois; esperados inalterados) | E-05 | `tests-before/tests/test_api.py` |

Diff completo: `E-10-diff-testes.patch` (segredos do original mascarados). Na Fase 2 esses ajustes foram previstos como T2. Como nenhum valor esperado mudou e só foi acrescentada a credencial, eles se enquadram em T1 (06 §8.3). O novo contrato (401/403) fica afirmado explicitamente nos testes T4.

## Testes adicionados (provas)
| Teste | Tipo | CT/F | O que comprova | Verde (código refatorado) | Vermelho (checkpoint original) |
|---|---|---|---|---|---|
| test_seguranca.py::test_ct01_admin_query_removida | integração | CT-01 / F-005 | rota removida (404/405), com ou sem token | E-05 | E-08 (`assert 200 in (404, 405)`) |
| test_seguranca.py::test_ct02_reset_db_exige_admin | integração | CT-02 / F-004 | sem/ inválido ⇒ 401; cliente ⇒ 403; nada apagado | E-05 | E-08 (`200 == 401`) |
| test_seguranca.py::test_ct03_relatorio_exige_admin | integração | CT-03 / F-004 | 401/401/403/200 | E-05 | E-08 |
| test_seguranca.py::test_ct04_escrita_de_produtos_exige_admin | integração | CT-04 / F-003 | escrita 401/403; leitura pública 200 | E-05 | E-08 |
| test_seguranca.py::test_ct05_usuarios_exigem_token | integração | CT-05 / F-003 | lista admin; por id próprio/admin; alheio 403 | E-05 | E-08 |
| test_seguranca.py::test_ct06_pedidos_exigem_token_e_propriedade | integração | CT-06 / F-003 | token, propriedade e perfil em todas as rotas de pedido | E-05 | E-08 |
| test_seguranca.py::test_ct07_login_emite_token_que_autentica | integração | CT-07 / F-003 | token emitido autentica; adulterado ⇒ 401 | E-05 | E-08 |
| test_seguranca.py::test_ct08_usuarios_sem_campo_senha | integração | CT-08 / F-006 | `senha` ausente na lista e no próprio usuário | E-05 | E-08 |
| test_seguranca.py::test_ct09_health_sem_segredos | integração | CT-09 / F-006 | health sem segredo/config | E-05 | E-08 |
| test_seguranca.py::test_ct10_cors_nao_libera_origem_arbitraria | integração | CT-10 / F-016 | sem `Access-Control-Allow-Origin` para origem arbitrária | E-05 | E-08 |
| test_seguranca.py::test_f016_cabecalhos_e_limite_de_tentativas_de_login | integração | F-016 | cabeçalhos; 6ª falha de login ⇒ 429 | E-05 | E-08 |
| test_seguranca.py::test_ct11_status_de_pedido_inexistente_retorna_404 | integração | CT-11 / F-025 | 404 + `sucesso: false` | E-05 | E-08 (`200 == 404`) |
| test_seguranca.py::test_ct12_integridade_email_unico_e_usuario_existente | integração | CT-12 / F-021 | 400 nos dois casos; estoque intacto | E-05 | E-08 (`201 == 400`) |
| test_seguranca.py::test_f007_senhas_armazenadas_com_hash | integração | F-007 | coluna `senha` com hash (cliente e admin de seed) | E-05 | E-09 (isolado: `assert False`) |
| test_seguranca.py::test_f008_login_nao_aceita_sql_injection | integração | F-008 | `' OR '1'='1' --` ⇒ 401 | E-05 | E-08 (`200 == 401`) |
| test_seguranca.py::test_f008_texto_com_aspas_e_tratado_como_dado | integração | F-008 | nome com aspas gravado/buscado literalmente | E-05 | E-08 (criação 500) |
| test_seguranca.py::test_f010_quantidade_invalida_nao_altera_estoque | integração | F-010 | -3, 0, "2", 1.5 ⇒ 400; estoque intacto | E-05 | E-08 (`-3` aceito) |
| test_seguranca.py::test_f010_tipos_invalidos_e_corpo_ausente_retornam_400 | integração | F-010 | tipos inválidos e corpo ausente ⇒ 400 | E-05 | E-08 (`500 == 400`) |
| test_seguranca.py::test_f011_email_nao_aparece_no_log | integração | F-011 | e-mail ausente do log do servidor | E-05 | E-08 (e-mail no log) |
| test_unidade.py::test_f001_f002_codigo_sem_segredos_nem_debug_fixo | unidade (estrutural) | F-001 / F-002 | sem chave literal, seed com senha literal, debug fixo ou bind 0.0.0.0 | E-05 | E-11 (6 ocorrências no original) |
| test_unidade.py::test_f001_f002_config_padrao_segura | unidade | F-001 / F-002 | padrões seguros; chave aleatória | E-05 | E-08 (ModuleNotFoundError: mecanismo inexistente) |
| test_unidade.py::test_f007_cadastro_grava_hash_e_login_verifica | unidade | F-007 | hash no cadastro; verificação | E-05 | E-08 (ModuleNotFoundError) |
| test_unidade.py::test_f007_senha_legada_em_texto_e_migrada_no_login | unidade | F-007 | migração de senha legada | E-05 | E-08 (ModuleNotFoundError) |
| test_unidade.py::test_ct07_token_assinado_e_verificado | unidade | CT-07 | assinatura/adulteração/outra chave | E-05 | E-08 (ModuleNotFoundError) |
| test_unidade.py::test_f012_falha_no_meio_desfaz_baixa_de_estoque | unidade | F-012 | rollback total em falha no meio; baixa condicional não vende além do estoque | E-05 | E-08 (ModuleNotFoundError; sensibilidade por ausência do mecanismo) |
| test_unidade.py::test_f014_regras_testaveis_sem_http | unidade | F-014 | desconto/total/regra de pedido sem HTTP nem banco | E-05 | E-08 (ModuleNotFoundError) |
| test_unidade.py::test_f015_apps_nao_compartilham_conexao | unidade | F-015 | sem conexão global; apps isoladas | E-05 | E-08 (ModuleNotFoundError) |
| test_unidade.py::test_f009_f013_sem_sql_fora_da_camada_de_dados | unidade (estrutural) | F-009 / F-013 | sem SQL/sqlite3 em controllers, routes, views, middlewares e app.py; camadas existem | E-05 | E-08 (`1 >= 8`) |

## Evidências de execução
(`E-00`, da Fase 1, foi gravado na Fase 2. Os arquivos brutos estão em `reports/evidence/project-1/20261116-195523/`.)

### E-01 · Checkpoint (pré-voo)
Comando: `git branch refactor-arch/checkpoint-20261116-195523 HEAD` + `git worktree add <tmp>\exec-p1\checkpoint ...` · Origem: K-00 · Classe C · Autorização: lote aprovado · 2026-11-16T20:00:21-03:00 · Exit code: 0/0 · Bruto: E-01-checkpoint.log

### E-02 · Suíte do projeto (baseline)
Comando: `.venv\Scripts\python.exe -m pytest -p no:cacheprovider` · Diretório: code-smells-project · Origem: K-01 · pytest.ini:1-3 · Classe B · automática · 2026-11-16T20:00:32-03:00 → 20:00:37 (5 s) · Exit code: 0 · Resultado: passed 23 | failed 0 | skipped 0 · Bruto: E-02-baseline-pytest.log

### E-03 · Execução local autenticada (baseline, cópia do checkpoint)
Comando: script temporário de boot + bateria (52 requisições) em `<tmp>\exec-p1\v4-baseline` · Origem: K-03/K-04 · Classe B (banco descartável, caminho conferido antes das rotas destrutivas) · 2026-11-16T20:02:01-03:00 → 20:02:06 · Credencial admin: seed versionado (admi***) · Resultado: todas as rotas abertas; login com SQL injection 200; `senha` e `secret_key` nas respostas; `loja.db` do projeto inalterado; porta liberada · Bruto: E-03-baseline-execucao-local.log

### E-04 · Compilação V5 (baseline)
4 arquivos compilados sem erro · 2026-11-16T20:04:10-03:00 · Exit code: 0 · Bruto: E-04-baseline-compilacao.log

### E-05 · Suíte do projeto (após refatoração)
Comando: o mesmo de E-02 · Exit code: 0 · Resultado: passed 51 | failed 0 | skipped 0 (baseline E-02: 23/0/0; 23 originais + 28 novos) · Integridade: 2 arquivos alterados, 2 adicionados, os mesmos de "Alterações em testes"/"Testes adicionados" (git diff, E-10) · Bruto: E-05-final-pytest.log

### E-06 · Compilação V5 (após refatoração)
35 arquivos compilados sem erro · Exit code: 0 · Bruto: E-06-final-compilacao.log

### E-07 · Execução local autenticada (final)
Mesma bateria, na cópia do código refatorado em `<tmp>\exec-p1\v4-final` · Banco `<tmp>\exec-p1\v4-final\v4.db` · Credenciais geradas por execução (SECRET_KEY, SEED_ADMIN_PASSWORD e SEED_CLIENTE_PASSWORD aleatórias, mascaradas) + token via `POST /login` (eyJp***) · Debug off, bind 127.0.0.1 · `loja.db` do projeto inalterado · porta liberada · Bruto: E-07-final-execucao-local.log

### E-08 · Provas vermelhas no checkpoint
Os 28 testes novos, rodados contra o código original (cópia fora do projeto): failed 28 / passed 0 · Exit code: 1 · Bruto: E-08-prova-vermelha-checkpoint.log

### E-09 · Prova vermelha isolada de F-007
failed 1 (`assert False`: senha em texto puro) · Bruto: E-09-prova-vermelha-f007-isolado.log

### E-10 · Diff dos testes
`git diff` de tests/ + arquivos novos · Bruto: E-10-diff-testes.patch · Snapshot: tests-before/tests/

### E-11 · Prova vermelha do teste de varredura (versão final dos padrões)
Checkpoint obtido do branch via `git show` · failed 1 (6 ocorrências: SECRET_KEY literal, secret_key na resposta, seed com senha literal, debug/bind) · Bruto: E-11-prova-vermelha-f001-varredura.log

### Execução local autenticada (V4)
Credenciais: no baseline, seed versionado do original; no final, geradas pela aplicação (SEED_* aleatórias por execução, lidas do ambiente) + `POST /login` para obter o token. Valores mascarados. Integrações: nenhuma (notificações apenas em log). Banco: descartável, arquivo em diretório temporário fora do projeto.

| Método | Rota | Credencial | ANTES (status) | DEPOIS (status) | Resultado | Prova |
|---|---|---|---|---|---|---|
| GET | / , /health, /produtos, /produtos/busca, /produtos/1 | sem | 200 | 200 | igual (health sem 3 campos: ALTERADO (aprovado CT-09)) | E-03, E-07 #01-05 |
| POST | /login | admin / cliente | 200 | 200 (+ `token`) | ALTERADO (aprovado CT-07) | #06, #09 |
| POST | /login | SQL injection | 200 | 401 | ALTERADO (correção F-008, sem contrato) | #07 |
| POST | /usuarios | sem | 201 | 201 | igual | #08 |
| POST | /produtos | sem / inválida / cliente / admin | 201/201/201/201 | 401/401/403/201 | ALTERADO (aprovado CT-04) | #10-13 |
| PUT | /produtos/<id> | sem / admin | 200/200 | 401/200 | ALTERADO (aprovado CT-04) | #14-15 |
| GET | /usuarios | sem / cliente / admin | 200/200/200 | 401/403/200 (sem `senha`) | ALTERADO (aprovado CT-05, CT-08) | #16-18 |
| GET | /usuarios/<id> | sem / próprio / alheio / admin | 200/200/200/200 | 401/200/403/200 | ALTERADO (aprovado CT-05, CT-08) | #19-22 |
| POST | /pedidos | sem / próprio / alheio | 201/201/201 | 401/201/403 | ALTERADO (aprovado CT-06) | #23-25 |
| POST | /pedidos | quantidade -3 | 201 | 400 | ALTERADO (correção F-010, sem contrato) | #26 |
| POST | /pedidos | admin, usuário inexistente | 201 | 400 | ALTERADO (aprovado CT-12) | #27 |
| GET | /pedidos | sem / cliente / admin | 200/200/200 | 401/403/200 | ALTERADO (aprovado CT-06) | #28-30 |
| GET | /pedidos/usuario/<id> | sem / próprio / alheio / admin | 200/200/200/200 | 401/200/403/200 | ALTERADO (aprovado CT-06) | #31-34 |
| PUT | /pedidos/<id>/status | sem / cliente / admin | 200/200/200 | 401/403/200 | ALTERADO (aprovado CT-06) | #35-37 |
| PUT | /pedidos/99999999/status | admin | 200 | 404 | ALTERADO (aprovado CT-11) | #38 |
| GET | /relatorios/vendas | sem / inválida / cliente / admin | 200×4 | 401/401/403/200 | ALTERADO (aprovado CT-03) | #39-42 |
| POST | /admin/query | sem / admin | 200/200 | 404/404 | ALTERADO (aprovado CT-01) | #43-44 |
| POST | /usuarios | e-mail duplicado | 201 | 400 | ALTERADO (aprovado CT-12) | #45 |
| DELETE | /produtos/<id> | sem / cliente / admin | 200/404/404 | 401/403/200 | ALTERADO (aprovado CT-04); no baseline a exclusão anônima (#46) já tinha apagado o produto | #46-48 |
| POST | /admin/reset-db | sem / cliente / admin | 200/200/200 | 401/403/200 | ALTERADO (aprovado CT-02); banco descartável zerado nos dois lados | #49-52 |

### Comparação antes/depois (rotas)
| Método | Rota | ANTES | DEPOIS | Resultado | Prova |
|---|---|---|---|---|---|
| GET | / | 200 {endpoints,mensagem,versao} | 200 {endpoints,mensagem,versao} | igual | E-03, E-07 |
| GET | /health | 200 {ambiente,counts,database,db_path,debug,secret_key,status,versao} | 200 {ambiente,counts,database,status,versao} | ALTERADO (aprovado CT-09) | E-07, E-05 |
| GET | /produtos, /produtos/busca, /produtos/<id> | 200 {dados,sucesso[,total]} | igual | igual | E-03, E-07, E-05 |
| POST/PUT/DELETE | /produtos… | 201/200 sem credencial | 401/403; 201/200 admin | ALTERADO (aprovado CT-04) | E-07, E-05 |
| GET | /usuarios, /usuarios/<id> | 200 com `senha` | 401/403; 200 sem `senha` | ALTERADO (aprovado CT-05, CT-08) | E-07, E-05 |
| POST | /usuarios | 201 | 201 (duplicado ⇒ 400) | igual / ALTERADO (aprovado CT-12) | E-07, E-05 |
| POST | /login | 200 {dados{email,id,nome,tipo}} | 200 {dados{email,id,nome,tipo,token}} | ALTERADO (aprovado CT-07) | E-07, E-05 |
| POST, GET, PUT | /pedidos… | abertas | token + propriedade/admin; inexistente ⇒ 404/400 | ALTERADO (aprovado CT-06, CT-11, CT-12) | E-07, E-05 |
| GET | /relatorios/vendas | 200 aberta | 401/403; 200 admin (mesmas chaves) | ALTERADO (aprovado CT-03) | E-07, E-05 |
| POST | /admin/reset-db | 200 aberta | 401/403; 200 admin | ALTERADO (aprovado CT-02) | E-07, E-05 |
| POST | /admin/query | 200 | removida (404) | ALTERADO (aprovado CT-01) | E-07, E-05 |

### Resumo da validação
| Degrau | Comando | Resultado | Evidência |
|---|---|---|---|
| V1 | `.venv\Scripts\python.exe -m pytest -p no:cacheprovider` | baseline: passed 23 / failed 0 / skipped 0 → final: passed 51 / failed 0 / skipped 0 | E-02, E-05 |
| V3 | boot `python app.py` (cópia descartável) | sobe sem erro; debug off; 127.0.0.1:5000 | E-03, E-07 |
| V4 | bateria autenticada (52 requisições) | todas as diferenças explicadas por CT aprovado ou correção F-008/F-010; nenhuma DIVERGENTE | E-03, E-07 |
| V5 | compilação | 4 → 35 arquivos sem erro | E-04, E-06 |
| Provas | testes novos no checkpoint | 28/28 vermelhos (+ E-09, E-11) | E-08, E-09, E-11 |
Veredito: VALIDADO (V1+V4)

## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente: Python, com .venv em 3.14.0 (E-00)
- [x] Framework detectado corretamente: Flask 3.1.1, confirmado por manifesto, import e `Flask(__name__)` (E-00)
- [x] Domínio da aplicação descrito corretamente: e-commerce com produtos, usuários, pedidos e relatório (E-00)
- [x] Número de arquivos analisados condiz com a realidade: 4 arquivos e 780 linhas por `wc -l` (E-00)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência: seções na ordem do 03 §3 (este arquivo)
- [x] Cada finding tem arquivo e linhas exatos: linhas relidas com Read antes de gravar
- [x] Findings ordenados por severidade (CRITICAL → LOW): F-001…F-009 CRITICAL, F-010…F-015 HIGH, F-016…F-025 MEDIUM, F-026…F-031 LOW
- [x] Mínimo de 5 findings identificados: 31
- [x] Detecção de APIs deprecated incluída: buscada e nenhuma encontrada ("DEP: nenhuma…" no Summary)
- [x] Skill pausa e pede confirmação antes da Fase 3: rodada P1–P4 respondida "1A 2A 3A 4A" ("Decisões do usuário")

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC: config/, models/, services/, controllers/, routes/, views/, middlewares/ e app.py; nenhum arquivo com 3+ papéis (test_f009_f013, E-05)
- [x] Configuração extraída para módulo de config: config/settings.py; a varredura não encontra segredo nem debug fixo (test_f001_f002, E-05/E-11). Rotação da chave histórica pendente, é ação externa
- [x] Models criados para abstrair dados: models/*.py; SQL só na camada de dados e sempre parametrizado (test_f009_f013, test_f008, E-05)
- [x] Views/Routes separadas para visualização ou roteamento: routes/__init__.py (mapeamento + proteção) e views/serializers.py (DTO)
- [x] Controllers concentram o fluxo da aplicação: controllers/* validam, chamam services e escolhem o status; sem SQL (test_f009_f013)
- [x] Error handling centralizado: middlewares/errors.py; nenhum `str(e)` (busca da reauditoria); erro 500 genérico
- [x] Entry point claro: app.py com `create_app()` e `python app.py` (README.md:9) (E-07)
- [x] Aplicação inicia sem erros (E-07; E-05 sobe a app via conftest)
- [x] Endpoints originais respondem corretamente: 18 de 19 rotas existem; 6 respondem igual ao baseline (GET /, /produtos, /produtos/busca, /produtos/<id> e POST /usuarios no caso válido; /health com as mesmas chaves menos as omitidas pela CT-09); 12 mudaram por contrato aprovado (CT-01…CT-12), com prova em E-05/E-07/E-08

## Itens residuais (reauditoria)
CRITICAL/HIGH sem correção: Nenhum
Corrigidos no código com ação manual pendente: F-001, porque a `SECRET_KEY` antiga (minh***) e as senhas de seed antigas (admi***, 1234***, senh***) continuam no histórico git e precisam ser consideradas comprometidas e rotacionadas. O `loja.db` local, não versionado, ainda guarda senhas legadas em texto puro até o primeiro login de cada usuário (migração automática); recomenda-se recriar o banco de dev.
Demais findings que continuam presentes:
- F-018 (MEDIUM, SEC-16): recomendação manual (`pip-audit` e lock das transitivas); não foi executado porque usa rede.
- F-021 (MEDIUM, ARC-10, parcial): o `loja.db` existente não é migrado (as restrições valem só para bancos novos), e `itens_pedido.produto_id` ficou sem FK para não mudar a exclusão de produtos com pedidos (exigiria novo contrato).
- F-022 (MEDIUM, ARC-12, parcial): o cálculo é em Decimal, mas o armazenamento continua REAL, porque a migração de schema é classe D e não foi aprovada.
- F-023 (MEDIUM, ARC-11, parcial): sem `limite`/`offset` as listagens ainda devolvem a tabela inteira, para manter o contrato. `SELECT *` e as múltiplas COUNT foram eliminados.
- F-026 (LOW, TST-02): README sem instruções de teste; recomendação manual (texto-base acima).
- Novo, OUTRO-02 (LOW): `LimitadorDeLogin` guarda as chaves de falha em memória e só as expurga quando a mesma chave volta a ser consultada, então o crescimento é proporcional ao número de pares IP+e-mail distintos. Recomendação: expurgo periódico ou limite de chaves.

## Observações da execução
- Stack detectada e confiança: Python 3.14 + Flask 3.1.1 (alta).
- Dicas específicas usadas × derivadas do sinal abstrato: só dicas Python/Flask do catálogo e do playbook; nada derivado.
- Nível de organização encontrado e como a Fase 3 se adaptou: o projeto era `monolito-sem-camadas`, então todas as camadas foram criadas por domínio, com app factory e blueprints, conforme a convenção Flask (04 §3/§4).
- Falsos positivos descartados: 7 (ver "Descartados"). Na reauditoria, as f-strings em SQL dos models interpolam só constantes internas e não são finding.
- Limitações da validação: V2 não existe no projeto. V3 só cobre o boot, porque não há coleção de requisições. Concorrência real de estoque não foi testada sob carga; a prova de F-012 é a atomicidade/rollback em teste de unidade. Os testes de unidade são vermelhos no checkpoint por ausência do mecanismo (ModuleNotFoundError). Os testes de integração são vermelhos por asserção.
- Tentativas/iterações na Fase 3 e reversões:
  - Nenhuma reversão. A suíte adaptada passou na primeira execução.
  - Depois disso, removi uma função de mascaramento não usada e reescrevi os padrões do teste de varredura, que antes continha os segredos antigos como literais; E-05 foi repetida (51/51) e E-11 registra o vermelho da versão final.
  - Um comando composto no Bash falhou com exit 127 antes de executar qualquer coisa; foi refeito por script temporário.
- Desvios registrados:
  - Seed de usuários sem senha aleatória quando a variável está ausente (playbook P-01).
  - `POST /admin/reset-db` exige admin, mas não recebeu a flag de ambiente sugerida pelo playbook, para não ampliar o contrato aprovado na CT-02 (recomendação).
  - Todas as respostas de erro ganharam `sucesso: false` (chave aditiva).
- Arquivos criados pela execução fora do código-fonte:
  - Branch `refactor-arch/checkpoint-20261116-195523`, mantido para o usuário.
  - Worktree e cópias em `<tmp>\exec-p1`, removidas.
  - Scripts temporários da V4 e da prova vermelha, removidos.
  - `__pycache__` gerados no projeto pelas execuções, removidos.
  - `reports/` (relatório e evidências).
  - Nenhum commit foi feito.

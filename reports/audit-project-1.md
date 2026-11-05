================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Path:    code-smells-project
Run:     2026-11-05T14:58:11-03:00          Run id: 20261105-145811
Stack:   Python (3.14.0 no ambiente; versão do projeto não declarada) + Flask 3.1.1 (confiança: alta)
Files:   4 analyzed | ~780 lines of code
Architecture: monolito-sem-camadas
Skill:   refactor-arch 1.0 | Catalog 1.0

## Summary
CRITICAL: 9 | HIGH: 6 | MEDIUM: 10 | LOW: 6
Total: 31 findings (184 ocorrências)
Por categoria: Segurança 14 | Arquitetura 10 | Deprecated 0 | Testes 1 | Qualidade 5 | Outro 1
Cobertura: 4/4 arquivos-fonte lidos integralmente; testes (tests/conftest.py, tests/test_api.py), README.md, requirements*.txt e pytest.ini também lidos integralmente

## Estrutura ANTES
```
code-smells-project/
├── app.py            (88)   entrypoint + config + rotas + 2 handlers admin com SQL
├── controllers.py    (292)  16 handlers, validação, notificações, health com SQL
├── database.py       (86)   conexão global + schema + seed
├── models.py         (314)  SQL + regra de negócio + serialização (4 domínios)
├── requirements.txt
└── README.md
(fora do escopo de código: tests/, pytest.ini, requirements-dev.txt — não versionados)
```

| Métrica | Valor |
|---|---|
| Arquivos-fonte | 4 |
| Linhas de código (aprox.) | 780 (contagem `wc -l`) |
| Camadas presentes (papéis) | entrypoint, config (inline), rotas, controllers, models (misturado com services), banco |
| Maior arquivo | models.py (314) |
| Arquivos com 3+ papéis | 4 (app.py, controllers.py, database.py, models.py) |

## Superfície de ataque
| Método | Rota | Handler (arquivo:linha) | Autenticação | Administrativa/destrutiva |
|---|---|---|---|---|
| GET | / | app.py:33 | não | não |
| GET | /produtos | controllers.py:5 | não | não |
| GET | /produtos/busca | controllers.py:111 | não | não |
| GET | /produtos/<id> | controllers.py:14 | não | não |
| POST | /produtos | controllers.py:24 | não | não |
| PUT | /produtos/<id> | controllers.py:64 | não | não |
| DELETE | /produtos/<id> | controllers.py:98 | não | sim |
| GET | /usuarios | controllers.py:128 | não | não (expõe `senha`) |
| GET | /usuarios/<id> | controllers.py:136 | não | não (expõe `senha`) |
| POST | /usuarios | controllers.py:146 | não | não |
| POST | /login | controllers.py:167 | não | não |
| POST | /pedidos | controllers.py:188 | não | não |
| GET | /pedidos | controllers.py:229 | não | não |
| GET | /pedidos/usuario/<usuario_id> | controllers.py:222 | não | não |
| PUT | /pedidos/<pedido_id>/status | controllers.py:237 | não | não |
| GET | /relatorios/vendas | controllers.py:257 | não | sim (financeiro) |
| GET | /health | controllers.py:264 | não | não (expõe segredo) |
| POST | /admin/reset-db | app.py:48 | não | sim |
| POST | /admin/query | app.py:60 | não | sim |

Entradas: body JSON, query (`q`, `categoria`, `preco_min`, `preco_max`), params de rota. Integrações externas: nenhuma (notificações são `print`).

## Findings

### [CRITICAL] F-001 · SEC-02 Segredos e credenciais hardcoded
File: app.py:7; database.py:76-78
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `app.config["SECRET_KEY"] = "minha-chav***"`; `("Admin", "admin@loja.com", "admi***", "admin")`
Description: `SECRET_KEY` fixa no código de inicialização (usada pelo Flask em runtime) e senhas de seed (admin e 2 clientes) em texto no fonte.
Impact: chave de assinatura de sessão conhecida por quem tiver o repositório; credencial do administrador publicamente conhecida.
Recommendation: ler segredos de variáveis de ambiente em um módulo de configuração (Playbook P-01). As senhas de seed permanecem como fixture de desenvolvimento porque os testes existentes dependem delas (residual declarado na Fase 3).

### [CRITICAL] F-002 · SEC-05 Modo debug ativo e bind público
File: app.py:8, 88
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-489 / A05:2021
Evidência: `app.config["DEBUG"] = True` · `app.run(host="0.0.0.0", port=5000, debug=True)`
Description: debug fixo (console Werkzeug interativo) com escuta em todas as interfaces.
Impact: execução remota de código via console de debug por qualquer host da rede.
Recommendation: DEBUG por variável de ambiente (padrão desligado) e bind `127.0.0.1` por padrão (Playbook P-01).

### [CRITICAL] F-003 · SEC-09 Autenticação/autorização ausente ou falsa
File: app.py:11-30; controllers.py:167-186
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021, A07:2021
Evidência: `usuario = models.login_usuario(email, senha)` → `return jsonify({"dados": usuario, ...}), 200`
Description: `/login` devolve o usuário sem emitir token; nenhuma das 19 rotas verifica identidade ou perfil (`tipo` = admin/cliente nunca é consultado). Qualquer cliente lê, cria, altera e apaga dados de usuários, pedidos e produtos.
Impact: acesso total anônimo a dados pessoais e escrita (CRITICAL pela rubrica: nenhuma rota verifica identidade, há PII e escrita).
Recommendation: login emitir token verificável e middleware de autorização por perfil nas rotas sensíveis (Playbook P-05). Escopo proposto: rotas administrativas/financeiras (CT-05); demais rotas dependem de decisão de produto (ver residuais).

### [CRITICAL] F-004 · SEC-03 Endpoint administrativo/destrutivo sem autenticação
File: app.py:47-57, 59-78, 28; controllers.py:257-262
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021
Evidência: `@app.route("/admin/reset-db", methods=["POST"])` → `cursor.execute("DELETE FROM usuarios")`
Description: `/admin/reset-db` apaga todas as tabelas, `/admin/query` executa SQL arbitrário e `/relatorios/vendas` (financeiro) responde a qualquer cliente, sem nenhuma verificação.
Impact: destruição total dos dados e vazamento financeiro por um atacante remoto anônimo.
Recommendation: exigir credencial administrativa (token de perfil admin) nas rotas administrativas e no relatório (Playbook P-05).

### [CRITICAL] F-005 · SEC-04 Execução arbitrária de SQL
File: app.py:59-78
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-94 / A03:2021
Evidência: `query = dados.get("sql", "")` … `cursor.execute(query)`
Description: o corpo da requisição é executado diretamente como SQL (qualquer comando, não só SELECT), sem autenticação.
Impact: leitura (inclusive de senhas), alteração e destruição arbitrária do banco.
Recommendation: remover a rota ou protegê-la por token administrativo e limitá-la a leitura (Playbook P-05, P-02, P-07; CT-02).

### [CRITICAL] F-006 · SEC-07 Dados sensíveis expostos em respostas
File: controllers.py:285-289; models.py:83, 99
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-200, CWE-201 / A02:2021
Evidência: `"secret_key": "minha-chav***"` · `"senha": row["senha"],`
Description: `GET /health` devolve `secret_key`, `db_path` e `debug`; `GET /usuarios` e `GET /usuarios/<id>` devolvem a coluna `senha` de todos os usuários.
Impact: qualquer cliente anônimo obtém a chave secreta e as senhas (texto puro) de todos os usuários, inclusive do admin.
Recommendation: serializar apenas campos públicos e remover segredos do health (Playbook P-04; CT-03, CT-04).

### [CRITICAL] F-007 · SEC-06 Armazenamento inseguro de senha
File: database.py:31, 76-78; models.py:105-111, 122-131
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-256, CWE-916 / A02:2021
Evidência: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
Description: a senha é gravada exatamente como recebida (`INSERT ... senha`) e o login compara a senha em texto puro dentro do SQL.
Impact: vazamento do banco (ou de F-005/F-006) expõe todas as senhas utilizáveis diretamente.
Recommendation: hash com KDF salgado (ex.: `werkzeug.security`, já instalado com o Flask) e verificação por `check_password_hash`; migração do legado no login (Playbook P-03).

### [CRITICAL] F-008 · SEC-01 SQL Injection
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-161, 163-166, 174, 188, 192, 220, 224, 279-281, 289-297
Ocorrências: 19 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-89 / A03:2021
Evidência: `"UPDATE pedidos SET status = '" + novo_status + "' WHERE id = " + str(pedido_id)` · `query += " AND categoria = '" + categoria + "'"`
Description: todas as consultas de `models.py` são montadas por concatenação com valores vindos de body/query (`nome`, `descricao`, `categoria`, `email`, `senha`, `termo`, `usuario_id`, `produto_id`, `quantidade`). Rastreado até `request.get_json()` / `request.args` em controllers.py (ex.: `termo` ← `q`, controllers.py:113-123; `email`/`senha` ← controllers.py:169-176).
Impact: `POST /login` com `' OR '1'='1' --` autentica como qualquer usuário; `GET /produtos/busca?q=` permite extrair o banco; escrita arbitrária via `POST /produtos`.
Recommendation: placeholders `?` com parâmetros em todas as consultas (Playbook P-02).

### [CRITICAL] F-009 · ARC-01 God File / monólito sem camadas
File: app.py:1-88; database.py:7-86; models.py:1-314
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `def criar_pedido(usuario_id, itens):` (models.py:133, regra de estoque/total + SQL + commit) · `def get_db():` cria conexão, schema e seed (database.py:7-86)
Description: app.py = entrypoint + config + rotas + acesso a dados (admin); database.py = config + conexão + DDL + seed; models.py = acesso a dados + regra de negócio (total, estoque, desconto do relatório) + serialização para 4 domínios (~314 linhas). controllers.py acumula controller + regras + SQL direto (health).
Impact: nada é testável isoladamente; qualquer mudança de regra toca SQL e HTTP.
Recommendation: separar em config/routes/controllers/services/models por domínio com app factory (Playbook P-08, P-09, P-13).

### [HIGH] F-010 · SEC-12 Validação de entrada ausente ou frágil
File: controllers.py:37-50, 81-90, 119-121, 148-160, 169-171, 195-203, 239-242; models.py:139-146; app.py:61-62
Ocorrências: 8 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-20 / A03:2021
Evidência: `if produto["estoque"] < item["quantidade"]:` (models.py:144) · `dados = request.get_json()` seguido de `dados.get(...)` (controllers.py:169-170)
Description: `quantidade` negativa/zero e `produto_id`/`usuario_id` sem tipo ou existência passam; `quantidade = -5` passa a checagem de estoque, reduz o `total` e *aumenta* o estoque (`estoque - (-5)`). `preco`/`estoque` sem checagem de tipo (string → TypeError → 500); `atualizar_produto` não valida nome/categoria (diferente de `criar_produto`); `float(preco_min)` sem tratamento; corpo `None` em login, status e `/admin/query` → `AttributeError` 500.
Impact: manipulação de total e estoque (regra financeira), 500 em entradas malformadas.
Recommendation: validar presença, tipo, faixa e existência antes do efeito, reaproveitando as mesmas regras em criar/atualizar (Playbook P-07; CT-06).

### [HIGH] F-011 · SEC-08 Dados sensíveis em logs
File: controllers.py:161, 179, 182
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-532 / A09:2021
Evidência: `print("Login falhou: " + email)`
Description: e-mails (PII) de cadastro e de tentativas de login são impressos em stdout sem mascaramento. Senhas não são logadas (verificado).
Impact: PII em logs de produção; facilita enumeração de contas.
Recommendation: `logging` com identificador não sensível ou e-mail mascarado (Playbook P-15).

### [HIGH] F-012 · SEC-15 Fluxo crítico sem transação / condição de corrida
File: models.py:133-169
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-362 / A04:2021
Evidência: `cursor.execute("SELECT * FROM produtos WHERE id = " ...)` (loop de checagem) seguido de `UPDATE produtos SET estoque = estoque - ...` (loop de escrita) e um único `db.commit()`
Description: checagem de estoque e baixa em passos separados, sem `BEGIN`/rollback explícito. Como a conexão é global compartilhada (F-015), uma exceção no meio deixa `INSERT`s pendentes que serão confirmados pelo próximo `commit()` de qualquer outra requisição; duas requisições simultâneas podem vender o mesmo estoque.
Impact: estoque negativo, pedidos parciais e inconsistência persistida.
Recommendation: transação única com rollback e baixa condicional atômica (`UPDATE ... WHERE estoque >= ?`) (Playbook P-10).

### [HIGH] F-013 · ARC-04 Acoplamento forte sem injeção de dependência
File: app.py:4, 49, 66; controllers.py:3, 266; models.py:5, 25, 44, 55, 66, 73, 90, 106, 123, 134, 172, 204, 236, 276, 286
Ocorrências: 18 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `from database import get_db` · `db = get_db()` (15 funções de models.py)
Description: cada função de models, e até controllers/app, obtém a infraestrutura chamando `get_db()` global em vez de recebê-la.
Impact: impossível testar com banco em memória/mocks; acoplamento transversal.
Recommendation: conexão por requisição fornecida pela camada de dados/composition root (Playbook P-13, P-08).

### [HIGH] F-014 · ARC-02 Lógica de negócio e persistência em controller/rota
File: app.py:47-78; controllers.py:52-54, 208-210, 242, 247-250, 264-292
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `categorias_validas = ["informatica", "moveis", ...]` (controllers.py:52) · `cursor.execute("SELECT COUNT(*) FROM produtos")` em `health_check` (controllers.py:269)
Description: handlers com regra de domínio (categorias e status válidos), orquestração de notificações, e SQL direto (`reset_database`, `executar_query`, `health_check`).
Impact: regras duplicadas e não testáveis sem HTTP.
Recommendation: handlers finos; regra em `services/`, SQL em `models/` (Playbook P-09).

### [HIGH] F-015 · ARC-03 Estado global mutável / conexão única global
File: database.py:4, 8-11
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `global db_connection` · `sqlite3.connect(db_path, check_same_thread=False)`
Description: uma única conexão SQLite compartilhada por todas as threads do servidor, com verificação de thread desativada.
Impact: corrida entre requisições, commits cruzados (ver F-012).
Recommendation: conexão por requisição com fechamento no teardown (Playbook P-13).

### [MEDIUM] F-016 · SEC-17 Falta de proteções HTTP básicas
File: app.py:9; controllers.py:167
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-770, CWE-693 / A05:2021
Evidência: `CORS(app)`
Description: CORS liberado para qualquer origem, sem limitação de taxa em `/login` e sem cabeçalhos de segurança (nenhum `flask-limiter`/`talisman` registrado).
Impact: força bruta de credenciais sem freio; qualquer site pode chamar a API a partir do navegador do usuário.
Recommendation: CORS por lista de origens de ambiente, cabeçalhos de segurança e limite de tentativas no login (Playbook P-19).

### [MEDIUM] F-017 · SEC-13 Vazamento de detalhes internos em erros
File: app.py:78; controllers.py:12, 22, 62, 96, 109, 126, 134, 144, 165, 186, 220, 227, 235, 255, 262, 292
Ocorrências: 17 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-209 / A05:2021
Evidência: `return jsonify({"erro": str(e)}), 500`
Description: o texto da exceção (SQL, nomes de colunas, caminhos) vai para o corpo da resposta; não há handler central.
Impact: facilita explorar F-008 (erros de SQL ecoados ao atacante).
Recommendation: mensagem genérica ao cliente e detalhe apenas no log (Playbook P-06).

### [MEDIUM] F-018 · SEC-16 Dependências vulneráveis, antigas ou não usadas
File: requirements.txt:1-2
Ocorrências: 2 · Confiança: SUSPECTED · Categoria: Segurança
CWE/OWASP: CWE-1104 / A06:2021
Evidência: `flask-cors==5.0.1`
Description: ambas as dependências são importadas (app.py:1-2) e fixadas, mas sem lockfile (dependências transitivas como Werkzeug não são fixadas). Por conhecimento não verificado nesta sessão, versões 5.x do `flask-cors` teriam avisos de segurança corrigidos em 6.x; falta confirmar em nota de versão/`pip-audit`.
Impact: possível exposição a CVEs de CORS; builds não reprodutíveis.
Recommendation: executar `pip-audit` (classe C, ver K-05) e avaliar atualização (Playbook P-18; recomendação manual, sem C-xx).

### [MEDIUM] F-019 · ARC-09 Tratamento de erro ruim
File: controllers.py:10-12, 20, 70, 103, 142, 183; app.py:77-78
Ocorrências: 17 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `except Exception as e:` repetido nos 16 handlers
Description: `try/except Exception` copiado em todos os handlers, sem handler central; respostas de erro inconsistentes (`"sucesso": False` presente em controllers.py:20 e 183, ausente em 70, 103, 142).
Impact: formato de erro imprevisível; código repetido.
Recommendation: `errorhandler` central e formato de erro único (Playbook P-06).

### [MEDIUM] F-020 · ARC-08 Código duplicado
File: controllers.py:30-50, 74-90; models.py:12-21, 31-40, 79-86, 95-102, 178-199, 211-231, 304-313
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: serialização `{"id": row["id"], "nome": row["nome"], ...}` repetida 3× para produtos
Description: serialização de produto 3×, de usuário 2×, montagem de pedido+itens 2× (~22 linhas idênticas), validação de produto criar/atualizar.
Impact: correções aplicadas em um ponto e esquecidas em outro.
Recommendation: serializadores e validadores únicos (Playbook P-16).

### [MEDIUM] F-021 · ARC-10 Integridade referencial ausente
File: database.py:14-53; models.py:65-70; controllers.py:146-165
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `usuario_id INTEGER,` / `pedido_id INTEGER,` sem `FOREIGN KEY`; `email TEXT,` sem `UNIQUE`
Description: schema sem FK, UNIQUE (e-mail duplicável) ou NOT NULL; `deletar_produto` deixa `itens_pedido` órfãos (o código já compensa com `"Desconhecido"`, models.py:196, 228); `PRAGMA foreign_keys` nunca ativado.
Impact: dados órfãos e contas duplicadas.
Recommendation: constraints no schema para bancos novos e tratamento de conflito (Playbook P-10; CT-08). `CREATE TABLE IF NOT EXISTS` não altera o `loja.db` já existente.

### [MEDIUM] F-022 · ARC-12 Dinheiro em ponto flutuante
File: database.py:19, 41, 51; models.py:146
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `preco REAL,` · `total = total + (produto["preco"] * item["quantidade"])`
Description: preço, total e preço unitário em `REAL`/`float`; totais somados em float.
Impact: erros de arredondamento acumulados em totais e relatório.
Recommendation: cálculo monetário com `Decimal`/centavos mantendo a saída JSON atual (Playbook P-17).

### [MEDIUM] F-023 · ARC-11 Sem paginação / carga total / SELECT *
File: models.py:7, 75, 206, 239-254, 289; controllers.py:268-275
Ocorrências: 6 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `cursor.execute("SELECT * FROM produtos")`
Description: listagens carregam a tabela inteira com `SELECT *`; `relatorio_vendas` faz 5 consultas e `health_check` 4 `COUNT` onde uma agregação resolveria.
Impact: custo cresce linearmente com os dados; consultas extras por requisição.
Recommendation: colunas explícitas e agregação única (Playbook P-11). Paginação mudaria o contrato e não é proposta.

### [MEDIUM] F-024 · ARC-07 Queries N+1
File: models.py:188, 192, 220, 224
Ocorrências: 4 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))`
Description: `get_pedidos_usuario` e `get_todos_pedidos` executam uma consulta de itens por pedido e uma de produto por item.
Impact: 1 + P + I consultas por listagem de pedidos.
Recommendation: `JOIN` único e agrupamento em memória (Playbook P-11).

### [MEDIUM] F-025 · OUTRO-01 Cancelamento de pedido não devolve estoque; status sem checagem de existência
File: controllers.py:247-250; models.py:275-283
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Outro
CWE/OWASP: n/a
Evidência: `print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " cancelado. Devolver estoque.")`
Description: ao cancelar, o código só imprime "Devolver estoque"; `atualizar_status_pedido` apenas faz `UPDATE` e `PUT /pedidos/<id>/status` devolve 200 mesmo para pedido inexistente.
Impact: estoque nunca retorna após cancelamento; falsos sucessos.
Recommendation: reposição de estoque na mesma transação e 404 para pedido inexistente (sem `P-xx` dedicado; relacionado a P-10; CT-07).

### [LOW] F-026 · TST-02 Instruções de execução/validação incompletas
File: README.md:5-12
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Testes
CWE/OWASP: n/a
Evidência: README documenta apenas `pip install -r requirements.txt` e `python app.py`
Description: não há seção de testes, nem CI, Makefile ou scripts; `tests/`, `pytest.ini` e `requirements-dev.txt` existem mas não estão versionados (`git status` mostra `??`).
Impact: quem clona o repositório não recebe a suíte nem sabe executá-la.
Recommendation: documentar `pip install -r requirements-dev.txt` e `python -m pytest` e versionar os testes (recomendação manual).

### [LOW] F-027 · QLT-04 print no lugar de logger
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Ocorrências: 19 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado ...")`
Description: `print` como log e como "notificação" simulada (e-mail/SMS/push).
Impact: sem níveis, formato ou destino configurável.
Recommendation: módulo `logging` (Playbook P-15).

### [LOW] F-028 · QLT-02 Nomes que sombreiam builtins ou pouco descritivos
File: controllers.py:14, 56, 64, 98, 136, 160; models.py:24, 54, 65, 89, 187, 191, 219, 223
Ocorrências: 14 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `def buscar_produto(id):` · `cursor2 = db.cursor()`
Description: parâmetro/variável `id` sombreia o builtin; `cursor2`/`cursor3` sem significado.
Impact: legibilidade.
Recommendation: renomear (`produto_id`, `cursor_itens`…) (Playbook P-16). Parâmetros de rota `<int:id>` exigem manter o nome ou ajustar `add_url_rule` consistentemente.

### [LOW] F-029 · QLT-01 Magic numbers e strings soltas
File: controllers.py:47-50, 52, 242, 285-288; models.py:257-262
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `if faturamento > 10000: desconto = faturamento * 0.1`
Description: faixas de desconto (10000/5000/1000 e 0.1/0.05/0.02), limites de nome (2/200), listas de categorias e status e `"1.0.0"`/`"producao"` literais.
Impact: regra de negócio sem nome nem ponto único de mudança.
Recommendation: constantes nomeadas (Playbook P-16).

### [LOW] F-030 · QLT-05 Estilo inconsistente / checagens por truthiness
File: controllers.py:118-121, 200; models.py:294-297
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `if not itens or len(itens) == 0:` · `if preco_max:`
Description: condição redundante; `preco_min`/`preco_max` = 0 são tratados como ausentes (`preco_max=0` devolve todos os produtos em vez de só os de preço 0).
Impact: filtro incorreto em caso limite; ruído.
Recommendation: comparar com `None` e simplificar condições (Playbook P-16).

### [LOW] F-031 · QLT-03 Imports mortos
File: database.py:2; models.py:2
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `import os` (database.py) · `import sqlite3` (models.py)
Description: nenhum dos dois é usado no respectivo arquivo (busca por nome em todo o projeto).
Impact: ruído.
Recommendation: remover (Playbook P-16).

DEP: nenhuma encontrada para Python 3.14 / flask==3.1.1 / flask-cors==5.0.1 (sem `before_first_request`, `flask.json.JSONEncoder`, `flask.escape`, `datetime.utcnow`, `imp`, `distutils`; datas de `CURRENT_TIMESTAMP` ficam no SQLite).

## Descartados / falsos positivos
- SEC-10 em controllers.py:153-155 / models.py:122 — descartado: `tipo` não é lido do corpo; o padrão `cliente` é fixo.
- SEC-11 — descartado: não existe identidade de usuário no fluxo; reportado como SEC-09 (F-003).
- SEC-14 em models.py:146 — descartado: o total é calculado no servidor a partir do preço do banco; não há fluxo de pagamento.
- ARC-05 — descartado: código síncrono, sem callbacks.
- ARC-06 em app.py:32-78 — descartado como finding separado: mesmas ocorrências já cobertas por ARC-01 (F-009) e ARC-02 (F-014).
- TST-01 — descartado: existe suíte (tests/test_api.py, 23 testes); não versionada, registrado em F-026.
- TST-03 — descartado: `pytest`/`requests` estão declarados em requirements-dev.txt; Flask/pytest ausentes no Python ativo é questão de ambiente (pré-requisito), não defeito dos testes.

## Mudanças de contrato propostas
| ID | Rota/campo | Mudança | Motivo (Finding) | Alternativa compatível |
|---|---|---|---|---|
| CT-01 | POST /admin/reset-db | exigir token administrativo (sem token → 401/403) | F-004 | manter a rota e proteger por token via variável de ambiente |
| CT-02 | POST /admin/query | remover a rota | F-004, F-005 | manter protegida por token admin e restrita a SELECT parametrizável |
| CT-03 | GET /usuarios, GET /usuarios/<id> | omitir o campo `senha` da resposta | F-006 | — (omitir é a correção compatível) |
| CT-04 | GET /health | omitir `secret_key`, `db_path`, `debug` | F-006 | — (omitir é a correção compatível) |
| CT-05 | GET /relatorios/vendas; POST /login | relatório passa a exigir token admin; `/login` ganha o campo `token` (aditivo) | F-003, F-004 | manter relatório aberto e deixar F-003/F-004 residual para essa rota |
| CT-06 | POST /pedidos, POST /produtos, PUT /produtos/<id>, GET /produtos/busca, POST /login, PUT /pedidos/<id>/status | entradas inválidas (quantidade ≤ 0, tipos errados, corpo ausente, `preco_min` não numérico) passam de 500/aceito para 400 | F-010 | — |
| CT-07 | PUT /pedidos/<id>/status | pedido inexistente → 404; cancelamento passa a devolver o estoque | F-025 | manter só o 404 e registrar a reposição como residual |
| CT-08 | POST /usuarios; DELETE /produtos/<id> | e-mail duplicado e produto referenciado em pedidos passam a retornar 409 | F-021 | manter comportamento atual e deixar F-021 residual |

Obs.: o teste existente `test_relatorio_vendas` chama `/relatorios/vendas` sem token; se CT-05 for aprovada ele exigirá ajuste (pergunta própria antes de editar, `07` seção 4.3).

## Plano de mudanças
Ordem provisória por dependência (a ordem canônica do playbook é confirmada na Fase 3).

| ID | Mudança | Sev. | Resolve | Arquivos | Padrão | Afeta contrato | Depende de |
|---|---|---|---|---|---|---|---|
| C-01 | Módulo de configuração por ambiente (SECRET_KEY, DEBUG=off, HOST=127.0.0.1, PORT, DB_PATH, ADMIN_TOKEN, CORS) | CRITICAL | F-001, F-002 | config.py (novo), app.py, database.py | P-01 | não | — |
| C-02 | Estrutura em camadas: app factory, `routes/`, `controllers/`, `models/` por domínio; `python app.py` preservado | CRITICAL | F-009 | app.py, controllers.py, models.py, database.py → novos módulos | P-08 | não | C-01 |
| C-03 | Conexão por requisição com fechamento no teardown e injeção da conexão nos models | HIGH | F-013, F-015 | database.py, models/* | P-13 | não | C-02 |
| C-04 | Camada de services (pedido, relatório, produtos, usuários) com a regra de negócio; handlers finos | HIGH | F-014, F-009 | controllers/*, services/* (novo) | P-09 | não | C-02, C-03 |
| C-05 | Consultas parametrizadas em todos os models | CRITICAL | F-008 | models/* | P-02 | não | C-02 |
| C-06 | Hash de senha (werkzeug.security) com migração do legado no login | CRITICAL | F-007 | services/usuarios, models/usuarios, database.py | P-03 | não | C-05 |
| C-07 | Serialização sem campos sensíveis (`senha`, `secret_key`, `db_path`, `debug`) | CRITICAL | F-006 | models/usuarios, controllers/health | P-04 | CT-03, CT-04 | C-02 |
| C-08 | Autenticação por token e autorização por perfil nas rotas admin/relatório; remoção de `/admin/query` | CRITICAL | F-003, F-004, F-005 | middlewares/auth (novo), routes/*, controllers/* | P-05 | CT-01, CT-02, CT-05 | C-01, C-06 |
| C-09 | Validação de entrada (tipo, faixa, existência, corpo ausente) compartilhada entre criar/atualizar | HIGH | F-010 | controllers/*, services/* | P-07 | CT-06 | C-04 |
| C-10 | Transação atômica e baixa condicional de estoque em `criar_pedido`; constraints de schema e `PRAGMA foreign_keys` | HIGH | F-012, F-021 | services/pedidos, models/pedidos, database.py | P-10 | CT-08 | C-03, C-05 |
| C-11 | Handler central de erros, sem `str(e)` ao cliente, formato de erro único | MEDIUM | F-017, F-019 | app.py, controllers/* | P-06 | não | C-02 |
| C-12 | Consultas com colunas explícitas, JOIN para pedidos/itens e agregação única no relatório/health | MEDIUM | F-023, F-024 | models/* | P-11 | não | C-05 |
| C-13 | `logging` no lugar de `print`, sem PII | HIGH | F-011, F-027 | todos os módulos | P-15 | não | C-02 |
| C-14 | Serializadores únicos, constantes nomeadas, renomear `id`/`cursor2`, remover imports mortos, corrigir truthiness | MEDIUM | F-020, F-028, F-029, F-030, F-031 | todos os módulos | P-16 | não | C-02 |
| C-15 | Cálculo monetário com Decimal/arredondamento (schema REAL mantido por compatibilidade com `loja.db`) | MEDIUM | F-022 | services/pedidos, services/relatorios | P-17 | não | C-04 |
| C-16 | Cabeçalhos de segurança, CORS por lista de origens do ambiente e limite de tentativas em `/login` (sem nova dependência) | MEDIUM | F-016 | app.py, middlewares | P-19 | não | C-01, C-08 |
| C-17 | Reposição de estoque ao cancelar e 404 para pedido inexistente | MEDIUM | F-025 | services/pedidos, models/pedidos | P-10 | CT-07 | C-10 |

Recomendações manuais (sem C-xx): F-018 (executar `pip-audit` e avaliar atualização de flask-cors; K-05) e F-026 (documentar e versionar a suíte de testes).
Riscos conhecidos: as senhas de seed (F-001) permanecem no fonte porque os testes existentes fazem login com `admin@loja.com`; F-003 só é resolvido nas rotas admin/financeiras (demais rotas permanecem públicas — exige decisão de produto).

## Plano de comandos
| ID | Comando | Finalidade | Origem | Classe | Efeitos colaterais |
|---|---|---|---|---|---|
| K-00 | `git switch -c refactor-arch/code-smells-20261105-145811` | checkpoint (branch, sem commit); reversão de arquivos versionados por `git checkout`/`git restore` seguro | 07 §2.2 | C | cria branch local |
| K-01 | `python -m venv .venv` | ambiente isolado para dependências (Flask/pytest ausentes no Python ativo) | 07 §2.2 | C | cria `.venv` na pasta do projeto |
| K-02 | `.venv\Scripts\python -m pip install -r requirements-dev.txt` | instalar flask, flask-cors, pytest, requests | requirements-dev.txt:1-3; README.md:8 | C | rede; escreve em `.venv` |
| K-03 | `.venv\Scripts\python -m py_compile app.py controllers.py database.py models.py` (e equivalente nos novos módulos) | V5 compila/importa (baseline e após cada bloco) | toolchain Python | B | escreve `__pycache__` |
| K-04 | `.venv\Scripts\python -m pytest` | V1: baseline e validação final (mesmo comando) | pytest.ini:1-3; tests/conftest.py:66-100 | B | sobe `python app.py` em cópia temporária na porta 5000; não toca `loja.db` real |
| K-05 | `.venv\Scripts\python -m pip install pip-audit` + `pip-audit -r requirements.txt` (opcional) | avaliar F-018 | catálogo SEC-16 | C | rede; só mediante aprovação |
| K-06 | `taskkill /F /T /PID <pid>` (apenas processos iniciados pela skill) | limpeza / liberar a porta 5000 | 06 §5 | B | encerra processo próprio |
| — | `POST /admin/reset-db`, `POST /admin/query` | NÃO serão executados (rotas administrativas/destrutivas) | app.py:47-78 | D | apagam/alteram dados; exigem pergunta individual |

Lido e classificado: `python app.py` (README.md:9) cria/semeia só se `produtos` estiver vazia (database.py:56-57), sem apagar; é coberto por K-04, então não há boot manual separado.

## Plano de validação
| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim (precisa de pré-requisitos) | `python -m pytest` (pytest.ini:1-3, B) | 23 testes de integração caixa-preta via HTTP (`requests`) em tests/test_api.py; fixture copia o projeto para diretório temporário, sobe `python app.py` e aguarda `/health` (conftest.py:72-96); aborta se a porta 5000 estiver ocupada (conftest.py:68-70) |
| V2 Script de verificação | não | — | sem Makefile, scripts, lint nem CI |
| V3 Boot + requisições existentes | não (coleção) | boot `python app.py` (README.md:9) | sem `.http`/Postman/`curl` no projeto; rotas cobertas via V1 |
| V4 Sondagem ad hoc | não aplicável | — | testes automatizados cobrem as rotas; P4 não será perguntada |
| V5 Estático | sim | `python -m py_compile …` (B) | — |
| Pré-requisitos | ausentes | K-01, K-02 (C) | `python -m pip show flask flask-cors pytest` → não encontrados no Python 3.14.0 ativo; `requests` 2.32.5 presente |
| Não exercitável | — | POST /admin/reset-db, POST /admin/query (D); asserções de ausência de `senha`/`secret_key`, quantidade negativa e erros 500 | V1 cobre 17 das 19 rotas (todas exceto as duas /admin) sem asserções sobre os pontos acima |

Teste e contrato: `test_relatorio_vendas` (tests/test_api.py:240-247) quebrará se CT-05 for aprovada (sem token). `test_health`, `test_login_sucesso` e demais permanecem compatíveis com CT-03, CT-04 e o campo aditivo `token`.

## Decisões do usuário
- P1 Escopo: "Sim, aplicar todas as mudanças do plano" (C-01 a C-17)
- P2 Modo de comandos: "Equilibrado (recomendado)"
- P3 Contrato: "Aprovar todas" (CT-01 a CT-08)
- P4 Sondagem ad hoc: não aplicável (há testes automatizados cobrindo as rotas)

================================
Total: 31 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---
# ANEXO — FASE 3 (Run id: 20261105-145811)

## Decisões do usuário (registro)
- Escopo: todas (C-01 a C-17)
- Modo de comandos: Equilibrado (lote C aprovado: "Executar todos" — K-00, K-01, K-02)
- Contrato: aprovadas CT-01 a CT-08
- Sondagem ad hoc: não aplicável
- Teste afetado por CT-05 (`test_relatorio_vendas`): "Editar o teste" (única alteração em teste, listada abaixo)

## Estrutura DEPOIS
```
code-smells-project/
├── app.py                     composition root (create_app + __main__)
├── constants.py · errors.py · serializers.py · validators.py
├── config/        settings.py · logging_config.py
├── database/      connection.py (conexão por requisição) · schema.py (DDL + seed)
├── models/        produto_model · usuario_model · pedido_model · sistema_model
├── services/      produto · usuario · pedido · relatorio · sistema · notificacao · container
├── controllers/   produto · usuario · pedido · relatorio · sistema
├── routes/        produto_routes · usuario_routes · pedido_routes · relatorio_routes · sistema_routes
├── middlewares/   auth · error_handler · security
├── .env.example · requirements.txt · README.md
```

| Métrica | ANTES | DEPOIS |
|---|---|---|
| Arquivos-fonte | 4 | 40 (7 deles `__init__.py`, 6 vazios) |
| Linhas de código (aprox.) | 780 | 1270 (`wc -l` nos .py fora de tests/.venv/.claude) |
| Camadas presentes | entrypoint, config inline, rotas, controllers, models+services misturados | config, database, models, services, controllers, routes, middlewares, serializers/validators, entrypoint |
| Maior arquivo | models.py (314) | validators.py (140) |
| Arquivos com 3+ papéis | 4 | 0 |

### Mapa antigo → novo
| Arquivo original | Destino(s) |
|---|---|
| app.py | app.py (composition root), config/settings.py, routes/*, controllers/sistema_controller.py, middlewares/security.py |
| controllers.py | controllers/*_controller.py, validators.py, serializers.py, services/notificacao_service.py |
| models.py | models/{produto,usuario,pedido,sistema}_model.py, services/{produto,usuario,pedido,relatorio}_service.py |
| database.py | database/connection.py, database/schema.py |
| (novo) | constants.py, errors.py, middlewares/{auth,error_handler}.py, services/container.py, config/logging_config.py, .env.example |

## Mudanças aplicadas
| ID | Status | Observação |
|---|---|---|
| C-01 | aplicada | config/settings.py: `SECRET_KEY`, `APP_DEBUG` (padrão off), `APP_HOST` (padrão 127.0.0.1), `DB_PATH` etc. por ambiente; `.env.example`. Sem `SECRET_KEY` usa chave efêmera aleatória com aviso (sem literal). `ADMIN_TOKEN` não foi criado: o token vem do `/login` (perfil admin). |
| C-02 | aplicada | app factory `create_app()`, camadas por domínio; `python app.py` preservado. |
| C-03 | aplicada | conexão por requisição (`flask.g` + teardown); `check_same_thread=False` e `global` removidos; services recebem o provedor da conexão (`Services(get_db)`). |
| C-04 | aplicada | regras (estoque, total, desconto, cancelamento) em `services/`; controllers sem SQL. |
| C-05 | aplicada | todas as consultas parametrizadas (`?`); busca com `LIKE ?`. |
| C-06 | aplicada | `werkzeug.security` (scrypt) em novos cadastros e no seed; senha legada em texto puro é verificada e regravada como hash no login. |
| C-07 | aplicada | `senha` removida de `/usuarios*`; `secret_key`/`db_path`/`debug` removidos de `/health` (CT-03, CT-04). |
| C-08 | aplicada | token Bearer assinado (itsdangerous, emitido em `/login`, campo `token`); `/admin/reset-db` e `/relatorios/vendas` exigem perfil admin; `/admin/query` removida (CT-01, CT-02, CT-05). |
| C-09 | aplicada | `validators.py` (tipos, faixas, corpo ausente, quantidade ≤ 0, existência de usuário/produto); mesmas regras em criar/atualizar produto (CT-06). |
| C-10 | aplicada | transação com rollback; baixa de estoque atômica (`UPDATE … WHERE estoque >= ?`); FK/UNIQUE/NOT NULL no DDL de bancos novos; `PRAGMA foreign_keys=ON`; 409 para e-mail duplicado e produto com pedidos (CT-08). |
| C-11 | aplicada | `AppError` + `errorhandler` central; sem `str(e)` ao cliente; erros HTTP do Flask (404/405) mantidos; erros com `"sucesso": false`. |
| C-12 | aplicada | pedidos+itens em um `JOIN`; relatório e health em uma consulta cada; colunas explícitas (sem `SELECT *`). |
| C-13 | aplicada | `logging` com e-mail mascarado (`admi***`); nenhum `print`. |
| C-14 | aplicada | serializadores únicos, constantes nomeadas, `id`/`cursor2` renomeados, imports mortos removidos (verificação AST: 0), `preco_min/max` comparados a `None`. |
| C-15 | aplicada | total e relatório com `Decimal` + `ROUND_HALF_UP`; coluna `REAL` mantida (migração de schema é classe D). |
| C-16 | aplicada | cabeçalhos de segurança (`after_request`), CORS por `CORS_ORIGINS` (padrão `*` preservado), limite de 10 tentativas/60 s por origem em `/login` (em memória, por processo). |
| C-17 | aplicada | cancelar devolve estoque na mesma transação (uma vez); pedido inexistente → 404 (CT-07). |

## Evidências de execução
Pasta: `reports/evidence/project-1/20261105-145811/`

### E-01 · Compilação dos módulos originais (baseline)
Comando: `.venv\Scripts\python -m py_compile app.py controllers.py database.py models.py` · Diretório: code-smells-project
Origem: K-03 · Classe B · Autorização: automática (classe B)
Fim: 2026-11-05T15:12:18-03:00 · Exit code: 0 · Ambiente: Python 3.14.0
Resultado: sem erros · Bruto: `E-01-compile-baseline.log`

### E-02 · pytest (baseline, código original)
Comando: `.venv\Scripts\python -m pytest` · Diretório: code-smells-project
Origem: K-04 · pytest.ini:1-3 · Classe B · Autorização: automática (classe B)
Início/Fim: 2026-11-05T15:12:18 → 15:12:23 (-03:00) · Exit code: 0 · Ambiente: Python 3.14.0, pytest 9.2.0, Flask 3.1.1
Resultado: passed 23 | failed 0 | skipped 0 (`23 passed in 4.16s`) · Bruto: `E-02-pytest-baseline.log`
Integridade: testes alterados: 0

### E-03 · Compilação dos módulos novos (após refatoração)
Comando: `.venv\Scripts\python -m py_compile <40 arquivos .py do código-fonte>` · Classe B · automática
Fim: 2026-11-05T15:21:27-03:00 · Exit code: 0 · Resultado: sem erros · Bruto: `E-03-compile-apos.log`

### E-04 · pytest após a refatoração, antes de ajustar o teste de CT-05
Comando: `.venv\Scripts\python -m pytest` · Classe B · automática · Início: 2026-11-05T15:17:24-03:00 · Exit code: 1
Resultado: passed 22 | failed 1 | skipped 0 — falha: `test_relatorio_vendas` (`assert 401 == 200`), consequência esperada de CT-05 · Bruto: `E-04-pytest-apos-1.log`

### E-05 · pytest final (mesmo comando do baseline)
Comando: `.venv\Scripts\python -m pytest` · Classe B · automática · Início/Fim: 2026-11-05T15:21:27 → 15:21:32 (-03:00) · Exit code: 0
Saída (resumo): `collected 23 items` · `tests\test_api.py .......................  [100%]` · `23 passed in 4.11s`
Resultado: passed 23 | failed 0 | skipped 0 (baseline E-02: 23/0/0) · Bruto: `E-05-pytest-final.log`
Integridade: testes alterados pela skill: 1 (aprovado) — ver abaixo. Nº de testes 23 → 23; skipped 0 → 0.

### E-06 · Rotas registradas após a refatoração
Comando: `DB_PATH=<scratchpad>/rotas.db python -c "from app import app; … url_map …"` · Classe B · automática (banco temporário; `loja.db` não tocado)
Resultado: 18 rotas (19 originais − `POST /admin/query`) · Bruto: `E-06-rotas-apos.log`

**Alteração de teste (aprovada pelo usuário, CT-05):** `tests/test_api.py::test_relatorio_vendas` passou a fazer `POST /login` com o admin do seed e a enviar `Authorization: Bearer <token>` em `GET /relatorios/vendas`; as asserções (status 200 e as 8 chaves) não mudaram. Os testes não são versionados (`git status`: `?? tests/`), então a integridade foi verificada pela edição única acima, não por `git diff`.

Processos: o pytest sobe e encerra o servidor por conta própria; após as execuções, `netstat` mostrou a porta 5000 apenas em `TIME_WAIT` (sem `LISTENING`).

### Comparação antes/depois (rotas)
Cobertura: baseline e validação usam os mesmos 23 testes (17 das 19 rotas); status/chaves verificados pelas asserções. Não cobertas: `/admin/reset-db` (classe D, não executada) e `/admin/query`.

| Método | Rota | ANTES | DEPOIS | Resultado |
|---|---|---|---|---|
| GET | / | 200 (teste) | 200 (teste) | igual |
| GET | /health | 200 com `secret_key`, `db_path`, `debug` | 200 sem esses campos | ALTERADO (aprovado CT-04) |
| GET/POST/PUT/DELETE | /produtos, /produtos/busca, /produtos/<id> | testes passando | testes passando | igual (entradas inválidas: 500/aceito → 400, CT-06) |
| GET | /usuarios, /usuarios/<id> | 200 com `senha` | 200 sem `senha` | ALTERADO (aprovado CT-03) |
| POST | /usuarios | 201 | 201 (e-mail duplicado → 409, CT-08) | igual / ALTERADO (aprovado) |
| POST | /login | 200 `dados` | 200 `dados` + `token` | ALTERADO (aprovado CT-05, aditivo) |
| POST/GET | /pedidos, /pedidos/usuario/<id> | testes passando | testes passando | igual (quantidade ≤ 0 e usuário inexistente → 400, CT-06) |
| PUT | /pedidos/<id>/status | 200 | 200 (inexistente → 404; cancelar devolve estoque, CT-07) | igual / ALTERADO (aprovado) |
| GET | /relatorios/vendas | 200 | 200 com token admin; sem token → 401 | ALTERADO (aprovado CT-05) |
| POST | /admin/reset-db | 200 sem credencial | exige token admin | ALTERADO (aprovado CT-01); NÃO EXERCITADA (destrutiva, classe D) |
| POST | /admin/query | 200 (SQL arbitrário) | removida | ALTERADO (aprovado CT-02); NÃO EXERCITADA |
| DELETE | /produtos/<id> | 200 | 200 (produto com pedidos → 409, CT-08) | igual / ALTERADO (aprovado) |

### Resumo da validação
| Degrau | Comando | Resultado | Evidência |
|---|---|---|---|
| V5 | `py_compile` (originais / novos) | exit 0 / exit 0 | E-01 / E-03 |
| V1 baseline | `python -m pytest` | passed 23 / failed 0 / skipped 0 | E-02 |
| V1 após | `python -m pytest` | passed 23 / failed 0 / skipped 0 (1 teste ajustado, aprovado) | E-05 |
Veredito: VALIDADO (V1) — ressalva: `/admin/reset-db`, `/admin/query` e as asserções de ausência de `senha`/`secret_key`, 401/403, 409 e devolução de estoque não são exercitadas pela suíte existente (sem sondagem ad hoc: P4 não aplicável).

## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python (`.py` em todos os arquivos-fonte; Python 3.14.0 por `python --version`)
- [x] Framework detectado corretamente — Flask 3.1.1: requirements.txt:1, `Flask(__name__)` (app.py original:6), instalado como flask-3.1.1 (K-02)
- [x] Domínio da aplicação descrito corretamente — tabelas `produtos/usuarios/pedidos/itens_pedido` (database.py original:14-53) e rotas de pedidos/relatório
- [x] Número de arquivos analisados condiz com a realidade — 4 (`Glob **/*` da Fase 1 listou apenas app.py, controllers.py, database.py, models.py como fonte da aplicação)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — seções na ordem de `03-template-relatorio.md` §3 (este arquivo)
- [x] Cada finding tem arquivo e linhas exatos — linhas relidas da saída numerada do Read dos 4 arquivos na Fase 2
- [x] Findings ordenados por severidade (CRITICAL → LOW) — F-001…F-031 (9/6/10/6)
- [x] Mínimo de 5 findings identificados — 31
- [x] Detecção de APIs deprecated incluída — "DEP: nenhuma encontrada para Python 3.14 / flask==3.1.1 / flask-cors==5.0.1"
- [x] Skill pausa e pede confirmação antes da Fase 3 — rodada de perguntas (escopo, comandos, contrato) respondida e registrada em "Decisões do usuário"

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — config/, database/, models/, services/, controllers/, routes/, middlewares/, app.py; 0 arquivos com 3+ papéis (ver Estrutura DEPOIS)
- [x] Configuração extraída para módulo de config (sem hardcoded) — config/settings.py; busca por `debug=True|0.0.0.0|SECRET_KEY *=|minha-chave` só retorna leitura de ambiente (app.py:29, config/settings.py:18). Exceção: senhas de seed de desenvolvimento em database/schema.py:70-72
- [x] Models criados para abstrair dados — models/*.py; busca de `execute(` com concatenação retorna só `_SELECT + " WHERE id = ?"` (constante + placeholder)
- [x] Views/Routes separadas para visualização ou roteamento — routes/*.py (mapeamento + decoradores) e serializers.py
- [x] Controllers concentram o fluxo da aplicação — controllers/*.py: validar → service → resposta; sem SQL
- [x] Error handling centralizado — middlewares/error_handler.py; busca por `str(e)` vazia
- [x] Entry point claro — app.py (`create_app` e `python app.py`)
- [x] Aplicação inicia sem erros — E-05 (fixture sobe `python app.py` e aguarda `/health` 200, conftest.py:79-96)
- [x] Endpoints originais respondem corretamente — E-05 (23/23); exceções aprovadas: CT-01…CT-08; não exercitadas: /admin/reset-db, /admin/query (removida)

## Itens residuais (reauditoria)
Varredura do catálogo reaplicada ao código novo (buscas por concatenação em `execute`, `str(e)`, `print(`, segredos/debug fixos, `global`, `get_db`, `id`/`cursor2`, `SELECT *`, imports mortos por AST; E-06 para rotas). Residuais:
- **F-001 (SEC-02, parcial):** senhas de seed de desenvolvimento permanecem no fonte (database/schema.py:70-72), gravadas com hash; mantidas porque os testes fazem login com o admin do seed. O valor antigo de `SECRET_KEY` continua no histórico git (a chave não é mais usada; rotacione se foi reutilizada).
- **F-003 (SEC-09, parcial):** só `/admin/reset-db` e `/relatorios/vendas` exigem token. `GET /usuarios*`, `GET /pedidos*`, `PUT /pedidos/<id>/status`, `POST/PUT/DELETE /produtos*` continuam públicos: exigem decisão de produto (perfis/propriedade) e quebrariam a suíte existente. SEC-11 passa a se aplicar quando houver identidade nessas rotas.
- **F-016 (SEC-17, parcial):** CORS padrão ainda `*` (restringível por `CORS_ORIGINS`); limite de login em memória, por processo.
- **F-018 (SEC-16):** `pip-audit` (K-05) não executado; recomendação manual mantida.
- **F-021 / F-022 (ARC-10 / ARC-12, parciais):** constraints só valem para bancos novos; o `loja.db` existente mantém o schema antigo (migração = classe D). Colunas monetárias seguem `REAL` (cálculo em `Decimal`).
- **F-023 (ARC-11, parcial):** listagens sem paginação (mudaria o contrato); `SELECT *` e consultas redundantes eliminados.
- **F-026 (TST-02):** README não atualizado; `tests/`, `pytest.ini`, `requirements-dev.txt` seguem não versionados.
Demais findings (F-002, F-004…F-015, F-017, F-019, F-020, F-024, F-025, F-027…F-031) sem ocorrências residuais nas buscas. **Não** se declara "No anti-patterns remaining": existem os residuais acima.

## Observações da execução
- Stack detectada e confiança: Python + Flask 3.1.1, alta.
- Dicas específicas usadas × derivadas: dicas do catálogo (Python/Flask/SQLite) em todos os findings; nenhuma `derivado`.
- Nível de organização encontrado e adaptação: `monolito-sem-camadas` → todas as camadas criadas, divididas por domínio.
- Falsos positivos descartados: 7 (SEC-10, SEC-11, SEC-14, ARC-05, ARC-06, TST-01, TST-03).
- Limitações da validação: degrau V1; sem sondagem ad hoc (P4 não aplicável); rotas /admin não exercitadas (classe D); 401/403/409, devolução de estoque ao cancelar, hash de senha e ausência de campos sensíveis não são assertados pela suíte existente.
- Tentativas/iterações: 1 falha após a primeira validação (E-04, esperada por CT-05), resolvida com a edição aprovada do teste; nenhuma reversão. Decisão de design: token assinado emitido pelo `/login` (em vez de `ADMIN_TOKEN` de ambiente), conforme CT-05 aprovada.
- Arquivos criados fora do código-fonte: `.venv/`, `__pycache__/`, `.pytest_cache/` no projeto; branch git `refactor-arch/code-smells-20261105-145811` (sem commit); `reports/evidence/project-1/20261105-145811/`; script temporário de verificação de imports no scratchpad da sessão. Removidos do projeto: controllers.py, models.py, database.py (substituídos pelos pacotes; recuperáveis no commit inicial).
- Nenhum commit/push foi feito. O `loja.db` existente não foi alterado (os testes usam cópia temporária).

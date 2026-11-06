# Relatório — Estado atual de execução e testes dos subprojetos

Data: 2026-11-04
Repositório analisado: raiz deste repositório
Escopo: verificar, em cada subprojeto, (1) se há instruções de execução, (2) se há testes, (3) se a aplicação sobe e responde, e (4) viabilizar uma forma independente de validar se a aplicação continua funcionando após mudanças.

Fora de escopo: issues, qualidade de código e lista de melhorias (já tratados em `RELATORIO-ISSUES.md`).

---

## 1. Ambiente utilizado

| Item | Versão |
|---|---|
| SO | Windows 11 Pro |
| Python | 3.14.0 |
| Node.js | v24.11.1 |
| npm | 11.6.4 |

As dependências Python foram instaladas em *virtualenvs* fora do repositório. O `npm install` foi executado em `ecommerce-api-legacy` (gera `node_modules/`, ignorado pelo `.gitignore`).

---

## 2. Resumo comparativo

| | `code-smells-project` | `ecommerce-api-legacy` | `task-manager-api` |
|---|---|---|---|
| Stack | Python / Flask, `sqlite3` | Node / Express, `sqlite3` | Python / Flask, Flask-SQLAlchemy |
| Descrição | API de E-commerce | LMS API com fluxo de checkout | API de Task Manager |
| Instruções no README | Sim | Sim | Sim |
| Porta | 5000 | 3000 | 5000 |
| Banco | `loja.db` (arquivo, criado no boot, com seeds) | SQLite em memória (seeds no boot) | `instance/tasks.db` (exige `seed.py` antes) |
| Testes automatizados **antes** | Não | Não | Não |
| Arquivo de exemplos de requisição | Não | `api.http` | Não |
| Sobe seguindo o README | Sim | Sim | Sim |

Observação: `code-smells-project` e `task-manager-api` usam a **mesma porta 5000**; não podem ser executados simultaneamente.

---

## 3. Análise por subprojeto

### 3.1 `code-smells-project` (Python/Flask — E-commerce)

**Arquivos:** `app.py`, `controllers.py`, `models.py`, `database.py`, `requirements.txt`, `README.md`.

**Instruções (README):**
```bash
pip install -r requirements.txt
python app.py
```
Sobe em `http://localhost:5000`; `loja.db` é criado no primeiro boot com 10 produtos e 3 usuários.

**Dependências:** `flask==3.1.1`, `flask-cors==5.0.1`.

**Endpoints identificados:**

| Método | Rota |
|---|---|
| GET | `/`, `/health` |
| GET / POST | `/produtos` |
| GET | `/produtos/busca` (`q`, `categoria`, `preco_min`, `preco_max`) |
| GET / PUT / DELETE | `/produtos/<id>` |
| GET / POST | `/usuarios` |
| GET | `/usuarios/<id>` |
| POST | `/login` |
| GET / POST | `/pedidos` |
| GET | `/pedidos/usuario/<usuario_id>` |
| PUT | `/pedidos/<id>/status` |
| GET | `/relatorios/vendas` |
| POST | `/admin/reset-db`, `/admin/query` |

**Dados de seed úteis:** usuário `admin@loja.com` / `admin123`; produto 1 = "Notebook Gamer".

**Testes existentes:** nenhum.

**Verificação manual:** todos os GETs testados retornaram 200; `POST /login`, `POST /pedidos` funcionaram; `POST /produtos` inválido retornou 400.

**Cuidados:** os endpoints `/admin/reset-db` e `/admin/query` são destrutivos — **não foram incluídos** na suíte de testes.

### 3.2 `ecommerce-api-legacy` (Node/Express — LMS API)

**Arquivos:** `src/app.js`, `src/AppManager.js`, `src/utils.js`, `api.http`, `package.json`, `package-lock.json`, `README.md`.

**Instruções (README):**
```bash
npm install
npm start
```
Sobe em `http://localhost:3000`; banco SQLite em memória com seeds no boot.

**Dependências:** `express ^4.18.2`, `sqlite3 ^5.1.6`. Único script original: `start`.

**Endpoints identificados:**

| Método | Rota |
|---|---|
| POST | `/api/checkout` (body: `usr`, `eml`, `pwd`, `c_id`, `card`) |
| GET | `/api/admin/financial-report` |
| DELETE | `/api/users/:id` |

**Dados de seed:** usuário 1 "Leonan" (`leonan@fullcycle.com.br`); cursos 1 "Clean Architecture" (997) e 2 "Docker" (497); uma matrícula paga do Leonan no curso 1.

**Regras observáveis do checkout:** cartão iniciando com `4` = aprovado (200); outros = recusado (400, "Pagamento recusado"); campos obrigatórios ausentes = 400; curso inexistente = 404; e-mail novo cria o usuário.

**Testes existentes:** nenhum (o arquivo `api.http` serve apenas como exemplos manuais).

**Verificação manual:** checkout aprovado (200) e recusado (400), relatório (200) e DELETE (200) funcionaram.

**Cuidados:** a ordem dos cursos no relatório financeiro depende de callbacks assíncronos; por isso os testes ordenam por nome antes de comparar. Como o banco é em memória, o estado reinicia a cada boot, o que favorece testes determinísticos.

### 3.3 `task-manager-api` (Python/Flask — Task Manager)

**Arquivos:** `app.py`, `database.py`, `seed.py`, `models/` (`task`, `user`, `category`), `routes/` (`task_routes`, `user_routes`, `report_routes`), `services/notification_service.py`, `utils/helpers.py`, `requirements.txt`, `README.md`.

**Instruções (README):**
```bash
pip install -r requirements.txt
python seed.py
python app.py
```
Sobe em `http://localhost:5000`. **O `seed.py` deve rodar antes do primeiro boot**, senão as listas retornam vazias. O `seed.py` apaga e recria os dados (3 usuários, 4 categorias, 10 tasks).

**Dependências:** `flask==3.0.0`, `flask-sqlalchemy==3.1.1`, `flask-cors==4.0.0`, `marshmallow==3.20.1`, `requests==2.31.0`, `python-dotenv==1.0.0`.

**Endpoints identificados:**

| Método | Rota |
|---|---|
| GET | `/`, `/health` |
| GET / POST | `/tasks` |
| GET / PUT / DELETE | `/tasks/<id>` |
| GET | `/tasks/search` (`q`, `status`, `priority`, `user_id`), `/tasks/stats` |
| GET / POST | `/users` |
| GET / PUT / DELETE | `/users/<id>` |
| GET | `/users/<id>/tasks` |
| POST | `/login` |
| GET | `/reports/summary`, `/reports/user/<id>` |
| GET / POST | `/categories` |
| PUT / DELETE | `/categories/<id>` |

**Dados de seed úteis:** `joao@email.com` / `1234` (admin), `maria@email.com` / `abcd`, `pedro@email.com` / `pass`.

**Testes existentes:** nenhum. (Um *match* de "test" em `seed.py` é apenas o título de uma task de exemplo.)

**Verificação manual:** todos os 9 GETs testados retornaram 200; `/login`, `POST /tasks` e `POST /users` funcionaram.

---

## 4. Observações operacionais (impactam a execução e os testes)

1. **Porta 5000 compartilhada** entre `code-smells-project` e `task-manager-api`: rodar uma suíte por vez.
2. **Reloader do Flask no Windows:** ambos os apps iniciam com `debug=True`, o que cria um processo filho (reloader). Encerrar apenas o processo pai deixa o filho ativo ocupando a porta. A suíte encerra a árvore de processos (`taskkill /T`).
3. **Codificação:** os apps imprimem caracteres acentuados/símbolos; ao redirecionar a saída no Windows é preciso `PYTHONIOENCODING=utf-8` (a suíte já define).
4. **Arquivos gerados em execução manual:** `loja.db`, `instance/tasks.db`, `__pycache__/` e `node_modules/` — todos cobertos pelo `.gitignore`.
5. **Compatibilidade:** as versões fixadas no `requirements.txt` instalaram e executaram sem problemas em Python 3.14.

---

## 5. Estratégia de testes adotada

**Tipo:** testes de fumaça/caracterização *caixa-preta via HTTP*. Validam o contrato externo atual (rotas, status, campos principais e regras de negócio observáveis), e **não** a estrutura interna. Assim, continuam válidos mesmo que arquivos, classes e camadas sejam reorganizados na refatoração.

**Isolamento e repetibilidade:**
- **Python:** a suíte copia o projeto para um diretório temporário, executa `seed.py` (no `task-manager-api`), sobe `python app.py` e encerra o processo ao final. Os bancos reais do projeto nunca são alterados.
- **Node:** sobe `node src/app.js`; o banco em memória é recriado a cada execução.
- Falham rápido, com mensagem clara, se a porta já estiver em uso ou se a aplicação não subir em 30 s (exibindo o log do servidor).

**Convenção por linguagem:**

| Projeto | Convenção adotada |
|---|---|
| Python | pasta `tests/` + `conftest.py` (fixtures) + `pytest.ini` + `requirements-dev.txt` (dependências de teste separadas das de produção) |
| Node | pasta `test/` + runner nativo `node --test` (sem nova dependência) + script `npm test` em `package.json` |

**Cobertura de cada suíte:**

| Projeto | Testes | Cobertura resumida |
|---|---|---|
| `code-smells-project` | 23 | raiz/health, CRUD e busca de produtos, validações, usuários, login, pedidos (total, baixa de estoque, estoque insuficiente, status), relatório de vendas |
| `task-manager-api` | 25 | raiz/health, login (inclusive usuário inativo), CRUD de usuários/tasks/categorias, validações, `overdue`, busca, estatísticas, relatórios |
| `ecommerce-api-legacy` | 8 | relatório inicial (seeds), checkout (400/404/recusado/sucesso), usuário novo e existente, impacto no relatório, DELETE |

**Resultados obtidos (estado atual, antes de qualquer alteração):**

| Projeto | Resultado | Tempo aprox. |
|---|---|---|
| `code-smells-project` | 23 passed | ~3 s |
| `task-manager-api` | 25 passed | ~5 s |
| `ecommerce-api-legacy` | 8 pass / 0 fail | ~2 s |

Validações adicionais:
- Cada suíte foi executada **duas vezes seguidas** com o mesmo resultado (repetível).
- Após as execuções, nenhuma porta 3000/5000 ficou ocupada (sem processos órfãos).
- **Verificação de sensibilidade:** alterei temporariamente a regra do cartão em `AppManager.js` (`startsWith("4")` → `"5"`); a suíte Node passou a reportar 4 falhas. A alteração foi revertida (`git checkout`).

Limitação: como as suítes descrevem o comportamento **atual**, uma mudança intencional de contrato (por exemplo, trocar formato de resposta ou status) fará testes falharem e exigirá atualização consciente do teste.

---

## 6. Arquivos criados/alterados

| Caminho (relativo ao repositório) | Tipo |
|---|---|
| `code-smells-project/tests/conftest.py` | novo |
| `code-smells-project/tests/test_api.py` | novo |
| `code-smells-project/pytest.ini` | novo |
| `code-smells-project/requirements-dev.txt` | novo |
| `task-manager-api/tests/conftest.py` | novo |
| `task-manager-api/tests/test_api.py` | novo |
| `task-manager-api/pytest.ini` | novo |
| `task-manager-api/requirements-dev.txt` | novo |
| `ecommerce-api-legacy/test/api.test.js` | novo |
| `ecommerce-api-legacy/package.json` | alterado (adicionado `"test": "node --test"`) |

Nenhum código de aplicação foi modificado.

---

## 7. Scripts a executar

Execute **uma suíte por vez** para os dois projetos Python (porta 5000). Todos os comandos partem da raiz do repositório.

### 7.1 Preparação (uma única vez por projeto)

```bash
# code-smells-project
cd code-smells-project
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
cd ..

# task-manager-api
cd task-manager-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
cd ..

# ecommerce-api-legacy
cd ecommerce-api-legacy
npm install
cd ..
```

### 7.2 Execução dos testes

| Projeto | Comando (dentro da pasta do projeto) | Resultado esperado hoje |
|---|---|---|
| `code-smells-project` | `python -m pytest` | 23 passed |
| `task-manager-api` | `python -m pytest` | 25 passed |
| `ecommerce-api-legacy` | `npm test` | 8 pass, 0 fail |

Opções úteis: `python -m pytest -x -q` (parar no primeiro erro, saída curta) e `python -m pytest -k login` (filtrar por nome).

### 7.3 Fluxo recomendado em cada rodada de mudanças

1. **Antes** de alterar: rodar a suíte do projeto e confirmar que está verde (linha de base).
2. Fazer a alteração.
3. **Depois**: rodar novamente a mesma suíte.
4. Se algum teste falhar: verificar se foi regressão (corrigir o código) ou mudança intencional de contrato (atualizar o teste conscientemente).

### 7.4 Execução manual da aplicação (quando necessário)

| Projeto | Comandos | URL |
|---|---|---|
| `code-smells-project` | `pip install -r requirements.txt` → `python app.py` | http://localhost:5000 |
| `task-manager-api` | `pip install -r requirements.txt` → `python seed.py` → `python app.py` | http://localhost:5000 |
| `ecommerce-api-legacy` | `npm install` → `npm start` (exemplos em `api.http`) | http://localhost:3000 |

### 7.5 Se algo falhar ao iniciar a suíte

- **"Porta 5000/3000 já está em uso"**: encerre a aplicação que está rodando manualmente (e, no Windows, o processo filho do reloader do Flask) e rode novamente.
- **Falha de importação (`flask`, `requests`, `pytest`)**: o *virtualenv* do projeto não está ativo ou `requirements-dev.txt` não foi instalado.
- **Timeout aguardando a aplicação**: a mensagem inclui o log do servidor; ele indica o erro de inicialização.

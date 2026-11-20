# Validação do resultado — Projeto 1 (code-smells-project)

- **Data:** 2026-11-16
- **Versão:** v3 — skill 1.2
- **Desafio:** `docs/DESAFIO.md` (seções "Validação" e "Critérios de Aceite")
- **Skill:** `code-smells-project/.claude/skills/refactor-arch/` (SKILL.md + 7 references; versão 1.2 introduzida no commit `20f9e72`)
- **Branch/commit:** `entrega-v2` @ `3e904d3` (refatorado); original `5303107`; checkpoint da execução `f77fadc` (código do projeto idêntico ao de `5303107`, o diff entre os dois só toca a skill)
- **Relatório validado:** `reports/audit-project-1.md` (Run id 20261116-195523)
- **Evidências:** `reports/evidence/project-1/20261116-195523/` (E-00 a E-11 + `tests-before/`)

## Veredito

**APROVADO, com ressalvas não bloqueantes.** Os 4 critérios de aceite e o checklist do desafio foram atendidos, e conferi isso por execução própria. Nenhum CRITICAL/HIGH do relatório continua no código, e as correções têm prova verde no refatorado e vermelha no original. As ressalvas são: um caso de borda de validação (NaN/Infinity ⇒ 500), o README do projeto desatualizado, fragmentos de segredo antigos sem máscara no E-08 e cabeçalhos E-nn heterogêneos.

## Método de verificação

1. **Suíte reexecutada:** `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` em `code-smells-project`, das 21:37:01 às 21:37:12 (-03:00), resultou em **51 passed**, exit 0 (bate com o E-05: 23 originais + 19 de integração + 9 de unidade).
2. **Prova vermelha independente:** copiei o código de `5303107` (`git show`) com os testes atuais para um diretório temporário. `tests/test_seguranca.py` + `tests/test_unidade.py` deram **28 failed / 0 passed** (exit 1), o mesmo que o E-08. O `test_api.py` adaptado, rodado contra o original, deu 17 passed / 6 failed (`KeyError: 'token'`; ver ponto 6).
3. **Execução local própria:** cópia do código refatorado em diretório temporário (sem `.venv`, `tests`, `.claude`, `loja.db`), com banco descartável via `DB_PATH`, `SECRET_KEY` e `SEED_ADMIN_PASSWORD`/`SEED_CLIENTE_PASSWORD` aleatórias (XOIm***, SB3K***). Fiz 21 requisições, das 21:39:43 às 21:39:49:
   - `GET /health` 200, sem `secret_key`/`db_path`/`debug`;
   - `GET /usuarios` sem token ⇒ 401; com token inválido ⇒ 401; com token admin obtido no `POST /login` (eyJp***) ⇒ 200, sem `senha`; com token de cliente ⇒ 403;
   - login com senha errada ⇒ 401; login com SQLi `' OR '1'='1' --` ⇒ 401;
   - `POST /admin/query` com `DELETE FROM produtos`, sem token e com token admin ⇒ **404**; produtos antes/depois = 10/10, ou seja, o SQL não foi executado;
   - `/relatorios/vendas` 401 sem token / 200 admin; `/admin/reset-db` 401 sem token / 403 cliente;
   - `POST /pedidos` com quantidade −3 ⇒ 400; pedido para outro usuário ⇒ 403; `preco: "abc"` ⇒ 400;
   - **bordas exploratórias:** `estoque: Infinity` ⇒ **500** (`OverflowError`); `preco: NaN` ⇒ **500** (`IntegrityError NOT NULL`). Nos dois casos o corpo é genérico (`{"erro":"Erro interno"}`) e nada é persistido;
   - cabeçalhos `X-Content-Type-Options`/`X-Frame-Options` presentes; sem `Access-Control-Allow-Origin` para origem arbitrária; senhas no banco com prefixo `scrypt:` (3/3);
   - log do servidor: `Debug mode: off`, bind `127.0.0.1:5000`, sem `0.0.0.0`, sem e-mail e sem senha.
   - Processo encerrado; porta 5000 livre antes e depois; `loja.db` do projeto com mtime inalterado (2026-11-04T09:30:21).
4. **Referências arquivo:linha:** conferi contra `git show 5303107:...` **todas** as referências dos 31 findings e as 19 linhas da tabela "Superfície de ataque" (mais de 100 referências; exemplos: app.py:7, 8, 88, 47-57, 59-78; controllers.py:161/179/182, 286-289; database.py:4-11, 75-79; models.py:109-111, 139-169, 187-199, 256-262, 289-299). **Nenhuma divergência.** Contagens: 88+292+86+314 = 780 linhas; F-017 = 17 ocorrências; F-027 = 19 ocorrências, ambas conferidas.
5. **Varredura do refatorado** (fora de `tests/`, `.venv`, `.claude`) por `debug=True`, `0.0.0.0`, `str(e)`, segredos/senhas literais do original, `SECRET_KEY = "..."`, `check_same_thread`, `global`, `print(`, `execute(... + ...)`, `+ str(`: **0 ocorrências**. As f-strings em SQL (`COLUNAS`, `TABELAS_EM_ORDEM`, marcadores `?`, `SUM(CASE ...)`) interpolam só constantes internas. `.env` e `*.db` estão no `.gitignore`.
6. **Integridade dos testes:** `tests-before/tests/conftest.py` é idêntico ao de `5303107`. `tests-before/tests/test_api.py` difere só na senha mascarada (admi***). O diff `5303107..3e904d3` de `test_api.py` só acrescenta `headers=`/fixtures; há **67 `assert` antes e 67 depois**, 23 testes nos dois lados e nenhum valor esperado alterado. O `conftest.py` só acrescenta as fixtures `credenciais`, `ambiente_app`, `admin_headers`, `caminho_banco`, `log_servidor` e as variáveis de ambiente, sem mexer na lógica de boot/encerramento.
7. **Leitura do código refatorado:** li integralmente os 28 arquivos com código: app, config, database, models, services, controllers, routes, views e middlewares.

## Critérios de aceite

| Critério | Status | Evidência |
|---|---|---|
| Fase 1 detecta stack corretamente | ✅ | E-00: Python (3.14.0 do .venv) + Flask 3.1.1, flask-cors 5.0.1, SQLite; confere com `requirements.txt` e `app.py:1-6` do original |
| Fase 2 encontra >= 5 findings | ✅ | 31 findings (146 ocorrências); referências conferidas sem divergência |
| Fase 2 inclui >= 1 CRITICAL ou HIGH | ✅ | 9 CRITICAL + 6 HIGH, todos confirmados no código original |
| Fase 3: aplicação funciona após refatoração | ✅ | 51/51 na reexecução própria; boot próprio sem erro (debug off, 127.0.0.1); rotas respondem conforme o contrato aprovado |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente: Python (E-00).
- [x] Framework detectado corretamente: Flask 3.1.1 (E-00; `requirements.txt:1`).
- [x] Domínio descrito corretamente: e-commerce com produtos, usuários/login, pedidos com baixa de estoque e relatório (confere com o código).
- [x] Número de arquivos condiz com a realidade: 4 arquivos-fonte / 780 linhas (recontado: 88+292+86+314).

### Fase 2 — Auditoria
- [x] Relatório segue o template: as seções e a ordem conferem com `03-template-relatorio.md` §3 e §4.
- [x] Cada finding tem arquivo e linhas exatos: todas as referências conferidas, nenhuma divergência.
- [x] Ordenados por severidade: F-001…F-009 CRITICAL, F-010…F-015 HIGH, F-016…F-025 MEDIUM, F-026…F-031 LOW.
- [x] Mínimo de 5 findings: 31.
- [x] APIs deprecated: busca registrada (DEP: nenhuma, com a lista do que foi buscado); concordo, porque não há uso de `datetime.utcnow`, `before_first_request`, `JSONEncoder` nem adaptadores de datetime do sqlite3.
- [x] Pausa e pede confirmação antes da Fase 3: "Decisões do usuário" (P1–P4 = 1A 2A 3A 4A) + linha `Proceed with refactoring (Phase 3)? [y/n]`.

### Fase 3 — Refatoração
- [x] Estrutura MVC: `config/`, `database/`, `models/`, `services/`, `controllers/`, `routes/`, `views/`, `middlewares/`, `app.py` (composition root).
- [x] Configuração extraída sem hardcoded: `config/settings.py` lê tudo do ambiente; `SECRET_KEY` aleatória por processo se ausente; varredura sem literais. A rotação do segredo histórico é ação externa.
- [x] Models abstraem dados: `models/*_model.py`, com consultas sempre parametrizadas; SQL só na camada de dados (conferido por leitura e por `test_f009_f013`).
- [x] Views/Routes separadas: `routes/__init__.py` (blueprints + proteção por rota) e `views/serializers.py` (lista branca).
- [x] Controllers concentram o fluxo: validam, aplicam autorização de propriedade, chamam services e escolhem o status; sem SQL.
- [x] Error handling centralizado: `middlewares/errors.py` (`AppError`, `HTTPException`, `Exception` ⇒ 500 genérico com log). Confirmado em execução: as bordas NaN/Infinity devolvem "Erro interno" sem detalhe.
- [x] Entry point claro: `python app.py` → `create_app(Settings())`.
- [x] Aplicação inicia sem erros: boot próprio + E-07.
- [x] Endpoints originais respondem corretamente: 18 de 19 rotas existem (a `/admin/query` foi removida pela CT-01); as rotas públicas mantêm o mesmo formato; as demais mudaram só por CT-01…CT-12 aprovados (Refatorar), com prova em E-05/E-07/E-08 e confirmação na minha execução.

## Critérios adicionais da versão 1.2

| Item | Status | Evidência |
|---|---|---|
| a. Nenhum CRITICAL/HIGH sem correção (exceto ação externa) | ✅ | Conferido no código: F-001/F-002 (`config/settings.py`, sem literais); F-003/F-004 (`routes/__init__.py` + `middlewares/auth.py`); F-005 (rota inexistente, 404 em execução); F-006 (`views/serializers.py`, health sem segredo); F-007 (scrypt, prefixos no banco); F-008 (`?` em todas as consultas; SQLi ⇒ 401); F-009/F-013 (camadas, DI no `create_app`); F-010 (`controllers/validators.py`; quantidade −3 ⇒ 400); F-011 (log sem e-mail, conferido); F-012 (`BEGIN IMMEDIATE` + `UPDATE ... WHERE estoque >= ?` + rollback); F-014 (services); F-015 (conexão por requisição em `g`). Fica pendente só a rotação da `SECRET_KEY`/senhas antigas do histórico git (externa). Ressalva de borda em F-010 no ponto 1 (não é HIGH). |
| b. P3 com 3 opções na ordem certa e resposta "Refatorar" | ✅ (evidência indireta) | Tabela "Correções que exigem mudança de contrato" com colunas Refatorar · Manter contrato\* · Híbrido; "Resumo para a pergunta": "Manter contrato\*: ficam sem correção 3 CRITICAL e 0 HIGH (F-003, F-004, F-005), exige segunda confirmação" (contagem correta); decisão "P3: Refatorar (recomendado) — (3A)". O texto literal da pergunta não foi gravado (ponto 5). |
| c. Prova por testes de unidade e integração (verde/vermelho) | ✅ | 19 de integração + 9 de unidade cobrem todos os CRITICAL/HIGH e CT-01…12. Verde: 51/51 (reexecução própria). Vermelho: 28/28 no original (reexecução própria, igual ao E-08) + E-09 (F-007 isolado) + E-11 (varredura). Os vermelhos de unidade vêm de `ModuleNotFoundError` (ponto 7). |
| d. Execução local autenticada com credenciais geradas pela aplicação, mascaradas | ✅ | E-03 (baseline, seed versionado do original, admi***) e E-07 (final, `SEED_*`/`SECRET_KEY` aleatórias + token do `/login`, mascarados), com 52 requisições cada; reproduzido por mim (21 requisições). Exceção à máscara no E-08 (ponto 3). |
| e. Evidências no formato E-nn | ⚠️ parcial | E-01, E-02, E-04, E-05, E-08, E-09 e E-11 seguem o cabeçalho completo (comando, diretório, origem, início/fim, exit code, ambiente, resultado, saída). E-03/E-07 não têm título `### E-nn` nem linhas "Exit code"/"Resultado" do comando; E-06 não tem "Fim"; E-00 e E-10 têm cabeçalho mínimo. A linha "Bruto" está nos blocos do relatório (ponto 4). |

## Resumo dos números

| Métrica | Antes | Depois |
|---|---|---|
| Arquivos-fonte (.py, sem tests/.venv/.claude) | 4 | 35 (28 com código + 7 `__init__.py` vazios) |
| Linhas de código | 780 | 1220 |
| Maior arquivo | models.py (314) | controllers/validators.py (121) |
| Arquivos com 3+ papéis | 3 (app.py, controllers.py, models.py) | 0 |
| Rotas | 19 | 18 (`/admin/query` removida — CT-01) |
| Testes | 23 (67 asserts em test_api.py) | 51 (23 originais, ainda com 67 asserts, + 19 integração + 9 unidade) |
| Findings CRITICAL | 9 | 0 |
| Findings HIGH | 6 | 0 |
| Findings MEDIUM | 10 | 4 residuais parciais/manuais (F-018, F-021, F-022, F-023) |
| Findings LOW | 6 | 2 residuais (F-026, OUTRO-02 novo) + borda de validação do ponto 1, não declarada |

## Pontos de atenção

1. **Borda de validação NaN/Infinity (não bloqueante).** O JSON do Python aceita `NaN`/`Infinity`. `POST /produtos` com `estoque: Infinity` dá `OverflowError` e `preco: NaN` dá `IntegrityError`, ambos ⇒ **500** em vez de 400. A resposta é genérica e nada é persistido, a rota exige admin e `quantidade` de pedido não é afetada (exige `int`). É um resíduo parcial de F-010 que a reauditoria não declarou. Correção sugerida: `math.isfinite` em `_numero` (`controllers/validators.py:9-10`). Num `loja.db` legado (sem NOT NULL), um `PUT` com `NaN` pode gravar NULL no preço.
2. **README do projeto desatualizado (não bloqueante).** `code-smells-project/README.md` não mudou e ainda diz que o banco é criado "já com produtos e usuários de exemplo". Sem `SEED_*`, nenhum usuário é semeado e as rotas protegidas ficam inutilizáveis com `python app.py` puro. O `.env.example` manda copiar para `.env`, mas nada carrega `.env` (não há `python-dotenv`). Isso foi declarado em parte (F-026 residual + texto-base no relatório).
3. **Segredo antigo parcialmente sem máscara no E-08 (não bloqueante).** As linhas 99-101 trazem os fragmentos `'...min123'` e `'minha-chave'` do original, fora da regra "4 caracteres + `***`". Esses valores já estão no histórico git e foram marcados para rotação, mas convém mascarar.
4. **Cabeçalhos E-nn heterogêneos (não bloqueante).** Ver critério adicional (e): faltam E-03/E-07 (título, exit code e resultado do comando), E-06 (fim), E-00 e E-10 (cabeçalho mínimo).
5. **P3 sem registro literal da pergunta (não bloqueante).** A ordem e o aviso estão comprovados pela tabela, pelo "Resumo para a pergunta" e pela resposta 3A, mas o texto exibido ao usuário não ficou em evidência.
6. **Classificação T1 dos ajustes de `test_api.py` é discutível (não bloqueante).** Contra o original, 6 dos 23 testes adaptados falham (`KeyError: 'token'`), porque dependem do CT-07. Não houve enfraquecimento: os esperados não mudaram, os asserts continuam 67 e os testes continuam 23.
7. **Sensibilidade dos testes de unidade (não bloqueante).** Os 9 vermelhos de unidade no original vêm de ausência de módulo (`ModuleNotFoundError`), não de asserção. O relatório declara isso; as provas de integração correspondentes falham por asserção.
8. **Checkpoint em `f77fadc` e não em `5303107` (informativo).** Conferi que o código do projeto é idêntico nos dois commits (o diff só toca a skill).

## Residuais declarados pela skill

- **F-001 (ação manual):** rotacionar a `SECRET_KEY` (minh***) e as senhas de seed antigas (admi***, 1234***, senh***) presentes no histórico git; recriar o `loja.db` local, que guarda senhas legadas em texto até o primeiro login de cada usuário.
- **F-018 (MEDIUM):** `pip-audit` e lock das dependências transitivas não executados (exigem rede).
- **F-021 (MEDIUM, parcial):** restrições só valem em bancos novos; `itens_pedido.produto_id` sem FK.
- **F-022 (MEDIUM, parcial):** cálculo em `Decimal`, mas o armazenamento continua `REAL` (migração classe D não aprovada).
- **F-023 (MEDIUM, parcial):** sem `limite`/`offset`, as listagens ainda devolvem a tabela inteira (contrato mantido).
- **F-026 (LOW):** README sem instruções de teste (recomendação manual).
- **OUTRO-02 (LOW, novo):** `LimitadorDeLogin` guarda as chaves de falha em memória sem expurgo periódico.
- Desvios declarados: seed sem senha aleatória quando a variável está ausente; `/admin/reset-db` sem flag de ambiente; `sucesso: false` acrescentado a todas as respostas de erro.

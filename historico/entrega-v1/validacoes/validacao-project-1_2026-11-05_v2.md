# Validação do resultado — Projeto 1 (code-smells-project)

> **Nota:** registro histórico do momento da validação. Itens como "Nada commitado" e "Pendências antes da entrega" já foram resolvidos em `main`.

- Data: 2026-11-05
- Versão: v2
- Desafio: Criação de Skills — Refatoração Arquitetural Automatizada
- Skill: `refactor-arch` 1.1 | Catálogo 1.0 (Claude Code)
- Branch: `code-smells-20261105-v2` (sem commit nem push). A execução da skill criou também `refactor-arch/checkpoint-20261105-175512`; a branch `refactor-arch/code-smells-20261105-145811` informada no pedido existe, mas não é a branch em uso.
- Relatório validado: `reports/audit-project-1.md` (Run id 20261105-175512)
- Evidências: `reports/evidence/project-1/20261105-175512/`

## Veredito

**O projeto 1 atende aos 4 critérios obrigatórios e a todos os itens do checklist.** Há 4 pontos de atenção, nenhum bloqueante. O principal é o item "endpoints originais", por causa das mudanças de contrato aprovadas.

## Método de verificação

- Leitura integral do README do desafio, do `reports/audit-project-1.md` (695 linhas) e do `03-template-relatorio.md`.
- Leitura das evidências `E-00` (Fase 1), `E-01` e `E-03` (pytest), `E-02` e `E-04` (rotas) e `E-05` (prova vermelha).
- Reexecução independente de `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` → **35 passed**.
- Conferência por amostragem de 14 referências de linha contra o commit original (`git show HEAD:...`): `app.py:7/8/88`, `controllers.py:161/264/268/289`, `database.py:2/76/77/78`, `models.py:2/109-111/146/163-164`. Todas conferem.
- Contagem dos arquivos originais: `app.py` 88, `controllers.py` 292, `database.py` 86, `models.py` 314 linhas (4 arquivos-fonte, 780 linhas). `git ls-files` confirma os mesmos 4 `.py` fora de `tests/`.
- Contagem do código novo: 44 arquivos `.py` fora de `tests/`, `.venv` e `.claude` (6 `__init__.py` vazios), somando 1257 linhas. Maior arquivo: `controllers/validacao.py` (134). Confere com o anexo da Fase 3.
- Grep no código refatorado (fora de `tests/`) por `minha-chave`, `admin123`, `debug=True`, `0.0.0.0`, `str(e)`, `print(` e `except Exception`: nenhuma ocorrência real (as únicas correspondências foram `Blueprint(` e `register_blueprint(`, que contêm o trecho `print(`).
- Integridade dos testes: `git status` mostra só `M tests/conftest.py` e `?? tests/test_contratos.py`; `tests/test_api.py` está inalterado.
- A pasta da skill (`.claude/skills/refactor-arch/`, `SKILL.md` + 7 referências) foi listada, mas só o `03-template-relatorio.md` foi lido nesta validação.

## Critérios de aceite

| Critério | Status | Evidência |
|---|---|---|
| Fase 1 detecta a stack corretamente | ✅ | Python 3.14.0 + Flask 3.1.1 (confiança alta) — E-00 |
| Fase 2 encontra >= 5 findings | ✅ | 31 findings |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | ✅ | 9 CRITICAL e 6 HIGH |
| Fase 3: aplicação funciona após a refatoração | ✅ | 35/35 testes (E-03 e reexecução); 18 rotas registradas (E-04) |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python 3.14.0 (runtime do `.venv`).
- [x] Framework detectado corretamente — Flask 3.1.1.
- [x] Domínio descrito corretamente — e-commerce (produtos, usuários/login, pedidos com itens, relatório de vendas).
- [x] Número de arquivos condiz com a realidade — 4 arquivos-fonte e 780 linhas, igual ao repositório.

### Fase 2 — Auditoria
- [x] Relatório segue o template dos arquivos de referência — seções e ordem do `03-template-relatorio.md` §3.
- [x] Cada finding tem arquivo e linhas exatos — amostra de 14 referências conferida contra o código original.
- [x] Findings ordenados CRITICAL → LOW — 9/6/10/6 = 31. Por categoria: Segurança 14, Arquitetura 10, Deprecated 0, Testes 1, Qualidade 5, Outro 1 = 31.
- [x] Mínimo de 5 findings — 31 (159 ocorrências).
- [x] Detecção de APIs deprecated incluída — buscada (`utcnow`, `before_first_request`, `JSONEncoder`, `flask.escape`, `imp`, `distutils`, adaptadores de datetime do `sqlite3`); registro "DEP: nenhuma encontrada" em "Descartados".
- [x] Skill pausa e pede confirmação antes da Fase 3 — linha `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e rodada de perguntas P1–P4, registrada em "Decisões do usuário".

### Fase 3 — Refatoração
- [x] Estrutura MVC — `config/`, `database/`, `models/`, `services/`, `controllers/`, `views/`, `routes/`, `middlewares/` e `app.py` (`create_app()`).
- [x] Configuração extraída (sem hardcoded) — `config/settings.py` lê tudo do ambiente; `.env.example` criado; senhas de seed só por `SEED_ADMIN_PASSWORD` e `SEED_CLIENTE_PASSWORD`. Literal de senha só em `tests/conftest.py`.
- [x] Models abstraem os dados — `models/*_model.py` com consultas parametrizadas; sem SQL em `controllers/`.
- [x] Views/Routes separadas — `routes/*_routes.py` (blueprints) e `views/` (`serializers.py`, `respostas.py`).
- [x] Controllers concentram o fluxo — `controllers/*_controller.py` validam, chamam services e escolhem a resposta.
- [x] Error handling centralizado — `middlewares/error_handler.py` com `AppError`; busca por `str(e)` e `except Exception` vazia fora dele.
- [x] Entry point claro — `app.py` (`create_app()` e `python app.py`, mesmo comando do README).
- [x] Aplicação inicia sem erros — a fixture do pytest sobe `python app.py` e aguarda `/health` (E-03 e reexecução).
- [x] Endpoints originais respondem — 5 de 19 rotas iguais; 14 alteradas por contrato aprovado (CT-01 a CT-09), com prova verde em E-03 e vermelha no código original em E-05; 0 divergências não aprovadas; os 23 testes originais passam. Ver ponto de atenção 1.

## Resumo dos números

| Item | Antes | Depois |
|---|---|---|
| Arquivos-fonte | 4 | 44 (8 `__init__.py`, 6 vazios) |
| Linhas de código | ~780 | 1257 |
| Maior arquivo | `models.py` (314) | `controllers/validacao.py` (134) |
| Arquivos com 3+ papéis | 3 | 0 |
| Rotas da API | 19 | 18 (`/admin/query` removida) |
| Testes | 23 passed (E-01) | 35 passed (E-03): 23 originais + 12 de contrato |
| Prova de sensibilidade | — | 11 dos 12 testes novos falham no código original; o 12º é guarda de rotas públicas (E-05) |

Findings por severidade: CRITICAL 9, HIGH 6, MEDIUM 10, LOW 6 (total 31, com 159 ocorrências).

## Pontos de atenção

1. **Contrato alterado.** O README do desafio pede que os "endpoints originais continuem respondendo". Das 19 rotas, 14 mudaram, com aprovação (Opção 2, CT-01 a CT-09):
   - `/admin/query` removida (404);
   - `/admin/reset-db` exige token admin e `ALLOW_DESTRUCTIVE=true`;
   - `/relatorios/vendas` exige token admin;
   - escrita de produtos, `GET /usuarios`, `GET /pedidos` e `PUT /pedidos/<id>/status` exigem admin; `GET /usuarios/<id>`, `GET /pedidos/usuario/<id>` e `POST /pedidos` exigem dono ou admin;
   - `POST /login` devolve também `dados.token`;
   - `/usuarios*` deixa de devolver `senha`; `/health` deixa de devolver `secret_key`, `db_path` e `debug`;
   - CORS restrito a `CORS_ORIGINS`;
   - pedido inexistente em `PUT /pedidos/<id>/status` passa de 200 para 404.

   Um avaliador que leia o item literalmente pode questionar. Recomendação: justificar no README, na seção de resultados (o relatório já traz o texto-base). A alternativa seria refazer com a Opção 1 (manter o contrato), que deixa CRITICAL residuais.
2. **Branch diferente da informada.** O pedido cita `refactor-arch/code-smells-20261105-145811`, mas a branch atual é `code-smells-20261105-v2`. A branch `refactor-arch/checkpoint-20261105-175512` foi criada pela skill (K-00) e mantida; remover se não for necessária.
3. **Nada commitado.** O README do desafio exige commitar o código refatorado. A skill não commita, então isso fica com o usuário (ver "Pendências").
4. **"Zero anti-patterns remaining" não vale literalmente.** O exemplo do enunciado mostra essa linha, mas a reauditoria da skill deixa 0 CRITICAL, 0 HIGH e 7 residuais MEDIUM/LOW, todos declarados.

## Residuais declarados pela skill (não são falhas da validação)

- F-016 (MEDIUM, parcial): sem rate limit no `/login` (exige dependência nova, ex. `flask-limiter`). Cabeçalhos de segurança e CORS foram corrigidos.
- F-018 (MEDIUM, SUSPECTED): dependências não auditadas; rodar `pip-audit -r requirements.txt` e declarar a versão de Python.
- F-021 (MEDIUM, parcial): listagens sem paginação (limite padrão mudaria o contrato). N+1, `SELECT *` e consultas redundantes foram resolvidos.
- F-022 (MEDIUM, parcial): sem FKs com enforcement; `NOT NULL` e `UNIQUE(email)` só valem para bancos novos; o `loja.db` existente exige migração (classe D).
- F-023 (MEDIUM, parcial): colunas monetárias continuam `REAL`; o cálculo usa `Decimal`.
- F-025 (MEDIUM): máquina de estados do pedido e devolução de estoque no cancelamento (decisão de negócio, não aplicada).
- F-026 (LOW): README do projeto sem instruções de teste e sem as novas variáveis de ambiente (texto-base no relatório).
- F-001: rotacionar a `SECRET_KEY` e a senha do admin que seguem no histórico git; no `loja.db` local, as senhas antigas ficam em texto puro até o próximo login de cada usuário (migram para hash).
- Limitações da validação: o caminho de sucesso de `POST /admin/reset-db` não foi exercitado (destrutivo); CT-07 (mensagem genérica nos 500) foi verificado só estaticamente; não há coleção de requisições, então V3 = boot da fixture.

## Pendências antes da entrega

- Commitar: `reports/`, `tests/conftest.py` (modificado), `tests/test_contratos.py` (novo), `.env.example`, os novos pacotes (`config/`, `controllers/`, `database/`, `middlewares/`, `models/`, `routes/`, `services/`, `views/`), `app.py` modificado e as remoções de `controllers.py`, `models.py` e `database.py` (recuperáveis pelo commit inicial).
- `.venv/` e `loja.db` já são ignorados pelo `.gitignore`.
- Atualizar o `README.md` do desafio (análise manual, construção da skill, resultados com o texto-base de contrato, como executar).
- Executar a skill nos projetos 2 (`ecommerce-api-legacy`) e 3 (`task-manager-api`) e validar com o mesmo checklist.

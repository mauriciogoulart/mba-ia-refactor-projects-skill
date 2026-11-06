# Validação do resultado — Projeto 1 (code-smells-project)

> **Nota:** registro histórico do momento da validação. Itens como "Nada commitado" e "Pendências antes da entrega" já foram resolvidos em `main`.

- Data: 2026-11-05
- Versão: v1
- Desafio: Criação de Skills — Refatoração Arquitetural Automatizada
- Skill: `refactor-arch` (Claude Code)
- Branch: `refactor-arch/code-smells-20261105-145811` (sem commit nem push)
- Relatório validado: `reports/audit-project-1.md`
- Evidências: `reports/evidence/project-1/20261105-145811/`

## Veredito

**O projeto 1 atende aos 4 critérios obrigatórios e a todos os itens do checklist.** Há 4 pontos de atenção, nenhum bloqueante.

## Método de verificação

- Leitura integral do README do desafio e do `reports/audit-project-1.md`.
- Reexecução independente de `.venv/Scripts/python -m pytest -q` → **23 passed**.
- Conferência por amostragem das linhas citadas contra o commit original (`git show HEAD:...`):
  `controllers.py:161/179/182` e `257-262`, `database.py:76-78`, `models.py:83/99/144/146`, `app.py:1-88`. Todas conferem.
- Contagem dos arquivos originais: `app.py` 88, `controllers.py` 292, `database.py` 86, `models.py` 314 linhas (4 arquivos-fonte, ~780 linhas).
- Grep no código refatorado por: `debug=True`, `0.0.0.0`, `minha-chave`, `print(`, `str(e)`, `SELECT *`, `global`, `check_same_thread`, concatenação em `execute(`.
- Contagem do código novo: 40 arquivos `.py` fora de `tests/`, `.venv` e `.claude`, somando 1270 linhas.
- Leitura do `SKILL.md` (3 fases, pausa na Fase 2) e dos 7 arquivos de referência (1494 linhas).
- Verificação da procedência dos testes: `tests/conftest.py`, `pytest.ini` e `requirements-dev.txt` têm data de 2026-11-04, anterior à execução da skill. Portanto o baseline não foi escrito pela skill.

## Critérios de aceite

| Critério | Status | Evidência |
|---|---|---|
| Fase 1 detecta a stack corretamente | ✅ | Python + Flask 3.1.1 (confiança alta) |
| Fase 2 encontra >= 5 findings | ✅ | 31 findings |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | ✅ | 9 CRITICAL e 6 HIGH |
| Fase 3: aplicação funciona após a refatoração | ✅ | 23/23 testes (E-05 e reexecução); 18 rotas registradas (E-06) |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python.
- [x] Framework detectado corretamente — Flask 3.1.1.
- [x] Domínio descrito corretamente — e-commerce (produtos, usuários, pedidos, itens_pedido).
- [x] Número de arquivos condiz com a realidade — 4 arquivos-fonte, igual ao repositório.

### Fase 2 — Auditoria
- [x] Relatório segue o template dos arquivos de referência.
- [x] Cada finding tem arquivo e linhas exatos — amostra conferida contra o código original.
- [x] Findings ordenados CRITICAL → LOW — 9/6/10/6 = 31. Soma por categoria: Segurança 14, Arquitetura 10, Testes 1, Qualidade 5, Outro 1 = 31.
- [x] Mínimo de 5 findings — 31.
- [x] Detecção de APIs deprecated incluída — linha `DEP: nenhuma encontrada para Python 3.14 / flask==3.1.1 / flask-cors==5.0.1`.
- [x] Skill pausa e pede confirmação antes da Fase 3 — linha `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e rodada de perguntas P1–P4, registrada em "Decisões do usuário".

### Fase 3 — Refatoração
- [x] Estrutura MVC — `config/`, `database/`, `models/`, `services/`, `controllers/`, `routes/`, `middlewares/`, mais `serializers.py`, `validators.py`, `errors.py`, `constants.py`.
- [x] Configuração extraída (sem hardcoded) — `config/settings.py`. Ressalva: senhas de seed em `database/schema.py:70-72`.
- [x] Models abstraem os dados — `models/*_model.py`; únicas concatenações em `execute` são `_SELECT + " WHERE ... = ?"` (seguras).
- [x] Views/Routes separadas — `routes/*_routes.py` (blueprints) e `serializers.py`.
- [x] Controllers concentram o fluxo — validar → service → resposta, sem SQL.
- [x] Error handling centralizado — `middlewares/error_handler.py` com `AppError`; grep por `str(e)` vazio.
- [x] Entry point claro — `app.py` (`create_app` e `python app.py`).
- [x] Aplicação inicia sem erros — a fixture do pytest sobe `python app.py` e aguarda `/health`.
- [x] Endpoints originais respondem — 23/23 testes. Exceções aprovadas: CT-01 a CT-08.

## Resumo dos números

| Item | Antes | Depois |
|---|---|---|
| Arquivos-fonte | 4 | 40 (7 `__init__.py`, 6 vazios) |
| Linhas de código | ~780 | 1270 |
| Maior arquivo | `models.py` (314) | `validators.py` (140) |
| Arquivos com 3+ papéis | 4 | 0 |
| Rotas | 19 | 18 (`/admin/query` removida) |
| Testes | 23 passed (E-02) | 23 passed (E-05) |

Findings por severidade: CRITICAL 9, HIGH 6, MEDIUM 10, LOW 6 (total 31, com 184 ocorrências).

## Pontos de atenção

1. **Contrato alterado.** O README do desafio pede que os "endpoints originais continuem respondendo". Houve mudanças aprovadas por você (CT-01 a CT-08):
   - `/admin/query` removida;
   - `/relatorios/vendas` e `/admin/reset-db` passam a exigir token admin;
   - `/usuarios*` deixa de devolver `senha`; `/health` deixa de devolver `secret_key`, `db_path` e `debug`;
   - entradas inválidas passam de 500/aceito para 400; e-mail duplicado e produto com pedidos retornam 409; pedido inexistente retorna 404.

   Recomendação: justificar no README, na seção de resultados.
2. **Teste editado.** `tests/test_api.py::test_relatorio_vendas` foi alterado por causa do CT-05 (login do admin do seed e envio de `Authorization: Bearer`). As asserções (status 200 e 8 chaves) não mudaram. A edição foi aprovada e está declarada no relatório, mas a regra 6 do `SKILL.md` diz "nunca edite testes", então é uma exceção que a skill não prevê. Considere ajustar a regra para tratar esse caso.
3. **Hardcoded residual.** As senhas de seed (hash gravado no banco, texto no fonte) continuam em `database/schema.py:70-72`, porque os testes fazem login com `admin@loja.com`. O relatório declara isso como residual; o item "sem hardcoded" fica parcial.
4. **Fase 1 fora do arquivo.** O `audit-project-1.md` não traz o bloco `PHASE 1: PROJECT ANALYSIS`, apenas o domínio no checklist. Se quiser prova da Fase 1, anexar a saída do terminal ao README.

## Residuais declarados pela skill (não são falhas da validação)

- F-001: senhas de seed no fonte; o valor antigo de `SECRET_KEY` segue no histórico git.
- F-003: só `/admin/reset-db` e `/relatorios/vendas` exigem token; as demais rotas continuam públicas (decisão de produto).
- F-016: CORS padrão ainda `*`; limite de login em memória, por processo.
- F-018: `pip-audit` não executado.
- F-021 / F-022: constraints só valem para bancos novos; colunas monetárias seguem `REAL` (cálculo em `Decimal`).
- F-023: listagens sem paginação.
- F-026: README do projeto não atualizado; `tests/`, `pytest.ini` e `requirements-dev.txt` não versionados.
- Rotas `/admin/*` não exercitadas (classe D); 401/403, 409, hash de senha e devolução de estoque não são assertados pela suíte existente.

## Pendências antes da entrega

O README do desafio pede o commit do código refatorado, e a skill proíbe commit, então isso fica com o usuário.

- Commitar: `reports/`, `tests/`, `pytest.ini`, `requirements-dev.txt`, a skill em `.claude/skills/` e o código refatorado (inclusive as remoções de `controllers.py`, `models.py` e `database.py`).
- `ecommerce-api-legacy/package.json` está modificado e não pertence ao projeto 1; revisar antes de incluir no commit.
- `.claude/settings.local.json` na raiz do repositório: avaliar se deve entrar no commit.
- `.venv/` já está coberto pelo `.gitignore`.
- Atualizar o `README.md` do desafio (análise manual, construção da skill, resultados, como executar).

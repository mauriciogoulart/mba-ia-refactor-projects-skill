# Validação do resultado — Projeto 3 (task-manager-api)

> **Nota:** registro histórico do momento da validação. Itens como "Nada commitado" e "Pendências antes da entrega" já foram resolvidos em `main`.

- Data: 2026-11-06
- Versão: v2
- Desafio: Criação de Skills — Refatoração Arquitetural Automatizada
- Skill: `refactor-arch` 1.1 | Catálogo 1.0 (Claude Code)
- Branch: `task-manager-api` (sem commit nem push). A execução da skill criou também `refactor-arch/checkpoint-20261106-140715` (K-00), mantida para decisão do usuário. Existem ainda outras branches `refactor-arch/*` de execuções anteriores (ver ponto de atenção 2).
- Relatório validado: `reports/audit-project-3.md` (Run id 20261106-140715)
- Evidências: `reports/evidence/project-3/20261106-140715/`

## Veredito

**O projeto 3 atende aos 4 critérios obrigatórios e a todos os itens do checklist.** Há 4 pontos de atenção, nenhum bloqueante. O principal é o item "endpoints originais", por causa das mudanças de contrato aprovadas. O item "Configuração sem hardcoded" é atendido de forma parcial (`[~]`) pela própria skill, por causa dos segredos que seguem no histórico git.

## Método de verificação

- Leitura integral do `reports/audit-project-3.md` (700 linhas), do `03-template-relatorio.md` (§§1–3) e das passagens do README do desafio sobre template, pausa e critérios.
- Listagem das evidências `E-00` a `E-06` e da pasta `.claude/skills/refactor-arch/` (`SKILL.md` + 7 referências). O conteúdo bruto dos logs não foi aberto: a conferência de E-01 a E-05 foi feita pelo resumo do relatório e pela reexecução independente abaixo.
- Reexecução independente de `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` → **35 passed**.
- Conferência por amostragem de 20 referências de linha contra o commit original (`git show HEAD:task-manager-api/...`): `app.py:13/15/34`, `models/user.py:21/29/32`, `models/task.py:15`, `routes/user_routes.py:52/83/134/185/210`, `routes/task_routes.py:42/51/252`, `routes/report_routes.py:105/157`, `services/notification_service.py:9/10`, `seed.py:19`. Todas conferem com o trecho citado.
- Contagem dos arquivos originais: 15 `.py` fora de `tests/`, somando 1158 linhas (`wc -l` sobre `git show`). Igual ao relatório; a soma das linhas por arquivo em "Estrutura ANTES" também fecha em 1158.
- Contagem do código novo: 41 arquivos `.py` fora de `tests/`, `.venv`, `__pycache__` e `.claude` (8 `__init__.py`, 4 vazios), somando 1483 linhas. Confere com o anexo da Fase 3.
- Soma do Summary: CRITICAL 7 + HIGH 4 + MEDIUM 11 + LOW 6 = 28; por categoria: Segurança 12, Arquitetura 8, Deprecated 2, Testes 1, Qualidade 5 = 28. Confere com a numeração F-001 a F-028.
- Ordenação: dentro de cada severidade, os findings seguem categoria e depois arquivo (ex.: HIGH = Segurança F-008, Arquitetura F-009 `app.py`, F-010 `routes/report_routes.py:12`, F-011 `routes/report_routes.py:157`), como o template pede.
- Grep no código refatorado (fora de `tests/`) por `senha123`, `super-secret`, `fake-jwt`, `debug=True`, `0.0.0.0`, `str(e)`, `except:`, `utcnow(` e `.query.get(`: **0 ocorrências**. O MD5 restante (`models/user.py`) existe só para verificar e migrar o hash legado.
- Integridade dos testes: `git status` mostra `M tests/conftest.py`, `M tests/test_api.py` e `?? tests/test_contratos.py`, exatamente os 3 arquivos registrados em "Alterações em testes". Diferente do projeto 1, aqui `test_api.py` foi alterado (1 teste, `test_login_sucesso`, classe T2, justificado por CT-01; asserts 83 → 84).

## Critérios de aceite

| Critério | Status | Evidência |
|---|---|---|
| Fase 1 detecta a stack corretamente | ✅ | Python 3.14.0 + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1 (confiança alta) — E-00 |
| Fase 2 encontra >= 5 findings | ✅ | 28 findings |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | ✅ | 7 CRITICAL e 4 HIGH |
| Fase 3: aplicação funciona após a refatoração | ✅ | 35/35 testes (E-03 e reexecução); 22 rotas registradas, idênticas ao original (E-02 × E-05) |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python 3.14.0 (runtime do `.venv`).
- [x] Framework detectado corretamente — Flask 3.0.0 (`requirements.txt:1`, `Flask(__name__)`).
- [x] Domínio descrito corretamente — gerenciador de tasks (tasks, usuários/login, categorias, relatórios), confirmado nas 22 rotas.
- [x] Número de arquivos condiz com a realidade — 15 arquivos-fonte e 1158 linhas, igual ao repositório (4 dos 15 são `__init__.py`).

### Fase 2 — Auditoria
- [x] Relatório segue o template dos arquivos de referência — seções e ordem do `03-template-relatorio.md` §3.
- [x] Cada finding tem arquivo e linhas exatos — amostra de 20 referências conferida contra o código original.
- [x] Findings ordenados CRITICAL → LOW — 7/4/11/6 = 28. Por categoria: Segurança 12, Arquitetura 8, Deprecated 2, Testes 1, Qualidade 5, Outro 0 = 28.
- [x] Mínimo de 5 findings — 28 (189 ocorrências).
- [x] Detecção de APIs deprecated incluída — F-021 (`datetime.utcnow()`, 22 ocorrências) e F-022 (`Query.get`, 16 ocorrências).
- [x] Skill pausa e pede confirmação antes da Fase 3 — linha `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e rodada de perguntas P1–P4, registrada em "Decisões do usuário".

### Fase 3 — Refatoração
- [x] Estrutura MVC — `config/`, `models/`, `services/`, `controllers/`, `views/`, `routes/`, `middlewares/` e `app.py` (`create_app()`); módulos de rotas com 8 a 17 linhas, só mapeamento.
- [~] Configuração extraída (sem hardcoded) — `config/settings.py` lê tudo do ambiente; `.env.example` criado; senhas de seed só por `SEED_ADMIN_PASSWORD`, `SEED_MANAGER_PASSWORD` e `SEED_USER_PASSWORD`; grep por literais de segredo/debug no código novo = vazio. Parcial porque `SECRET_KEY`, senha SMTP e senhas de seed antigas seguem no histórico git (F-001, rotação manual). Ver ponto de atenção 4.
- [x] Models abstraem os dados — `models/*.py` com `get`, `list_*`, `count_*`, `search`; controllers sem `db`.
- [x] Views/Routes separadas — `routes/*.py` (só `add_url_rule`) e `views/serializers.py` (DTOs sem senha).
- [x] Controllers concentram o fluxo — `controllers/*.py` validam, chamam services e serializam.
- [x] Error handling centralizado — `middlewares/error_handler.py` (`AppError` + handler genérico JSON); busca por `except:` e `str(e)` vazia.
- [x] Entry point claro — `app.py` (`create_app()` e `python app.py`, mesmo comando do README).
- [x] Aplicação inicia sem erros — a fixture do pytest sobe `python app.py` (seed + boot) e aguarda `/health` (E-03 e reexecução).
- [x] Endpoints originais respondem — 2 de 22 rotas iguais; 20 alteradas por contrato aprovado (CT-01 a CT-07), com prova verde em E-03 e vermelha no código original em E-04; 0 rotas divergentes sem aprovação; as asserções originais das 22 rotas passam com token. Ver ponto de atenção 1.

## Resumo dos números

| Item | Antes | Depois |
|---|---|---|
| Arquivos-fonte | 15 | 41 (8 `__init__.py`, 4 vazios) |
| Linhas de código | ~1158 | 1483 |
| Maior arquivo | `routes/task_routes.py` (299) | `controllers/validators.py` (244) |
| Arquivos com 3+ papéis | 4 | 0 |
| Rotas da API | 22 | 22 (nenhuma removida) |
| Testes | 25 passed (E-01) | 35 passed (E-03): 25 originais + 10 de contrato |
| Prova de sensibilidade | — | 9 dos 10 testes novos/T2 falham no código original (9 failed, 2 passed); os 2 que passam são guardas de regressão (rotas públicas e token válido) (E-04) |

Findings por severidade: CRITICAL 7, HIGH 4, MEDIUM 11, LOW 6 (total 28, com 189 ocorrências).

## Pontos de atenção

1. **Contrato alterado.** O README do desafio pede que os "endpoints originais continuem respondendo". Das 22 rotas, 20 mudaram, com aprovação (Opção 2, CT-01 a CT-07):
   - `POST /login` devolve token assinado (itsdangerous, 8 h) no lugar de `fake-jwt-token-<id>`;
   - `/tasks*`, `/categories*`, `/reports/*`, `GET /users`, `GET /users/<id>` e `GET /users/<id>/tasks` exigem `Authorization: Bearer` (401 sem token);
   - `PUT` e `DELETE /users/<id>`: `DELETE` e alteração de `role`/`active` só admin (403); demais campos, o próprio usuário ou admin;
   - `POST /users` com `role` diferente de `user` exige admin (403);
   - `password` deixa de ser devolvido em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`;
   - CORS restrito a `CORS_ORIGINS` (padrão: nenhuma origem);
   - entradas com tipo inválido passam de 500 (HTML) ou 200/201 para 400 `{'error': ...}`.

   Continuam públicos: `/`, `/health`, `/login` e `POST /users` com perfil `user`. Um avaliador que leia o item literalmente pode questionar. Recomendação: justificar no README, na seção de resultados (o relatório já traz o texto-base). A alternativa seria refazer com a Opção 1 (manter o contrato), que deixa 3 CRITICAL residuais (F-002, F-006, F-007).
2. **Branches de execuções anteriores.** Além da `refactor-arch/checkpoint-20261106-140715` (deste run), existem `refactor-arch/checkpoint-20261105-175512`, `refactor-arch/checkpoint-20261106-131947` e `refactor-arch/code-smells-20261105-145811` no mesmo repositório. Remover as que não forem necessárias.
3. **Nada commitado.** O README do desafio exige commitar o código refatorado. A skill não commita, então isso fica com o usuário (ver "Pendências").
4. **Dois itens do checklist não são 100% literais.** "Sem hardcoded" é `[~]` pelo histórico git (F-001); e "Zero anti-patterns remaining" não vale: a reauditoria deixa 0 HIGH, mas ainda há residuais CRITICAL no histórico git (F-001, parcial) e MEDIUM/LOW, todos declarados.
5. **`python seed.py` mudou de comportamento.** O seed agora exige `SEED_*_PASSWORD` e aborta sem elas; o README do projeto ainda não menciona isso (F-023). Quem seguir o README antigo recebe a mensagem "Seed não executado: defina ...".

## Residuais declarados pela skill (não são falhas da validação)

- F-001 (parcial, CRITICAL no histórico): rotacionar `SECRET_KEY`, senha SMTP e senhas de seed já presentes no histórico git.
- F-005 (dados legados): hashes MD5 já gravados em `instance/tasks.db` permanecem até o próximo login de cada usuário (migração automática para KDF do werkzeug).
- F-012 (parcial, MEDIUM): sem rate limit no `/login` (exige dependência nova, ex. `flask-limiter`). Cabeçalhos de segurança e CORS foram corrigidos.
- F-015 (parcial, MEDIUM): versões fixadas de 2023 (`flask==3.0.0`, `flask-cors==4.0.0`, `requests==2.31.0`) não auditadas; rodar `pip-audit -r requirements.txt` e declarar a versão de Python.
- F-016 (observação): o `instance/tasks.db` existente mantém o schema antigo (sem `ondelete='SET NULL'`); a desvinculação é feita no service. Migrar o schema é classe D.
- F-018 (parcial, MEDIUM): listagens sem paginação (limite padrão mudaria o contrato). N+1 e contagens por consulta foram resolvidos.
- F-023 (LOW): README do projeto sem instruções de teste e sem as variáveis `SEED_*` (texto-base no relatório).
- F-024 (parcial, LOW): `NotificationService` continua sem uso; decidir integrar ou remover.
- Precedência de erros: a validação de formato (C-06) roda antes das checagens de existência/unicidade; entrada com dois problemas ao mesmo tempo pode receber 400 em vez de 404/409. Entradas com um único problema mantêm status e mensagem originais.
- `SECRET_KEY` ausente ⇒ chave aleatória por processo (aviso no log); tokens não sobrevivem a reinícios. Definir em produção.
- Limitações da validação: o `python seed.py` no banco real (destrutivo) não foi executado; `instance/tasks.db` intacto; não há coleção de requisições, então V3 = boot da fixture; rate limit e `pip-audit` não executados.

## Pendências antes da entrega

- Commitar: `reports/` (`audit-project-3.md` e `evidence/project-3/`), `tests/conftest.py` e `tests/test_api.py` (modificados), `tests/test_contratos.py` (novo), `.env.example`, os novos pacotes (`config/`, `controllers/`, `middlewares/`, `views/`), os novos `routes/category_routes.py` e `routes/system_routes.py`, os novos `services/*` e `utils/constants.py`, e os arquivos modificados (`app.py`, `seed.py`, `models/*`, `routes/*`, `services/notification_service.py`, `utils/helpers.py`, `requirements*.txt`).
- `.venv/` e `instance/tasks.db` já são ignorados pelo `.gitignore`.
- Decidir sobre `task-manager-api/.claude/` (skill), que aparece como não rastreado.
- Atualizar o `README.md` do desafio (análise manual, construção da skill, resultados com o texto-base de contrato, como executar) e o README do projeto (F-023, variáveis `SEED_*`).
- Executar a validação do projeto 2 (`ecommerce-api-legacy`) com o mesmo checklist, se ainda não feita.

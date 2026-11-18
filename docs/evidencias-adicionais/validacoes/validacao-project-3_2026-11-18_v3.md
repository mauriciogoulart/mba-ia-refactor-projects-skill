# Validação do resultado — Projeto 3 (task-manager-api)

- **Data:** 2026-11-18
- **Versão:** v3 — skill 1.2
- **Desafio:** `docs/DESAFIO.md` (seções "Validação" e "Critérios de Aceite")
- **Skill:** `task-manager-api/.claude/skills/refactor-arch/` (última alteração em `20f9e72`; idêntica à cópia de `code-smells-project`)
- **Branch/commit:** `entrega-v2` @ `fcc9fc4` (refatorado, sem diferença na working tree em `task-manager-api/`); original `5303107`
- **Relatório validado:** `reports/audit-project-3.md` (Run id 20261116-214549)
- **Evidências:** `reports/evidence/project-3/20261116-214549/` (E-00 a E-09 + `tests-before/`)

## Veredito

**NÃO APROVADO na versão 1.2, por 1 ponto bloqueante. Os critérios de aceite do desafio estão atendidos.**

- **Desafio:** os 4 critérios de aceite foram atendidos e conferidos em execução própria.
- **Bloqueante (critério adicional 3a):** o F-029 (SEC-11, HIGH) foi corrigido só nas rotas que ele lista. Um usuário comum recebe 403 em `GET /users/1/tasks`, mas recebe **200 com as mesmas tasks** em `GET /tasks/search?user_id=1`. Basta uma conta criada no cadastro público. A afirmação "CRITICAL/HIGH sem correção: Nenhum" do relatório não se sustenta.
- **Demais critérios adicionais:** 3c, 3d e 3e atendidos; 3b atendido com evidência documental.

## Método de verificação

1. **Suíte reexecutada:** `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`, com a porta 5000 livre antes e depois: **85 passed**, exit 0. Bate com o E-03.
2. **Execução real própria:** script fora do projeto, em cópia temporária, com `SECRET_KEY` e senhas `SEED_*` geradas por mim e nunca impressas. Foram **6 subidas da aplicação, 2 boots recusados de propósito (produção sem chave e com debug), 162 requisições e 137 verificações: 137 ok, 0 falhas**, mais 30 sondagens registradas à parte. A primeira rodada acusou 1 falha falsa, causada por erro no meu script (comparação de tupla); corrigi o script e repeti a bateria inteira.
   - Sem token e com `fake-jwt-token-1`: 401. Login válido e rota com token: 200.
   - Usuário comum criando `role: admin`: 403. Alterando ou excluindo task alheia: 403, com a task intacta.
   - Usuário comum em `/users`, `/users/1`, `/users/1/tasks`, `/reports/user/1` e `/reports/summary`: 403.
   - Admin nas mesmas operações: sucesso, incluindo exclusão de task, categoria e usuário.
   - `password` ausente em login, `GET /users`, `GET`/`POST`/`PUT` de usuário.
   - 13 payloads de tipo inválido, 4 parâmetros inválidos e 4 corpos malformados: 400.
   - Token adulterado, expirado, de outra chave, de usuário desativado e de usuário excluído: 401.
   - 5 falhas de login levam a 429. Hash MD5 legado migra para KDF no login. Log sem senha, chave, nome ou e-mail. Boot com debug desligado em 127.0.0.1.
   - Processos encerrados e porta 5000 livre ao final.
3. **Controle no original (`5303107`):** `GET /tasks` sem token 200, `password` e token previsível no login, admin criado por anônimo 201.
4. **Prova vermelha própria:** testes novos contra o código original: **53 failed, 4 passed, 4 errors**, igual ao E-04. Os 4 aprovados são os controles positivos declarados. A suíte original no código original: 25 passed.
5. **Teste de mutação próprio** (cópia temporária, um defeito por vez): **21 de 24 mutantes mortos** (ver ponto de atenção 7).
6. **Referências arquivo:linha:** **183 referências conferidas** contra `git show 5303107:...`, comparando o trecho esperado em cada linha: **0 divergências**. Cobrem 26 findings diretamente; F-012 e F-015 apontam para linhas conferidas em F-002 e F-014. Recontei 28 findings, 181 ocorrências, 22 linhas com `utcnow`, 16 `.query.get(`, 12 `except:` e 4 `except Exception`.
7. **Varredura do refatorado (fora de `tests/`):**

   | Busca | Ocorrências | Observação |
   |---|---|---|
   | Segredos literais | 0 | |
   | `debug=True` | 0 | |
   | `0.0.0.0` | 0 | |
   | `md5` | 1 | `models/user.py:31`, migração de hash legado |
   | `fake-jwt` | 0 | |
   | `except:` | 0 | |
   | `str(e)` em respostas | 0 | |
   | `utcnow(` | 12 | todas do helper `utils/clock.py`; `datetime.utcnow()` não é usado |
   | `.query.get(` | 0 | |

8. **Integridade dos testes:** `tests-before/` é idêntico a `5303107` (mesmo hash git).
   - `tests/test_api.py`: 25 testes antes e depois, nenhum removido ou pulado; asserções de 81 para 83.
   - Só `test_login_sucesso` mudou (3 para 5 asserções). A única asserção substituída é o formato `fake-jwt-token-<id>`, exigido pelo CT-02, e foi trocada por verificações mais fortes.
   - `tests/conftest.py`: autenticação e senhas geradas; nenhuma asserção removida. **Nenhuma asserção enfraquecida.**

## Critérios de aceite

| Critério | Requisito | Resultado | Evidência |
|---|---|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO | **Atendido** | Python 3.14 + Flask 3.0.0, domínio Task Manager (E-00) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO | **Atendido** | 28 findings, mais F-029 na reauditoria |
| Fase 2 inclui ao menos 1 CRITICAL/HIGH | OBRIGATÓRIO | **Atendido** | 7 CRITICAL e 4 HIGH (5 HIGH com F-029) |
| Fase 3: aplicação funciona | OBRIGATÓRIO | **Atendido** | Boot sem erros; 22 de 22 rotas respondem na execução própria |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python 3.14
- [x] Framework detectado corretamente — Flask 3.0.0
- [x] Domínio da aplicação descrito corretamente — tasks, usuários, categorias e relatórios
- [x] Número de arquivos analisados condiz com a realidade — 15 arquivos e 1158 linhas, recontados

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — seções e ordem iguais às de `03-template-relatorio.md`
- [x] Cada finding tem arquivo e linhas exatos — 183 referências, 0 divergências
- [x] Findings ordenados por severidade (CRITICAL → LOW) — F-001 a F-028; o F-029 está no anexo por ter surgido na reauditoria
- [x] Mínimo de 5 findings identificados — 28
- [x] Detecção de APIs deprecated incluída (se aplicável) — F-021 e F-022
- [~] Skill pausa e pede confirmação antes da Fase 3 — só há evidência documental: o relatório termina com a pergunta e registra `1A 2A 3A 4A`; a pausa em si não é observável depois da execução

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — config, models, views, controllers, routes, services, validators e middleware
- [x] Configuração extraída para módulo de config (sem hardcoded) — `config/settings.py`
- [x] Models criados para abstrair dados — consultas em `models/`; `db.session` fora deles só em `services/persistence.py`
- [x] Views/Routes separadas para visualização ou roteamento — `routes/` e `views/serializers.py`
- [x] Controllers concentram o fluxo da aplicação — `controllers/`
- [x] Error handling centralizado — `middleware/error_handler.py`; 404 e 405 em JSON conferidos
- [x] Entry point claro — `app.py` com `create_app()`
- [x] Aplicação inicia sem erros — 6 subidas sem erro
- [x] Endpoints originais respondem corretamente — 22 de 22 rotas; mudanças de status cobertas por CT-01 a CT-09

## Critérios adicionais da versão 1.2

| Item | Critério | Resultado | Conferência |
|---|---|---|---|
| a | Nenhum CRITICAL/HIGH sem correção | **Não atendido** | 7 CRITICAL e 4 HIGH da Fase 2 corrigidos. O F-029 segue aberto na leitura de tasks de terceiros (ponto de atenção 1). Rotação de segredos publicados é ação manual externa |
| b | P3 com 3 opções na ordem definida; resposta Refatorar | **Atendido (documental)** | A política `07` fixa a ordem; a tabela de contrato traz Refatorar, Manter contrato\* e Híbrido; o resumo avisa 3 CRITICAL e 0 HIGH sem correção em Manter contrato\* (recontado); resposta `3A` = Refatorar. O texto literal da pergunta não foi guardado |
| c | Correções provadas por testes | **Atendido** | 85 verdes no refatorado; 53 failed e 4 errors no original; 12 testes de unidade e 48 de integração novos |
| d | Execução local autenticada, segredos mascarados | **Atendido** | E-02 e E-05 com 117 requisições cada; tokens mascarados; nenhum token, hash ou senha gerada nos logs. No baseline, as credenciais são as do seed original, como o relatório declara |
| e | Evidências no formato `E-nn` | **Atendido** | E-00 a E-09, todas citadas no relatório |

## Resumo dos números

| Métrica | Antes | Depois |
|---|---|---|
| Arquivos-fonte | 15 | 44 |
| Linhas | 1158 | 1486 |
| Maior arquivo | `routes/task_routes.py` (299) | `validators/task_validator.py` (113) |
| Arquivos com 3+ papéis | 4 | 0 |
| Rotas | 22 | 22 |
| Testes | 25 | 85 |
| Findings CRITICAL | 7 | 0 |
| Findings HIGH | 4 (5 com F-029) | 1 (F-029, parcial) |
| Findings MEDIUM | 11 | 4 parciais declarados (F-013, F-014, F-016, F-018) |
| Findings LOW | 6 | 2 declarados (F-023, F-025) |

A coluna "Depois" dos findings reflete esta validação, não o relatório, que declara 0 HIGH.

## Pontos de atenção

1. **BLOQUEANTE — F-029 corrigido só em parte (leitura de tasks de terceiros).** Fato observado com usuário comum e com conta recém-criada no cadastro público:
   - `GET /users/1/tasks` responde 403, mas `GET /tasks/search?user_id=1` responde 200 com os mesmos ids e títulos.
   - `GET /tasks/1` (task alheia) responde 200, e `GET /tasks` lista as tasks de todos com o `user_name` de cada dono.
   - Isso corresponde ao sinal do SEC-11 no catálogo. O teste da reauditoria (E-07) e a bateria E-05 não cobrem `search?user_id=`.
   - **Para resolver:** filtrar as leituras de tasks por responsável ou gestão, com testes. Se as tasks forem compartilhadas por decisão de produto, isso precisa ser aprovado e registrado, e a restrição de `/users/<id>/tasks` precisa ser revista, porque hoje as duas regras se contradizem.
2. **Não bloqueante — atribuição de tasks a terceiros.** Usuário comum cria task em nome de outro (`POST /tasks` com `user_id`: 201) e transfere a própria task a outro (`PUT`: 200).
3. **Não bloqueante — categorias.** Qualquer autenticado, inclusive de cadastro público, cria e renomeia categorias (201 e 200). Só a exclusão exige admin.
4. **Não bloqueante — tipos inválidos ainda geram 500.** `user_id` ou `category_id` com `[]` ou `{}` e inteiros gigantes em rota, `offset`, `user_id` e `priority` respondem 500 com corpo genérico, sem vazar detalhes. `priority: 2.5`, `priority: true`, `user_id: true` e `user_id: 0` são aceitos (201). Nos casos repetidos no original (`[]`, inteiro gigante, `2.5`) o comportamento é o mesmo, então não é regressão, mas o relatório não lista isso como residual do F-014.
5. **Não bloqueante — login.** E-mail inexistente respondeu em 4 ms e existente em 124 ms (uma amostra), o que indica possível enumeração por tempo. E-mail com outra caixa (`JOAO@email.com`) cria conta separada.
6. **Não bloqueante — token após troca de senha.** O token antigo continua válido até expirar.
7. **Não bloqueante — lacunas de teste.** Sobreviveram 3 mutantes: usuário inativo mantendo acesso por token, senha literal de fallback no seed e paginação sem teto. Os três comportamentos estão corretos na minha execução, mas nenhum teste automatizado os protege.
8. **Não bloqueante — README desatualizado (F-023, declarado).** Seguindo o README atual, o seed gera senhas aleatórias não exibidas e não há como fazer login.
9. **Não bloqueante — dependências diretas não declaradas.** `itsdangerous`, `werkzeug` e `sqlalchemy` são importados no código, mas só chegam como dependências transitivas.

## Residuais declarados pela skill

- **Ação manual:** rotacionar `SECRET_KEY`, senha SMTP e senhas de seed publicadas no histórico git (F-001, F-009).
- **F-013 (MEDIUM, parcial):** sem lockfile; flask e flask-cors não atualizados; `pip-audit` não executado.
- **F-014 (MEDIUM, parcial):** senha mínima de 4 caracteres mantida.
- **F-016 (MEDIUM, parcial):** schema sem `ondelete`. A parte de registros órfãos era falso positivo, o que confirmei no original (`category_id` fica nulo).
- **F-018 (MEDIUM, parcial):** `GET /users/<id>`, `GET /users/<id>/tasks` e relatórios sem paginação.
- **F-023 (LOW):** README não atualizado.
- **F-025 (LOW, parcial):** datas serializadas com `str()` para preservar o formato.
- **Limitação declarada:** limite de login em memória, por processo.

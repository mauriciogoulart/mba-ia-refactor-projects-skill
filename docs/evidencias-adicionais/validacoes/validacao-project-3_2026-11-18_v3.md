# Validação do resultado — Projeto 3 (task-manager-api)

- **Data:** 2026-11-18
- **Versão:** v3 — skill 1.2
- **Desafio:** `docs/DESAFIO.md` (seções "Validação" e "Critérios de Aceite")
- **Skill:** `task-manager-api/.claude/skills/refactor-arch/` (última alteração em `20f9e72`; idêntica à cópia de `code-smells-project`)
- **Branch/commit:** `entrega-v2` @ `adfb99d` (terceira rodada, 2026-11-19); segunda rodada em `5ba4f4b`; primeira em `fcc9fc4`; original `5303107`. Sem diferença na working tree em `task-manager-api/`
- **Relatório validado:** `reports/audit-project-3.md` (Run id 20261116-214549)
- **Evidências:** `reports/evidence/project-3/20261116-214549/` (E-00 a E-27, `tests-before/`, `tests-before-validacao/` e `tests-before-validacao-2/`)

## Veredito

**Veredito final (terceira rodada, `adfb99d`): APROVADO na versão 1.2, com ressalvas não bloqueantes. Os critérios de aceite do desafio continuam atendidos.**

- **Bloqueante da segunda rodada: resolvido.** O token de uma conta excluída responde 401 em todas as rotas, inclusive depois que outra conta herda o id. Troca de senha, desativação e rebaixamento de perfil também têm efeito imediato.
- **Bloqueante da primeira rodada: continua resolvido.** Usuário comum não lê nem deduz tasks alheias.
- **Ajustes pedidos:** confirmados (surrogate, `priority`, referências 0).
- **Ressalvas:** detalhadas em "Terceira rodada de validação"; nenhuma impede a aprovação.

### Registro da segunda rodada (`5ba4f4b`): reprovado

**NÃO APROVADO na versão 1.2, por 1 ponto bloqueante novo. Os critérios de aceite do desafio continuavam atendidos.**

- **Bloqueante da primeira rodada: resolvido.** Usuário comum e conta de cadastro público já não liam nem deduziam tasks alheias; admin e manager continuavam vendo tudo.
- **Bloqueante novo:** o token de uma conta excluída voltava a valer quando o id dela era reutilizado por um novo cadastro. Com ele foi possível ler as tasks e o perfil da nova conta e **trocar a senha dela**. Reproduzi 3 vezes em 3 rodadas.
- **Demais itens pedidos:** atribuição, valores inválidos, dependências, integridade das asserções e residuais R-01 a R-05 atendidos.

### Registro da primeira rodada (`fcc9fc4`): reprovado

**NÃO APROVADO na versão 1.2, por 1 ponto bloqueante. Os critérios de aceite do desafio estavam atendidos.**

- **Desafio:** os 4 critérios de aceite foram atendidos e conferidos em execução própria.
- **Bloqueante (critério adicional 3a):** o F-029 (SEC-11, HIGH) foi corrigido só nas rotas que ele lista. Um usuário comum recebia 403 em `GET /users/1/tasks`, mas **200 com as mesmas tasks** em `GET /tasks/search?user_id=1`. Bastava uma conta criada no cadastro público. A afirmação "CRITICAL/HIGH sem correção: Nenhum" do relatório não se sustentava.
- **Demais critérios adicionais:** 3c, 3d e 3e atendidos; 3b atendido com evidência documental.

As seções de "Método de verificação" a "Residuais declarados pela skill" registram a primeira rodada e foram mantidas como estavam.

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

## Segunda rodada de validação

Código validado: `5ba4f4b` (`fix(task-manager-api): conclui F-029 após validação independente`).

### Método e números

1. **Suíte completa:** **121 passed**, exit 0, igual ao E-11.
2. **Bateria real própria** em cópia temporária, porta 5000, com senhas e chave geradas por mim: **586 requisições e 325 verificações: 320 ok e 5 divergências**, todas no mesmo caso de URL com 5000 dígitos (ponto de atenção 4). Teste de isolamento em duas identidades (usuário comum do seed e conta de cadastro público):
   - Tasks alheias criadas com um marcador em título, descrição e tags; nenhuma resposta do usuário comum contém o marcador.
   - **Teste diferencial:** alterei tasks alheias (status, prioridade, categoria, atraso) e comparei cada resposta antes e depois; nenhuma mudou, o que descarta dedução por contagens em `/tasks/stats` e no `task_count` de `/categories`.
   - HEAD, PUT e DELETE em task alheia ou sem responsável: 403.
3. **Reprodução isolada do bloqueante novo:** script separado, 3 rodadas com o mesmo resultado, mais 1 controle.
4. **Prova vermelha própria:** testes atuais contra o código de `fcc9fc4`: **35 failed, 86 passed**.
5. **Mutação das correções novas:** **16 de 18 mutantes mortos** (ponto de atenção 2).
6. **Integridade dos testes:** comparação por AST contra `5303107`, `tests-before/` e `fcc9fc4`.
7. Processos encerrados, porta 5000 livre, cópias temporárias removidas e `instance/tasks.db` do projeto intacto.

### Resultado por item

| Item | Verificação | Resultado |
|---|---|---|
| 1 | Suíte completa | **Atendido:** 121 passed |
| 2 | Comum não lê nem deduz tasks alheias em `/tasks`, `/tasks/<id>`, `/tasks/search`, `/tasks/stats`, `/users/<id>/tasks`, `/reports/*` e `task_count`; gestão vê tudo | **Atendido** nessas rotas |
| 3 | Outros caminhos para os mesmos dados | **Não atendido:** token de conta excluída com id reutilizado (ponto de atenção 1) |
| 4 | Atribuição e valores inválidos | **Atendido:** criar ou transferir para outro responde 403 sem gravar; `[]`, `{}`, booleanos, decimais e inteiros gigantes respondem 400; id gigante na URL responde 404 até 2^63; nenhum 500 nesses campos |
| 5 | Dependências diretas declaradas | **Atendido:** os 7 pacotes importados estão em `requirements.txt`, nas versões instaladas; `pip check` sem conflitos |
| 6 | Asserções e residuais | **Atendido:** nenhuma asserção original enfraquecida; R-01 a R-05 declarados no relatório |

Sobre o item 6: desde `fcc9fc4`, `test_api.py` e `conftest.py` não mudaram. `test_seguranca.py` foi de 72 para 107 asserções e `test_unidade.py` de 29 para 38, sem remoção. O único teste antigo alterado é `test_listagem_limita_a_100_itens_por_padrao`: mudou o cenário e manteve as 2 asserções. Contra `5303107`, segue valendo a única troca já registrada (formato `fake-jwt-token-<id>`, exigida pelo CT-02).

### Números atualizados

| Métrica | Primeira rodada | Segunda rodada |
|---|---|---|
| Arquivos-fonte | 44 | 45 |
| Linhas | 1486 | 1550 |
| Maior arquivo | `validators/task_validator.py` (113) | `validators/task_validator.py` (136) |
| Rotas | 22 | 22 |
| Testes | 85 | 121 |

### Pontos de atenção

1. **BLOQUEANTE — token de conta excluída assume a conta que herda o id.**
   - **Sequência reproduzida:** a conta A faz login; o admin exclui A (o token passa a responder 401); um novo cadastro B recebe o mesmo id; o token antigo de A volta a responder 200.
   - **Impacto observado:** com o token de A, li as tasks e o e-mail de B e troquei a senha de B via `PUT /users/<id>`. A senha original de B passou a responder 401 e a do invasor, 200.
   - **Causa:** o token guarda só `user_id`, e o SQLite reutiliza o maior id quando a última linha é excluída.
   - **Condições:** a conta excluída precisa ter o maior id e o novo cadastro precisa ocorrer dentro da validade do token (1 h no padrão). No controle, com a conta excluída fora do maior id, o token seguiu em 401.
   - **Por que bloqueia (avaliação minha):** a exploração depende de uma exclusão feita pelo admin, mas o cadastro é público, a exclusão costuma atingir justamente quem não deve mais ter acesso, e o resultado é a tomada da conta. O caso não consta do relatório.
   - **Para resolver:** vincular o token à conta, por exemplo com um valor derivado do hash da senha ou com `created_at`, e rejeitar quando não conferir, com teste de regressão. Usar o hash da senha também fecharia o R-02.
2. **Não bloqueante — lacuna de teste nas estatísticas.** Sobreviveram os mutantes que retiram o escopo das contagens por status e de atraso em `/tasks/stats`. O código está correto (o teste diferencial confirmou), mas nenhum teste automatizado protege esses dois valores.
3. **Não bloqueante — título com surrogate inválido (`\ud800`) em `POST /tasks` responde 500** com corpo genérico. Foi a única resposta 5xx da bateria.
4. **Não bloqueante — URL com 5000 dígitos responde 405 em vez de 404** em 5 combinações de PUT e DELETE. Não há 500 nem acesso a dados; não investiguei a causa. Ids de 23 dígitos e os limites de 2^63 respondem 404.
5. **Não bloqueante — validação ainda permissiva.** `priority: 2.5` e `priority: true` são aceitos (201), e admin pode criar task com `user_id: 0`, que fica com responsável inexistente.
6. **Não bloqueante — existência de task.** Task alheia responde 403 e inexistente, 404, o que revela quais ids existem, sem expor conteúdo.
7. **Não bloqueante — escopo do CT-09.** O relatório aplicou a ampliação "dentro da C-17 / CT-09 já aprovada", mas ela muda o resultado de `GET /tasks`, `/tasks/search`, `/tasks/stats`, `/categories` e `POST /tasks`. Não há registro de nova aprovação do usuário para esse escopo maior.
8. **Residuais declarados:** R-01 (categorias por qualquer autenticado) e R-04 (e-mail com outra caixa) continuam presentes, como o relatório informa. R-02, R-03 e R-05 foram conferidos só quanto à declaração nesta rodada.

## Terceira rodada de validação

Código validado: `adfb99d` (`fix(task-manager-api): vincula token à conta após 2ª validação independente`), em 2026-11-19. O token passou a carregar uma impressão (HMAC truncado) do hash de senha atual. A impressão é conferida a cada requisição, junto com a busca da conta ativa.

### Método e números

1. **Suíte completa:** **141 passed**, exit 0, igual ao E-19.
2. **Bateria de identidade e token** em cópia temporária, porta 5000, com chave e senhas geradas por mim: **307 requisições, 64 verificações, 64 ok, 0 falhas, nenhum 5xx e nenhum traceback**. Cada cenário de invalidação testa as 19 rotas protegidas (as 18 do CT-01 mais HEAD) e `POST /users` com `role: admin`.
3. **Regressão da segunda rodada**, com as expectativas novas: **618 requisições, 363 verificações, 363 ok, nenhum 5xx**. Inclui o teste diferencial de isolamento entre usuários e a reutilização de id.
4. **Regressão da primeira rodada:** a bateria original inteira, com 6 subidas e os critérios de aceite do desafio: **162 requisições, 137 de 137 ok**.
5. **Prova vermelha própria:** testes atuais contra o código de `5ba4f4b`: **15 failed, 126 passed**.
6. **Mutação:** **11 de 12 mutantes mortos** (ponto de atenção 1). Os 2 mutantes de estatísticas que sobreviveram na segunda rodada agora são mortos.
7. **Integridade dos testes:** comparação por AST contra `5303107`, `tests-before/` e `5ba4f4b`.
8. Processos encerrados, porta 5000 livre, cópias temporárias removidas e `instance/tasks.db` do projeto intacto.

### Resultado por item

| Item | Verificação | Resultado |
|---|---|---|
| 1 | Suíte completa | **Atendido:** 141 passed |
| 2 | Conta A excluída, conta B herda o id | **Atendido:** em 3 de 3 rodadas o token de A responde 401 em todas as rotas, já logo após a exclusão; a senha e o token de B ficam intactos |
| 2 | Troca de senha | **Atendido:** pelo próprio, pelo admin e até para a mesma senha, todos os tokens anteriores respondem 401 nas 19 rotas; o novo login funciona |
| 2 | Desativação | **Atendido:** 401 em todas as rotas; login responde 403 |
| 2 | Rebaixamento de perfil | **Atendido:** efeito imediato em `/users`, `/reports/*`, dados de terceiros, listagem, atribuição e DELETE de admin |
| 3 | Outros caminhos de identidade ou token | **Nenhum problema encontrado** (detalhes abaixo) |
| 4 | Surrogate isolado | **Atendido:** 400 em 10 combinações de corpo em tasks, categorias, usuários e login, inclusive em chave e em tags; emoji válido aceito (201) |
| 4 | `priority` | **Atendido:** `2.5`, `true`, `false`, `1.0`, `"2"`, `0` e `6` respondem 400 em POST e PUT; `3` responde 201 |
| 4 | Referências 0 | **Atendido:** `user_id: 0` e `category_id: 0` respondem 404 (admin e comum); usuário comum atribuindo `user_id: 0` recebe 403 no POST e no PUT |
| 5 | Regressão | **Atendido:** isolamento de tasks preservado; critérios de aceite atendidos; nenhuma asserção original enfraquecida |
| 6 | Residuais | **Atendido:** R-01 e R-03 a R-07 declarados; o R-02 saiu da lista como corrigido, o que confirmei |

**Outros caminhos testados (item 3), todos com resposta 401:**
- Token assinado com a chave correta, mas sem `fp`, com `fp` vazio ou errado, com `user_id` booleano, texto, inexistente ou gigante, ou com payload em lista.
- Token de outra chave e token com outro salt.
- Conta recriada com o mesmo e-mail e a mesma senha (o salt muda o hash).

**Comportamentos esperados conferidos:**
- Alterar nome ou e-mail mantém o token.
- O token do admin continua válido depois que ele troca a senha de outra conta.
- Na migração de hash MD5 legado, o token emitido no login já vale, e um novo login não invalida o anterior.

**Integridade dos testes:**
- Desde `5ba4f4b`, `test_api.py` e `conftest.py` não mudaram, e `tests-before-validacao-2/` é idêntico a `5ba4f4b`.
- `test_seguranca.py` foi de 107 para 129 asserções e `test_unidade.py` de 38 para 49, sem remoção.
- O único teste antigo reescrito, `test_token_assinado_valida_adulteracao_e_expiracao`, manteve as 4 asserções (válido, adulterado, outra chave, expirado), adaptadas à nova assinatura `issue(user)` / `verify(token, carregar)`; não houve enfraquecimento.
- Contra `5303107`, continua só a troca já registrada do formato `fake-jwt-token-<id>`.

### Números atualizados

| Métrica | Segunda rodada | Terceira rodada |
|---|---|---|
| Arquivos-fonte | 45 | 45 |
| Linhas | 1550 | 1588 |
| Maior arquivo | `validators/task_validator.py` (136) | `validators/task_validator.py` (136) |
| Rotas | 22 | 22 |
| Testes | 121 | 141 |

### Pontos de atenção (nenhum bloqueante)

1. **Lacuna de teste em contas desativadas.** O mutante que deixa uma conta inativa continuar autenticando pelo token sobrevive à suíte; a mesma lacuna já aparecia na primeira rodada. O comportamento está correto na execução real (401 em todas as rotas), mas nenhum teste automatizado o protege.
2. **Reativação restaura tokens.** Um token emitido antes de desativar a conta volta a responder 200 depois que ela é reativada, se ainda estiver dentro da validade (1 h no padrão). Pode ser intencional, mas não está documentado.
3. **Residuais declarados e confirmados:**
   - R-01: usuário comum cria e renomeia categorias (201 e 200).
   - R-03: e-mail inexistente respondeu em 17 ms e existente em 136 ms, numa amostra; o relatório diz "não medido".
   - R-04: e-mail com outra caixa cria conta separada.
   - R-06: task alheia responde 403 e inexistente, 404.
   - R-07: URL com milhares de dígitos responde 405, sem 500.
   - R-05 foi conferido só quanto à declaração.
4. **Lacunas de teste da primeira rodada, não reavaliadas:** os mutantes de senha literal de fallback no seed e de paginação sem teto (M20 e M21) não foram rodados de novo.

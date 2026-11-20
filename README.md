# refactor-arch — Refatoração Arquitetural Automatizada com Claude Code

Solução do desafio **"Criação de Skills — Refatoração Arquitetural Automatizada"** (enunciado original em [docs/DESAFIO.md](docs/DESAFIO.md)).

A skill `refactor-arch` (Claude Code) analisa uma codebase de backend, audita anti-patterns e vulnerabilidades com severidade, arquivo e linha, gera um relatório, **pausa para confirmação** e, após aprovação, refatora para MVC e valida com evidências reais de execução. Esta é a **entrega v2**: a skill foi revisada (versão 1.2) e executada nos 3 projetos a partir do código-fonte original.

## Critérios de aceite (3/3 projetos)

| Critério | code-smells-project (Python/Flask) | ecommerce-api-legacy (Node/Express) | task-manager-api (Python/Flask) |
|---|---|---|---|
| Fase 1 detecta stack corretamente | ✅ Python 3.14 + Flask 3.1.1 | ✅ Node.js 24 + Express 4.22.1 | ✅ Python 3.14 + Flask 3.0.0 / Flask-SQLAlchemy |
| Fase 2 encontra >= 5 findings | ✅ 31 | ✅ 25 | ✅ 28 (+1 na reauditoria) |
| Fase 2 inclui >= 1 CRITICAL ou HIGH | ✅ 9 CRITICAL, 6 HIGH | ✅ 6 CRITICAL, 7 HIGH | ✅ 7 CRITICAL, 4 HIGH |
| Fase 3: aplicação funciona após refatoração | ✅ 51/51 testes + execução local | ✅ 33/33 testes + `api.http` + execução local | ✅ 141/141 testes + execução local |
| CRITICAL/HIGH sem correção ao final | 0 | 0 | 0 |
| Relatório | [audit-project-1.md](reports/audit-project-1.md) | [audit-project-2.md](reports/audit-project-2.md) | [audit-project-3.md](reports/audit-project-3.md) |

## Sumário

- [Revisão pós-avaliação (entrega v2)](#revisão-pós-avaliação-entrega-v2)
- [Processo: como o desafio foi resolvido](#processo-como-o-desafio-foi-resolvido)
- [A) Análise Manual](#a-análise-manual)
- [B) Construção da Skill](#b-construção-da-skill)
- [C) Resultados](#c-resultados)
- [D) Como Executar](#d-como-executar)
- [Estrutura do repositório](#estrutura-do-repositório)

---

## Revisão pós-avaliação (entrega v2)

A primeira entrega foi avaliada e recebeu esta solicitação de correção:

> No ecommerce-api-legacy, a Fase 3 rodou com a opção de manter o contrato e deixou três CRITICAL do próprio relatório abertos: as rotas de relatório financeiro e de exclusão de usuário continuam sem autenticação, o checkout continua sem verificar a senha da conta existente e o gateway simulado continua aprovando como PAID qualquer cartão que começa com "4". Ajuste a skill para que a opção de manter o contrato não possa deixar CRITICAL ou HIGH sem correção, acrescente ao playbook um padrão que resolva de fato o pagamento simulado (o P-09 hoje só isola esse código) e rode a skill de novo nesse projeto.

| Ponto solicitado | O que foi feito | Evidência |
|---|---|---|
| Rotas de relatório financeiro e exclusão sem autenticação | Exigem `Authorization: Bearer <ADMIN_API_KEY>`; sem a variável definida, negam tudo | F-003 em [audit-project-2.md](reports/audit-project-2.md); [E-08](reports/evidence/project-2/20261116-213657/E-08-final-execucao-local.log) |
| Checkout sem verificar a senha da conta existente | Senha verificada com scrypt; ausente ou incorreta responde 401 e nada é gravado | F-008; E-08. Classificado HIGH na v2 (era CRITICAL na v1, F-001), com justificativa no relatório; corrigido da mesma forma |
| Gateway simulado aprovando cartão iniciado em "4" | Novo padrão **P-20**: recusa por padrão sem provedor configurado; mock só com `PAYMENT_PROVIDER=mock` e `APP_ENV` em `test`/`development` | F-002; [P-20](ecommerce-api-legacy/.claude/skills/refactor-arch/references/05-playbook-refatoracao.md); E-08 |
| Opção de manter o contrato deixando CRITICAL/HIGH abertos | `Refatorar` passou a ser a primeira opção e a recomendada da pergunta de contrato; as 3 execuções usaram `Refatorar` e terminaram com 0 CRITICAL/HIGH abertos | [Critérios de aceite](#critérios-de-aceite-33-projetos); [07-politica-comandos-aprovacoes.md](ecommerce-api-legacy/.claude/skills/refactor-arch/references/07-politica-comandos-aprovacoes.md), seção 4 |
| Rodar a skill de novo no projeto | Executada a partir do código original, nos 3 projetos | Run `20261116-213657`: [audit-project-2.md](reports/audit-project-2.md); [E-04](reports/evidence/project-2/20261116-213657/E-04-baseline-execucao-local.log) × [E-08](reports/evidence/project-2/20261116-213657/E-08-final-execucao-local.log) (rotas administrativas 200 → 401 sem credencial; senha errada 200 → 401; pagamento sem provedor 200 → 400); [validação do projeto 2](docs/evidencias-adicionais/validacoes/validacao-project-2_2026-11-18_v3.md) |

**O que mudou na skill (1.1 → 1.2):**

- **Pergunta de contrato:** `Refatorar` (recomendado). As opções `Manter contrato*` e `Híbrido` existem para quando não for possível mudar o contrato e avisam quantos CRITICAL/HIGH ficariam abertos; não foram usadas nesta entrega.
- **P-20:** o pagamento simulado passa a ser corrigido em **todas** as opções.
- **Provas:** toda correção CRITICAL/HIGH ganha teste de unidade ou integração, e os endpoints são executados localmente com credenciais geradas pela própria aplicação (degrau V4), antes e depois da refatoração.

**Onde está a entrega anterior:** [historico/entrega-v1/](historico/entrega-v1/LEIA-ME.md) guarda relatórios, evidências, validações e README da v1. A tag git `entrega-v1` aponta para o repositório como foi entregue. O passo a passo desta revisão está em [05-controle-entrega-v2.md](docs/evidencias-adicionais/05-controle-entrega-v2.md).

---

## Processo: como o desafio foi resolvido

Linha do tempo completa em [00-timeline-execucao-desafio.md](docs/evidencias-adicionais/00-timeline-execucao-desafio.md).

| # | Etapa | Artefato |
|---|---|---|
| 1 | Leitura do desafio para entender objetivo, entregáveis e critérios de aceite | [docs/DESAFIO.md](docs/DESAFIO.md) |
| 2 | Análise manual dos 3 projetos (com apoio de IA, ver nota na seção A) | [01-relatorio-issues-analise-manual.md](docs/evidencias-adicionais/01-relatorio-issues-analise-manual.md) |
| 3 | Levantamento de como executar cada projeto e criação de **testes de caracterização** caixa-preta via HTTP (baseline para comparar antes/depois) | [02-relatorio-analise-execucao-testes.md](docs/evidencias-adicionais/02-relatorio-analise-execucao-testes.md) |
| 4 | Análise e decisões arquiteturais da skill | [03-analise-arquitetural-skill.md](docs/evidencias-adicionais/03-analise-arquitetural-skill.md) |
| 5 | Refinamento do escopo com IA e plano de ação | [04-plano-acao-criacao-skill.md](docs/evidencias-adicionais/04-plano-acao-criacao-skill.md) |
| 6 | Skill v1.0 e v1.1, execução nos 3 projetos e primeira entrega | [historico/entrega-v1/](historico/entrega-v1/LEIA-ME.md) |
| 7 | Avaliação, arquivamento da v1 e skill 1.2, com revisão independente antes de executar | [05-controle-entrega-v2.md](docs/evidencias-adicionais/05-controle-entrega-v2.md) |
| 8 | Restauração do código original e nova execução nos 3 projetos | [reports/](reports/) |
| 9 | Validação independente de cada execução, por agentes sem contexto da execução | [validacoes/](docs/evidencias-adicionais/validacoes/) |

---

## A) Análise Manual

A análise foi feita **antes** de criar a skill, com apoio de IA (um modelo mais simples), por falta de familiaridade com as linguagens; os achados foram revisados e usados como insumo do catálogo de anti-patterns e como gabarito para avaliar a skill. Relatório completo, com local exato e justificativa de cada item: [01-relatorio-issues-analise-manual.md](docs/evidencias-adicionais/01-relatorio-issues-analise-manual.md).

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| code-smells-project | 6 | 5 | 8 | 6 | 25 |
| ecommerce-api-legacy | 6 | 6 | 6 | 5 | 23 |
| task-manager-api | 5 | 4 | 9 | 5 | 23 |

Abaixo, os principais problemas de cada projeto.

### code-smells-project (Python/Flask — API de E-commerce)

| ID | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| CS-C1 | CRITICAL | SQL Injection: queries montadas por concatenação com dados do request | `models.py` (28, 48-50, 92, 110, 127-128, 140-166…) | Bypass de login (`' OR '1'='1`), leitura, alteração e exclusão arbitrária de dados |
| CS-C2 | CRITICAL | `POST /admin/query` executa SQL enviado no body, sem autenticação | `app.py:59-78` | Qualquer cliente lê, altera ou destrói todo o banco |
| CS-C4 | CRITICAL | `SECRET_KEY` hardcoded e devolvida em `/health`; senha do admin no seed | `app.py:7`, `controllers.py:285-289`, `database.py:76` | Vazamento pelo repositório e por endpoint público; permite forjar sessões |
| CS-C5 | CRITICAL | Senhas em texto puro e retornadas em `GET /usuarios` | `models.py:83, 99, 110, 128` | Qualquer consulta expõe credenciais reais |
| CS-H1 | HIGH | Regras de negócio (desconto, estoque, pedido) em models/controllers; sem camada de serviço | `models.py:133-169, 235-273` | Lógica não testável isoladamente; mudanças afetam várias camadas |
| CS-H2 | HIGH | Conexão SQLite global mutável com `check_same_thread=False` | `database.py:4-12` | Não é thread-safe e impede isolamento em testes |
| CS-M1 | MEDIUM | Queries N+1 na listagem de pedidos (3 níveis de loop com queries) | `models.py:171-233` | Número de consultas cresce com o volume de dados |
| CS-M3 | MEDIUM | Validações ausentes (tipos, quantidade ≤ 0, e-mail) | `controllers.py:43-46, 198-203…` | Erros 500 e manipulação de estoque/preço |
| CS-M4 | MEDIUM | `str(e)` devolvido ao cliente; sem handler global | `controllers.py` (~20 respostas) | Vaza detalhes de SQL e estrutura interna |
| CS-L1 | LOW | Magic numbers nas faixas de desconto e limites | `models.py:257-262`, `controllers.py:47-52` | Regra de negócio escondida em literais |
| CS-L4 | LOW | `print()` no lugar de logging, inclusive com e-mail do usuário | `controllers.py` (8, 57, 179…) | Sem níveis/destino configurável; dado pessoal em stdout |

### ecommerce-api-legacy (Node.js/Express — LMS API com checkout)

| ID | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| EC-C1 | CRITICAL | Senha de banco, chave de gateway `pk_live_...` e usuário SMTP no fonte | `utils.js:1-7` | Segredos versionados; chave "live" permite uso indevido do gateway |
| EC-C2 | CRITICAL | Número completo do cartão registrado em log | `AppManager.js:45` | Violação de PCI-DSS e LGPD |
| EC-C3 | CRITICAL | Pagamento aprovado se o cartão começa com "4" | `AppManager.js:46-48` | Matrícula sem pagamento real; fraude trivial |
| EC-C6 | CRITICAL | God Class `AppManager`: banco, schema, seed, rotas, checkout e relatório | `AppManager.js:4-139` | Quebra total de separação de responsabilidades |
| EC-H3 | HIGH | Callback hell com até 6 níveis e contadores manuais | `AppManager.js:37-78, 83-128` | Difícil de ler, propenso a erros de fluxo |
| EC-H4 | HIGH | Estado global mutável (`globalCache` sem limite, `totalRevenue`) | `utils.js:9-15, 25` | Vazamento de memória e estado compartilhado entre requisições |
| EC-M1 | MEDIUM | Queries N+1 no relatório financeiro | `AppManager.js:83-126` | Consultas crescem linearmente com os dados |
| EC-M4 | MEDIUM | Sem tratamento de erro central, rate limit ou cabeçalhos de segurança | `app.js:5-10` | Exceções derrubam rotas; sem proteção contra abuso |
| EC-L1 | LOW | Nomes crípticos (`u`, `e`, `p`, `cc`, payload `usr`/`eml`/`pwd`) | `AppManager.js:29-33` | Baixa legibilidade |
| EC-L2 | LOW | Magic numbers e strings (`10000`, `"4"`, `"PAID"`, `"123456"`) | `utils.js:19-22`, `AppManager.js:46, 68` | Significado oculto; deveriam ser constantes |

### task-manager-api (Python/Flask — Task Manager, parcialmente organizado)

| ID | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| TM-C1 | CRITICAL | `SECRET_KEY` e credenciais SMTP no código; `debug=True` em `0.0.0.0` | `app.py:13, 34`, `services/notification_service.py:9-10` | Credenciais versionadas; debugger do Werkzeug permite execução remota |
| TM-C2 | CRITICAL | Hash de senha com MD5 sem salt | `models/user.py:27-32` | Quebrável por rainbow tables |
| TM-C4 | CRITICAL | Login devolve `fake-jwt-token-<id>`; nenhuma rota valida token | `routes/user_routes.py:207-211` | Qualquer pessoa lista/apaga usuários e tarefas |
| TM-C5 | CRITICAL | `POST /users` aceita `role: "admin"` do cliente | `routes/user_routes.py:52, 71-78` | Escalação de privilégio por qualquer visitante |
| TM-H1 | HIGH | Regras de negócio nos handlers; `services/` com serviço nunca usado | `routes/*.py` | Controllers gordos, difíceis de testar |
| TM-H2 | HIGH | CRUD de categorias dentro do blueprint de relatórios | `routes/report_routes.py:157-223` | Viola SRP/MVC |
| TM-M1 | MEDIUM | Queries N+1 (`User.query.get` por tarefa, `len(u.tasks)` por usuário) | `routes/task_routes.py:41-57`… | Consultas crescem com os dados |
| TM-M4 | MEDIUM | `except:` genérico descartando o erro | `task_routes.py:62, 137…` | Oculta bugs e dificulta diagnóstico |
| TM-M7 | MEDIUM | APIs deprecated: `Model.query.get()` e `datetime.utcnow()` | rotas e `models/*.py` | Warnings hoje e quebra em versões futuras |
| TM-L1 | LOW | Imports não utilizados (`os`, `sys`, `json`, `time`…) | `app.py:7`, `routes/*.py`, `helpers.py:2-7` | Ruído e dependências falsas |
| TM-L2 | LOW | Magic numbers e listas de status/roles repetidas | `task_routes.py:96-113`, `user_routes.py:64, 71` | Alterar uma regra exige editar vários pontos |

---

## B) Construção da Skill

Skill: [`.claude/skills/refactor-arch/`](code-smells-project/.claude/skills/refactor-arch/) — cópia idêntica em [ecommerce-api-legacy](ecommerce-api-legacy/.claude/skills/refactor-arch/) e [task-manager-api](task-manager-api/.claude/skills/refactor-arch/). Documentos de projeto: [03-analise-arquitetural-skill.md](docs/evidencias-adicionais/03-analise-arquitetural-skill.md) e [04-plano-acao-criacao-skill.md](docs/evidencias-adicionais/04-plano-acao-criacao-skill.md).

### Decisões de design

**`SKILL.md` curto como orquestrador + conhecimento em referências carregadas por fase.** Cada fase lê só o que precisa, o que reduz contexto e evita que o agente adiante a refatoração:

| Fase | O que faz | Referências lidas |
|---|---|---|
| 1 — Análise | detecta stack, banco, domínio, arquitetura (por papel do código), superfície de ataque e **como validar** | `01-analise-projeto.md` |
| 2 — Auditoria | cruza o código com o catálogo, gera e salva o relatório, **pausa e pergunta** | `02-catalogo-antipatterns.md`, `03-template-relatorio.md`, `07-politica-comandos-aprovacoes.md` |
| 3 — Refatoração | aplica as mudanças aprovadas, valida com evidências, reaudita | `04-guidelines-mvc.md`, `05-playbook-refatoracao.md`, `06-protocolo-validacao.md`, `07-politica-comandos-aprovacoes.md` |

**Cobertura das 5 áreas obrigatórias** (+ 2 áreas adicionais):

| Área de conhecimento | Arquivo | Conteúdo |
|---|---|---|
| Análise de projeto | [01-analise-projeto.md](code-smells-project/.claude/skills/refactor-arch/references/01-analise-projeto.md) | manifestos, framework e versão, banco, domínio, arquitetura por papel, superfície de ataque, inventário de validação e de credenciais de teste |
| Catálogo de anti-patterns | [02-catalogo-antipatterns.md](code-smells-project/.claude/skills/refactor-arch/references/02-catalogo-antipatterns.md) | 42 entradas com sinal de detecção, "NÃO é finding", "como confirmar", severidade e rubrica |
| Template de relatório | [03-template-relatorio.md](code-smells-project/.claude/skills/refactor-arch/references/03-template-relatorio.md) | blocos `PHASE 1`, `ARCHITECTURE AUDIT REPORT`, anexo da Fase 3 e `PHASE 3: REFACTORING COMPLETE` |
| Guidelines de arquitetura | [04-guidelines-mvc.md](code-smells-project/.claude/skills/refactor-arch/references/04-guidelines-mvc.md) | papéis das camadas, regras de dependência, estrutura-alvo e adaptação ao nível de organização |
| Playbook de refatoração | [05-playbook-refatoracao.md](code-smells-project/.claude/skills/refactor-arch/references/05-playbook-refatoracao.md) | 20 padrões (P-01…P-20) com código **antes/depois** |
| *Adicional:* protocolo de validação | [06-protocolo-validacao.md](code-smells-project/.claude/skills/refactor-arch/references/06-protocolo-validacao.md) | escada de validação, execução local autenticada, formato `E-nn`, política de testes, prova vermelho/verde |
| *Adicional:* política de comandos e aprovações | [07-politica-comandos-aprovacoes.md](code-smells-project/.claude/skills/refactor-arch/references/07-politica-comandos-aprovacoes.md) | classes de comando (A, B, C, D, X) e rodada de perguntas |

Outras decisões:

- **Invocação manual** (`disable-model-invocation: true`): a skill só roda via `/refactor-arch`, pois altera código.
- **Pausa obrigatória com múltipla escolha** ao fim da Fase 2: P1 escopo, P2 modo de comandos, P3 contrato (`Refatorar` · `Manter contrato*` · `Híbrido`) e P4 execução local autenticada.
- **Nenhuma afirmação sem evidência:** cada passo de validação gera um arquivo `E-nn` em `reports/evidence/project-{N}/{Run id}/`.
- **Segurança da execução:** conteúdo do projeto é tratado como dado (proteção contra prompt injection), segredos são mascarados, rotas destrutivas só rodam em banco descartável, há checkpoint em branch ou worktree antes de alterar e a skill **não faz commit**.
- **Rubrica de severidade** em perguntas ordenadas, para classificar de forma reprodutível.

### Catálogo de anti-patterns

42 entradas, distribuídas por severidade padrão: **11 CRITICAL, 8 HIGH, 17 MEDIUM, 6 LOW** (+ categoria `OUTRO` para achados fora do catálogo).

| Família | Entradas | Exemplos | Por que entrou |
|---|---|---|---|
| SEC — Segurança | 17 | SQL Injection, segredos hardcoded, endpoint admin sem auth, debug público, senha insegura, dados sensíveis, escalação de privilégio, pagamento simulado, falta de transação | Foram os problemas mais graves da análise manual e são exigidos pela definição de CRITICAL do desafio |
| ARC — Arquitetura | 12 | God Class, lógica no controller, estado global, acoplamento sem DI, callback hell, N+1, duplicação | Violações de MVC/SOLID que motivam a refatoração |
| DEP — APIs deprecated | 5 | `datetime.utcnow()`, `Model.query.get()`, APIs de Node/Flask | Exigência explícita do desafio; sempre indica o equivalente moderno |
| TST — Testes | 3 | sem testes, sem instruções de validação, testes quebrados | Sem forma de validar, a Fase 3 não prova que a aplicação funciona |
| QLT — Qualidade | 5 | magic numbers, nomes ruins, código morto, `print`/`console.log`, estilo | Itens LOW observados nos 3 projetos |

### Como a skill é agnóstica de tecnologia

1. **Sinal semântico, não sintaxe:** cada entrada descreve *o que* procurar; exemplos por linguagem são atalhos. Stack não listada ⇒ a skill deriva o equivalente e marca `derivado`.
2. **Arquitetura classificada por papel do código**, não por nome de pasta.
3. **Comandos descobertos no projeto** (manifestos, README, scripts, testes, `api.http`), nunca embutidos na skill.
4. **Guidelines MVC adaptáveis:** monólito ⇒ criar camadas; parcialmente organizado ⇒ mover só o que está fora do lugar.
5. **Escada de validação** que degrada com aviso: testes do projeto → scripts → boot + requisições existentes → execução local autenticada → verificação estática.
6. **Nenhuma referência aos projetos de exemplo** dentro da skill.
7. **Prova:** a mesma skill rodou em Flask monolítico, Express com God Class e Flask parcialmente em camadas.

### Desafios encontrados e como foram resolvidos

| Desafio | Solução |
|---|---|
| Os projetos não tinham testes; sem baseline não há como provar que "continua funcionando" | Antes da skill, criei suítes de caracterização caixa-preta via HTTP (23 / 8 / 25 testes) ([relatório](docs/evidencias-adicionais/02-relatorio-analise-execucao-testes.md)) |
| Pouca familiaridade com Python e Node | Análise manual com apoio de IA e skill construída para atuar como "dev novo no projeto" |
| Corrigir CRITICAL de segurança muda o contrato da API, mas o desafio pede que os endpoints continuem respondendo | Pergunta P3 explícita, criada por essa ambiguidade do enunciado; os testes originais continuam válidos com credencial de teste e testes novos provam cada mudança: **verdes** no código novo e **vermelhos** no original |
| v1.0: Fase 1 sem registro, regra "nunca edite testes" em conflito com contrato aprovado, senhas de seed no fonte ([pontos de atenção](historico/entrega-v1/validacoes/validacao-project-1_2026-11-05_v1.md)) | v1.1: evidência `E-00`, política de alteração de testes, prova vermelho/verde e senhas por `SEED_*` |
| v1.1: a opção de manter o contrato deixou CRITICAL abertos e o P-09 apenas isolava o pagamento simulado (avaliação da entrega) | v1.2: 3 opções na P3, segunda confirmação, P-20, testes de prova em qualquer opção e execução local autenticada |
| Revisão independente da v1.2 apontou fail-open no P-20 e contradições de política antes da execução | Mock só por lista branca de ambiente, nunca como padrão; exceção explícita para o diretório temporário; status `ALTERADO (correção F-xxx, sem contrato)` |
| Reauditoria do task-manager-api achou um HIGH novo (usuário comum acessando dados de terceiros), e a validação independente reprovou duas vezes (leituras de tasks abertas; token de conta excluída reaproveitado pelo mesmo id) | A skill parou e perguntou; a correção C-17 / CT-09 foi incluída e completada após cada reprovação, com o token vinculado à conta, repetindo toda a validação |
| Ambiente Windows: reloader do Flask, porta 5000 compartilhada, encoding, comandos com aspas aninhadas | Encerramento da árvore de processos, um projeto Flask por vez e scripts temporários fora do projeto |

---

## C) Resultados

### Findings por severidade (Fase 2)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Ocorrências | Deprecated |
|---|---:|---:|---:|---:|---:|---:|---|
| code-smells-project | 9 | 6 | 10 | 6 | **31** | 146 | buscadas; nenhuma para Flask 3.1.1 / Python 3.14 |
| ecommerce-api-legacy | 6 | 7 | 7 | 5 | **25** | 53 | buscadas; nenhuma para Express 4.22 / Node 24 |
| task-manager-api | 7 | 4 | 11 | 6 | **28** | 181 | F-021 `datetime.utcnow()`, F-022 `Query.get()` |

No task-manager-api, a reauditoria acrescentou o **F-029** (HIGH, SEC-11), corrigido na mesma execução.

### Análise manual × skill

No projeto 1, a skill encontrou os problemas da análise manual (o desafio pede no mínimo 5):

| Análise manual | Finding da skill |
|---|---|
| CS-C1 SQL Injection | F-008 SEC-01 |
| CS-C2 `/admin/query` executa SQL | F-005 SEC-04 |
| CS-C3 reset do banco sem auth | F-004 SEC-03 |
| CS-C4 segredos hardcoded | F-001 SEC-02 + F-006 SEC-07 |
| CS-C5 senhas em texto puro | F-007 SEC-06 + F-006 SEC-07 |
| CS-C6 debug e bind 0.0.0.0 | F-002 SEC-05 |
| CS-H1 regra de negócio em model/controller | F-014 ARC-02 + F-009 ARC-01 |
| CS-H2 conexão global mutável | F-015 ARC-03 |
| CS-H3 pedido sem transação | F-012 SEC-15 |
| CS-H4 sem autenticação / CORS aberto | F-003 SEC-09 + F-016 SEC-17 |
| CS-H5 acoplamento sem DI | F-013 ARC-04 |
| CS-M1 N+1 | F-024 ARC-07 |
| CS-M2 código duplicado | F-020 ARC-08 |
| CS-M3 validações ausentes | F-010 SEC-12 |
| CS-M4 detalhes internos nos erros | F-017 SEC-13 + F-019 ARC-09 |
| CS-M5 dinheiro em float | F-022 ARC-12 |
| CS-M6 schema sem constraints | F-021 ARC-10 |
| CS-M7 fluxo de status/cancelamento | F-025 OUTRO-01 (parcial: status de pedido inexistente) |
| CS-M8 sem paginação / `SELECT *` | F-023 ARC-11 |
| CS-L1 magic numbers | F-030 QLT-01 |
| CS-L2 nomes ruins | F-029 QLT-02 |
| CS-L3 imports não usados | F-031 QLT-03 |
| CS-L4 `print` no lugar de logging | F-027 QLT-04 + F-011 SEC-08 |
| CS-L6 estilo inconsistente | F-028 QLT-05 |

Nos projetos 2 e 3 os principais itens também foram detectados: EC-C1→F-004, EC-C2→F-001, EC-C3→F-002, EC-C4→F-005, EC-C5→F-003, EC-C6→F-006; TM-C1→F-001/F-003, TM-C2→F-005, TM-C3→F-004, TM-C4→F-002, TM-C5→F-007, TM-M7→F-021/F-022.

As severidades podem diferir da análise manual (ex.: CS-H4 HIGH → F-003 CRITICAL) porque a rubrica do catálogo classifica pelo impacto concreto.

### Antes × depois da estrutura

**code-smells-project** — monólito de 4 arquivos → camadas MVC completas.

```
ANTES                                   DEPOIS
app.py         entry + config + rotas   app.py          composition root (create_app)
controllers.py handlers + regra + SQL   config/         settings.py, logging_config.py
models.py      SQL + regra + serializ.  database/       connection.py, schema.py
database.py    conexão global + seed    models/         produto, usuario, pedido, admin
                                        services/       regras de negócio, auth, dinheiro, erros
                                        controllers/    fluxo por domínio + validators.py
                                        routes/         blueprints + proteção por rota
                                        views/          serializers.py (DTOs)
                                        middlewares/    auth.py, errors.py, security.py
```

**ecommerce-api-legacy** — God Class → camadas MVC em `src/`.

```
ANTES                                   DEPOIS
src/app.js                              src/app.js       composition root + entry point
src/AppManager.js  God Class            src/config/      settings.js, constants.js
src/utils.js       config + cache +     src/database/    connection.js, schema.js
                   "crypto" + log       src/models/      user, course, enrollment, payment, auditLog, report
                                        src/services/    checkout, password, report, user, payment/gatewayFactory
                                        src/controllers/ checkout, report, user
                                        src/routes/      index.js
                                        src/middlewares/ errorHandler, rateLimiter, requireAdmin, securityHeaders
                                        src/validators/  checkoutValidator.js
                                        src/errors/, src/utils/
```

**task-manager-api** — camadas parciais → camadas completas.

```
ANTES                                   DEPOIS
app.py          entry + config literal  app.py          composition root (create_app)
models/         models + MD5 + to_dict  config/         settings.py
routes/         rotas + controller +    models/         entidades + consultas
                regra + SQL             validators/     common, task, user, category
services/       1 serviço sem uso       services/       auth, token, task, user, category, report
utils/          helpers sem uso         controllers/    auth, task, user, category, report
                                        routes/         só mapeamento
                                        views/          serializers.py (DTOs sem senha)
                                        middleware/     auth, error_handler, security
```

| Métrica | P1 antes → depois | P2 antes → depois | P3 antes → depois |
|---|---|---|---|
| Arquivos-fonte | 4 → 35 | 3 → 28 | 15 → 45 |
| Linhas de código | ~780 → ~1220 | ~180 → ~693 | ~1158 → ~1588 |
| Maior arquivo | `models.py` (314) → `controllers/validators.py` (121) | `AppManager.js` (141) → `app.js` (78) | `routes/task_routes.py` (299) → `validators/task_validator.py` (136) |
| Arquivos com 3+ papéis | 3 → 0 | 2 → 0 | 4 → 0 |
| Rotas da API | 19 → 18 (`/admin/query` removida) | 3 → 3 | 22 → 22 |
| Testes | 23 → 51 (+9 unidade, +19 integração) | 8 → 33 (+18 unidade, +7 integração) | 25 → 141 (+42 unidade, +74 integração) |

### Checklist de validação

`✅` atendido com evidência · `~` parcial (finding residual citado). O checklist completo, com a evidência de cada item, está na seção "Checklist de Validação" de cada relatório.

| Item | P1 | P2 | P3 |
|---|:-:|:-:|:-:|
| **Fase 1** — Linguagem detectada corretamente | ✅ | ✅ | ✅ |
| Framework detectado corretamente | ✅ | ✅ | ✅ |
| Domínio da aplicação descrito corretamente | ✅ | ✅ | ✅ |
| Número de arquivos analisados condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 15 |
| **Fase 2** — Relatório segue o template das referências | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados por severidade (CRITICAL → LOW) | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 31 | ✅ 25 | ✅ 28 |
| Detecção de APIs deprecated | ✅ nenhuma | ✅ nenhuma | ✅ 2 |
| Skill pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura de diretórios segue MVC | ✅ | ✅ | ✅ |
| Configuração extraída para módulo de config (sem hardcoded) | ✅ | ✅ | ✅ |
| Models criados para abstrair dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ~ (1) | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem corretamente | ✅ (2) | ✅ (2) | ✅ (2) |

1. Handler central existe e é usado; erros continuam em texto e sucessos em JSON para preservar o formato (F-019, parcial).
2. Com mudanças de contrato aprovadas (ver abaixo), comprovadas por testes e pela execução local.

### Evidências de execução (logs)

| Evidência | P1 — [20261116-195523](reports/evidence/project-1/20261116-195523/) | P2 — [20261116-213657](reports/evidence/project-2/20261116-213657/) | P3 — [20261116-214549](reports/evidence/project-3/20261116-214549/) |
|---|---|---|---|
| Fase 1 (bloco `PHASE 1`) | [E-00](reports/evidence/project-1/20261116-195523/E-00-fase1-analise.txt) | [E-00](reports/evidence/project-2/20261116-213657/E-00-fase1-analise.txt) | [E-00](reports/evidence/project-3/20261116-214549/E-00-fase1-analise.txt) |
| Testes no código original | [E-02](reports/evidence/project-1/20261116-195523/E-02-baseline-pytest.log) 23 passed | [E-02](reports/evidence/project-2/20261116-213657/E-02-baseline-npm-test.log) 8 pass | [E-01](reports/evidence/project-3/20261116-214549/E-01-baseline-pytest.log) 25 passed |
| Execução local no original | [E-03](reports/evidence/project-1/20261116-195523/E-03-baseline-execucao-local.log) | [E-04](reports/evidence/project-2/20261116-213657/E-04-baseline-execucao-local.log) | [E-18](reports/evidence/project-3/20261116-214549/E-18-baseline-execucao-local.log) |
| Testes após refatoração | [E-05](reports/evidence/project-1/20261116-195523/E-05-final-pytest.log) **51 passed** | [E-06](reports/evidence/project-2/20261116-213657/E-06-final-npm-test.log) **33 pass** | [E-19](reports/evidence/project-3/20261116-214549/E-19-final-pytest.log) **141 passed** |
| Execução local autenticada após refatoração | [E-07](reports/evidence/project-1/20261116-195523/E-07-final-execucao-local.log) 52 requisições | [E-08](reports/evidence/project-2/20261116-213657/E-08-final-execucao-local.log) 21 requisições | [E-21](reports/evidence/project-3/20261116-214549/E-21-final-execucao-local.log) 171 requisições |
| Prova vermelha no código original | [E-08](reports/evidence/project-1/20261116-195523/E-08-prova-vermelha-checkpoint.log) 28 falham | [E-09](reports/evidence/project-2/20261116-213657/E-09-sensibilidade-checkpoint.log) 14 falhas | [E-20](reports/evidence/project-3/20261116-214549/E-20-prova-vermelha-checkpoint.log) 103 falhas + 7 erros |
| Diff dos testes | [E-10](reports/evidence/project-1/20261116-195523/E-10-diff-testes.patch) | [E-10](reports/evidence/project-2/20261116-213657/E-10-diff-testes.patch) | [E-25](reports/evidence/project-3/20261116-214549/E-25-diff-testes.patch) |

Trechos dos logs:

```text
# P1 — E-05-final-pytest.log
tests\test_unidade.py .........                                          [100%]
============================= 51 passed in 10.02s =============================

# P2 — E-08-final-execucao-local.log (credenciais aleatórias, mascaradas)
01 | GET /api/admin/financial-report | cred=sem | status 401
02 | GET /api/admin/financial-report | cred=inválida | status 401
03 | GET /api/admin/financial-report | cred=admin | status 200

# P3 — E-19-final-pytest.log
141 passed
```

### Validação independente

Cada execução foi conferida por um agente sem contexto da execução, que reexecutou os testes, subiu a aplicação e comparou o relatório com o código original.

| Projeto | Resultado | Documento |
|---|---|---|
| code-smells-project | Aprovado, com ressalvas não bloqueantes | [validacao-project-1](docs/evidencias-adicionais/validacoes/validacao-project-1_2026-11-16_v3.md) |
| ecommerce-api-legacy | Aprovado, com ressalvas não bloqueantes | [validacao-project-2](docs/evidencias-adicionais/validacoes/validacao-project-2_2026-11-18_v3.md) |
| task-manager-api | Aprovado na 3ª rodada, com ressalvas não bloqueantes; as rodadas 1 e 2 reprovaram por correção incompleta do F-029 e por token reaproveitado pelo mesmo id, ambos corrigidos | [validacao-project-3](docs/evidencias-adicionais/validacoes/validacao-project-3_2026-11-18_v3.md) |

### Mudanças de contrato (endpoints originais)

Os 3 projetos usaram a opção **Refatorar**. Cada mudança tem justificativa na seção "Contratos — resultado" do relatório e prova nos testes e na execução local.

- **P1 — 12 mudanças:** `POST /admin/query` removida; rotas administrativas, de escrita de produtos, de usuários e de pedidos exigem o token de `POST /login`, com checagem de perfil e de propriedade; `senha` e configuração interna saem das respostas; CORS restrito; três casos inválidos passam a responder 404/400.
- **P2 — 4 mudanças:** relatório financeiro e exclusão de usuário exigem `ADMIN_API_KEY`; checkout de conta existente exige a senha correta; exclusão remove matrículas e pagamentos e responde 404 para id inexistente. Sem provedor configurado, o pagamento é recusado (P-20).
- **P3 — 9 mudanças:** rotas de dados exigem token assinado e vinculado à conta (id reaproveitado ou troca de senha invalidam tokens antigos); `password` sai das respostas; `role`/`active` e exclusões só por admin; CORS restrito; validação de entrada; listagens limitadas a 100 itens; leitura, alteração e atribuição de tasks restritas ao responsável e à gestão (`admin`/`manager`).

### Itens residuais (reauditoria)

Nenhum CRITICAL/HIGH ficou sem correção. Permanecem:

- **Ação manual nos 3 projetos:** rotacionar os segredos antigos que continuam no histórico git.
- **P1:** F-018 (`pip-audit`/lock), F-021, F-022 e F-023 parciais (migração do banco existente, coluna monetária `REAL`, paginação), F-026 (README do projeto) e OUTRO-02 (limite de login em memória).
- **P2:** F-018 (relatório sem paginação), F-019 (erros em texto) e F-025 (chaves do payload), mantidos para preservar o contrato. Integração com provedor de pagamento real fica pendente: sem ela, o checkout recusa todo pagamento fora do modo mock.
- **P3:** F-013 (lock e versões), F-014 (senha mínima de 4 caracteres), F-016 (schema sem `ondelete`), F-018 (paginação parcial), F-023 (README do projeto), F-025 (formato de datas) e R-01, R-03 a R-07 (categorias editáveis por qualquer autenticado, possível enumeração de e-mail no login e no cadastro, e-mail com caixa diferente criando conta separada, 403 × 404 revelando ids existentes, id com milhares de dígitos respondendo 405).

Pontos adicionais apontados pelas validações independentes, sem correção nesta entrega:

- **P1:** `POST /produtos` com `Infinity`/`NaN` responde 500 em vez de 400 (rota restrita a admin; nada é gravado).
- **P3:** token emitido antes de uma desativação volta a valer se a conta for reativada (dentro da validade de 1 h); falta teste automatizado para conta inativa.
- **P2:** e-mail com caixa diferente cria conta separada; `CHECKOUT_RATE_LIMIT_MAX` não numérico desativa o limite; compras simultâneas com o mesmo e-mail novo exigem tratamento de estorno antes de integrar um provedor real. A ressalva de não haver teste para "sem `ADMIN_API_KEY`, as rotas administrativas negam tudo" foi verificada por fora, sem alterar o código: 10/10 casos OK, com 401 sem a chave e 200 só com a chave correta ([evidência complementar](docs/evidencias-adicionais/validacoes/evidencia-project-2-admin-sem-chave_2026-11-20.md)).
- **READMEs dos projetos e `api.http`:** continuam com as instruções originais; use a seção [Como Executar](#d-como-executar) deste documento. Nada carrega o arquivo `.env` automaticamente: as variáveis precisam estar exportadas no shell.

### Comportamento da skill em stacks diferentes

| Projeto | Nível de organização detectado | Como a Fase 3 se adaptou |
|---|---|---|
| code-smells-project | `monolito-sem-camadas` | Criou todas as camadas por domínio, com app factory e blueprints |
| ecommerce-api-legacy | `monolito-sem-camadas` (God Class) | Criou todas as camadas e manteve `src/app.js` como entry point; callbacks viraram `async/await`; aplicou o P-20 |
| task-manager-api | `parcialmente-em-camadas` | Manteve models e blueprints, moveu regra e dados para as camadas corretas e corrigiu as APIs deprecated |

A execução foi feita por agentes do Claude Code seguindo o `SKILL.md`, com pausa real na Fase 2. As respostas às perguntas foram enviadas conforme as decisões registradas em [05-controle-entrega-v2.md](docs/evidencias-adicionais/05-controle-entrega-v2.md).

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado.
- Git.
- Python 3 (testado com 3.14.0) para os projetos Flask.
- Node.js 18+ (necessário para `node --test`; testado com 24.11.1) e npm para o projeto Express.

### Executar a skill

A skill fica em `.claude/skills/refactor-arch/` dentro de cada projeto e é invocada manualmente:

```bash
cd code-smells-project
claude "/refactor-arch"
```

```bash
cd ecommerce-api-legacy
claude "/refactor-arch"
```

```bash
cd task-manager-api
claude "/refactor-arch"
```

Fluxo: a Fase 1 imprime `PHASE 1: PROJECT ANALYSIS`; a Fase 2 salva `reports/audit-project-{N}.md` na raiz do repositório e para em `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` com as perguntas P1–P4; a Fase 3 cria o checkpoint, refatora, valida e anexa os resultados ao relatório. A skill não faz commit.

### Validar os projetos refatorados

Os testes sobem a aplicação real e geram as próprias credenciais de teste. `code-smells-project` e `task-manager-api` usam a porta 5000: rode um de cada vez.

**code-smells-project** (esperado: `51 passed`)

```bash
cd code-smells-project
python -m venv .venv
source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

**ecommerce-api-legacy** (esperado: `33 pass, 0 fail`)

```bash
cd ecommerce-api-legacy
npm install
npm test
```

**task-manager-api** (esperado: `141 passed`)

```bash
cd task-manager-api
python -m venv .venv
source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

### Rodar as aplicações manualmente

Cada projeto tem um `.env.example` com os nomes das variáveis. **Exporte-as no shell antes de iniciar**, pois nada carrega o `.env` automaticamente.

| Projeto | Variáveis principais | Comandos | URL |
|---|---|---|---|
| code-smells-project | `SECRET_KEY`, `SEED_ADMIN_PASSWORD`, `SEED_CLIENTE_PASSWORD`, `CORS_ORIGINS` | `pip install -r requirements.txt` → `python app.py` | http://localhost:5000 |
| ecommerce-api-legacy | `ADMIN_API_KEY`, `SEED_USER_PASSWORD`, `APP_ENV`, `PAYMENT_PROVIDER`, `PAYMENT_MOCK_APPROVED_PREFIXES` | `npm install` → `npm start` | http://localhost:3000 |
| task-manager-api | `SECRET_KEY`, `SEED_ADMIN_PASSWORD`, `SEED_MANAGER_PASSWORD`, `SEED_USER_PASSWORD`, `CORS_ORIGINS` | `pip install -r requirements.txt` → `python seed.py` → `python app.py` | http://localhost:5000 |

Observações:

- **Autenticação:** nos projetos 1 e 3, obtenha o token em `POST /login` e envie `Authorization: Bearer <token>`. No projeto 2, as rotas administrativas usam `Authorization: Bearer <ADMIN_API_KEY>`.
- **Pagamento no projeto 2:** sem `PAYMENT_PROVIDER`, todo pagamento é recusado. Para desenvolvimento local, use `APP_ENV=development`, `PAYMENT_PROVIDER=mock` e `PAYMENT_MOCK_APPROVED_PREFIXES=4`. O mock é bloqueado em qualquer outro ambiente.
- **Usuários de demonstração:** no projeto 1, sem as variáveis `SEED_*`, os usuários não são criados. No projeto 3, o `seed.py` apaga e recria os dados.

---

## Estrutura do repositório

```
.
├── README.md                          # este documento
├── docs/
│   ├── DESAFIO.md                     # enunciado original do desafio
│   └── evidencias-adicionais/         # timeline, análises, plano, controle da v2
│       └── validacoes/                # validações independentes da entrega v2
├── historico/
│   └── entrega-v1/                    # relatórios, evidências, validações e README da v1
├── code-smells-project/               # Projeto 1 — refatorado
│   └── .claude/skills/refactor-arch/  # SKILL.md + 7 referências
├── ecommerce-api-legacy/              # Projeto 2 — refatorado
│   └── .claude/skills/refactor-arch/  # cópia da skill
├── task-manager-api/                  # Projeto 3 — refatorado
│   └── .claude/skills/refactor-arch/  # cópia da skill
└── reports/
    ├── audit-project-{1,2,3}.md       # saída da Fase 2 + anexo da Fase 3
    └── evidence/project-{1,2,3}/      # evidências E-nn de cada execução
```

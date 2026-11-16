# refactor-arch — Refatoração Arquitetural Automatizada com Claude Code

Solução do desafio **"Criação de Skills — Refatoração Arquitetural Automatizada"** (enunciado original em [docs/DESAFIO.md](docs/DESAFIO.md)).

A skill `refactor-arch` (Claude Code) analisa uma codebase de backend, audita anti-patterns e vulnerabilidades com severidade, arquivo e linha, gera um relatório, **pausa para confirmação** e, após aprovação, refatora para MVC e valida com evidências reais de execução. Foi executada, sem nenhuma alteração entre um projeto e outro, nos 3 projetos do repositório.

## Critérios de aceite (3/3 projetos)

| Critério | code-smells-project (Python/Flask) | ecommerce-api-legacy (Node/Express) | task-manager-api (Python/Flask) |
|---|---|---|---|
| Fase 1 detecta stack corretamente | ✅ Python 3.14 + Flask 3.1.1 | ✅ Node.js 24 + Express 4.22.1 | ✅ Python 3.14 + Flask 3.0.0 / Flask-SQLAlchemy |
| Fase 2 encontra >= 5 findings | ✅ 31 | ✅ 25 | ✅ 28 |
| Fase 2 inclui >= 1 CRITICAL ou HIGH | ✅ 9 CRITICAL, 6 HIGH | ✅ 8 CRITICAL, 5 HIGH | ✅ 7 CRITICAL, 4 HIGH |
| Fase 3: aplicação funciona após refatoração | ✅ 35/35 testes | ✅ 8/8 testes + boot + `api.http` | ✅ 35/35 testes |
| Relatório | [audit-project-1.md](reports/audit-project-1.md) | [audit-project-2.md](reports/audit-project-2.md) | [audit-project-3.md](reports/audit-project-3.md) |

## Sumário

- [Processo: como o desafio foi resolvido](#processo-como-o-desafio-foi-resolvido)
- [A) Análise Manual](#a-análise-manual)
- [B) Construção da Skill](#b-construção-da-skill)
- [C) Resultados](#c-resultados)
- [D) Como Executar](#d-como-executar)
- [Estrutura do repositório](#estrutura-do-repositório)

---

## Processo: como o desafio foi resolvido

Linha do tempo completa em [00-timeline-execucao-desafio.md](docs/evidencias-adicionais/00-timeline-execucao-desafio.md).

| # | Etapa | Artefato |
|---|---|---|
| 1 | Leitura do desafio para entender objetivo, entregáveis e critérios de aceite | [docs/DESAFIO.md](docs/DESAFIO.md) |
| 2 | Análise manual dos 3 projetos (com apoio de IA, ver nota na seção A) | [01-relatorio-issues-analise-manual.md](docs/evidencias-adicionais/01-relatorio-issues-analise-manual.md) |
| 3 | Levantamento de como executar cada projeto e criação de **testes de caracterização** caixa-preta via HTTP (baseline para comparar antes/depois) | [02-relatorio-analise-execucao-testes.md](docs/evidencias-adicionais/02-relatorio-analise-execucao-testes.md) |
| 4 | Análise e decisões arquiteturais da skill (fases, referências, rubrica, validação, agnosticismo, riscos) | [03-analise-arquitetural-skill.md](docs/evidencias-adicionais/03-analise-arquitetural-skill.md) |
| 5 | Refinamento do escopo com IA (validação com evidências reais, aderência ao enunciado, imparcialidade, agnosticismo) e plano de ação | [04-plano-acao-criacao-skill.md](docs/evidencias-adicionais/04-plano-acao-criacao-skill.md) |
| 6 | Criação da skill com Claude Code (v1) e primeira execução no projeto 1 | [validacao-project-1 v1](docs/evidencias-adicionais/validacoes/validacao-project-1_2026-11-05_v1.md) |
| 7 | Ajustes na skill (v1.1) a partir dos pontos de atenção da v1 e nova execução no projeto 1 | [validacao-project-1 v2](docs/evidencias-adicionais/validacoes/validacao-project-1_2026-11-05_v2.md) |
| 8 | Execução da mesma skill nos projetos 2 e 3 | [validacao-project-2](docs/evidencias-adicionais/validacoes/validacao-project-2_2026-11-06_v2.md) · [validacao-project-3](docs/evidencias-adicionais/validacoes/validacao-project-3_2026-11-06_v2.md) |
| 9 | Validação independente de cada execução contra os critérios de aceite e o checklist (prompt no passo 12 da timeline) | pasta [validacoes/](docs/evidencias-adicionais/validacoes/) |

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

Skill: [`.claude/skills/refactor-arch/`](code-smells-project/.claude/skills/refactor-arch/) — cópia idêntica (verificada com `diff -r`) em [ecommerce-api-legacy](ecommerce-api-legacy/.claude/skills/refactor-arch/) e [task-manager-api](task-manager-api/.claude/skills/refactor-arch/). Documentos de projeto da skill: [03-analise-arquitetural-skill.md](docs/evidencias-adicionais/03-analise-arquitetural-skill.md) e [04-plano-acao-criacao-skill.md](docs/evidencias-adicionais/04-plano-acao-criacao-skill.md).

### Decisões de design

**`SKILL.md` curto como orquestrador (78 linhas) + conhecimento em referências carregadas por fase.** Cada fase lê só o que precisa, o que reduz contexto e evita que o agente "adiante" a refatoração:

| Fase | O que faz | Referências lidas |
|---|---|---|
| 1 — Análise | detecta stack, banco, domínio, arquitetura (por papel do código), superfície de ataque e **como validar** | `01-analise-projeto.md` |
| 2 — Auditoria | cruza o código com o catálogo, gera e salva o relatório, **pausa e pergunta** | `02-catalogo-antipatterns.md`, `03-template-relatorio.md`, `07-politica-comandos-aprovacoes.md` |
| 3 — Refatoração | aplica as mudanças aprovadas, valida com evidências, reaudita | `04-guidelines-mvc.md`, `05-playbook-refatoracao.md`, `06-protocolo-validacao.md`, `07-politica-comandos-aprovacoes.md` |

**Cobertura das 5 áreas obrigatórias** (+ 2 áreas adicionais):

| Área de conhecimento | Arquivo | Conteúdo |
|---|---|---|
| Análise de projeto | [01-analise-projeto.md](code-smells-project/.claude/skills/refactor-arch/references/01-analise-projeto.md) | manifestos/lockfiles, framework e versão, banco, domínio, classificação de arquitetura por papel, superfície de ataque, inventário de validação, descoberta de comandos |
| Catálogo de anti-patterns | [02-catalogo-antipatterns.md](code-smells-project/.claude/skills/refactor-arch/references/02-catalogo-antipatterns.md) | 42 entradas com sinal de detecção, "NÃO é finding", "como confirmar", severidade e rubrica |
| Template de relatório | [03-template-relatorio.md](code-smells-project/.claude/skills/refactor-arch/references/03-template-relatorio.md) | blocos `PHASE 1`, `ARCHITECTURE AUDIT REPORT`, anexo da Fase 3 e `PHASE 3: REFACTORING COMPLETE` |
| Guidelines de arquitetura | [04-guidelines-mvc.md](code-smells-project/.claude/skills/refactor-arch/references/04-guidelines-mvc.md) | papéis das camadas, regras de dependência, estrutura-alvo, adaptação ao nível de organização, checklist de estrutura |
| Playbook de refatoração | [05-playbook-refatoracao.md](code-smells-project/.claude/skills/refactor-arch/references/05-playbook-refatoracao.md) | 19 padrões (P-01…P-19) com código **antes/depois** em Python e JavaScript |
| *Adicional:* protocolo de validação | [06-protocolo-validacao.md](code-smells-project/.claude/skills/refactor-arch/references/06-protocolo-validacao.md) | escada de validação, baseline × final, formato de evidência `E-nn`, política de alteração de testes, prova vermelho/verde |
| *Adicional:* política de comandos e aprovações | [07-politica-comandos-aprovacoes.md](code-smells-project/.claude/skills/refactor-arch/references/07-politica-comandos-aprovacoes.md) | classes de comando (A leitura, B compilar/subir/testar, C instalar/alterar ambiente, D destrutivo, X proibido) e rodada de perguntas |

Outras decisões:

- **Invocação manual** (`disable-model-invocation: true`): a skill só roda via `/refactor-arch`, pois altera código.
- **Pausa obrigatória com perguntas de múltipla escolha** ao fim da Fase 2: P1 escopo, P2 modo de comandos, P3 contrato (**Opção 1: manter o contrato** ou **Opção 2: atualizar com testes que comprovem**) e P4 sondagem ad hoc. Assim o usuário decide, por exemplo, se endpoints inseguros são mantidos ou corrigidos.
- **Nenhuma afirmação sem evidência**: cada passo de validação gera um arquivo `E-nn` em `reports/evidence/project-{N}/{Run id}/` (comando, exit code, saída).
- **Segurança da execução**: conteúdo do projeto é tratado como dado (proteção contra prompt injection), segredos são mascarados no relatório, rotas destrutivas nunca são chamadas automaticamente, checkpoint em branch git antes de alterar e **sem commit** (o usuário decide).
- **Rubrica de severidade** em perguntas ordenadas (pare no primeiro "sim"), para classificar de forma reprodutível.

### Catálogo de anti-patterns

42 entradas, distribuídas por severidade padrão: **11 CRITICAL, 8 HIGH, 17 MEDIUM, 6 LOW** (+ categoria `OUTRO` para achados fora do catálogo).

| Família | Entradas | Exemplos | Por que entrou |
|---|---|---|---|
| SEC — Segurança | 17 | SQL Injection, segredos hardcoded, endpoint admin sem auth, debug/bind público, senha insegura, dados sensíveis em resposta/log, escalação de privilégio, pagamento simulado, falta de transação | Foram os problemas mais graves encontrados na análise manual nos 3 projetos e são exigidos pela definição de CRITICAL do desafio |
| ARC — Arquitetura | 12 | God Class/File, lógica no controller, estado global, acoplamento sem DI, callback hell, N+1, duplicação, erro mal tratado, dinheiro em float | Violações de MVC/SOLID que motivam a refatoração (HIGH/MEDIUM do desafio) |
| DEP — APIs deprecated | 5 | `datetime.utcnow()`, `Model.query.get()`, APIs de Node/Flask, genérico da stack | Exigência explícita do desafio; sempre indica o equivalente moderno |
| TST — Testes | 3 | sem testes, sem instruções de validação, testes quebrados | Sem forma de validar, a Fase 3 não pode provar que a aplicação funciona |
| QLT — Qualidade | 5 | magic numbers, nomes ruins, código morto, `print`/`console.log`, estilo inconsistente | Itens LOW observados nos 3 projetos |

### Como a skill é agnóstica de tecnologia

1. **Sinal semântico, não sintaxe**: cada entrada descreve *o que* procurar (ex.: "dado externo chega a um sink de consulta sem parametrização"); exemplos por linguagem são atalhos. Stack não listada ⇒ a skill deriva o equivalente e marca `derivado`.
2. **Arquitetura classificada por papel do código**, não por nome de pasta — a mesma regra trata `AppManager.js` (tudo numa classe) e `routes/` do Flask.
3. **Comandos descobertos no projeto** (manifestos, README, scripts, testes, `api.http`), nunca embutidos na skill.
4. **Guidelines MVC adaptáveis**: estrutura-alvo de referência e regra "seguir a convenção do framework"; monólito ⇒ criar camadas; parcialmente organizado ⇒ mover só o que está fora do lugar.
5. **Escada de validação** que degrada com aviso: testes do projeto → scripts → boot + requisições existentes → sondagem ad hoc → verificação estática.
6. **Nenhuma referência aos projetos de exemplo** dentro da skill.
7. **Prova**: a mesma skill, sem alteração, rodou em Flask monolítico, Express com God Class e Flask parcialmente em camadas.

### Desafios encontrados e como foram resolvidos

| Desafio | Solução |
|---|---|
| Os projetos não tinham testes; sem baseline não há como provar que "continua funcionando" | Antes da skill, criei suítes de caracterização caixa-preta via HTTP (23 / 8 / 25 testes) e confirmei que detectam regressões alterando temporariamente uma regra ([relatório](docs/evidencias-adicionais/02-relatorio-analise-execucao-testes.md)). A skill usa os testes existentes como degrau principal de validação |
| Pouca familiaridade com Python e Node | Análise manual com apoio de IA e skill construída para atuar como "dev novo no projeto": descobre tudo lendo o código, sem presumir |
| Corrigir CRITICALs de segurança muda o contrato da API, mas o desafio pede que os endpoints originais continuem respondendo | Pergunta P3 com duas opções explícitas. Na Opção 2, os testes originais continuam passando (só autenticação adicionada na fixture) e testes de contrato novos provam cada mudança: **verdes** no código novo e **vermelhos** no código original (checkpoint) |
| v1 da skill: bloco da Fase 1 não ficava registrado; regra "nunca edite testes" conflitava com contrato aprovado; senhas de seed continuavam no fonte ([pontos de atenção da v1](docs/evidencias-adicionais/validacoes/validacao-project-1_2026-11-05_v1.md)) | v1.1 (commit `5303107`, 7 arquivos, +193/−48): evidência `E-00` da Fase 1; política de alteração de testes com snapshot, diff e justificativa; testes de contrato com prova vermelho/verde; senhas de seed como finding e via `SEED_*`; legenda `[x]`/`[~]`/`[ ]` no checklist |
| Ambiente Windows: reloader do Flask mantém processo filho na porta, porta 5000 compartilhada por dois projetos, encoding do console, comandos Bash com aspas aninhadas falhando no agente | Encerramento da árvore de processos, um projeto por vez, `PYTHONIOENCODING=utf-8`, e scripts temporários fora do projeto quando o shell falhava (registrado em "Observações da execução" dos relatórios) |
| Risco de linhas "alucinadas" e falsos positivos | Procedimento obrigatório de reler o trecho antes de reportar, campo "NÃO é finding" e seção "Descartados" no relatório; em cada validação, amostras das referências de linha foram conferidas contra o commit original |

---

## C) Resultados

### Findings por severidade (Fase 2)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Ocorrências | Deprecated |
|---|---:|---:|---:|---:|---:|---:|---|
| code-smells-project | 9 | 6 | 10 | 6 | **31** | 159 | buscadas; nenhuma para Flask 3.1.1 / Python 3.14 |
| ecommerce-api-legacy | 8 | 5 | 7 | 5 | **25** | 55 | buscadas; nenhuma para Express 4.22 / Node 24 |
| task-manager-api | 7 | 4 | 11 | 6 | **28** | 189 | F-021 `datetime.utcnow()`, F-022 `Query.get()` |

### Análise manual × skill

No projeto 1, a skill encontrou praticamente todos os problemas da análise manual (o desafio pede no mínimo 5):

| Análise manual | Finding da skill |
|---|---|
| CS-C1 SQL Injection | F-008 SEC-01 SQL Injection |
| CS-C2 `/admin/query` executa SQL | F-005 SEC-04 Execução arbitrária de SQL |
| CS-C3 reset do banco sem auth | F-004 SEC-03 Endpoints administrativos sem autenticação |
| CS-C4 segredos hardcoded | F-001 SEC-02 Segredos hardcoded + F-006 SEC-07 dados sensíveis em respostas |
| CS-C5 senhas em texto puro | F-007 SEC-06 Senhas em texto puro + F-006 |
| CS-C6 debug e bind 0.0.0.0 | F-002 SEC-05 Modo debug e bind público |
| CS-H1 regra de negócio em model/controller | F-014 ARC-02 + F-009 ARC-01 God File |
| CS-H2 conexão global mutável | F-015 ARC-03 |
| CS-H3 pedido sem transação | F-012 SEC-15 |
| CS-H4 sem autenticação / CORS aberto | F-003 SEC-09 |
| CS-H5 acoplamento sem DI | F-013 ARC-04 |
| CS-M1 N+1 | F-024 ARC-07 |
| CS-M2 código duplicado | F-020 ARC-08 |
| CS-M3 validações ausentes | F-010 SEC-12 |
| CS-M4 detalhes internos nos erros | F-017 SEC-13 + F-019 ARC-09 |
| CS-M5 dinheiro em float | F-023 ARC-12 |
| CS-M6 schema sem constraints | F-022 ARC-10 |
| CS-M7 cancelamento incompleto | F-025 OUTRO-01 |
| CS-M8 sem paginação / `SELECT *` | F-021 ARC-11 |
| CS-L1 magic numbers | F-029 QLT-01 |
| CS-L2 nomes ruins | F-028 QLT-02 |
| CS-L3 imports não usados | F-031 QLT-03 |
| CS-L4 `print` no lugar de logging | F-027 QLT-04 + F-011 SEC-08 (e-mail em log) |
| CS-L6 estilo inconsistente | F-030 QLT-05 |

Nos projetos 2 e 3 os principais itens também foram detectados, por exemplo: EC-C1→F-005, EC-C2→F-002, EC-C3→F-003, EC-C4→F-006, EC-C5→F-004, EC-C6→F-007; TM-C1→F-001/F-003, TM-C2→F-005, TM-C3→F-004, TM-C4→F-002, TM-C5→F-006, TM-M7→F-021/F-022.

Algumas severidades da skill são mais altas que as da análise manual (ex.: CS-H4 HIGH → F-003 CRITICAL; CS-M3 MEDIUM → F-010 HIGH), porque a rubrica do catálogo classifica pelo impacto concreto (dado sensível exposto, ação sem autenticação) e não pela categoria do problema.

### Antes × depois da estrutura

**code-smells-project** — 4 arquivos com papéis misturados → camadas MVC completas.

```
ANTES                                   DEPOIS
app.py         entry + config + rotas   app.py          composition root (create_app)
controllers.py handlers + regra + SQL   config/         settings.py, logging_config.py
models.py      SQL + regra + serializ.  database/       connection.py, schema.py, seed.py
database.py    conexão global + seed    models/         produto_, usuario_, pedido_, sistema_model.py
                                        services/       regras de negócio, auth, Decimal
                                        controllers/    fluxo por domínio + validacao.py
                                        views/          serializers.py (DTOs), respostas.py
                                        routes/         blueprints por domínio
                                        middlewares/    auth.py, error_handler.py, security.py
```

**ecommerce-api-legacy** — God Class → camadas MVC em `src/`.

```
ANTES                                   DEPOIS
src/app.js                              src/app.js       composition root (createApp + start)
src/AppManager.js  God Class            src/config/      settings.js, constants.js
src/utils.js       config + cache +     src/database/    connection.js, schema.js
                   "crypto" + log       src/models/      user, course, enrollment, payment, auditLog, report
                                        src/services/    checkout, password (scrypt), paymentGateway, report
                                        src/controllers/ checkout, report, user
                                        src/routes/      index.js
                                        src/middlewares/ errorHandler, rateLimit, securityHeaders, validateCheckout
                                        src/utils/       appError, logger, money
```

**task-manager-api** — camadas parciais → camadas completas, preservando as pastas existentes.

```
ANTES                                   DEPOIS
app.py          entry + config literal  app.py          composition root (create_app)
models/         models + MD5 + to_dict  config/         settings.py, logging_config.py
routes/         rotas + controller +    models/         entidades + consultas
                regra + SQL + categorias services/      task, user, category, report, auth, notification
services/       1 serviço sem uso       controllers/    fluxo por domínio + validators.py
utils/          helpers sem uso         views/          serializers.py (DTOs sem senha)
                                        routes/         só mapeamento (+ category_routes, system_routes)
                                        middlewares/    auth.py, error_handler.py, security.py
                                        utils/          constants.py, helpers.py (usados)
```

| Métrica | P1 antes → depois | P2 antes → depois | P3 antes → depois |
|---|---|---|---|
| Arquivos-fonte | 4 → 44 | 3 → 26 | 15 → 41 |
| Linhas de código | ~780 → ~1257 | ~180 → ~566 | ~1158 → ~1483 |
| Maior arquivo | `models.py` (314) → `controllers/validacao.py` (134) | `AppManager.js` (141) → `app.js` (71) | `routes/task_routes.py` (299) → `controllers/validators.py` (244) |
| Arquivos com 3+ papéis | 3 → 0 | 2 → 0 | 4 → 0 |
| Rotas da API | 19 → 18 (`/admin/query` removida) | 3 → 3 | 22 → 22 |
| Testes | 23 → 35 (23 originais + 12 de contrato) | 8 → 8 (inalterados) | 25 → 35 (25 originais + 10 de contrato) |

Detalhes (mapa antigo → novo, mudanças aplicadas) no anexo "FASE 3" de cada relatório.

### Checklist de validação

`✅` atendido com evidência · `~` parcial (finding residual citado). Checklist completo, com a evidência de cada item, na seção "Checklist de Validação" de cada relatório e nas [validações independentes](docs/evidencias-adicionais/validacoes/).

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
| Configuração extraída para módulo de config (sem hardcoded) | ✅ | ✅ | ~ (1) |
| Models criados para abstrair dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ~ (2) | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem corretamente | ✅ (3) | ✅ | ✅ (3) |

1. O código não tem mais segredos, mas os valores antigos seguem no histórico git (F-001): rotação manual recomendada.
2. Handler central existe e é usado; `DELETE /api/users/:id` continua respondendo 200 mesmo com id inexistente, porque corrigir mudaria o contrato (Opção 1 escolhida).
3. Com mudanças de contrato aprovadas (ver abaixo); os testes originais continuam passando.

### Evidências de execução (logs)

Todas as evidências são geradas pela própria skill durante a execução:

| Evidência | P1 — [20261105-175512](reports/evidence/project-1/20261105-175512/) | P2 — [20261106-131947](reports/evidence/project-2/20261106-131947/) | P3 — [20261106-140715](reports/evidence/project-3/20261106-140715/) |
|---|---|---|---|
| Fase 1 (bloco `PHASE 1`) | [E-00](reports/evidence/project-1/20261105-175512/E-00-fase1-analise.txt) | [E-00](reports/evidence/project-2/20261106-131947/E-00-fase1-analise.txt) | [E-00](reports/evidence/project-3/20261106-140715/E-00-fase1-analise.txt) |
| Testes no código original (baseline) | [E-01](reports/evidence/project-1/20261105-175512/E-01-baseline-pytest.log) 23 passed | [E-01](reports/evidence/project-2/20261106-131947/E-01-baseline-npm-test.log) 8 pass | [E-01](reports/evidence/project-3/20261106-140715/E-01-baseline-pytest.log) 25 passed |
| Rotas / boot / requisições (baseline) | [E-02](reports/evidence/project-1/20261105-175512/E-02-baseline-rotas.log) 19 rotas | [E-02](reports/evidence/project-2/20261106-131947/E-02-baseline-boot.log) boot · [E-03](reports/evidence/project-2/20261106-131947/E-03-baseline-api-http.log) `api.http` | [E-02](reports/evidence/project-3/20261106-140715/E-02-baseline-rotas.log) 22 rotas |
| Testes após refatoração | [E-03](reports/evidence/project-1/20261105-175512/E-03-final-pytest.log) **35 passed** | [E-05](reports/evidence/project-2/20261106-131947/E-05-final-npm-test.log) **8 pass** | [E-03](reports/evidence/project-3/20261106-140715/E-03-final-pytest.log) **35 passed** |
| Rotas / boot / requisições (após) | [E-04](reports/evidence/project-1/20261105-175512/E-04-final-v5-rotas.log) 18 rotas | [E-06](reports/evidence/project-2/20261106-131947/E-06-final-boot.log) boot · [E-07](reports/evidence/project-2/20261106-131947/E-07-final-api-http.log) `api.http` | [E-05](reports/evidence/project-3/20261106-140715/E-05-final-v5-rotas.log) 22 rotas |
| Prova vermelha (testes de contrato no código original) | [E-05](reports/evidence/project-1/20261105-175512/E-05-vermelho-checkpoint.log) 11 failed / 1 guarda | não aplicável (contrato mantido) | [E-04](reports/evidence/project-3/20261106-140715/E-04-vermelho-checkpoint.log) 9 failed / 2 guardas |
| Diff dos testes | [E-06](reports/evidence/project-1/20261105-175512/E-06-diff-testes.patch) | testes inalterados | [E-06](reports/evidence/project-3/20261106-140715/E-06-diff-testes.patch) |
| Reauditoria | anexo do relatório | [E-08](reports/evidence/project-2/20261106-131947/E-08-reauditoria.log) | anexo do relatório |

Trechos dos logs:

```text
# P1 — E-03-final-pytest.log
tests/test_contratos.py::test_ct02_reset_db_exige_admin PASSED           [100%]
============================= 35 passed in 6.04s ==============================

# P2 — E-06-final-boot.log
{"time":"2026-11-06T16:36:34.630Z","level":"info","msg":"LMS API rodando na porta 3000"}
{"time":"2026-11-06T16:36:34.768Z","level":"info","msg":"checkout concluído","userId":2,"courseId":2,"enrollmentId":2}

# P2 — E-07-final-api-http.log (POST /api/checkout)
HTTP/1.1 200 OK
{"msg":"Sucesso","enrollment_id":2}

# P3 — E-03-final-pytest.log
tests/test_contratos.py::test_c06_validacoes_adicionais PASSED           [100%]
============================= 35 passed in 8.43s ==============================
```

Nos projetos Python, o boot real (`python app.py`) é feito pela fixture do pytest, que sobe a aplicação numa cópia temporária e aguarda `/health` antes dos testes. Cada execução também foi conferida de forma independente (reexecução dos testes, boot e `curl`, amostra de linhas do relatório contra o commit original): ver [validações](docs/evidencias-adicionais/validacoes/).

### Mudanças de contrato (endpoints originais)

A skill pergunta, na pausa da Fase 2, se as correções que alteram o contrato devem ser aplicadas. Usei as duas opções para demonstrar a escolha:

- **P1 e P3 — Opção 2 (atualizar contrato, com prova):** os riscos eram CRITICAL (SQL arbitrário via HTTP, reset do banco sem autenticação, token falso, hash de senha exposto, qualquer visitante virando admin).
  - **P1:** 14 de 19 rotas mudaram: `POST /admin/query` removida; rotas de dados e administrativas passam a exigir `Authorization: Bearer <token>` emitido por `POST /login`, com checagem de perfil e de propriedade; `senha`, `secret_key`, `db_path` e `debug` saem das respostas; CORS restrito a `CORS_ORIGINS`.
  - **P3:** 20 de 22 rotas mudaram: login emite token assinado no lugar de `fake-jwt-token-<id>`; rotas de dados exigem token; alterar perfil e excluir usuários exige admin; `password` sai das respostas; CORS restrito; tipos inválidos passam de 500 para 400.
  - Os testes originais continuam passando: no P1 só a fixture passou a autenticar (`test_api.py` inalterado); no P3, além da fixture, 1 teste (`test_login_sucesso`) foi adaptado ao novo token com asserções reforçadas (diff em E-06). 12 (P1) e 10 (P3) testes de contrato provam cada mudança, verdes no código novo e vermelhos no original. Justificativa por item (finding, CWE/OWASP, impacto para o cliente) na seção "Contratos — resultado" de [audit-project-1.md](reports/audit-project-1.md) e [audit-project-3.md](reports/audit-project-3.md).
- **P2 — Opção 1 (manter contrato):** as 3 rotas mantêm status e formato (7 cenários iguais); os 8 testes passam sem alteração. Em troca, 2 CRITICAL ficam como residuais declarados (F-001 checkout sem verificar senha de conta existente; F-004 relatório e `DELETE` sem autenticação).

### Itens residuais (reauditoria)

A Fase 3 reaplica o catálogo ao código novo e só diria "zero anti-patterns" se não houvesse residuais:

- **P1:** 0 CRITICAL, 0 HIGH; 7 MEDIUM/LOW parciais (rate limit no login, `pip-audit`, paginação, FKs e tipo monetário no banco existente, máquina de estados do pedido, README do projeto).
- **P2:** 2 CRITICAL por contrato (Opção 1) e gateway de pagamento ainda simulado (isolado em `services/paymentGateway.js`); 3 MEDIUM parciais.
- **P3:** 0 HIGH; F-001 parcial (segredos no histórico git) e MEDIUM/LOW parciais (rate limit, `pip-audit`, paginação, `NotificationService` sem uso, README do projeto).

### Comportamento da skill em stacks diferentes

| Projeto | Nível de organização detectado | Como a Fase 3 se adaptou |
|---|---|---|
| code-smells-project | `parcialmente-em-camadas` (4 arquivos com papéis misturados) | Criou services, views e middlewares inexistentes; substituiu `controllers.py`, `models.py` e `database.py` por pacotes |
| ecommerce-api-legacy | `monolito-sem-camadas` (God Class) | Criou todas as camadas; manteve `src/app.js` como entry point (em vez de `server.js`) porque `npm start` e os testes o executam; callbacks → `async/await` |
| task-manager-api | `parcialmente-em-camadas` (models/routes/services/utils) | Manteve as pastas existentes e moveu só o que estava fora do lugar; categorias ganharam módulo próprio; corrigiu as APIs deprecated |

- Em Node, a skill usou as dicas do catálogo (SEC-08, SEC-14, ARC-05, ARC-07) e **derivou** um achado fora do catálogo: exceção em callback assíncrono derrubando o processo (F-008, DoS remoto).
- Em Python, o mesmo catálogo detectou APIs deprecated só onde existiam (P3), registrando a busca negativa nos demais.
- Quando o projeto tinha coleção de requisições (`api.http` no P2), a validação subiu um degrau: boot real + as mesmas requisições antes e depois.

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
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

Fluxo: a Fase 1 imprime `PHASE 1: PROJECT ANALYSIS`; a Fase 2 salva `reports/audit-project-{N}.md` na raiz do repositório e para em `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` com as perguntas P1–P4; a Fase 3 cria uma branch de checkpoint, refatora, valida e anexa os resultados ao relatório. A skill não faz commit.

### Validar os projetos refatorados

Os testes sobem a aplicação real e fazem requisições HTTP. `code-smells-project` e `task-manager-api` usam a porta 5000: rode um de cada vez.

**code-smells-project**

```bash
cd code-smells-project
python -m venv .venv
source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

Esperado: `35 passed`.

**ecommerce-api-legacy**

```bash
cd ecommerce-api-legacy
npm install
npm test
```

Esperado: `8 pass, 0 fail`.

**task-manager-api**

```bash
cd task-manager-api
python -m venv .venv
source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

Esperado: `35 passed`.

### Rodar as aplicações manualmente

A configuração agora vem do ambiente. Cada projeto tem um `.env.example` com os nomes das variáveis (valores fictícios); exporte-as no shell antes de iniciar.

| Projeto | Variáveis principais | Comandos | URL |
|---|---|---|---|
| code-smells-project | `SECRET_KEY`, `SEED_ADMIN_PASSWORD`, `SEED_CLIENTE_PASSWORD`, `CORS_ORIGINS`, `ALLOW_DESTRUCTIVE` | `pip install -r requirements.txt` → `python app.py` | http://localhost:5000 |
| ecommerce-api-legacy | `PORT`, `SEED_USER_PASSWORD`, `LOG_LEVEL`, `CHECKOUT_RATE_MAX` | `npm install` → `npm start` (exemplos em `api.http`) | http://localhost:3000 |
| task-manager-api | `SECRET_KEY`, `SEED_ADMIN_PASSWORD`, `SEED_MANAGER_PASSWORD`, `SEED_USER_PASSWORD`, `CORS_ORIGINS` | `pip install -r requirements.txt` → `python seed.py` → `python app.py` | http://localhost:5000 |

Observações:

- Sem `SECRET_KEY`, uma chave aleatória é gerada a cada boot (tokens deixam de valer ao reiniciar).
- No `task-manager-api`, `python seed.py` exige as três variáveis `SEED_*` e apaga e recria os dados.
- Nos projetos 1 e 3, as rotas de dados exigem `Authorization: Bearer <token>`: obtenha o token com `POST /login` usando o usuário admin do seed.

---

## Estrutura do repositório

```
.
├── README.md                          # este documento
├── docs/
│   ├── DESAFIO.md                     # enunciado original do desafio
│   └── evidencias-adicionais/         # timeline, análise manual, análise de testes,
│       └── validacoes/                # decisões da skill, plano de ação e validações
├── code-smells-project/               # Projeto 1 — refatorado
│   ├── .claude/skills/refactor-arch/  # SKILL.md + 7 referências
│   └── tests/                         # caracterização + contratos
├── ecommerce-api-legacy/              # Projeto 2 — refatorado
│   ├── .claude/skills/refactor-arch/  # cópia da skill
│   └── test/
├── task-manager-api/                  # Projeto 3 — refatorado
│   ├── .claude/skills/refactor-arch/  # cópia da skill
│   └── tests/
└── reports/
    ├── audit-project-1.md             # saída da Fase 2 + anexo da Fase 3
    ├── audit-project-2.md
    ├── audit-project-3.md
    └── evidence/project-{1,2,3}/      # evidências E-nn de cada execução
```

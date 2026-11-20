# Validação do resultado — Projeto 2 (ecommerce-api-legacy)

> **Nota:** registro histórico do momento da validação. Itens como "Nada commitado" e "Pendências antes da entrega" já foram resolvidos em `main`.

- Data: 2026-11-06
- Versão: v2
- Desafio: Criação de Skills — Refatoração Arquitetural Automatizada
- Skill: `refactor-arch` 1.1 | Catálogo 1.0 (Claude Code)
- Branch: `code-smells-20261105-v2` (sem commit nem push). A execução da skill criou também `refactor-arch/checkpoint-20261106-131947` (HEAD 5303107).
- Relatório validado: `reports/audit-project-2.md` (Run id 20261106-131947)
- Evidências: `reports/evidence/project-2/20261106-131947/` (`E-00` a `E-08`)

## Veredito

**O projeto 2 atende aos 4 critérios obrigatórios e a todos os itens do checklist.** Há 5 pontos de atenção, nenhum bloqueante. O principal é que 2 findings CRITICAL (F-001 e F-004) continuam abertos, porque a Opção 1 (manter o contrato) foi escolhida.

## Método de verificação

- Leitura integral do README do desafio, do `reports/audit-project-2.md` (600 linhas) e da evidência `E-00` (Fase 1).
- Listagem dos 9 arquivos de evidência `E-00` a `E-08`; só o `E-00` foi lido nesta validação.
- Reexecução independente de `npm test` → **8 passed, 0 failed**.
- Boot independente com `node src/app.js` (log `LMS API rodando na porta 3000`) e 4 requisições via `curl`:
  - `POST /api/checkout` com cartão `4…` → 200 `{"msg":"Sucesso","enrollment_id":2}`;
  - `POST /api/checkout` com cartão `5…` → `Pagamento recusado`;
  - `GET /api/admin/financial-report` → 200 com `course`, `revenue` e `students[{student, paid}]`;
  - `DELETE /api/users/1` → texto original de exclusão.
- Conferência por amostragem das referências de linha contra o commit original (`git show HEAD:...`): `AppManager.js:26-80` e `:131-136` (checkout, log do cartão, prefixo `"4"`, `badCrypto`, `DELETE`), `utils.js:1-25` (config com segredos, cache global, `badCrypto`) e `app.js:1-14`. Todas conferem.
- Contagem dos arquivos originais: `app.js` 14, `AppManager.js` 141, `utils.js` 25 linhas (3 arquivos-fonte, 180 linhas). Confere com `E-00`.
- Contagem do código novo: 26 arquivos `.js` em `src/`, somando 566 linhas. Maior arquivo: `src/app.js` (71). Confere com o anexo da Fase 3.
- Grep em `src/` por `pk_live`, `senha_super` e `console.log`: nenhuma ocorrência.
- Integridade dos testes: `git status` e `git diff --stat` de `test/`, `package.json`, `api.http` e `README.md` não mostram alterações; `test/api.test.js` está inalterado.
- A pasta da skill (`.claude/skills/refactor-arch/`, `SKILL.md` + 7 referências) foi listada, mas só os títulos do `03-template-relatorio.md` foram lidos nesta validação.

## Critérios de aceite

| Critério | Status | Evidência |
|---|---|---|
| Fase 1 detecta a stack corretamente | ✅ | JavaScript (Node.js v24.11.1) + Express 4.22.1 (confiança alta) — E-00 |
| Fase 2 encontra >= 5 findings | ✅ | 25 findings (55 ocorrências) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | ✅ | 8 CRITICAL e 5 HIGH |
| Fase 3: aplicação funciona após a refatoração | ✅ | 8/8 testes (E-05 e reexecução); boot e 3 rotas respondendo (E-06, E-07 e reexecução) |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — JavaScript, Node.js v24.11.1.
- [x] Framework detectado corretamente — Express 4.22.1 (lock) com `express()` em `src/app.js`.
- [x] Domínio descrito corretamente — LMS com checkout (cursos, matrículas, pagamentos, usuários) e relatório financeiro.
- [x] Número de arquivos condiz com a realidade — 3 arquivos-fonte e 180 linhas, igual ao repositório.

### Fase 2 — Auditoria
- [x] Relatório segue o template dos arquivos de referência — seções e ordem do `03-template-relatorio.md` §3 (Summary, Estrutura ANTES, Superfície de ataque, Findings, Descartados, Contratos, Testes afetados, Planos, Decisões).
- [x] Cada finding tem arquivo e linhas exatos — amostra conferida contra o código original.
- [x] Findings ordenados CRITICAL → LOW — 8/5/7/5 = 25. Por categoria: Segurança 9, Arquitetura 10, Deprecated 0, Testes 0, Qualidade 5, Outro 1 = 25.
- [x] Mínimo de 5 findings — 25 (55 ocorrências).
- [x] Detecção de APIs deprecated incluída — buscada (`new Buffer`, `url.parse`, `body-parser`, `req.param`); registro "DEP-03/DEP-05: nenhuma encontrada" em "Descartados".
- [x] Skill pausa e pede confirmação antes da Fase 3 — linha `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e rodada de perguntas P1–P4, registrada em "Decisões do usuário".

### Fase 3 — Refatoração
- [x] Estrutura MVC — `config/`, `database/`, `models/`, `services/`, `controllers/`, `routes/`, `middlewares/`, `utils/` e `app.js` (composition root).
- [x] Configuração extraída (sem hardcoded) — `config/settings.js` lê `PORT`, `SEED_USER_PASSWORD`, `LOG_LEVEL` e `CHECKOUT_RATE_MAX` do ambiente; `.env.example` criado; chave `pk_live`, credenciais de banco e senha de seed removidas do código.
- [x] Models abstraem os dados — `models/*Model.js` (user, course, enrollment, payment, auditLog, report) e `database/`; sem SQL em `controllers/`.
- [x] Views/Routes separadas — `routes/index.js` só mapeia as 3 rotas. O projeto é uma API JSON, então não há views.
- [x] Controllers concentram o fluxo — `controllers/*Controller.js` chamam services e models.
- [x] Error handling centralizado — `middlewares/errorHandler.js` com `asyncHandler` e `AppError`. Item marcado `[~]` pela skill (ver ponto de atenção 2).
- [x] Entry point claro — `src/app.js` (`createApp` + `start`), mesmo comando `npm start`.
- [x] Aplicação inicia sem erros — boot reexecutado, log `LMS API rodando na porta 3000`.
- [x] Endpoints originais respondem — 3 de 3 rotas (7 cenários) com mesmo status e formato; 0 alteradas por contrato; os 8 testes originais passam sem alteração.

## Resumo dos números

| Item | Antes | Depois |
|---|---|---|
| Arquivos-fonte | 3 | 26 |
| Linhas de código | ~180 | 566 |
| Maior arquivo | `AppManager.js` (141) | `app.js` (71) |
| Arquivos com 3+ papéis | 2 | 0 |
| Rotas da API | 3 | 3 |
| Testes | 8 passed (E-01) | 8 passed (E-05), sem testes novos |
| Prova de sensibilidade | — | não aplicável (Opção 1, sem contrato alterado) |

Findings por severidade: CRITICAL 8, HIGH 5, MEDIUM 7, LOW 5 (total 25, com 55 ocorrências).

## Pontos de atenção

1. **CRITICAL residuais (F-001 e F-004).** O checkout ainda reutiliza conta existente sem verificar a senha, e o relatório financeiro e o `DELETE /api/users/:id` continuam sem autenticação. Foi a escolha P3 ("Manter o contrato como está"). Corrigir exige a Opção 2 (CT-01 a CT-03). Um avaliador que espere zero CRITICAL pode questionar; a justificativa é o contrato preservado.
2. **Error handling parcial.** A skill marca `[~]`: `DELETE` ainda responde 200 mesmo com erro ou ID inexistente (CT-04), e erro de banco na busca do curso vira 404. O handler central existe e é usado.
3. **F-003 residual.** O gateway continua simulado (aprova cartão iniciado em `4`), agora isolado em `services/paymentGateway.js` e sinalizado. Integração real está fora do escopo.
4. **F-008 não exercitado em execução.** A correção do crash com `card` ou `pwd` numérico (agora 400) foi validada só por leitura e `node --check`; a sondagem ad hoc não foi aplicada.
5. **Nada commitado e branch compartilhada.** O README do desafio exige commitar o código refatorado; a skill não commita. A branch `code-smells-20261105-v2` é a mesma do projeto 1.

## Residuais declarados pela skill (não são falhas da validação)

- F-001 e F-004 (CRITICAL): ver ponto de atenção 1.
- F-003 (CRITICAL, parcial): gateway simulado isolado e sinalizado.
- F-015 (MEDIUM, parcial): validação de formato de `eml`, `card` e `c_id` e `pwd` obrigatório exigem CT-05.
- F-016 (MEDIUM, parcial): constraints aplicadas; matrículas e pagamentos órfãos ao excluir usuário dependem de decisão de negócio.
- F-019 (MEDIUM, parcial): ver ponto de atenção 2.
- Rotacionar `pk_l***` e `senh***`, que seguem no histórico git; rodar `npm audit` e declarar `engines.node`.
- Mudanças em caminhos internos de erro, não alcançáveis por cliente com banco em memória: falha na auditoria agora faz rollback e responde 500 (antes era ignorada); JSON inválido responde 400 em texto (antes, página padrão do Express com stack).
- Ajuste aditivo: `X-Powered-By` removido e cabeçalhos de segurança adicionados; rate limit de 30 req/min por IP no checkout (configurável).
- Ordem dos cursos no relatório passa a ser por id (antes dependia dos callbacks; o teste já ordena).
- Limitações da validação: caminhos de falha interna de banco não foram exercitados; `api.http` foi usado só via `curl` nas 4 requisições.

## Pendências antes da entrega

- Commitar: `reports/`, `.env.example`, os novos pacotes (`src/config/`, `src/controllers/`, `src/database/`, `src/middlewares/`, `src/models/`, `src/routes/`, `src/services/`, `src/utils/`), `src/app.js` modificado e as remoções de `src/AppManager.js` e `src/utils.js` (recuperáveis pelo commit inicial).
- `README.md` do projeto não foi alterado: as novas variáveis de ambiente estão só no `.env.example`.
- Remover a branch `refactor-arch/checkpoint-20261106-131947` se não for necessária.
- Atualizar o `README.md` do desafio (análise manual, construção da skill, resultados, como executar).
- Executar a skill no projeto 3 (`task-manager-api`) e validar com o mesmo checklist.

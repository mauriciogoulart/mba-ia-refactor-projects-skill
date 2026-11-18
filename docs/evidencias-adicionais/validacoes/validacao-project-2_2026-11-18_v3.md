# Validação do resultado — Projeto 2 (ecommerce-api-legacy)

- **Data:** 2026-11-18
- **Versão:** v3 — skill 1.2
- **Desafio:** `docs/DESAFIO.md` (seções "Validação" e "Critérios de Aceite")
- **Skill:** `ecommerce-api-legacy/.claude/skills/refactor-arch/` (SKILL.md + 7 references; sem alteração desde `20f9e72` e idêntica à cópia de `code-smells-project`)
- **Branch/commit:** `entrega-v2` @ `e8f4625` (refatorado, sem diferença na working tree); original `5303107`; checkpoint da execução `bb765d3` (`src/`, `test/` e `package.json` do projeto idênticos aos de `5303107`)
- **Relatório validado:** `reports/audit-project-2.md` (Run id 20261116-213657)
- **Evidências:** `reports/evidence/project-2/20261116-213657/` (E-00 a E-12 + `tests-before/`)

## Veredito

**APROVADO, com ressalvas não bloqueantes.** Os 4 itens da solicitação do avaliador, os 4 critérios de aceite e o checklist do desafio foram atendidos, e conferi isso em execução própria. Nenhum CRITICAL/HIGH do relatório continua no código; resta só a rotação externa dos segredos publicados no histórico git. As ressalvas principais são a falta de teste automatizado para "sem `ADMIN_API_KEY` nega tudo" (o comportamento está correto), o e-mail com caixa diferente que cria conta separada e mudanças de validação não classificadas como contrato.

## Método de verificação

1. **Suíte reexecutada:** `npm test` em `ecommerce-api-legacy` (porta 3000 livre antes e depois): **33 passed / 0 failed / 0 skipped**, exit 0. Bate com o E-06.
2. **Execução real própria:** bateria em script fora do projeto, com `ADMIN_API_KEY` (o4-0\*\*\*), `SEED_USER_PASSWORD` (KVj3\*\*\*) e `PAYMENT_GATEWAY_KEY` (test\*\*\*) geradas por mim. Foram **23 subidas (22 do refatorado e 1 do original), 126 requisições e 113 verificações: 113 ok, 0 falhas**. Ambiente limpo a cada subida (variáveis da aplicação removidas antes de definir as do cenário). Cenários:
   - **Admin:** relatório e DELETE sem credencial, com Bearer inválido, esquema Basic, chave sem esquema e chave truncada ⇒ 401; chave válida ⇒ 200; usuário preservado após os DELETEs negados; id inexistente ⇒ 404; exclusão sem órfãos.
   - **Sem `ADMIN_API_KEY`** (ausente e vazia): 5 variações de credencial nas 2 rotas ⇒ 401 em todas, com aviso no log.
   - **Checkout de conta existente:** senha errada, ausente, vazia e a antiga do seed ⇒ 401, com relatório idêntico antes e depois (nada gravado); senha correta ⇒ 200 e compra vinculada à conta.
   - **Sem provedor:** cartões iniciados em "4" ⇒ 400 `Pagamento recusado`, nada gravado. Provedor vazio, `stripe`, `MOCK` e `constructor` também recusam, mesmo com `APP_ENV=test` e prefixos definidos.
   - **`PAYMENT_PROVIDER=mock` fora da lista branca:** `APP_ENV=production`, ausente, vazio, `staging`, `TEST` e só `NODE_ENV=test` ⇒ o processo encerra com exit 1 no boot e nenhuma requisição é atendida.
   - **`PAYMENT_PROVIDER=mock` com `APP_ENV=test`:** prefixos `42, 51` aprovam 42\* e 51\* e recusam 41\* e 37\*; lista vazia recusa tudo; `APP_ENV=development` aprova o prefixo configurado.
   - **Log:** sem cartão completo, chave do gateway, chave admin ou senha de seed; só `last4`.
   - **Controle no original (`5303107`), mesmas requisições:** relatório e DELETE abertos (200), senha errada aceita (200), cartão "4" aprovado (200), cartão completo no log e queda do processo com cartão numérico.
   - Processos encerrados; porta 3000 livre ao final; nenhum processo `node` restante.
3. **Prova vermelha própria:** testes atuais contra o código de `5303107`: **8 passed / 14 failed**, exit 1, igual ao E-09. Os 8 são os testes originais adaptados.
4. **Teste de mutação próprio** (cópia fora do projeto, um defeito por vez): **14 de 15 mutantes mortos**. Sobreviveu apenas M03 (ponto de atenção 1). Mortos: remoção de `requireAdmin` nas 2 rotas, checkout sem verificar senha, cobrança antes da senha, aprovação sem provedor, mock em qualquer ambiente, mock com ambiente ausente, mock como padrão, mock ignorando prefixos, cartão completo no log, ausência de rollback, DELETE sem cascata, senha padrão e validador sem checagem de cartão.
5. **Referências arquivo:linha:** **70 referências conferidas** contra `git show 5303107:...`, comparando o trecho esperado em cada linha, cobrindo 24 dos 25 findings (F-015 aponta para `src/app.js:6`, conferida em F-003) e referências de descartes e comandos. **0 divergências.** Recontei também 25 findings, 53 ocorrências, categorias 10/10/5 e 3 arquivos com 180 linhas.
6. **Varredura do refatorado (fora de `test/`):**
   - `startsWith(`: 1 ocorrência, em `src/services/payment/gatewayFactory.js:34`, dentro do mock e usando prefixos da configuração.
   - `pk_live`, `senha_super`, `admin_master`, `123456`, `"123"`, senhas literais, números de cartão e `console.*`: **0 ocorrências**.
   - Log de cartão: as 2 chamadas usam `cardLast4`.
   - Mock como padrão: não existe em `settings.js`, `.env.example` (`PAYMENT_PROVIDER=` e `APP_ENV=` vazios) nem em `package.json` (`start` = `node src/app.js`).
7. **Integridade dos testes:** o diff de `test/api.test.js` contra `5303107` tem 77 inserções e 5 remoções. As 5 linhas trocadas são sondagem, `relatorio()`, `spawn`, a senha do checkout e o cabeçalho do DELETE, nenhuma é asserção. Asserções: **23 antes, 45 depois** (as 23 mantidas); testes: 8 ⇒ 14. `tests-before/test/api.test.js` é idêntico ao original.
8. **Leitura integral:** 28 arquivos de `src/` (693 linhas), 7 de `test/`, `.env.example`, seções P3/4.2 da política `07` e P-20 do playbook `05`.

## Solicitação do avaliador

| Item | Status | Evidência |
|---|---|---|
| 1. Relatório financeiro e exclusão de usuário com autenticação | ✅ | `src/routes/index.js:5-6` + `src/middlewares/requireAdmin.js:8-17`. Execução: sem credencial/inválida ⇒ 401; chave válida ⇒ 200; sem `ADMIN_API_KEY` ⇒ 401 em tudo. Original: 200 aberto. |
| 2. Checkout verifica a senha da conta existente | ✅ | `src/services/checkoutService.js:22-23`, antes da cobrança (linha 25). Execução: senha errada/ausente ⇒ 401 e nada gravado; correta ⇒ 200. Original: 200 com senha errada. Borda de caixa do e-mail no ponto 2. |
| 3. Gateway não aprova cartão iniciado em "4" | ✅ | `src/services/payment/gatewayFactory.js:10-20`. Execução: sem provedor ⇒ 400; mock com `production` ou sem `APP_ENV` ⇒ não sobe; mock com `test` ⇒ só prefixos configurados. Original: 200. |
| 4a. Manter contrato não deixa CRITICAL/HIGH sem correção de forma implícita | ✅ | `references/07-politica-comandos-aprovacoes.md:82` (contagem no asterisco) e `:99-103` (segunda confirmação); `SKILL.md:58-59`. |
| 4b. Playbook com padrão que resolve o pagamento simulado | ✅ | `references/05-playbook-refatoracao.md:494` (P-20: provedor configurado, recusa por padrão, mock só por lista branca). A implementação segue o padrão. |

## Critérios de aceite

| Critério | Status | Evidência |
|---|---|---|
| Fase 1 detecta stack corretamente | ✅ | E-00: JavaScript/Node.js + Express 4.22.1 + sqlite3; confere com `package.json` e o código original |
| Fase 2 encontra >= 5 findings | ✅ | 25 findings (53 ocorrências), referências sem divergência |
| Fase 2 inclui >= 1 CRITICAL ou HIGH | ✅ | 6 CRITICAL + 7 HIGH, confirmados no código original |
| Fase 3: aplicação funciona após refatoração | ✅ | 33/33 na reexecução; 16 subidas próprias com configuração válida; as 3 rotas respondem conforme o contrato aprovado |

## Checklist de validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente: JavaScript/Node.js (E-00).
- [x] Framework detectado corretamente: Express 4.22.1 (E-00; `package.json:11` + lockfile).
- [x] Domínio descrito corretamente: LMS com checkout, matrículas, pagamentos e relatório financeiro.
- [x] Número de arquivos condiz com a realidade: 3 arquivos / 180 linhas (recontado: 14 + 141 + 25).

### Fase 2 — Auditoria
- [x] Relatório segue o template: seções e ordem conferem com `03-template-relatorio.md` §3 e §4.
- [x] Cada finding tem arquivo e linhas exatos: 70 referências conferidas, nenhuma divergência.
- [x] Ordenados por severidade: F-001…F-006 CRITICAL, F-007…F-013 HIGH, F-014…F-020 MEDIUM, F-021…F-025 LOW.
- [x] Mínimo de 5 findings: 25.
- [x] APIs deprecated: busca registrada ("DEP: nenhuma encontrada", com a lista do que foi buscado); a leitura do original não mostra uso dessas APIs.
- [x] Pausa e pede confirmação antes da Fase 3: "Decisões do usuário" (`1A 2A 3A 4A`) + linha `Proceed with refactoring (Phase 3)? [y/n]`. Evidência indireta (ponto 7).

### Fase 3 — Refatoração
- [x] Estrutura MVC: `config/`, `database/`, `models/`, `services/`, `controllers/`, `routes/`, `middlewares/`, `validators/`, `errors/`, `utils/`.
- [x] Configuração extraída sem hardcoded: `src/config/settings.js` lê tudo do ambiente; varredura sem literais.
- [x] Models abstraem dados: `src/models/*`; SQL só em `models/` e `database/`.
- [x] Views/Routes separadas: `src/routes/index.js` (API JSON, sem camada de view própria).
- [x] Controllers concentram o fluxo: leem a requisição, chamam services e escolhem a resposta, sem SQL.
- [~] Error handling centralizado: `src/middlewares/errorHandler.js` funciona (JSON malformado ⇒ 400 sem stack), mas erros em texto e sucesso em JSON continuam misturados para preservar o contrato (F-019 parcial, declarado).
- [x] Entry point claro: `src/app.js` (`npm start`).
- [x] Aplicação inicia sem erros: 16 subidas próprias com configuração válida; as 6 com mock proibido encerram de propósito.
- [x] Endpoints originais respondem corretamente: 3 de 3 rotas; alterações cobertas por CT-01 a CT-04 e pelas correções declaradas, exceto as bordas do ponto 3.

## Critérios adicionais da versão 1.2

| Item | Status | Evidência |
|---|---|---|
| a. Nenhum CRITICAL/HIGH sem correção (exceto ação externa) | ✅ | Conferido no código: F-001 (`cardLast4`, log limpo); F-002 (`gatewayFactory.js`); F-003 (`requireAdmin`); F-004 (`settings.js`, sem literais); F-005 (`passwordService.js`, scrypt com salt); F-006 (maior arquivo com 78 linhas); F-007 (`checkoutValidator.js`; cartão numérico ⇒ 400 e processo vivo); F-008 (`checkoutService.js:22-23`); F-009 (`db.transaction` com rollback, mutante M12 morto); F-010 (composition root); F-011 (services); F-012 (async/await); F-013 (cache global removido). Pendente só a rotação externa da chave e da senha do histórico git (F-004). |
| b. P3 com 3 opções na ordem certa e resposta "Refatorar" | ✅ (evidência indireta) | Colunas Refatorar · Manter contrato\* · Híbrido no relatório (linha 292); "Resumo para a pergunta" com contagem correta: 1 CRITICAL (F-003) e 1 HIGH (F-008), "exige segunda confirmação" (linha 299); resposta `3A` = Refatorar (linhas 362 e 376). O texto exibido ao usuário não foi gravado (ponto 7). |
| c. Prova por testes de unidade e integração (verde/vermelho) | ✅ | Verde: 33/33. Vermelho: 14 falhas no original (reexecução própria). Mutação: 14 de 15 detectados, o que compensa o vermelho estrutural dos testes de unidade (ponto 8). |
| d. Execução local autenticada com credenciais geradas, mascaradas | ✅ | E-04 (baseline) e E-08 (final), 21 requisições cada, com chaves aleatórias mascaradas. Reproduzido por mim com credenciais próprias. Varredura das evidências sem a chave do gateway e a senha de banco originais; os cartões que aparecem no E-10 são sintéticos dos testes. |
| e. Evidências no formato `E-nn` | ⚠️ parcial | 13 arquivos E-00 a E-12, todos citados no relatório. E-01 a E-09 têm cabeçalho completo; E-00, E-10, E-11 e E-12 têm cabeçalho mínimo (ponto 9). |

## Resumo dos números

| Métrica | Antes | Depois |
|---|---|---|
| Arquivos-fonte (`src/`) | 3 | 28 |
| Linhas de código (`src/`) | 180 | 693 |
| Maior arquivo | `src/AppManager.js` (141) | `src/app.js` (78) |
| Arquivos com 3+ papéis | 2 | 0 |
| Rotas | 3 | 3 |
| Rotas administrativas sem autenticação | 2 | 0 |
| Testes | 8 | 33 |
| Asserções em `test/api.test.js` | 23 | 45 |
| Findings CRITICAL | 6 | 0 |
| Findings HIGH | 7 | 0 |
| Findings MEDIUM | 7 | 2 residuais parciais (F-018, F-019) |
| Findings LOW | 5 | 1 residual parcial (F-025) |

## Pontos de atenção

1. **Sem teste automatizado para "sem `ADMIN_API_KEY` nega tudo" (não bloqueante).** O comportamento está correto em execução real, mas o mutante M03, que libera as rotas quando a chave está ausente, passou pelos 33 testes. Uma regressão nesse ponto não seria detectada pela suíte.
2. **E-mail com caixa diferente cria conta separada (não bloqueante, não declarado).** `LEONAN@fullcycle.com.br` com senha qualquer responde 200, porque a comparação diferencia maiúsculas. A sonda mostrou que a conta real não é alcançada: a compra sobrevive à exclusão do usuário 1 e a variante passa a ter senha própria. O efeito é uma conta duplicada que aparece no relatório com o nome informado pelo cliente. O original tem a mesma comparação.
3. **Mudanças de resposta fora da tabela de contratos (não bloqueante, não declarado como contrato).** `c_id: "abc"` passou de 404 para 400, `card: "41"` de 200 para 400, e o checkout ganhou o status 429. O plano marca C-07 e C-13 como "não afeta contrato", embora `07:81` cite "validação mais estrita" entre as mudanças de contrato.
4. **Limite de taxa desativado por valor inválido (não bloqueante, não declarado).** Com `CHECKOUT_RATE_LIMIT_MAX=abc`, 35 requisições seguidas não geraram nenhum 429, porque `Number("abc")` vira `NaN` (`src/config/settings.js:17`).
5. **Compra simultânea com o mesmo e-mail novo (não bloqueante hoje, declarado).** Reproduzido: respostas 200 e 500, com só uma compra gravada. Precisa de estorno ou reserva antes de integrar um provedor real, pois a segunda cobrança já teria sido aprovada.
6. **README e `api.http` desatualizados (não bloqueante, declarado em parte).** Não documentam `Authorization`, provedor nem variáveis novas. Além disso, nada carrega o arquivo `.env` (sem `dotenv` ou `--env-file`), ponto que o relatório não menciona: as variáveis precisam estar no ambiente do processo.
7. **P3 sem registro literal da pergunta (não bloqueante).** A ordem das opções e o aviso estão comprovados pela política, pela tabela, pelo resumo e pela resposta `3A`, mas o texto exibido ao usuário não ficou em evidência.
8. **Vermelho estrutural nos testes de unidade (não bloqueante, declarado).** Parte dos vermelhos no original vem de módulo inexistente. A mutação própria confirmou a sensibilidade dessas provas.
9. **Cabeçalhos E-nn heterogêneos (não bloqueante).** E-00, E-10, E-11 e E-12 não têm as linhas de comando, exit code e resultado presentes nos demais.

## Residuais declarados pela skill

- **F-004 (ação manual):** rotacionar a chave do gateway (pk_l\*\*\*) e a senha de banco (senh\*\*\*) publicadas no histórico git.
- **F-018 (MEDIUM, parcial):** relatório sem paginação; mantido porque é agregado e paginar mudaria o contrato.
- **F-019 (MEDIUM, parcial):** erros em texto e sucesso em JSON; mantido para preservar o contrato.
- **F-025 (LOW, parcial):** chaves do payload `usr`, `eml`, `pwd` e `c_id` mantidas por serem contrato.
- **Pontos novos declarados na reauditoria:** o 401 do checkout revela que o e-mail está cadastrado (consequência de CT-03); compras simultâneas com o mesmo e-mail novo (ponto 5); `api.http` e `README.md` desatualizados (ponto 6).
- **Recomendação manual:** rodar `npm audit` quando houver aprovação de rede.

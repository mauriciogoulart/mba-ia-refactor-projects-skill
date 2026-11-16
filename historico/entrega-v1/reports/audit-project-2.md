================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Path:    ecommerce-api-legacy
Run:     2026-11-06T13:19:47-03:00          Run id: 20261106-131947
Stack:   JavaScript (Node.js v24.11.1) + Express 4.22.1 (confiança: alta)
Files:   3 analyzed | ~180 lines of code
Architecture: monolito-sem-camadas
Skill:   refactor-arch 1.1 | Catalog 1.0
Evidence: reports/evidence/project-2/20261106-131947/

## Summary
CRITICAL: 8 | HIGH: 5 | MEDIUM: 7 | LOW: 5
Total: 25 findings (55 ocorrências)
Por categoria: Segurança 9 | Arquitetura 10 | Deprecated 0 | Testes 0 | Qualidade 5 | Outro 1
Cobertura: 3/3 lidos integralmente; 0 inspecionados por busca

## Estrutura ANTES
```
ecommerce-api-legacy/
├── api.http
├── package.json
├── README.md
├── src/
│   ├── app.js
│   ├── AppManager.js
│   └── utils.js
└── test/
    └── api.test.js
```

| Métrica | Valor |
|---|---|
| Arquivos-fonte | 3 |
| Linhas de código (aprox.) | ~180 |
| Camadas presentes (papéis) | entrypoint, config, rotas/controller, regra de negócio, acesso a dados (tudo misturado; sem services, models, middlewares) |
| Maior arquivo | src/AppManager.js (141) |
| Arquivos com 3+ papéis | 2 (src/AppManager.js, src/utils.js) |

## Superfície de ataque
| Método | Rota | Handler (arquivo:linha) | Autenticação | Administrativa/destrutiva |
|---|---|---|---|---|
| POST | /api/checkout | src/AppManager.js:28 | não | não (cria usuário, matrícula e pagamento) |
| GET | /api/admin/financial-report | src/AppManager.js:80 | não | sim (relatório financeiro com nomes de alunos) |
| DELETE | /api/users/:id | src/AppManager.js:131 | não | sim (exclusão de usuário) |

## Findings

### [CRITICAL] F-001 · SEC-09 Autenticação ausente: checkout age em nome de conta existente sem verificar senha
File: src/AppManager.js:40, 73-75
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A07:2021
Evidência: `this.db.get("SELECT id FROM users WHERE email = ?", [e], ...` → `} else { processPaymentAndEnroll(user.id); }`
Description: quando o e-mail (`eml`) já existe, o checkout reutiliza a conta sem comparar `pwd` com a senha armazenada. Nenhuma rota da API verifica identidade e há escrita de dados (matrícula, pagamento) — critério CRITICAL do SEC-09.
Impact: qualquer cliente que saiba o e-mail de um aluno matricula essa conta e gera pagamentos em nome dela.
Recommendation: verificar a senha do usuário existente (hash, P-03) e responder 401 em caso de divergência (Playbook P-05). Exige contrato (CT-03).

### [CRITICAL] F-002 · SEC-08 Número de cartão e chave do gateway em log
File: src/AppManager.js:45
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-532 / A09:2021
Evidência: `` console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`); ``
Description: o número completo do cartão (`req.body.card`) e a chave do gateway (`pk_l***`) são impressos em todo checkout.
Impact: PAN e segredo de pagamento vão para stdout/agregadores de log (violação PCI-DSS, vazamento da chave).
Recommendation: logger com mascaramento (no máximo os 4 últimos dígitos) e nunca registrar chave (Playbook P-15).

### [CRITICAL] F-003 · SEC-14 Aprovação de pagamento simulada pelo prefixo do cartão
File: src/AppManager.js:46
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-602 / A04:2021
Evidência: `let status = cc.startsWith("4") ? "PAID" : "DENIED";`
Description: o "gateway" aprova qualquer cartão que comece com `4`; o status `PAID` libera a matrícula e entra na receita do relatório.
Impact: matrícula em curso pago sem cobrança real (qualquer número `4…` é aceito).
Recommendation: isolar o pagamento num adapter de gateway injetável, explicitamente marcado como simulado e selecionado por configuração; integração real com o provedor fica como recomendação manual (Playbook P-09).

### [CRITICAL] F-004 · SEC-03 Rotas administrativa e destrutiva sem autenticação
File: src/AppManager.js:80, 131
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021
Evidência: `app.get('/api/admin/financial-report', (req, res) => {` · `app.delete('/api/users/:id', (req, res) => {`
Description: as rotas são registradas direto no `app`, sem middleware nem verificação de identidade/perfil (cadeia lida até `src/app.js:6-10`).
Impact: qualquer cliente remoto lê receita e nomes de alunos e apaga usuários por ID.
Recommendation: exigir credencial de administrador nas duas rotas (Playbook P-05). Exige contrato (CT-01, CT-02).

### [CRITICAL] F-005 · SEC-02 Segredos e credenciais hardcoded
File: src/utils.js:2-4; src/AppManager.js:18
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `dbUser: "admi***", dbPass: "senh***"`, `paymentGatewayKey: "pk_l***"`; seed `VALUES ('Leonan', 'leonan@fullcycle.com.br', '***')`
Description: credencial de banco de "prod", chave `pk_live_` (usada em runtime em `src/AppManager.js:45`) e senha do usuário de seed em texto no código versionado.
Impact: qualquer pessoa com acesso ao repositório obtém as credenciais; elas permanecem no histórico do git.
Recommendation: ler de variáveis de ambiente via módulo de config, `.env.example` com nomes fictícios, senha de seed via ambiente; **rotacionar** a chave e a senha expostas (Playbook P-01).

### [CRITICAL] F-006 · SEC-06 Armazenamento inseguro de senha
File: src/utils.js:17-23; src/AppManager.js:18, 68
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-916 / CWE-256 / A02:2021
Evidência: `hash += Buffer.from(pwd).toString('base64').substring(0, 2);` … `return hash.substring(0, 10);`
Description: `badCrypto` repete os 2 primeiros caracteres do base64 da senha e trunca em 10: o "hash" depende só dos ~12 primeiros bits da senha (ex.: toda senha iniciada por `se` vira `c2c2c2c2c2`), sem salt e reversível no prefixo; o seed grava a senha em texto puro.
Impact: colisões triviais e recuperação do início da senha em caso de vazamento do banco; senha de seed legível.
Recommendation: KDF com salt (`crypto.scrypt` nativo do Node, sem dependência nova) e seed gravado com hash (Playbook P-03).

### [CRITICAL] F-007 · ARC-01 God Class `AppManager`
File: src/AppManager.js:4-139
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `constructor() { this.db = new sqlite3.Database(':memory:'); }` · `initDb()` (DDL + seed) · `setupRoutes(app)` (3 rotas com SQL e regras)
Description: uma classe cria a conexão, define o schema, semeia dados, registra rotas e contém handlers, regras de pagamento/matrícula e todas as queries (6 papéis).
Impact: nada é testável isoladamente; qualquer mudança toca o arquivo inteiro.
Recommendation: separar em config, database, models, services, controllers, routes e middlewares (Playbook P-08, P-09, P-13).

### [CRITICAL] F-008 · OUTRO-01 Exceção em callback assíncrono derruba o processo (DoS remoto)
File: src/AppManager.js:46, 68; src/utils.js:20
Ocorrências: 2 · Confiança: LIKELY · Categoria: Outro
CWE/OWASP: CWE-248 / CWE-1287 / A05:2021
Evidência: `cc.startsWith("4")` (com `card` numérico no JSON) · `badCrypto(p || "123456")` → `Buffer.from(pwd)` (com `pwd` numérico)
Description: `card` e `pwd` só são checados por "truthy" (`src/AppManager.js:35`); se o cliente enviar número, `startsWith`/`Buffer.from` lançam `TypeError` dentro do callback do `sqlite3`, fora do alcance do Express, e não há handler de erro. Severidade pela rubrica (atacante remoto não autenticado compromete disponibilidade). LIKELY: rastreado pela leitura, não executado (Fase 2 não executa).
Impact: um único `POST /api/checkout` com `"card": 4111` encerra o servidor para todos os usuários.
Recommendation: validar tipos na borda e capturar erros assíncronos num handler central (padrões equivalentes P-07 e P-06).

### [HIGH] F-009 · SEC-15 Checkout sem transação; escritas dependentes sem rollback
File: src/AppManager.js:50-61, 66-72
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-362 / A04:2021
Evidência: `INSERT INTO enrollments` → `INSERT INTO payments` → `INSERT INTO audit_logs` encadeados; `INSERT INTO users` antes da decisão de pagamento
Description: matrícula, pagamento e auditoria são gravados em passos separados sem `BEGIN/COMMIT/ROLLBACK`; o usuário é criado antes de o pagamento ser decidido (pagamento recusado deixa o usuário criado); erro da auditoria é ignorado (linha 57).
Impact: falha intermediária deixa matrícula sem pagamento ou pagamento sem auditoria.
Recommendation: executar o fluxo em uma transação e decidir o pagamento antes de gravar (Playbook P-10).

### [HIGH] F-010 · ARC-04 Acoplamento forte sem injeção de dependência
File: src/AppManager.js:2, 7
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `this.db = new sqlite3.Database(':memory:');` · `const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');`
Description: a classe instancia a infraestrutura de banco e usa `config` global diretamente; não há como substituir banco ou gateway.
Impact: impede testes isolados e troca de banco/gateway.
Recommendation: composition root em `src/app.js` criando dependências e injetando-as (Playbook P-13).

### [HIGH] F-011 · ARC-02 Lógica de negócio nos handlers de rota
File: src/AppManager.js:28-78, 80-129
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: handler de `/api/checkout` decide pagamento, cria usuário, matrícula, pagamento e auditoria; handler do relatório soma receita
Description: regras de pagamento/matrícula e o cálculo de receita estão dentro das funções de rota.
Impact: regra não reutilizável nem testável sem HTTP.
Recommendation: extrair `CheckoutService` e `ReportService`; controllers finos (Playbook P-09).

### [HIGH] F-012 · ARC-05 Callback hell e contadores manuais
File: src/AppManager.js:37-77, 83-128
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: 6 níveis de `db.get/db.run(..., (err) => {` no checkout; `coursesPending--` / `enrPending--` no relatório
Description: fluxo assíncrono manual com aninhamento profundo, contadores de conclusão e mistura `this`/`self`/`function` para obter `lastID`.
Impact: erros perdidos, ordem de resposta não determinística (o teste precisa ordenar o relatório).
Recommendation: helpers com Promise e `async/await` (Playbook P-12).

### [HIGH] F-013 · ARC-03 Estado global mutável
File: src/utils.js:9-10, 14
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `let globalCache = {};` · `globalCache[key] = data;` (chamado em `src/AppManager.js:59`) · `let totalRevenue = 0;` exportado
Description: cache de módulo mutado a cada checkout (`last_checkout_<id>`), nunca lido nem limitado; contador global exportado.
Impact: crescimento de memória ilimitado por usuário; estado compartilhado entre requisições.
Recommendation: remover o cache sem leitores e o contador; estado só via dependências injetadas (Playbook P-13).

### [MEDIUM] F-014 · SEC-17 Sem proteções HTTP básicas
File: src/app.js:5-6
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-770 / CWE-693 / A05:2021
Evidência: `const app = express(); app.use(express.json());`
Description: sem limitação de taxa no checkout, sem cabeçalhos de segurança, `X-Powered-By: Express` habilitado, sem limite explícito de corpo.
Impact: abuso do checkout (força bruta de cartões/e-mails) e fingerprinting.
Recommendation: middleware de cabeçalhos, `x-powered-by` desligado e rate limit no checkout, sem dependência nova (Playbook P-19).

### [MEDIUM] F-015 · SEC-12 Validação de entrada ausente
File: src/AppManager.js:29-35, 68
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-20 / A03:2021
Evidência: `if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");` · `badCrypto(p || "1234***")`
Description: apenas presença é checada; tipo/formato de `eml`, `c_id`, `card` não são validados; `pwd` ausente cria conta com senha fixa previsível.
Impact: dados inválidos persistidos; contas com senha conhecida; alimenta o crash do F-008.
Recommendation: validação de tipos e formato na borda; senha ausente não pode virar valor fixo (Playbook P-07). Validação de formato que rejeite entradas hoje aceitas exige contrato (CT-05).

### [MEDIUM] F-016 · ARC-10 Integridade referencial ausente
File: src/AppManager.js:12-16, 131-136
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)` · `res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.")`
Description: sem `NOT NULL`, `UNIQUE(email)` nem `FOREIGN KEY`; a exclusão de usuário deixa matrículas e pagamentos órfãos (a própria resposta admite).
Impact: e-mails duplicados sob concorrência; relatório com aluno `Unknown`.
Recommendation: constraints no schema e transação; o destino de matrículas/pagamentos ao excluir usuário é decisão de negócio (Playbook P-10).

### [MEDIUM] F-017 · ARC-12 Dinheiro em ponto flutuante
File: src/AppManager.js:13, 15, 109
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `price REAL` · `amount REAL` · `courseData.revenue += payment.amount;`
Description: preços, pagamentos e receita em `REAL`/float.
Impact: erros de arredondamento acumulados na receita.
Recommendation: armazenar centavos inteiros e converter na borda, mantendo o mesmo formato numérico na resposta (Playbook P-17).

### [MEDIUM] F-018 · ARC-11 `SELECT *` e carga total sem paginação
File: src/AppManager.js:37, 83, 92
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `SELECT * FROM courses WHERE id = ?` · `SELECT * FROM courses` · `SELECT * FROM enrollments WHERE course_id = ?`
Description: consultas trazem todas as colunas e o relatório carrega todas as tabelas em memória.
Impact: custo crescente com o volume; colunas desnecessárias trafegadas.
Recommendation: selecionar colunas e agregar no SQL (Playbook P-11; paginação só se retrocompatível).

### [MEDIUM] F-019 · ARC-09 Tratamento de erro ruim
File: src/AppManager.js:38, 57, 92-93, 104-106, 133-135
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `if (err || !course) return res.status(404)...` · `(err) => {` sem uso de `err` (57, 104, 106, 133) · `let enrPending = enrollments.length;` sem checar `err`
Description: erro de banco vira 404 no checkout; erros ignorados em callbacks; `DELETE` responde sucesso mesmo com erro ou ID inexistente; respostas misturam texto e JSON; sem handler central.
Impact: falhas mascaradas como sucesso; `enrollments` indefinido derruba o processo.
Recommendation: helpers async + middleware central de erros (Playbook P-06). Corrigir status de erro (404/500) exige contrato (CT-04).

### [MEDIUM] F-020 · ARC-07 Queries N+1 no relatório financeiro
File: src/AppManager.js:89-124
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `courses.forEach(c => { this.db.all(... enrollments ...` → `enrollments.forEach(enr => { this.db.get(... users ...` → `this.db.get(... payments ...`
Description: 1 + C + 2·M consultas (C cursos, M matrículas).
Impact: latência linear no nº de matrículas.
Recommendation: uma consulta com `JOIN` e agregação em memória por curso (Playbook P-11).

### [LOW] F-021 · QLT-04 `console.log` como mecanismo de log
File: src/app.js:13; src/AppManager.js:45; src/utils.js:13
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `` console.log(`[LOG] Salvando no cache: ${key}`); ``
Description: logs ad hoc sem nível nem mascaramento.
Impact: logs não filtráveis; facilita vazamentos como o F-002.
Recommendation: logger único com nível e mascaramento (Playbook P-15).

### [LOW] F-022 · QLT-03 Código e configuração mortos
File: src/AppManager.js:2; src/utils.js:2-3, 5, 10, 25
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `totalRevenue` importado e nunca usado; `dbUser`, `dbPass`, `smtpUser` sem uso (banco é `:memory:`); `globalCache` exportado e nunca lido
Description: busca por nome em `src/` e `test/` confirma ausência de uso.
Impact: ruído e falsa impressão de dependência de banco externo/SMTP.
Recommendation: remover (Playbook P-16).

### [LOW] F-023 · QLT-01 Magic strings e números
File: src/AppManager.js:21, 46, 48, 68, 108; src/utils.js:19
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `'PAID'`/`"DENIED"` repetidos; prefixo `"4"`; `for(let i = 0; i < 10000; i++)`
Description: status de pagamento e regras como literais soltos.
Impact: divergência fácil entre gravação e leitura de status.
Recommendation: constantes nomeadas (Playbook P-16).

### [LOW] F-024 · QLT-05 Estilo inconsistente
File: src/AppManager.js:26, 29-33, 54
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `const self = this;` misturado com `this.db` e `function(err) { ... this.lastID }`; `let` em variáveis nunca reatribuídas
Description: três formas de referenciar o contexto e `let` onde cabe `const`.
Impact: leitura difícil e risco de `this` errado.
Recommendation: `const`, arrow functions e async/await uniformes (Playbook P-16).

### [LOW] F-025 · QLT-02 Nomes crípticos
File: src/AppManager.js:29-33
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd; let cid = req.body.c_id; let cc = req.body.card;`
Description: variáveis de uma letra; as chaves do payload (`usr`, `eml`, `pwd`, `c_id`) são contrato público e serão mantidas.
Impact: legibilidade.
Recommendation: nomes descritivos internos, mapeando as chaves do payload na borda (Playbook P-16).

## Descartados / falsos positivos
- SEC-01 em src/AppManager.js:37, 40, 50, 54, 57, 69, 92, 104, 106, 133 — descartado porque todas as consultas usam placeholders `?`.
- SEC-07 em src/AppManager.js:112-115 — nomes de alunos no relatório são consequência da rota administrativa aberta (coberto pelo F-004); senha/hash nunca são serializados.
- SEC-11 em src/AppManager.js:131 — sem identidade no fluxo; reportado como F-004/F-001 conforme o catálogo.
- SEC-13 em src/AppManager.js:38-135 — respostas de erro são textos fixos; nenhum detalhe de exceção chega ao cliente.
- SEC-16 em package.json:11-12 — lockfile presente (express 4.22.1, sqlite3 5.1.7), ambas importadas; sem base segura para afirmar vulnerabilidade sem consulta de rede (ver Recomendações manuais: `npm audit`).
- SEC-04, SEC-05, SEC-10 — sem `eval`/`exec`/`child_process`, sem flag de debug, sem campos de privilégio.
- DEP-03/DEP-05: nenhuma encontrada para Express 4.22.1 / sqlite3 5.1.7 / Node.js 24 (`Buffer.from` é a API moderna; sem `new Buffer`, `url.parse`, `body-parser`, `req.param`).
- TST-01/02/03 — há suíte `node:test` com 8 testes de integração, `npm test` em package.json:8 e instruções de execução no README; nenhuma referência estática quebrada.

## Correções que exigem mudança de contrato

| ID | Rota/campo | Mudança | Sev. | Motivo (Finding) | Impacto para clientes | Resolvido na Opção 1? | Prova prevista na Opção 2 |
|---|---|---|---|---|---|---|---|
| CT-01 | GET /api/admin/financial-report | exigir credencial de administrador (sem ⇒ 401) | CRITICAL | F-004 | enviar `Authorization` com a credencial de admin | não (fica residual) | teste novo (sem/inválida ⇒ 401; válida ⇒ 200) |
| CT-02 | DELETE /api/users/:id | exigir credencial de administrador (sem ⇒ 401) | CRITICAL | F-004 | enviar `Authorization` com a credencial de admin | não (fica residual) | teste novo (sem ⇒ 401; válida ⇒ 200) |
| CT-03 | POST /api/checkout (e-mail já cadastrado) | verificar `pwd` contra o hash; divergente ⇒ 401 e nada é gravado | CRITICAL | F-001 | cliente precisa enviar a senha correta da conta existente | não (fica residual) | teste novo (senha errada ⇒ 401, relatório inalterado) |
| CT-04 | DELETE /api/users/:id | ID inexistente ⇒ 404; erro de banco ⇒ 500 (hoje sempre 200) | MEDIUM | F-019 | tratar 404 | não (fica residual) | teste novo (ID inexistente ⇒ 404) |
| CT-05 | POST /api/checkout | rejeitar com 400: `pwd` ausente, `eml` sem formato de e-mail, `card` fora de 13–19 dígitos, `c_id` não inteiro positivo | MEDIUM | F-015 | enviar payload válido; `pwd` passa a ser obrigatório | parcial (tipos não-string ⇒ 400 sem mudar casos hoje bem-sucedidos; senha ausente vira senha aleatória em vez de fixa) | teste novo (cada caso ⇒ 400) |

Resumo para a pergunta: 5 correções exigem contrato; na Opção 1 ficam residuais 2 CRITICAL (F-001, F-004) e 0 HIGH. Independente da opção, F-003 (integração real de pagamento) e a parte "órfãos ao excluir usuário" do F-016 ficam residuais (exigem decisão de negócio/integração externa).

## Testes afetados
| Teste | Motivo (C-xx/CT-xx) | Classe (T1/T2/T4) | Ajuste previsto |
|---|---|---|---|
| test/api.test.js::before / aguardarServidor / relatorio() | CT-01 (só Opção 2) | T1 | enviar credencial de admin nas chamadas ao relatório; definir variáveis de ambiente de teste no `spawn` (credencial admin, senha de seed); asserções idênticas |
| test/api.test.js::"DELETE /api/users/:id retorna 200" | CT-02 (só Opção 2) | T1 | enviar credencial de admin; asserções idênticas |
| test/api.test.js::"checkout de usuário já existente reutiliza o cadastro" | CT-03 + C-01 (só Opção 2) | T1 | senha de seed `123` passa a vir do ambiente definido no `spawn`; asserções idênticas |
| test/contratos.test.js (novo) | CT-01…CT-05 (só Opção 2) | T4 | provas de cada contrato; vermelho no checkpoint original |

Opção 1: nenhum teste afetado (entrypoint `src/app.js`, rotas, status e dados de seed preservados).

## Plano de mudanças
| ID | Mudança | Sev. | Resolve | Arquivos | Padrão | Afeta contrato | Depende de |
|---|---|---|---|---|---|---|---|
| C-01 | `src/config/settings.js` lendo ambiente (PORT, PAYMENT_GATEWAY_KEY, SEED_USER_PASSWORD, ADMIN_API_KEY na Opção 2); `.env.example`; remover literais e chaves mortas; senha de seed vinda do ambiente (aleatória se ausente, mesmos dados de seed) | CRITICAL | F-005, F-022 (parcial) | src/utils.js, src/config/settings.js, .env.example | P-01 | não | — |
| C-02 | `src/database/` (conexão, helpers Promise, schema com NOT NULL/UNIQUE(email)/FKs de curso e matrícula, `PRAGMA foreign_keys`, seed) e `src/models/` (user, course, enrollment, payment, auditLog); dinheiro em centavos convertido na borda | CRITICAL | F-007 (parcial), F-016 (parcial), F-017 | src/AppManager.js, src/database/*, src/models/* | P-08 (+P-02, P-17, P-10) | não | C-01 |
| C-03 | hash de senha com `crypto.scrypt` + salt (nativo) e comparação em tempo constante; seed com hash | CRITICAL | F-006 | src/utils.js, src/services/passwordHasher.js | P-03 | não | C-02 |
| C-04 | `src/services/` checkoutService (pagamento decidido antes de gravar; transação BEGIN/COMMIT/ROLLBACK), paymentGateway (adapter simulado explícito, injetável), reportService, userService | CRITICAL | F-009, F-011, F-007 (parcial), F-003 (parcial) | src/services/* | P-09 (+P-10) | não | C-02, C-03 |
| C-05 | validação na borda do checkout: tipos string/inteiro (evita o crash), senha ausente ⇒ aleatória; Opção 2 acrescenta CT-05 | CRITICAL | F-008, F-015 (parcial; total na Opção 2) | src/middlewares/validateCheckout.js | P-07 | CT-05 (só Opção 2) | C-04 |
| C-06 | middleware de credencial admin nas rotas de relatório e exclusão; verificação de senha no checkout | CRITICAL | F-004, F-001 | src/middlewares/requireAdmin.js, src/services/checkoutService.js, src/routes/* | P-05 | CT-01, CT-02, CT-03 (**só Opção 2**) | C-03, C-04 |
| C-07 | wrapper async + middleware central de erros (mesmos status e textos na Opção 1; CT-04 na Opção 2) | CRITICAL | F-008, F-019 | src/middlewares/errorHandler.js, src/controllers/* | P-06 | CT-04 (só Opção 2) | C-04 |
| C-08 | logger com nível e mascaramento; remover log de cartão e chave | CRITICAL | F-002, F-021 | src/utils/logger.js, src/services/* | P-15 | não | C-04 |
| C-09 | callbacks → async/await; relatório com uma consulta `JOIN` e colunas explícitas | HIGH | F-012, F-018, F-020 | src/models/*, src/services/reportService.js | P-12 / P-11 | não | C-02, C-04 |
| C-10 | composition root em `src/app.js` (cria db, models, services, controllers, rotas e injeta); remover `AppManager` e cache global | HIGH | F-010, F-013, F-007 | src/app.js, src/routes/*, src/controllers/* | P-13 | não | C-04, C-09 |
| C-11 | cabeçalhos de segurança, `x-powered-by` desligado, limite de corpo e rate limit no checkout (sem dependência nova; limite folgado para não afetar a suíte) | MEDIUM | F-014 | src/middlewares/securityHeaders.js, src/middlewares/rateLimit.js, src/app.js | P-19 | não | C-10 |
| C-12 | limpeza: constantes de status, nomes descritivos internos (chaves do payload mantidas), `const`, remoção de `src/utils.js`/código morto | LOW | F-022, F-023, F-024, F-025 | src/** | P-16 | não | C-10 |

Recomendações manuais (sem `C-xx`):
- **Rotacionar** a chave `pk_l***` e a senha `senh***`: continuam no histórico do git mesmo após o C-01.
- Integrar um provedor de pagamento real (F-003): fora do escopo da refatoração; o adapter simulado fica isolado e sinalizado.
- Decidir a regra de negócio para matrículas/pagamentos ao excluir usuário (cascata × bloqueio 409) (F-016).
- Rodar `npm audit` (classe C, usa rede) e declarar `engines.node` no package.json.

## Plano de comandos
| ID | Comando | Finalidade | Origem | Classe | Efeitos colaterais |
|---|---|---|---|---|---|
| K-00 | `git branch refactor-arch/checkpoint-20261106-131947` | checkpoint do código original (arquivos rastreados do projeto estão limpos em HEAD) | política 07, 2.2 | C | cria ref local; sem commit |
| K-00b | cópia de `src/`, `test/`, `package*.json` e `node_modules/` para `<scratchpad>/checkpoint-20261106-131947/` | base para provas vermelhas (Opção 2) | política 07, 2.2 | C | escreve no scratchpad, fora do projeto |
| K-01 | `node --version` | registrar runtime | — | A | nenhum |
| K-02 | `npm test` (`node --test`) | baseline e validação final (V1) | package.json:8 | B | sobe a app na porta 3000 (banco em memória) e encerra |
| K-03 | `node --check <arquivo>` em cada `src/**/*.js` | validação rápida/estática (V5) | toolchain | B | nenhum |
| K-04 | `npm start` (em background) | boot (V3) | package.json:7; README.md:9 | B | ocupa a porta 3000 até K-07 |
| K-05 | requisições 1 e 2 de `api.http` (POST /api/checkout) via `curl` em `http://localhost:3000` | V3 com a coleção existente | api.http:3-25 | B | grava no banco em memória |
| K-06 | requisições 3 e 4 de `api.http` (GET /api/admin/financial-report, DELETE /api/users/1) | V3 em rota administrativa/destrutiva | api.http:27-31 | D | DELETE em usuário; já coberto pela suíte (V1) ⇒ recomendado pular |
| K-07 | encerrar o processo iniciado em K-04 (por PID) | limpeza | — | B | libera a porta 3000 |
| K-08 | `node --test test/contratos.test.js` na cópia K-00b | prova de sensibilidade (vermelho) — só Opção 2 | 06, 8.9 | B | executa na cópia fora do projeto |
| K-09 | `git diff --stat -- ecommerce-api-legacy` e `git diff -- ecommerce-api-legacy/test` | integridade dos testes | — | A | nenhum |

Instalação: não necessária (`node_modules` presente com express e sqlite3 compilado — `node_sqlite3.node`). `npm install` (README.md:8, classe C) só se o baseline falhar por dependência.

## Plano de validação
| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim | `npm test` (package.json:8, B) | 8 testes de integração caixa-preta HTTP (`node:test`) cobrindo as 3 rotas |
| V2 Script de verificação do projeto | não | — | sem lint/check/CI |
| V3 Boot + requisições existentes | sim | boot `npm start` + `api.http` (K-05 B; K-06 D) | 2 de 4 requisições automáticas; admin/DELETE só com aprovação individual |
| V4 Sondagem ad hoc | não aplicável | — | testes e coleção cobrem todas as rotas (P4 não será perguntada) |
| V5 Estático | sempre | `node --check` (B) | todos os arquivos de `src/` |
| Pré-requisitos | | `npm install` (C) | já satisfeitos; não previsto |
| Testes afetados previstos | | ver "Testes afetados" | Opção 1: nenhum; Opção 2: T1 em 3 pontos + T4 novo arquivo |
| Prova prevista por `CT-xx` (Opção 2) | | teste novo em `test/contratos.test.js` (verde no refatorado; vermelho na cópia K-00b) | CT-01…CT-05 |
| Não exercitável | | integração real de pagamento (inexistente); porta 3000 fixa (a suíte exige porta livre) | — |

Degrau alvo: V1 + V3 (+ V5).

## Decisões do usuário
- P1 Escopo: "Sim, aplicar todas" (C-01…C-12)
- P2 Modo de comandos: "Equilibrado (recomendado)"
- P3 Contrato: "Manter o contrato como está (recomendado)" — Opção 1 (CT-01…CT-05 não aplicados; residuais)
- P4 Sondagem ad hoc: não aplicável (testes e coleção cobrem todas as rotas)

================================
Total: 25 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---
# ANEXO — FASE 3 (Run id: 20261106-131947)

## Decisões do usuário (registro)
- Escopo: todas (C-01…C-12)
- Modo de comandos: Equilibrado
- Contrato: Opção 1 — manter o contrato
- Sondagem ad hoc: não aplicável
- Lote classe C (K-00 branch de checkpoint): "Executar todos" · K-00b não executado (desnecessário na Opção 1)
- Classe D individual: K-06a (GET /api/admin/financial-report) "Executar"; K-06b (DELETE /api/users/1) "Executar"

## Estrutura DEPOIS
```
ecommerce-api-legacy/
├── .env.example
├── api.http
├── package.json
├── README.md
├── src/
│   ├── app.js                      # composition root + início do servidor
│   ├── config/        constants.js, settings.js
│   ├── controllers/   checkoutController.js, reportController.js, userController.js
│   ├── database/      connection.js, schema.js
│   ├── middlewares/   errorHandler.js, rateLimit.js, securityHeaders.js, validateCheckout.js
│   ├── models/        auditLogModel.js, courseModel.js, enrollmentModel.js, paymentModel.js, reportModel.js, userModel.js
│   ├── routes/        index.js
│   ├── services/      checkoutService.js, passwordService.js, paymentGateway.js, reportService.js
│   └── utils/         appError.js, logger.js, money.js
└── test/
    └── api.test.js                 # inalterado
```

| Métrica | ANTES | DEPOIS |
|---|---|---|
| Arquivos-fonte | 3 | 26 |
| Linhas de código (aprox.) | ~180 | ~566 |
| Camadas presentes | tudo misturado em AppManager/utils | config, database, models, services, controllers, routes, middlewares, utils, composition root |
| Maior arquivo | src/AppManager.js (141) | src/app.js (71) |
| Arquivos com 3+ papéis | 2 (AppManager.js, utils.js) | 0 |

Método de contagem: `wc -l` (mesmo da Fase 1) — E-00 e E-08.

### Mapa antigo → novo
| Arquivo original | Destino(s) |
|---|---|
| src/app.js | src/app.js (composition root: `createApp` + `start`; mesmo comando `node src/app.js`) |
| src/AppManager.js | database/connection.js, database/schema.js (initDb), models/*, services/checkoutService.js, services/reportService.js, services/paymentGateway.js, controllers/*, routes/index.js — arquivo removido |
| src/utils.js | config/settings.js (config), services/passwordService.js (badCrypto → scrypt), utils/logger.js (logAndCache → logger); `globalCache`/`totalRevenue` removidos — arquivo removido |
| (novo) | middlewares/*, utils/appError.js, utils/money.js, config/constants.js, .env.example |

## Mudanças aplicadas
| ID | Status | Observação |
|---|---|---|
| C-01 | aplicada | `config/settings.js` lê PORT, SEED_USER_PASSWORD, LOG_LEVEL, CHECKOUT_RATE_MAX; `.env.example` com valores fictícios; literais removidos. `paymentGatewayKey`, `dbUser`, `dbPass`, `smtpUser` removidos por não terem uso (a chave só alimentava o log do F-002); PAYMENT_GATEWAY_KEY deve ser introduzida junto da integração real. Seed: senha do ambiente ou aleatória, mesmos dados |
| C-02 | aplicada | conexão com helpers Promise; DDL com NOT NULL, UNIQUE(email), FKs de `course_id`/`enrollment_id`, `PRAGMA foreign_keys`; dinheiro em centavos (colunas `price`/`amount` mantidas, tipo INTEGER — banco em memória, sem migração); `enrollments.user_id` sem FK para preservar o DELETE |
| C-03 | aplicada | `crypto.scrypt` + salt de 16 bytes (`scrypt$salt$hash`); seed gravado com hash. Função de verificação não criada: na Opção 1 nada compara senha (seria código morto) |
| C-04 | aplicada | checkoutService decide o pagamento antes de gravar e grava usuário/matrícula/pagamento/auditoria em transação (fila serializada na conexão única); gateway simulado isolado e sinalizado; reportService. `userService` do plano não criado: o DELETE não tem regra de negócio, o controller usa `userModel` direto |
| C-05 | aplicada (variante Opção 1) | campos obrigatórios como antes (400 "Bad Request"); `card` não-string ou `pwd` truthy não-string ⇒ 400 (antes derrubava o processo); `pwd` ausente ⇒ senha aleatória |
| C-06 | não aplicável | Opção 1: P-05 não se aplica; F-001 e F-004 residuais |
| C-07 | aplicada | `asyncHandler` + handler central; mesmos status e textos; erros 4xx do parser respondem só o texto do status (sem página com stack); DELETE mantém 200 e agora registra o erro |
| C-08 | aplicada | logger JSON com nível; cartão só como `***<4 últimos>`; chave nunca registrada (E-06) |
| C-09 | aplicada | async/await em todo o fluxo; relatório com uma consulta `LEFT JOIN` e colunas explícitas (antes 1 + C + 2·M consultas) |
| C-10 | aplicada | dependências criadas em `createApp` e injetadas; `AppManager` e cache global removidos |
| C-11 | aplicada | `x-powered-by` desligado; X-Content-Type-Options, X-Frame-Options, Referrer-Policy e CSP; corpo JSON ≤ 10kb; rate limit 30/min por IP no checkout (configurável) |
| C-12 | aplicada | `PAYMENT_STATUS`, `SIMULATED_APPROVED_PREFIX`; nomes internos descritivos (chaves do payload mantidas); `const`/arrow uniformes; `src/utils.js` removido |

## Contratos — resultado
Contrato preservado: rotas, métodos, status e formato das respostas inalterados.

| Finding | Severidade | O que ficou sem corrigir | O que exigiria (Opção 2) |
|---|---|---|---|
| F-004 | CRITICAL | relatório financeiro e DELETE de usuário sem autenticação | CT-01/CT-02: credencial de admin + testes que comprovem |
| F-001 | CRITICAL | checkout reutiliza conta existente sem verificar senha | CT-03: verificar `pwd` (hash) ⇒ 401 + teste |
| F-019 | MEDIUM (parcial) | DELETE sempre 200 (erro agora é registrado em log); erro de banco na busca do curso ⇒ 404 | CT-04: 404/500 + teste |
| F-015 | MEDIUM (parcial) | formato de `eml`/`card`/`c_id` e `pwd` obrigatório | CT-05: 400 por regra + teste |

Ajustes de conteúdo sem mudança de formato: cabeçalho `X-Powered-By` removido e cabeçalhos de segurança adicionados (C-11, aditivo).

## Alterações em testes
Nenhuma (E-08: `git diff -- test` vazio).

## Testes adicionados (Opção 2)
Não aplicável (Opção 1).

## Evidências de execução
(`E-00` — Fase 1 — foi gravado na Fase 2; ver `06-protocolo-validacao.md`, seção 7.)

### E-01 · Suíte de testes (baseline)
Comando:      `npm test` (→ `node --test`)          Diretório: ecommerce-api-legacy
Origem:       K-02 · package.json:8 · Classe B · Autorização: automática (classe B)
Início/Fim:   2026-11-06T13:31:46-03:00 → 2026-11-06T13:31:50-03:00 (4 s)        Exit code: 0
Ambiente:     Node.js v24.11.1, npm 11.6.4, express 4.22.1, sqlite3 5.1.7
Resultado:    passed 8 | failed 0 | skipped 0
Bruto:        reports/evidence/project-2/20261106-131947/E-01-baseline-npm-test.log
Integridade:  testes alterados/adicionados: 0

### E-02 · Boot da aplicação (baseline)
Comando:      `npm start` (background)          Diretório: ecommerce-api-legacy
Origem:       K-04 · package.json:7; README.md:9 · Classe B · Autorização: automática
Resultado:    "Frankenstein LMS rodando na porta 3000..."; log mostra `Processando cartão 4111*** na chave pk_l***` (prova do F-002; mascarado na evidência)
Bruto:        reports/evidence/project-2/20261106-131947/E-02-baseline-boot.log
Encerramento: K-07 · PID 6948 (node) encerrado; porta 3000 liberada

### E-03 · Requisições de api.http (baseline)
Comando:      `curl` das 4 requisições de api.http, na ordem          Diretório: ecommerce-api-legacy
Origem:       K-05 (req. 1–2, B, automática) · K-06a/K-06b (req. 3–4, D, individual aprovada) · api.http:3-31
Início/Fim:   2026-11-06T13:32:45-03:00 → 2026-11-06T13:32:45-03:00        Exit code: 0
Resultado:    200 `{msg, enrollment_id}` · 400 "Pagamento recusado" · 200 `[{course, revenue, students[{student, paid}]}]` · 200 texto de exclusão
Bruto:        reports/evidence/project-2/20261106-131947/E-03-baseline-api-http.log (contém o cartão de teste versionado em api.http)

### E-04 · Verificação estática (após refatoração)
Comando:      `node --check <arquivo>` para cada `src/**/*.js` + `node -e "require('./src/app.js')"`
Origem:       K-03 · toolchain · Classe B · Autorização: automática
Início/Fim:   2026-11-06T13:36:15-03:00 → 2026-11-06T13:36:17-03:00        Exit code: 0
Resultado:    26/26 OK; import OK (`createApp` = function)
Bruto:        reports/evidence/project-2/20261106-131947/E-04-final-node-check.log

### E-05 · Suíte de testes (após refatoração)
Comando:      `npm test` (→ `node --test`)          Diretório: ecommerce-api-legacy
Origem:       K-02 · package.json:8 · Classe B · Autorização: automática
Início/Fim:   2026-11-06T13:36:22-03:00 → 2026-11-06T13:36:25-03:00 (3 s)        Exit code: 0
Resultado:    passed 8 | failed 0 | skipped 0   (baseline E-01: passed 8 | failed 0 | skipped 0)
Bruto:        reports/evidence/project-2/20261106-131947/E-05-final-npm-test.log
Integridade:  testes alterados/adicionados: 0 (verificado por `git diff -- test`, E-08)

### E-06 · Boot da aplicação (após refatoração)
Comando:      `npm start` (background)
Origem:       K-04 · Classe B · Autorização: automática
Resultado:    `{"level":"info","msg":"LMS API rodando na porta 3000"}`; logs de pagamento com `"card":"***4444"`, sem chave
Bruto:        reports/evidence/project-2/20261106-131947/E-06-final-boot.log
Encerramento: K-07 · PID 19324 (node) encerrado; porta 3000 liberada

### E-07 · Requisições de api.http (após refatoração)
Comando:      mesmas 4 requisições de E-03, mesma ordem
Origem:       K-05 (B) · K-06a/K-06b (D, individual aprovada)
Início/Fim:   2026-11-06T13:36:34-03:00 → 2026-11-06T13:36:35-03:00        Exit code: 0
Resultado:    status e corpos iguais aos de E-03 (ETag idêntico nas req. 1, 2 e 4); relatório com o mesmo conteúdo, cursos ordenados por id
Bruto:        reports/evidence/project-2/20261106-131947/E-07-final-api-http.log

### E-08 · Reauditoria por busca, integridade e métricas
Comando:      script de buscas `grep` somente leitura (no scratchpad, fora do projeto) + `git diff --stat -- test` + `git status` + `wc -l`
Origem:       K-09 · Classe A
Início/Fim:   2026-11-06T13:37:21-03:00 → 2026-11-06T13:37:23-03:00
Resultado:    nenhum sinal de SEC-01/02/06/08, ARC-03/04/05/11/12, QLT-01/04 ou senha fixa; SQL só em models/database; rotas sem verificação de identidade (residual); testes inalterados
Bruto:        reports/evidence/project-2/20261106-131947/E-08-reauditoria.log

### Comparação antes/depois (rotas)
| Método | Rota | ANTES | DEPOIS | Resultado | Prova |
|---|---|---|---|---|---|
| POST | /api/checkout (sucesso) | 200 {msg, enrollment_id} | 200 {msg, enrollment_id} | igual | E-03, E-07, E-01, E-05 |
| POST | /api/checkout (pagamento recusado) | 400 "Pagamento recusado" | 400 "Pagamento recusado" | igual | E-03, E-07 |
| POST | /api/checkout (campos ausentes) | 400 | 400 | igual | E-01, E-05 |
| POST | /api/checkout (curso inexistente) | 404 | 404 | igual | E-01, E-05 |
| POST | /api/checkout (usuário existente) | 200 | 200 | igual | E-01, E-05 |
| GET | /api/admin/financial-report | 200 [{course, revenue, students}] | 200 [{course, revenue, students}] | igual (conteúdo idêntico; ordem dos cursos passa a ser por id — no original dependia dos callbacks, e o teste já ordena) | E-03, E-07 |
| DELETE | /api/users/:id | 200 texto | 200 texto | igual | E-03, E-07, E-01, E-05 |

### Resumo da validação
| Degrau | Comando | Resultado | Evidência |
|---|---|---|---|
| V1 | `npm test` | passed 8 / failed 0 / skipped 0 (baseline 8/0/0) | E-01, E-05 |
| V3 | `npm start` + api.http (4 req.) | 4/4 iguais ao baseline | E-02, E-03, E-06, E-07 |
| V5 | `node --check` + import | 26/26 OK | E-04 |
Veredito: VALIDADO (V1+V3)

## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — JavaScript, Node.js v24.11.1 (package.json, `node --version`) (E-00)
- [x] Framework detectado corretamente — Express 4.22.1 (lock) + `express()` em src/app.js (E-00)
- [x] Domínio da aplicação descrito corretamente — LMS com checkout (tabelas courses/enrollments/payments; README.md:3) (E-00)
- [x] Número de arquivos analisados condiz com a realidade — 3 arquivos, 180 linhas por `wc -l` (E-00)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — reports/audit-project-2.md, seções na ordem do template
- [x] Cada finding tem arquivo e linhas exatos — linhas tiradas da leitura numerada dos 3 arquivos
- [x] Findings ordenados por severidade (CRITICAL → LOW) — F-001…F-008 CRITICAL, F-009…F-013 HIGH, F-014…F-020 MEDIUM, F-021…F-025 LOW
- [x] Mínimo de 5 findings identificados — 25
- [x] Detecção de APIs deprecated incluída (se aplicável) — busca feita; "DEP: nenhuma encontrada para Express 4.22.1 / sqlite3 5.1.7 / Node.js 24"
- [x] Skill pausa e pede confirmação antes da Fase 3 — linha `Phase 2 complete...` + rodada de perguntas; respostas em "Decisões do usuário"

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — config/, models/, services/, controllers/, routes/, middlewares/; 0 arquivos com 3+ papéis (E-08)
- [x] Configuração extraída para módulo de config (sem hardcoded) — src/config/settings.js; busca SEC-02 vazia (E-08). Segredo antigo segue no histórico git: rotação recomendada
- [x] Models criados para abstrair dados — src/models/*, src/database/*; SQL fora deles: nenhum (E-08)
- [x] Views/Routes separadas para visualização ou roteamento — src/routes/index.js:8-10 só mapeia
- [x] Controllers concentram o fluxo da aplicação — src/controllers/* chamam services/models; sem SQL (E-08)
- [~] Error handling centralizado — src/middlewares/errorHandler.js; residual F-019 (DELETE sempre 200; erro de banco na busca de curso ⇒ 404, por contrato)
- [x] Entry point claro — src/app.js (`createApp` + `start`), `npm start` (E-06)
- [x] Aplicação inicia sem erros — E-06
- [x] Endpoints originais respondem corretamente — 3 de 3 rotas (7 cenários) iguais; 0 alteradas por contrato (E-05, E-07)

## Itens residuais (reauditoria)
| Finding | Sev. | Situação | Motivo |
|---|---|---|---|
| F-004 SEC-03 | CRITICAL | presente | risco de contrato (Opção 1); exige CT-01/CT-02 |
| F-001 SEC-09 | CRITICAL | presente | risco de contrato (Opção 1); exige CT-03 |
| F-003 SEC-14 | CRITICAL | parcial | gateway simulado isolado e sinalizado; integração real fora de escopo |
| F-015 SEC-12 | MEDIUM | parcial | tipos validados (crash eliminado); validação de formato exige CT-05 |
| F-016 ARC-10 | MEDIUM | parcial | constraints aplicadas; órfãos no DELETE dependem de decisão de negócio |
| F-019 ARC-09 | MEDIUM | parcial | handler central aplicado; status de erro do DELETE e da busca de curso exigem CT-04 |

Resolvidos: F-002, F-005, F-006, F-007, F-008 (só validação estática), F-009, F-010, F-011, F-012, F-013, F-014, F-017, F-018, F-020, F-021, F-022, F-023, F-024, F-025.

## Observações da execução
- Stack detectada e confiança: JavaScript (Node.js 24.11.1) + Express 4.22.1, confiança alta.
- Dicas específicas usadas × derivadas do sinal abstrato: dicas Node usadas em SEC-02, SEC-06, SEC-08, SEC-14, ARC-05, ARC-07; OUTRO-01 (exceção em callback derruba o processo) é derivado, pois o catálogo não tem entrada para isso.
- Nível de organização encontrado e como a Fase 3 se adaptou: `monolito-sem-camadas` ⇒ todas as camadas criadas. Mantive o entrypoint em `src/app.js`, sem criar `server.js` como sugere a convenção Express, porque os testes e o `npm start` executam esse arquivo.
- Falsos positivos descartados: 8 grupos (SEC-01, SEC-07, SEC-11, SEC-13, SEC-16, SEC-04/05/10, DEP, TST).
- Limitações da validação: a correção do F-008 (`card`/`pwd` numérico ⇒ 400) não foi exercitada em execução, porque a sondagem ad hoc não se aplica; está validada por leitura e V5. Caminhos de falha interna de banco não foram exercitados.
- Mudanças em caminhos internos de erro, nenhuma alcançável por cliente com o banco em memória:
  - falha na gravação da auditoria agora faz rollback e responde 500 "Erro Auditoria"; antes era ignorada e respondia 200;
  - pagamento recusado não cria mais o usuário (isso não é observável pela API);
  - JSON inválido responde 400 "Bad Request" em texto; antes vinha a página padrão do Express com stack.
- Tentativas/iterações na Fase 3 e reversões: 1 tentativa, nenhuma reversão.
- Arquivos criados pela execução fora do código-fonte:
  - branch local `refactor-arch/checkpoint-20261106-131947` (HEAD 5303107), que você pode remover;
  - scripts temporários `api-http.sh` e `reaudit.sh` no scratchpad, fora do projeto;
  - evidências em `reports/evidence/project-2/20261106-131947/`;
  - `.env.example` no projeto (previsto no C-01).
- Ambiente: comandos Bash com crases/aspas aninhadas falharam no harness (exit 127). Por isso a bateria e a reauditoria rodaram por script no scratchpad.
- Recomendações pendentes:
  - rotacionar `pk_l***` e `senh***`, que continuam no histórico do git;
  - reexecutar com a Opção 2 para fechar F-001/F-004;
  - integrar um gateway real;
  - decidir a regra para órfãos;
  - rodar `npm audit`.

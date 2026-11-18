================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Path:    ecommerce-api-legacy
Run:     2026-11-16T21:36:57-03:00          Run id: 20261116-213657
Stack:   JavaScript (Node.js) + Express 4.22.1 (confiança: alta)
Files:   3 analyzed | ~180 lines of code
Architecture: monolito-sem-camadas
Skill:   refactor-arch 1.2 | Catalog 1.2
Evidence: reports/evidence/project-2/20261116-213657/

## Summary
CRITICAL: 6 | HIGH: 7 | MEDIUM: 7 | LOW: 5
Total: 25 findings (53 ocorrências)
Por categoria: Segurança 10 | Arquitetura 10 | Deprecated 0 | Testes 0 | Qualidade 5 | Outro 0
Cobertura: 3/3 arquivos-fonte lidos integralmente; 0 inspecionados por busca (teste, manifesto, README e api.http também lidos integralmente)

## Estrutura ANTES
```
ecommerce-api-legacy/
├── README.md
├── api.http
├── package.json
├── src/
│   ├── app.js            (14)
│   ├── AppManager.js     (141)
│   └── utils.js          (25)
└── test/
    └── api.test.js       (127)
```

| Métrica | Valor |
|---|---|
| Arquivos-fonte | 3 |
| Linhas de código (aprox.) | ~180 (`wc -l`) |
| Camadas presentes (papéis) | entrypoint (app.js); config misturada a estado global/crypto/log (utils.js); infra + schema/seed + rotas + controllers + regra de negócio + acesso a dados (AppManager.js) |
| Maior arquivo | src/AppManager.js (141) |
| Arquivos com 3+ papéis | 2 (src/AppManager.js, src/utils.js) |

## Superfície de ataque
| Método | Rota | Handler (arquivo:linha) | Autenticação | Administrativa/destrutiva |
|---|---|---|---|---|
| POST | /api/checkout | src/AppManager.js:28 | não | não |
| GET | /api/admin/financial-report | src/AppManager.js:80 | não | sim |
| DELETE | /api/users/:id | src/AppManager.js:131 | não | sim |

## Findings

### [CRITICAL] F-001 · SEC-08 Dados sensíveis em logs
File: src/AppManager.js:45
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-532 / A09:2021
Evidência: `console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);`
Description: a cada checkout o número completo do cartão (`req.body.card`, linha 33) e a chave do gateway de pagamento são escritos na saída padrão.
Impact: qualquer pessoa com acesso aos logs obtém PAN completo dos clientes e a chave do gateway (violação PCI-DSS; vazamento de segredo).
Recommendation: logger com mascaramento (somente os 4 últimos dígitos do cartão; nunca a chave) (Playbook P-15).

### [CRITICAL] F-002 · SEC-14 Regra financeira simulada
File: src/AppManager.js:46-48
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-602 / CWE-840 / A04:2021
Evidência: `let status = cc.startsWith("4") ? "PAID" : "DENIED";`
Description: a aprovação do pagamento é decidida pelo primeiro dígito do cartão enviado pelo cliente; não há integração com provedor nem configuração que restrinja a simulação a teste. O status `PAID` libera a matrícula (linhas 50-60).
Impact: qualquer cliente remoto obtém matrícula paga (bem liberado) sem cobrança real, informando um número começando com "4".
Recommendation: gateway de pagamento por configuração, mock só com configuração explícita de teste e recusa por padrão sem provedor (Playbook P-20).

### [CRITICAL] F-003 · SEC-03 Endpoint administrativo/destrutivo sem autenticação
File: src/AppManager.js:80-129, 131-137
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / A01:2021
Evidência: `app.get('/api/admin/financial-report', (req, res) => {` · `app.delete('/api/users/:id', (req, res) => {`
Description: as rotas são registradas diretamente em `setupRoutes` sem nenhum middleware (src/app.js:6 só registra `express.json()`); o relatório financeiro devolve receita por curso e nomes de alunos, e o DELETE remove qualquer usuário pelo id. Como não existe identidade no fluxo, o IDOR do DELETE é reportado aqui (regra SEC-11 do catálogo).
Impact: atacante remoto não autenticado lê dados financeiros e PII (nomes) e apaga usuários arbitrariamente.
Recommendation: exigir credencial de administrador nas duas rotas, com testes sem/inválida/válida (Playbook P-05) — exige contrato (CT-01, CT-02).

### [CRITICAL] F-004 · SEC-02 Segredos e credenciais hardcoded
File: src/utils.js:3-4; src/AppManager.js:18
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-798 / A07:2021
Evidência: `dbPass: "senh***"` · `paymentGatewayKey: "pk_l***"` · `INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '***')`
Description: senha de banco rotulada como produção e chave de gateway com prefixo `pk_live_` estão literais no objeto `config` versionado; a chave é usada em runtime (src/AppManager.js:45). A senha do usuário de seed também é literal no fonte.
Impact: qualquer pessoa com acesso ao repositório obtém as credenciais; a chave `live` permite operar no gateway.
Recommendation: ler configuração e segredos de variáveis de ambiente, senha de seed por variável/aleatória por execução (Playbook P-01); rotacionar os valores já publicados no histórico git (ação manual).

### [CRITICAL] F-005 · SEC-06 Armazenamento inseguro de senha
File: src/utils.js:17-23; src/AppManager.js:18, 68-69
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-256 / CWE-327 / CWE-916 / A02:2021
Evidência: `hash += Buffer.from(pwd).toString('base64').substring(0, 2);` · `let hash = badCrypto(p || "123456");`
Description: `badCrypto` repete os 2 primeiros caracteres do base64 da senha e trunca em 10: o "hash" é reversível ao prefixo, sem salt, e colide para qualquer senha com o mesmo início. O seed grava a senha em texto puro (linha 18) e, sem `pwd`, o usuário recebe a senha padrão conhecida "123456" (linha 68).
Impact: vazamento do banco expõe as senhas (ou seus prefixos); contas criadas sem senha ficam com senha previsível.
Recommendation: KDF com salt (scrypt do `node:crypto`, sem dependência nova), sem senha padrão (Playbook P-03).

### [CRITICAL] F-006 · ARC-01 God Class / God File
File: src/AppManager.js:1-141
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `class AppManager { constructor() { this.db = new sqlite3.Database(':memory:'); } initDb() {...} setupRoutes(app) {...} }`
Description: uma única classe cria a conexão (linha 7), define o schema e semeia dados (10-23), registra rotas (25-137), contém controllers, regra de pagamento (46), orquestração de entidades e todas as queries.
Impact: nenhuma parte pode ser testada ou alterada isoladamente; qualquer mudança arrisca todos os fluxos.
Recommendation: separar config, models/repositórios, services, controllers e rotas (Playbook P-08, P-09, P-13).

### [HIGH] F-007 · SEC-12 Validação de entrada ausente (chega à regra financeira)
File: src/AppManager.js:29-35, 46
Ocorrências: 2 · Confiança: LIKELY · Categoria: Segurança
CWE/OWASP: CWE-20 / A03:2021
Evidência: `if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");` · `cc.startsWith("4")`
Description: só a presença dos campos é verificada; tipo e formato de `card`, `c_id`, `eml` não. Um `card` não-string (ex.: número) faz `cc.startsWith` lançar `TypeError` dentro do callback do sqlite3, fora do alcance do Express. Severidade elevada a HIGH porque o dado chega à regra de pagamento. Confiança LIKELY: o travamento do processo não foi executado (Fase 2 não executa).
Impact: requisição única malformada pode derrubar o processo (indisponibilidade) e valores arbitrários entram na regra de pagamento.
Recommendation: validar tipo/formato na borda e responder com o erro já existente `400 Bad Request` (Playbook P-07).

### [HIGH] F-008 · SEC-09 Autenticação ausente no checkout de usuário existente
File: src/AppManager.js:40, 66-75
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-306 / CWE-287 / A07:2021
Evidência: `this.db.get("SELECT id FROM users WHERE email = ?", [e], ...` · `} else { processPaymentAndEnroll(user.id); }`
Description: quando o e-mail já existe, o `pwd` recebido é ignorado e a compra é vinculada à conta só pelo e-mail. Nenhuma rota da API verifica identidade; HIGH (e não CRITICAL) porque o efeito é parcial (associa matrícula/pagamento à conta de terceiro, sem leitura de dados) e as rotas administrativas já estão em F-003.
Impact: qualquer pessoa que conheça um e-mail cadastrado grava matrículas e pagamentos na conta dessa pessoa.
Recommendation: verificar a senha do usuário existente contra o hash e responder 401 quando ausente/incorreta (Playbook P-05) — exige contrato (CT-03).

### [HIGH] F-009 · SEC-15 Fluxo de checkout sem transação
File: src/AppManager.js:50-63, 66-72
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-362 / A04:2021
Evidência: `this.db.run("INSERT INTO enrollments ...` → `self.db.run("INSERT INTO payments ...` → `self.db.run("INSERT INTO audit_logs ...", ..., (err) => {`
Description: matrícula, pagamento e auditoria são três escritas independentes, sem `BEGIN/COMMIT/ROLLBACK`; o erro da auditoria é ignorado (linha 57). O usuário novo é criado (linhas 68-72) antes da decisão do pagamento (linha 48), ficando gravado mesmo com pagamento recusado.
Impact: falha intermediária deixa matrícula sem pagamento (acesso sem registro financeiro) e usuários órfãos de checkouts recusados.
Recommendation: executar criação de usuário, matrícula, pagamento e auditoria numa transação, só após a aprovação (Playbook P-10).

### [HIGH] F-010 · ARC-04 Acoplamento forte sem injeção de dependência
File: src/AppManager.js:2, 7
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');` · `this.db = new sqlite3.Database(':memory:');`
Description: a conexão é instanciada dentro do construtor e a configuração vem de um objeto global importado; handlers usam `this.db` diretamente.
Impact: impossível substituir banco, gateway ou configuração em testes sem subir o processo inteiro.
Recommendation: composition root que cria a infraestrutura e a injeta em repositórios/services/controllers (Playbook P-13, P-08).

### [HIGH] F-011 · ARC-02 Lógica de negócio em rota
File: src/AppManager.js:28-78, 80-129
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `let processPaymentAndEnroll = (userId) => { ... let status = cc.startsWith("4") ? "PAID" : "DENIED";` · `courseData.revenue += payment.amount;`
Description: o handler do checkout decide o pagamento, cria usuário, matrícula, pagamento e auditoria; o do relatório agrega receita por curso.
Impact: regra de negócio inacessível a testes de unidade e acoplada ao HTTP.
Recommendation: extrair `CheckoutService` e serviço de relatório; controller só lê a requisição e escolhe a resposta (Playbook P-09).

### [HIGH] F-012 · ARC-05 Callback hell / fluxo assíncrono manual
File: src/AppManager.js:37-77, 83-128
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `this.db.all(... (err, enrollments) => { let enrPending = enrollments.length; ... this.db.get(... (err, user) => { this.db.get(... (err, payment) => {`
Description: o checkout aninha 6 níveis de callbacks; o relatório aninha 6 níveis com contadores manuais (`coursesPending`, `enrPending`, linhas 86, 93, 97, 117, 120) e ignora os erros dos callbacks internos.
Impact: fluxo difícil de seguir, respostas duplicadas/perdidas quando um callback falha.
Recommendation: promisificar o acesso ao banco e usar async/await (Playbook P-12).

### [HIGH] F-013 · ARC-03 Estado global mutável
File: src/utils.js:9, 12-15; src/AppManager.js:59
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `let globalCache = {};` · `globalCache[key] = data;` · `logAndCache(`last_checkout_${userId}`, course.title);`
Description: cada checkout grava num objeto de módulo exportado, compartilhado por todas as requisições e nunca lido nem limpo.
Impact: crescimento ilimitado de memória por usuário e estado oculto compartilhado entre requisições.
Recommendation: remover o cache global (não é consumido) ou encapsulá-lo como dependência injetada (Playbook P-13).

### [MEDIUM] F-014 · SEC-17 Falta de proteções HTTP básicas
File: src/app.js:5-6
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Segurança
CWE/OWASP: CWE-770 / CWE-693 / A05:2021
Evidência: `const app = express(); app.use(express.json());`
Description: nenhum cabeçalho de segurança, `X-Powered-By: Express` ativo e nenhuma limitação de taxa no checkout.
Impact: força bruta/abuso do checkout e exposição desnecessária da stack.
Recommendation: cabeçalhos aditivos, desativar `x-powered-by` e limitar taxa do checkout sem dependência nova (Playbook P-19).

### [MEDIUM] F-015 · SEC-13 Vazamento de detalhes internos em erros
File: src/app.js:6
Ocorrências: 1 · Confiança: LIKELY · Categoria: Segurança
CWE/OWASP: CWE-209 / A05:2021
Evidência: `app.use(express.json());` (sem middleware de erro registrado)
Description: sem handler central de erros e com `NODE_ENV` não definido, o handler padrão do Express devolve o stack trace (ex.: JSON malformado no checkout gera página com `SyntaxError` e caminhos de `node_modules`). Não executado na Fase 2.
Impact: revela estrutura interna e versões a qualquer cliente.
Recommendation: middleware central de erros com resposta genérica no formato existente (Playbook P-06).

### [MEDIUM] F-016 · ARC-10 Integridade referencial ausente
File: src/AppManager.js:12-16, 131-137
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)` · `res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");`
Description: sem `UNIQUE` em `users.email` (chave de identificação no checkout), sem `NOT NULL` e sem `FOREIGN KEY`; o DELETE deixa matrículas e pagamentos órfãos, como a própria resposta admite.
Impact: e-mails duplicados por corrida e registros financeiros apontando para usuários inexistentes.
Recommendation: `UNIQUE`/`NOT NULL` no schema; exclusão do usuário com suas matrículas/pagamentos na mesma transação (Playbook P-10) — a parte do DELETE exige contrato (CT-04).

### [MEDIUM] F-017 · ARC-12 Dinheiro em ponto flutuante
File: src/AppManager.js:13, 15, 109
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `price REAL` · `amount REAL` · `courseData.revenue += payment.amount;`
Description: preços e pagamentos são `REAL` e a receita é somada em ponto flutuante.
Impact: erros de arredondamento acumulados em totais financeiros.
Recommendation: armazenar em centavos (`INTEGER`) e converter na saída mantendo o mesmo formato numérico (Playbook P-17).

### [MEDIUM] F-018 · ARC-11 `SELECT *` / carga total
File: src/AppManager.js:37, 83, 92
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `SELECT * FROM courses WHERE id = ? AND active = 1` · `SELECT * FROM courses` · `SELECT * FROM enrollments WHERE course_id = ?`
Description: consultas trazem todas as colunas e o relatório carrega todas as tabelas em memória para agregar no JavaScript.
Impact: tráfego e memória proporcionais ao banco inteiro; colunas novas vazam para a lógica sem controle.
Recommendation: colunas explícitas e agregação no SQL; paginação não recomendada neste relatório agregado (mudaria o contrato) (Playbook P-11).

### [MEDIUM] F-019 · ARC-09 Tratamento de erro ruim
File: src/AppManager.js:57, 92-93, 104, 106, 133-135
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `this.db.all("SELECT * FROM enrollments ...", [c.id], (err, enrollments) => { let enrPending = enrollments.length;` · `this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => { res.send(...`
Description: `err` é ignorado em 5 callbacks; na linha 93 um erro deixa `enrollments` indefinido e lança `TypeError` (queda do processo); o DELETE responde 200 mesmo com erro ou id inexistente. Respostas misturam texto (`send("Bad Request")`) e JSON.
Impact: falhas silenciosas, quedas do processo e respostas enganosas.
Recommendation: tratar todos os erros e centralizar a resposta (Playbook P-06); o 404 do DELETE faz parte de CT-04.

### [MEDIUM] F-020 · ARC-07 Queries N+1
File: src/AppManager.js:89-106
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Arquitetura
CWE/OWASP: n/a
Evidência: `courses.forEach(c => { this.db.all(... course_id = ?` → `enrollments.forEach(enr => { this.db.get(... users ...` → `this.db.get(... payments ...`
Description: 1 consulta por curso e 2 por matrícula (1 + C + 2·M consultas por chamada).
Impact: latência cresce linearmente com matrículas.
Recommendation: uma consulta agregada com `JOIN`/`LEFT JOIN` (Playbook P-11).

### [LOW] F-021 · QLT-04 `console.log` no lugar de logger
File: src/app.js:13; src/AppManager.js:45; src/utils.js:13
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `console.log(`[LOG] Salvando no cache: ${key}`);`
Description: saída por `console.log` como mecanismo de log, sem nível nem mascaramento.
Impact: logs não filtráveis e propensos a vazar dados (ver F-001).
Recommendation: logger mínimo com nível e mascaramento (Playbook P-15).

### [LOW] F-022 · QLT-03 Imports, variáveis e código mortos
File: src/AppManager.js:2; src/utils.js:2-3, 5, 10, 25
Ocorrências: 3 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `let totalRevenue = 0;` · `module.exports = { config, logAndCache, badCrypto, globalCache, totalRevenue };`
Description: `totalRevenue` é exportado e importado (AppManager.js:2) mas nunca usado; `globalCache` exportado e não consumido; `config.dbUser`, `config.dbPass` e `config.smtpUser` não são referenciados em lugar nenhum (busca por nome).
Impact: ruído e falsa impressão de funcionalidades.
Recommendation: remover (Playbook P-16).

### [LOW] F-023 · QLT-01 Magic numbers e strings soltas
File: src/AppManager.js:21, 46, 48, 108; src/utils.js:19
Ocorrências: 5 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `"PAID" : "DENIED"` · `status === 'PAID'` · `for(let i = 0; i < 10000; i++)`
Description: status de pagamento e limites repetidos como literais.
Impact: divergência silenciosa ao alterar um dos usos.
Recommendation: constantes nomeadas (Playbook P-16).

### [LOW] F-024 · QLT-05 Estilo inconsistente
File: src/AppManager.js:26, 29-33
Ocorrências: 2 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `const self = this;` (mistura `this.db` e `self.db` nas linhas 50-57) · `let u = req.body.usr;`
Description: mistura `this`/`self` e `let` onde cabe `const`.
Impact: legibilidade.
Recommendation: padronizar (Playbook P-16).

### [LOW] F-025 · QLT-02 Nomes ruins
File: src/AppManager.js:29-33
Ocorrências: 1 · Confiança: CONFIRMED · Categoria: Qualidade
CWE/OWASP: n/a
Evidência: `let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd; let cid = req.body.c_id; let cc = req.body.card;`
Description: variáveis de uma letra/abreviadas; as chaves do payload (`usr`, `eml`, `pwd`, `c_id`) também são crípticas, mas fazem parte do contrato e serão mantidas.
Impact: legibilidade.
Recommendation: renomear variáveis internas, mantendo as chaves do payload (Playbook P-16).

DEP: nenhuma encontrada para Node.js v24.11.1 (runtime local; projeto sem `engines`), Express 4.22.1 e sqlite3 5.1.7 — sem `new Buffer()`, `url.parse`, `body-parser` avulso, `req.param()`, `crypto.createCipher` ou pacote `request`.

## Descartados / falsos positivos
- SEC-01 em src/AppManager.js:37, 40, 50, 54, 57, 69, 92, 104, 106, 133 — descartado porque todas as consultas com dado externo usam placeholders `?`; as demais são literais internos.
- SEC-04 — descartado: nenhum `eval`/`Function`/`child_process` no código-fonte (o `spawn` de test/api.test.js:61 usa argumentos fixos).
- SEC-05 — descartado: não há flag de debug fixa nem `NODE_ENV` forçado; o efeito do modo padrão está em F-015.
- SEC-07 em src/AppManager.js:104 — descartado porque `email` é lido mas não serializado e senha/hash nunca são devolvidos; a exposição de nomes no relatório está em F-003.
- SEC-10 — descartado: nenhum campo de privilégio aceito do cliente.
- SEC-11 em src/AppManager.js:131 — não há identidade no fluxo; reportado como F-003 (regra do catálogo).
- SEC-16 em package.json:10-13 — descartado: `express` e `sqlite3` são importados (src/app.js:1, src/AppManager.js:1), há lockfile e as versões não são antigas; recomenda-se `npm audit` (classe C, não executado).
- ARC-06 — coberto por F-006 (tudo no mesmo arquivo).
- ARC-08 em src/AppManager.js:96-98, 119-121 — bloco de conclusão repetido 2 vezes (< 3).
- TST-01/TST-02/TST-03 — descartados: há 8 testes de integração (test/api.test.js), README.md:5-12 e package.json:7-8 documentam execução, e o teste não importa módulos inexistentes.

## Correções que exigem mudança de contrato
(Cada correção do plano é classificada **compatível** — não altera o contrato — ou **exige contrato** — altera rota, status, formato ou acesso. Só as que exigem contrato entram aqui; a P3 da rodada de perguntas decide entre **Refatorar** (recomendado), **Manter contrato\*** e **Híbrido**, ver `07-politica-comandos-aprovacoes.md`, seção 4.1.)

| ID | Rota/campo | Mudança | Sev. | Motivo (Finding) | Impacto para clientes | Refatorar | Manter contrato\* | Híbrido | Prova prevista |
|---|---|---|---|---|---|---|---|---|---|
| CT-01 | GET /api/admin/financial-report | exigir credencial de administrador (sem/inválida ⇒ 401) | CRITICAL | F-003 | cliente precisa enviar a credencial de admin; resposta autenticada inalterada | aplica | não (fica sem correção) | aplica — variante mínima (CRITICAL/HIGH) | teste novo (integração) + execução local autenticada |
| CT-02 | DELETE /api/users/:id | exigir credencial de administrador (sem/inválida ⇒ 401) | CRITICAL | F-003 | idem | aplica | não (fica sem correção) | aplica — variante mínima (CRITICAL/HIGH) | teste novo (integração) + execução local autenticada |
| CT-03 | POST /api/checkout (e-mail já cadastrado) | verificar `pwd` contra o hash; ausente/incorreta ⇒ 401 | HIGH | F-008 | cliente existente precisa enviar a senha correta; novo cadastro e resposta de sucesso inalterados | aplica | não (fica sem correção) | aplica — variante mínima (CRITICAL/HIGH) | teste novo (integração) + execução local autenticada |
| CT-04 | DELETE /api/users/:id | excluir matrículas e pagamentos do usuário na mesma transação; id inexistente ⇒ 404; corpo "Usuário deletado." (sem a frase de dados sujos) | MEDIUM | F-016, F-019 | relatório deixa de listar o usuário excluído; 404 para id inexistente; texto do corpo muda (continua contendo "deletado") | aplica | não (F-016/F-019 parcialmente residuais) | não aplica (MEDIUM/LOW) | teste novo (integração) + execução local autenticada |

Resumo para a pergunta: 4 correções exigem contrato. Refatorar: corrige todas. Manter contrato\*: ficam sem correção 1 CRITICAL (F-003) e 1 HIGH (F-008), exige segunda confirmação. Híbrido: aplica 3 (CT-01, CT-02, CT-03 — CRITICAL/HIGH); ficam sem correção 2 MEDIUM (F-016 e F-019, parcialmente, via CT-04).

## Testes afetados
| Teste | Motivo (C-xx/CT-xx) | Classe (T1/T2/T4) | Ajuste previsto |
|---|---|---|---|
| test/api.test.js::before / aguardarServidor | C-01, C-06 (config e gateway por ambiente), CT-01 (prontidão via rota admin) | T1/T2 | `spawn` com variáveis de ambiente de teste (provedor mock, credencial de admin e senha de seed aleatórias por execução) e cabeçalho de credencial na sondagem |
| test/api.test.js::relatório financeiro inicial reflete os seeds | CT-01 | T2 | enviar credencial de admin em `relatorio()`; asserções mantidas |
| test/api.test.js::relatório financeiro reflete o checkout aprovado | CT-01 | T2 | idem |
| test/api.test.js::checkout com cartão recusado retorna 400 · checkout com sucesso cria usuário e matrícula | C-06 (P-20) | T1 | dependem do provedor mock habilitado por ambiente de teste; asserções mantidas |
| test/api.test.js::checkout de usuário já existente reutiliza o cadastro | CT-03, CT-01, C-01 (senha de seed por ambiente) | T2 | enviar a senha de seed definida pelo teste no `spawn`; asserções mantidas |
| test/api.test.js::DELETE /api/users/:id retorna 200 | CT-02, CT-04 | T2 | enviar credencial de admin; `/deletado/i` continua válido |
| test/*.test.js (novos) | CT-01…CT-04; F-001, F-002, F-004, F-005, F-006, F-007, F-009…F-013 | T4 | integração: 401 sem/inválida e 200 com credencial; 401 senha errada; cartão não-string ⇒ 400 sem queda; log sem PAN/chave; DELETE em cascata/404. Unidade: gateway recusa sem provedor; hash com salt verificável e sem senha padrão; config sem segredo literal; checkout transacional (rollback) e services com dependências injetadas |

## Plano de mudanças
| ID | Mudança | Sev. | Resolve | Arquivos | Padrão | Afeta contrato | Depende de |
|---|---|---|---|---|---|---|---|
| C-01 | Módulo de config lido do ambiente (porta, chave do gateway, provedor de pagamento, credencial de admin, senha de seed); remover literais e campos não usados | CRITICAL | F-004, F-022 (parte) | src/config/*, src/utils.js (removido) | P-01 | não | — |
| C-02 | Extrair conexão, schema (UNIQUE/NOT NULL, dinheiro em centavos), seed e repositórios; transação no checkout | CRITICAL | F-006 (parte), F-009, F-016 (schema), F-017, F-018 | src/database/*, src/models/* | P-08 + P-17 + P-10 | não | C-01 |
| C-03 | DELETE de usuário com matrículas/pagamentos na mesma transação; 404 para id inexistente; corpo sem a frase de dados sujos | MEDIUM | F-016 (exclusão), F-019 (DELETE) | src/models/*, controller de usuários | P-10 | CT-04 | C-02 |
| C-04 | Hash de senha com scrypt + salt (`node:crypto`), sem senha padrão; seed com senha do ambiente/aleatória | CRITICAL | F-005 | src/services/* (ou util de senha) | P-03 | não | C-01, C-02 |
| C-05 | Extrair `CheckoutService` e serviço de relatório | HIGH | F-011, F-006 (parte) | src/services/* | P-09 | não | C-02 |
| C-06 | Gateway de pagamento por configuração: mock só com configuração explícita, recusa por padrão | CRITICAL | F-002 | src/services/* (gateway) | P-20 | não | C-01, C-05 |
| C-07 | Validação de entrada do checkout (tipo/formato) com o `400 Bad Request` existente | HIGH | F-007 | src/controllers/* ou middleware | P-07 | não | C-05 |
| C-08 | Middleware de credencial de admin nas rotas admin/DELETE; verificação de senha do usuário existente no checkout | CRITICAL | F-003, F-008 | src/middlewares/*, src/routes/*, src/services/* | P-05 | CT-01, CT-02, CT-03 | C-01, C-04, C-05 |
| C-09 | Handler central de erros e tratamento de todos os `err` | MEDIUM | F-015, F-019 | src/middlewares/*, src/app.js | P-06 | não | C-05 |
| C-10 | Logger mínimo com mascaramento (cartão só 4 últimos dígitos, nunca a chave) | CRITICAL | F-001, F-021 | src/utils/logger ou equivalente | P-15 | não | C-06 |
| C-11 | Promisificar sqlite3 e usar async/await; relatório com uma consulta agregada | HIGH | F-012, F-020, F-018 | src/database/*, src/models/*, src/services/* | P-12 + P-11 | não | C-02, C-05 |
| C-12 | Composition root com injeção de dependências; remover cache global | HIGH | F-010, F-013, F-006 (parte) | src/app.js, src/server ou equivalente | P-13 | não | C-02, C-05 |
| C-13 | Cabeçalhos de segurança, `x-powered-by` desativado e limite de taxa no checkout (sem dependência nova) | MEDIUM | F-014 | src/middlewares/*, src/app.js | P-19 | não | C-12 |
| C-14 | Limpeza: constantes nomeadas, nomes, estilo, código morto | LOW | F-022, F-023, F-024, F-025 | arquivos novos | P-16 | não | C-01…C-13 |

Recomendações manuais:
- F-004: rotacionar a chave do gateway (`pk_l***`) e a senha de banco (`senh***`) já publicadas no histórico git (ação externa ao código).
- SEC-16 (descartado): rodar `npm audit` quando houver aprovação de rede (classe C).
- README: documentar as variáveis de ambiente novas (texto-base no anexo da Fase 3).

## Plano de comandos
| ID | Comando | Finalidade | Origem | Classe | Efeitos colaterais |
|---|---|---|---|---|---|
| K-00 | `git branch refactor-arch/checkpoint-20261116-213657` + `git worktree add --detach <tmp>/checkpoint refactor-arch/checkpoint-20261116-213657` + junção de `node_modules` do projeto na cópia | checkpoint do código original e cópia fora do projeto para provas de sensibilidade e baseline V4 | política 07 §2.2 | C | cria branch local e worktree no diretório temporário (sem commit) |
| K-01 | `node --check src/<arquivo>.js` (cada arquivo-fonte) | V5 estático | toolchain | B | nenhum |
| K-02 | `npm test` (`node --test`) | V1 baseline e final | package.json:8 | B | sobe a app na porta 3000 durante o teste |
| K-03 | `npm start` + as 2 requisições de checkout de `api.http` | V3 boot + coleção existente | README.md:9; package.json:7; api.http:3-25 | B | porta 3000; banco em memória |
| K-04 | requisições `GET /api/admin/financial-report` e `DELETE /api/users/1` de `api.http` | rota administrativa/destrutiva da coleção | api.http:27-31 | D | só executadas dentro da V4, contra o banco em memória criado nesta execução |
| K-05 | boot da cópia do checkpoint/código final com ambiente de teste + script de requisições em `<tmp>` | V4 execução local autenticada (baseline e final) | política 07 §5 | B | porta 3000; banco em memória; scripts fora do projeto |
| K-06 | `node --test <testes novos>` na cópia do checkpoint | prova de sensibilidade (vermelho no original) | 06 §8.9 | B | executa na cópia fora do projeto |
| K-07 | encerrar processos iniciados; `git worktree remove <tmp>/checkpoint`; remover scripts temporários | limpeza | política 07 §2 | C | remove a cópia temporária; a branch de checkpoint é mantida e registrada |
| — | `npm install` | instalar dependências | README.md:8 | C | não necessário: `node_modules` já existe |

## Plano de validação
| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim | `npm test` (package.json:8, B) | 8 testes de integração (node:test + fetch contra `node src/app.js`) |
| V2 Script de verificação do projeto | não | — | sem lint/check/CI |
| V3 Boot + requisições existentes | sim | boot `npm start` + `api.http` | 2 checkouts (B); admin/DELETE só na V4 |
| V4 Execução local autenticada | depende de P4 | boot com ambiente de teste + requisições com credenciais geradas pela aplicação | baseline na cópia do checkpoint (sem auth: seed versionado e cadastro via checkout); final com credencial de admin e senha de seed aleatórias por execução |
| V5 Estático | sempre | `node --check` (B) | — |
| Pré-requisitos | | `npm install` (C) | não necessário (node_modules presente) |
| Testes afetados previstos | | test/api.test.js (6 de 8 testes + before) | T1/T2; novos T4 |
| Prova prevista (`CT-xx` aplicados e correções CRITICAL/HIGH) | | testes novos de integração (CT-01…CT-04, F-001, F-007) e unidade (F-002, F-004, F-005, F-006, F-009…F-013) + V4 | vermelho na cópia do checkpoint quando aplicável |
| Não exercitável | | integração real de pagamento | não existe provedor real; só mock por configuração |

## Decisões do usuário
Respostas da rodada de perguntas: `1A 2A 3A 4A` (aplicar todas as mudanças · Equilibrado · Refatorar · execução local incluindo escrita em banco descartável). Lote classe C (K-00a, K-00b, K-00c, K-07): `Executar todos`. Decisão de design P-05: chave de administração vinda do ambiente (`ADMIN_API_KEY`, `Authorization: Bearer`), negando tudo quando ausente.

================================
Total: 25 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

---
# ANEXO — FASE 3 (Run id: 20261116-213657)

## Decisões do usuário (registro)
- Escopo: todas (`1A`: "Sim, aplicar todas as mudanças do plano")
- Modo de comandos: Equilibrado (`2A`); lote classe C K-00a, K-00b, K-00c e K-07: "Executar todos"
- Contrato: Refatorar (`3A`; CT-01, CT-02, CT-03 e CT-04 aplicados)
- Execução local autenticada (P4): incluindo escrita em banco descartável (`4A`)
- Decisão de design P-05: chave de administração vinda do ambiente (`ADMIN_API_KEY` como Bearer; sem a variável, as rotas administrativas negam tudo)

## Estrutura DEPOIS
```
ecommerce-api-legacy/
├── .env.example
├── src/
│   ├── app.js                     (composition root + entry point)
│   ├── config/                    settings.js, constants.js
│   ├── controllers/               checkoutController.js, reportController.js, userController.js
│   ├── database/                  connection.js, schema.js
│   ├── errors/                    AppError.js
│   ├── middlewares/               errorHandler.js, rateLimiter.js, requireAdmin.js, securityHeaders.js
│   ├── models/                    auditLogModel.js, courseModel.js, enrollmentModel.js, paymentModel.js, reportModel.js, userModel.js
│   ├── routes/                    index.js
│   ├── services/                  checkoutService.js, passwordService.js, reportService.js, userService.js, payment/gatewayFactory.js
│   ├── utils/                     asyncHandler.js, logger.js
│   └── validators/                checkoutValidator.js
└── test/                          api.test.js, checkout-service.test.js, composition-root.test.js, password-service.test.js, payment-gateway.test.js, report-service.test.js, settings.test.js
```

| Métrica | ANTES | DEPOIS |
|---|---|---|
| Arquivos-fonte | 3 | 28 |
| Linhas de código (aprox.) | ~180 | ~693 |
| Camadas presentes | entrypoint; config misturada; tudo o mais em AppManager.js | config, database, models, services, controllers, routes, middlewares, validators, errors, utils, composition root |
| Maior arquivo | src/AppManager.js (141) | src/app.js (78) |
| Arquivos com 3+ papéis | 2 | 0 |

### Mapa antigo → novo
| Arquivo original | Destino(s) |
|---|---|
| src/app.js | src/app.js (composition root), src/routes/index.js |
| src/AppManager.js (conexão, schema, seed) | src/database/connection.js, src/database/schema.js |
| src/AppManager.js (queries) | src/models/*.js |
| src/AppManager.js (checkout) | src/controllers/checkoutController.js, src/validators/checkoutValidator.js, src/services/checkoutService.js, src/services/payment/gatewayFactory.js |
| src/AppManager.js (relatório) | src/controllers/reportController.js, src/services/reportService.js, src/models/reportModel.js |
| src/AppManager.js (DELETE) | src/controllers/userController.js, src/services/userService.js |
| src/utils.js (config) | src/config/settings.js, src/config/constants.js, .env.example |
| src/utils.js (`badCrypto`) | src/services/passwordService.js (scrypt) |
| src/utils.js (`logAndCache`, `globalCache`, `totalRevenue`) | src/utils/logger.js; cache e contador removidos (nunca eram lidos) |

## Mudanças aplicadas
| ID | Status | Observação |
|---|---|---|
| C-01 | aplicada | Config por ambiente; literais removidos; `.env.example` criado |
| C-02 | aplicada | Schema com UNIQUE/NOT NULL/FK, dinheiro em centavos (`price_cents`, `amount_cents`; banco em memória recriado a cada boot, sem migração), transação no checkout |
| C-03 | aplicada | DELETE em transação, 404 para id inexistente (CT-04) |
| C-04 | aplicada | scrypt com salt; sem senha padrão. O usuário de seed continua sendo criado para manter os dados observáveis; sem `SEED_USER_PASSWORD` recebe senha aleatória não divulgada |
| C-05 | aplicada | `checkoutService`, `reportService` e `userService` |
| C-06 | aplicada | Recusa por padrão; mock só com `PAYMENT_PROVIDER=mock` e `APP_ENV=test` ou `development` |
| C-07 | aplicada | Tipo/formato validados; resposta `400 Bad Request` existente |
| C-08 | aplicada | `requireAdmin` nas rotas administrativas; senha verificada no checkout de e-mail existente |
| C-09 | aplicada | Handler central; erros 500 genéricos, detalhe só no log |
| C-10 | aplicada | Logger JSON; cartão só com os 4 últimos dígitos; chave nunca registrada |
| C-11 | aplicada | Promises/async-await; relatório em uma consulta com JOIN |
| C-12 | aplicada | Composition root com injeção; cache global removido |
| C-13 | aplicada | Cabeçalhos de segurança, `x-powered-by` desativado, limite de taxa no checkout (30/min por IP, configurável) |
| C-14 | aplicada | Constantes, nomes internos, estilo e código morto |

## Contratos — resultado
| CT | Rota/campo | Antes → Depois | Por que (F-xxx, CWE/OWASP) | Impacto e como adaptar o cliente | Prova (E-nn) |
|---|---|---|---|---|---|
| CT-01 | GET /api/admin/financial-report | aberta → exige `Authorization: Bearer <ADMIN_API_KEY>` (sem/inválida ⇒ 401) | F-003, CWE-306/A01 | enviar o cabeçalho; resposta autenticada inalterada | E-06 verde; E-09 vermelho; E-04 × E-08 (linhas 1-3) |
| CT-02 | DELETE /api/users/:id | aberta → exige a mesma credencial (sem/inválida ⇒ 401) | F-003, CWE-306/A01 | enviar o cabeçalho | E-06 verde; E-09 vermelho; E-04 × E-08 (linhas 13-14) |
| CT-03 | POST /api/checkout (e-mail cadastrado) | senha ignorada → `pwd` verificado; ausente/incorreta ⇒ 401, sem cobrança nem escrita | F-008, CWE-306/A07 | cliente existente envia a senha da conta | E-06 verde; E-09 vermelho; E-04 × E-08 (linhas 8-10) |
| CT-04 | DELETE /api/users/:id | deixava órfãos e respondia 200 sempre → remove matrículas e pagamentos na mesma transação; id inexistente ⇒ 404; corpo `Usuário deletado.` | F-016, F-019, CWE-459 | tratar 404; o usuário excluído sai do relatório financeiro | E-06 verde; E-09 vermelho; E-04 × E-08 (linhas 15-17) |

**Texto-base para o README (seção Resultados):** a refatoração alterou o contrato de 2 rotas administrativas e do checkout de e-mail já cadastrado, em 4 mudanças (CT-01 a CT-04). O relatório financeiro e a exclusão de usuário passaram a exigir `Authorization: Bearer <ADMIN_API_KEY>`; o checkout de conta existente passou a exigir a senha da conta; a exclusão agora remove matrículas e pagamentos e responde 404 para id inexistente. As mudanças corrigem acesso sem autenticação e dados órfãos, e foram aprovadas na rodada de perguntas do Run 20261116-213657. Sem `PAYMENT_PROVIDER` configurado todo pagamento é recusado; para desenvolvimento use `APP_ENV=development`, `PAYMENT_PROVIDER=mock` e `PAYMENT_MOCK_APPROVED_PREFIXES`. Justificativa e provas estão em `reports/audit-project-2.md`.

## Alterações em testes
Snapshot: `reports/evidence/project-2/20261116-213657/tests-before/test/api.test.js` · Diff: `E-10-diff-testes.patch`. Nenhuma asserção original foi removida ou afrouxada.

| Teste | Motivo | Classe | Antes/Depois (trecho do diff) | Asserções | Reexecução | Snapshot |
|---|---|---|---|---|---|---|
| test/api.test.js::before | C-01, C-06 | T1 | `{ cwd: RAIZ }` → `{ cwd: RAIZ, env: AMBIENTE_TESTE }` | mantidas | E-06 | `tests-before/test/api.test.js` |
| test/api.test.js::aguardarServidor | CT-01 | T2 | `fetch(url)` → `fetch(url, { headers: AUTH_ADMIN })` | mantidas | E-06 | idem |
| test/api.test.js::relatorio (usado por 4 testes) | CT-01 | T2 | `fetch(url)` → `fetch(url, { headers: AUTH_ADMIN })` | mantidas | E-06 | idem |
| test/api.test.js::checkout de usuário já existente reutiliza o cadastro | CT-03, C-01 | T2 | `pwd: '***'` → `pwd: SENHA_SEED` | mantidas | E-06 | idem |
| test/api.test.js::DELETE /api/users/:id retorna 200 | CT-02 | T2 | `{ method: 'DELETE' }` → `{ method: 'DELETE', headers: AUTH_ADMIN }` | mantidas | E-06 | idem |

Os 8 testes originais adaptados também passam no código original (E-09), o que confirma que a adaptação preservou a intenção.

## Testes adicionados (provas)
| Teste | Tipo | CT/F | O que comprova | Verde (código refatorado) | Vermelho (checkpoint original) |
|---|---|---|---|---|---|
| api.test.js::CT-01 | integração | CT-01 / F-003 | sem/inválida ⇒ 401; válida ⇒ 200 | E-06 | E-09 |
| api.test.js::CT-02 | integração | CT-02 / F-003 | sem/inválida ⇒ 401 e nada removido | E-06 | E-09 |
| api.test.js::CT-04 | integração | CT-04 / F-016, F-019 | id inexistente ⇒ 404; sem órfãos no relatório | E-06 | E-09 |
| api.test.js::CT-03 | integração | CT-03 / F-008 | senha errada/ausente ⇒ 401 e nada gravado; correta ⇒ 200 | E-06 | E-09 |
| api.test.js::F-001 | integração | F-001 | log sem cartão completo nem chave | E-06 | E-09 |
| api.test.js::F-007 | integração | F-007 | cartão numérico ⇒ 400 e processo vivo | E-06 | E-09 |
| settings.test.js (3) | unidade | F-004 | sem segredo literal; sem credencial padrão; leitura do ambiente | E-06 | E-09 (varredura vermelha pelo segredo; os outros 2 por módulo inexistente) |
| payment-gateway.test.js (4) | unidade | F-002 | recusa por padrão; mock restrito | E-06 | E-09 por módulo inexistente; comportamento comprovado em E-04 × E-08, linha 20 (200 → 400) |
| password-service.test.js (2) | unidade | F-005 | scrypt com salt; só a senha exata | E-06 | E-09 por módulo inexistente |
| checkout-service.test.js (6) | unidade | F-005, F-008, F-009, F-010, F-011 | rollback, recusa sem escrita, senha, sem senha padrão, regra sem HTTP | E-06 | E-09 por módulo inexistente |
| report-service.test.js (3) | unidade | F-012, F-017 | agregação, centavos, erro propagado | E-06 | E-09 por módulo inexistente |
| composition-root.test.js (1) | integração | F-006, F-010, F-013 | duas aplicações no mesmo processo sem estado compartilhado | E-06 | E-09 por módulo inexistente |

Limite da prova: nos 5 arquivos marcados "por módulo inexistente", o vermelho é estrutural, porque o código original não tem esses módulos; ele não demonstra sozinho a sensibilidade de cada asserção.

## Evidências de execução
Arquivos em `reports/evidence/project-2/20261116-213657/`.

| E-nn | Descrição | Momento | Comando | Exit | Resultado |
|---|---|---|---|---|---|
| E-00 | Análise da Fase 1 | Fase 2 | somente leitura | — | 3 arquivos, ~180 linhas |
| E-01 | V5 `node --check` | baseline | `node --check` | 0 | 3/3 ok |
| E-02 | V1 testes | baseline | `npm test` | 0 | passed 8 / failed 0 / skipped 0 |
| E-03 | V3 boot + api.http | baseline | `npm start` + 2 checkouts | 0 | 200, 400 |
| E-04 | V4 execução local | baseline | bateria de 21 requisições | 0 | ver tabela abaixo |
| E-05 | V5 `node --check` | final | `node --check` | 0 | 35/35 ok |
| E-06 | V1 testes | final | `npm test` | 0 | passed 33 / failed 0 / skipped 0 |
| E-07 | V3 boot + api.http | final | `npm start` + 2 checkouts (mock) | 0 | 200, 400 |
| E-08 | V4 execução local | final | mesma bateria de E-04 | 0 | ver tabela abaixo |
| E-09 | Sensibilidade no checkpoint | prova | `node --test` na cópia | 1 (esperado) | passed 8 / failed 14 |
| E-10 | Diff dos testes | prova | `git diff` | — | 1 arquivo alterado |
| E-11 | Reauditoria | final | varredura do catálogo | 0 | 0 ocorrências nos sinais verificados |
| E-12 | Limpeza | final | K-07 | 0 | worktree e temporários removidos; porta livre |

### Execução local autenticada (V4)
Credenciais: `ADMIN_API_KEY`, `SEED_USER_PASSWORD` e `PAYMENT_GATEWAY_KEY` aleatórias por execução; valores mascarados. Integrações: provedor mock ativado por configuração de teste. Banco: SQLite em memória, descartável.

| # | Método | Rota | Credencial | ANTES (status) | DEPOIS (status) | Resultado | Prova |
|---|---|---|---|---|---|---|---|
| 1 | GET | /api/admin/financial-report | sem | 200 | 401 | ALTERADO (aprovado CT-01) | E-04, E-08 |
| 2 | GET | /api/admin/financial-report | inválida | 200 | 401 | ALTERADO (aprovado CT-01) | E-04, E-08 |
| 3 | GET | /api/admin/financial-report | admin | 200 | 200 | igual | E-04, E-08 |
| 4 | POST | /api/checkout (campos ausentes) | sem | 400 | 400 | igual | E-04, E-08 |
| 5 | POST | /api/checkout (curso inexistente) | sem | 404 | 404 | igual | E-04, E-08 |
| 6 | POST | /api/checkout (cartão recusado) | sem | 400 | 400 | igual | E-04, E-08 |
| 7 | POST | /api/checkout (novo usuário) | sem | 200 | 200 | igual | E-04, E-08 |
| 8 | POST | /api/checkout (e-mail cadastrado) | senha correta | 200 | 200 | igual | E-04, E-08 |
| 9 | POST | /api/checkout (e-mail cadastrado) | senha errada | 200 | 401 | ALTERADO (aprovado CT-03) | E-04, E-08 |
| 10 | POST | /api/checkout (e-mail cadastrado) | sem senha | 200 | 401 | ALTERADO (aprovado CT-03) | E-04, E-08 |
| 11 | GET | /api/admin/financial-report | admin | 200 (Docker 1988) | 200 (Docker 994) | ALTERADO (aprovado CT-03: as 2 compras indevidas deixaram de existir) | E-04, E-08 |
| 12 | POST | /api/checkout (JSON malformado) | sem | 400 com stack trace | 400 `Bad Request` | ALTERADO (correção F-015, sem contrato) | E-04, E-08 |
| 13 | DELETE | /api/users/999 | sem | 200 | 401 | ALTERADO (aprovado CT-02) | E-04, E-08 |
| 14 | DELETE | /api/users/1 | inválida | 200 | 401 | ALTERADO (aprovado CT-02) | E-04, E-08 |
| 15 | DELETE | /api/users/999 | admin | 200 | 404 | ALTERADO (aprovado CT-04) | E-04, E-08 |
| 16 | DELETE | /api/users/1 | admin | 200 | 200 (`Usuário deletado.`) | ALTERADO (aprovado CT-04) | E-04, E-08 |
| 17 | GET | /api/admin/financial-report | admin | 200 (aluno `Unknown`) | 200 (sem órfãos) | ALTERADO (aprovado CT-04) | E-04, E-08 |
| 18 | POST | /api/checkout (cartão numérico) | sem | sem resposta (processo caiu) | 400 | ALTERADO (correção F-007, sem contrato) | E-04, E-08 |
| 19 | GET | /api/admin/financial-report | admin | sem resposta | 200 | ALTERADO (correção F-007, sem contrato) | E-04, E-08 |
| 20 | POST | /api/checkout (sem provedor configurado) | sem | 200 | 400 `Pagamento recusado` | ALTERADO (correção F-002, sem contrato) | E-04, E-08 |
| 21 | GET | /api/admin/financial-report (sem provedor) | admin | 200 (Docker 497) | 200 (Docker 0) | ALTERADO (correção F-002, sem contrato) | E-04, E-08 |

Log da aplicação após a refatoração: sem número completo de cartão, sem chave do gateway e sem senha de seed (E-08). Nenhum resultado `DIVERGENTE`.

### Comparação antes/depois (rotas)
| Método | Rota | ANTES | DEPOIS | Resultado | Prova |
|---|---|---|---|---|---|
| POST | /api/checkout (api.http, sucesso) | 200 {msg,enrollment_id} | 200 {msg,enrollment_id} | igual | E-03, E-07 |
| POST | /api/checkout (api.http, recusado) | 400 `Pagamento recusado` | 400 `Pagamento recusado` | igual | E-03, E-07 |
| POST | /api/checkout (e-mail cadastrado, senha errada/ausente) | 200 | 401 | ALTERADO (aprovado CT-03) | E-04, E-08 |
| GET | /api/admin/financial-report | 200 aberta | 401 sem credencial; 200 com credencial, mesmo formato | ALTERADO (aprovado CT-01) | E-04, E-08 |
| DELETE | /api/users/:id | 200 aberta | 401 sem credencial; 200 ou 404 com credencial | ALTERADO (aprovado CT-02, CT-04) | E-04, E-08 |

### Resumo da validação
| Degrau | Comando | Resultado | Evidência |
|---|---|---|---|
| V1 | `npm test` | passed 33 / failed 0 / skipped 0 (baseline: 8 / 0 / 0) | E-02, E-06 |
| V3 | `npm start` + 2 checkouts de api.http | iguais ao baseline | E-03, E-07 |
| V4 | bateria autenticada de 21 requisições | 6 iguais; 15 alteradas por contrato aprovado ou correção; 0 divergentes | E-04, E-08 |
| V5 | `node --check` | 35/35 ok | E-01, E-05 |

Veredito: VALIDADO (V1+V3+V4)

## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — JavaScript/Node.js, por package.json e código (E-00)
- [x] Framework detectado corretamente — Express 4.22.1, por manifesto, lockfile e `express()` (E-00)
- [x] Domínio da aplicação descrito corretamente — LMS com checkout e relatório financeiro (E-00)
- [x] Número de arquivos analisados condiz com a realidade — 3 arquivos, 180 linhas por `wc -l` (E-00)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — seções na ordem de `03-template-relatorio.md`
- [x] Cada finding tem arquivo e linhas exatos — campos `File:` conferidos na leitura integral dos 3 arquivos-fonte
- [x] Findings ordenados por severidade (CRITICAL → LOW) — F-001 a F-025
- [x] Mínimo de 5 findings identificados — 25
- [x] Detecção de APIs deprecated incluída (se aplicável) — "DEP: nenhuma encontrada" para as versões declaradas
- [x] Skill pausa e pede confirmação antes da Fase 3 — resposta `1A 2A 3A 4A` registrada em "Decisões do usuário"

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — camadas separadas; 0 arquivos com 3+ papéis (E-11)
- [x] Configuração extraída para módulo de config (sem hardcoded) — src/config/settings.js; varredura sem segredos (E-06, E-11)
- [x] Models criados para abstrair dados — src/models/*; nenhum SQL fora de models/database (E-11)
- [x] Views/Routes separadas para visualização ou roteamento — src/routes/index.js
- [x] Controllers concentram o fluxo da aplicação — src/controllers/*, sem SQL (E-11)
- [~] Error handling centralizado — src/middlewares/errorHandler.js (E-08); F-019 parcial: erros em texto e sucesso em JSON mantidos para preservar o contrato
- [x] Entry point claro — src/app.js, `npm start` (E-07)
- [x] Aplicação inicia sem erros — E-07, E-08
- [x] Endpoints originais respondem corretamente — 3 de 3 rotas respondem; 6 cenários iguais e 15 alterados por CT-01 a CT-04 ou correção comprovada (E-08)

## Itens residuais (reauditoria)
CRITICAL/HIGH sem correção: Nenhum
Corrigidos no código com ação manual pendente: F-004 — rotacionar a chave do gateway (`pk_l***`) e a senha de banco (`senh***`) publicadas no histórico git
Demais findings ainda presentes:
- F-019 (MEDIUM, parcial): erros em texto e sucesso em JSON; mantido para preservar o contrato.
- F-018 (MEDIUM, parcial): relatório sem paginação; mantido porque o relatório é agregado e paginar mudaria o contrato.
- F-025 (LOW, parcial): chaves do payload `usr`, `eml`, `pwd`, `c_id` mantidas por serem contrato.

Pontos novos observados na reauditoria (fora do plano aprovado, sem correção aplicada):
- O 401 do checkout revela que um e-mail está cadastrado (consequência de CT-03).
- Duas compras simultâneas com o mesmo e-mail novo: a segunda responde 500 com rollback depois de o gateway aprovar. Com um provedor real, será preciso estornar ou reservar a cobrança.
- `api.http` e `README.md` não foram alterados e estão desatualizados: as requisições administrativas precisam do cabeçalho `Authorization`, e o checkout precisa de provedor configurado.

## Observações da execução
- Stack detectada e confiança: JavaScript (Node.js) + Express 4.22.1, confiança alta.
- Dicas específicas usadas × derivadas do sinal abstrato: dicas de Node/Express do catálogo; nenhum finding derivado.
- Nível de organização encontrado e como a Fase 3 se adaptou: `monolito-sem-camadas`; todas as camadas foram criadas.
- Falsos positivos descartados: 10 entradas (ex.: SEC-01, com todas as consultas parametrizadas).
- F-007 e F-015 foram registrados como LIKELY na Fase 2 e confirmados em execução no baseline (E-04, linhas 12 e 18).
- Limitações da validação: não existe provedor de pagamento real, só o mock; o `{N}=2` foi escolhido sem ler o relatório de outro projeto, conforme a regra da execução.
- Tentativas/iterações na Fase 3 e reversões: a execução foi interrompida por limite de uso e retomada em 2026-11-18, após conferir arquivos, worktree e porta; a primeira rodada do script de validação falhou por colisão de variável no próprio script temporário e foi repetida sem mudança no projeto. Nenhuma reversão.
- Arquivos criados pela execução fora do código-fonte: branch local `refactor-arch/checkpoint-20261116-213657` (mantida); worktree, junção de `node_modules` e scripts no diretório temporário (removidos, E-12); `.env.example` no projeto; relatório e evidências em `reports/`.

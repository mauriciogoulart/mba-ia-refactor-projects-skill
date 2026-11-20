# Evidência complementar — Projeto 2: rotas administrativas sem `ADMIN_API_KEY`

Complemento **manual** à execução da skill (Run `20261116-213657`). Responde à ressalva da [validação independente do projeto 2](validacao-project-2_2026-11-18_v3.md): não havia teste automatizado para "sem `ADMIN_API_KEY`, as rotas administrativas negam tudo".

Foi usada uma verificação externa para não alterar o código nem a suíte gerados pela skill: os 33 testes e as evidências `E-nn` do relatório continuam como foram gerados.

| Item | Valor |
|---|---|
| Data | 2026-11-20 |
| Commit verificado | `afe3385` (branch `entrega-v2`) |
| Projeto | `ecommerce-api-legacy/` |
| Node | v24.11.1 |
| Como | script temporário **fora** do projeto que importa `createApplication` e `loadSettings` (o mesmo caminho usado por `npm start` em `src/app.js`), sobe a aplicação em porta aleatória com SQLite em memória e faz as requisições |
| Comando | `node admin-sem-chave.js <raiz do repositório>/ecommerce-api-legacy` |
| Exit code | 0 |
| Resultado | **10/10 OK**. Sem a variável (ausente ou vazia), as 8 requisições às rotas administrativas responderam 401, inclusive com `Bearer` vazio, `Bearer qualquer` e `Bearer undefined`. No controle, com a chave definida, só a chave correta recebeu 200 |
| Arquivos alterados no projeto | nenhum (`git status` limpo após a execução) |

## Saída

```text
Executado em: 2026-11-20T13:22:50.737Z
Node: v24.11.1

## 1. Sem ADMIN_API_KEY (variável ausente)
Ambiente: APP_ENV=test ADMIN_API_KEY=(vazia)
Avisos da aplicação no boot: SEED_USER_PASSWORD não definida: usuário de seed criado com senha aleatória | ADMIN_API_KEY não definida: rotas administrativas negam todas as requisições
01 | GET /api/admin/financial-report | cred=sem cabeçalho | status 401 | esperado 401 | OK
02 | GET /api/admin/financial-report | cred=Bearer vazio | status 401 | esperado 401 | OK
03 | GET /api/admin/financial-report | cred=Bearer qualquer | status 401 | esperado 401 | OK
04 | GET /api/admin/financial-report | cred=Bearer undefined | status 401 | esperado 401 | OK
05 | DELETE /api/users/1 | cred=sem cabeçalho | status 401 | esperado 401 | OK
06 | DELETE /api/users/1 | cred=Bearer qualquer | status 401 | esperado 401 | OK

## 2. ADMIN_API_KEY vazia
Ambiente: APP_ENV=test ADMIN_API_KEY=(vazia)
Avisos da aplicação no boot: SEED_USER_PASSWORD não definida: usuário de seed criado com senha aleatória | ADMIN_API_KEY não definida: rotas administrativas negam todas as requisições
07 | GET /api/admin/financial-report | cred=Bearer vazio | status 401 | esperado 401 | OK
08 | DELETE /api/users/1 | cred=Bearer vazio | status 401 | esperado 401 | OK

## 3. Controle: ADMIN_API_KEY definida (aleatória)
Ambiente: APP_ENV=test ADMIN_API_KEY=ZgLq***
Avisos da aplicação no boot: SEED_USER_PASSWORD não definida: usuário de seed criado com senha aleatória
09 | GET /api/admin/financial-report | cred=sem cabeçalho | status 401 | esperado 401 | OK
10 | GET /api/admin/financial-report | cred=chave correta | status 200 | esperado 200 | OK

Resultado: 10/10 OK, 0 falha(s)
exit=0
```

## Script utilizado

Mantido aqui para reprodução; não fica no projeto.

```js
// Evidência manual: rotas administrativas do ecommerce-api-legacy sem ADMIN_API_KEY.
// Uso: node admin-sem-chave.js <caminho do ecommerce-api-legacy>
const path = require('node:path');
const crypto = require('node:crypto');

const raiz = path.resolve(process.argv[2]);
const { createApplication } = require(path.join(raiz, 'src/app'));
const { loadSettings } = require(path.join(raiz, 'src/config/settings'));

const avisos = [];
const logger = { info() {}, warn(m) { avisos.push(m); }, error() {} };
const mascarar = (v) => (v ? `${v.slice(0, 4)}***` : '(vazia)');

async function subir(env) {
    const { app, db } = await createApplication(loadSettings(env), logger);
    const server = await new Promise((r) => { const s = app.listen(0, '127.0.0.1', () => r(s)); });
    return { db, server, base: `http://127.0.0.1:${server.address().port}` };
}

async function descer({ server, db }) {
    server.closeAllConnections();
    await new Promise((r) => server.close(r));
    await db.close();
}

async function bateria(titulo, env, casos) {
    console.log(`\n## ${titulo}`);
    console.log(`Ambiente: APP_ENV=${env.APP_ENV} ADMIN_API_KEY=${mascarar(env.ADMIN_API_KEY)}`);
    avisos.length = 0;
    const inst = await subir(env);
    console.log(`Avisos da aplicação no boot: ${avisos.length ? avisos.join(' | ') : '(nenhum)'}`);
    let falhas = 0;
    for (const [n, metodo, rota, cred, cabecalho, esperado] of casos) {
        const headers = cabecalho === null ? {} : { Authorization: cabecalho };
        const r = await fetch(inst.base + rota, { method: metodo, headers });
        const ok = r.status === esperado;
        if (!ok) falhas += 1;
        console.log(`${n} | ${metodo} ${rota} | cred=${cred} | status ${r.status} | esperado ${esperado} | ${ok ? 'OK' : 'FALHA'}`);
    }
    await descer(inst);
    return falhas;
}

(async () => {
    console.log(`Executado em: ${new Date().toISOString()}`);
    console.log(`Node: ${process.version}`);
    let falhas = 0;

    falhas += await bateria('1. Sem ADMIN_API_KEY (variável ausente)', { APP_ENV: 'test' }, [
        ['01', 'GET', '/api/admin/financial-report', 'sem cabeçalho', null, 401],
        ['02', 'GET', '/api/admin/financial-report', 'Bearer vazio', 'Bearer ', 401],
        ['03', 'GET', '/api/admin/financial-report', 'Bearer qualquer', 'Bearer qualquer', 401],
        ['04', 'GET', '/api/admin/financial-report', 'Bearer undefined', 'Bearer undefined', 401],
        ['05', 'DELETE', '/api/users/1', 'sem cabeçalho', null, 401],
        ['06', 'DELETE', '/api/users/1', 'Bearer qualquer', 'Bearer qualquer', 401],
    ]);

    falhas += await bateria('2. ADMIN_API_KEY vazia', { APP_ENV: 'test', ADMIN_API_KEY: '' }, [
        ['07', 'GET', '/api/admin/financial-report', 'Bearer vazio', 'Bearer ', 401],
        ['08', 'DELETE', '/api/users/1', 'Bearer vazio', 'Bearer ', 401],
    ]);

    const chave = crypto.randomBytes(24).toString('base64url');
    falhas += await bateria('3. Controle: ADMIN_API_KEY definida (aleatória)', { APP_ENV: 'test', ADMIN_API_KEY: chave }, [
        ['09', 'GET', '/api/admin/financial-report', 'sem cabeçalho', null, 401],
        ['10', 'GET', '/api/admin/financial-report', 'chave correta', `Bearer ${chave}`, 200],
    ]);

    console.log(`\nResultado: ${10 - falhas}/10 OK, ${falhas} falha(s)`);
    process.exitCode = falhas ? 1 : 0;
})().catch((e) => { console.error(e); process.exitCode = 2; });
```

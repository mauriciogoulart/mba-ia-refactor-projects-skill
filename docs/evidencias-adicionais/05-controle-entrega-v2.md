# Controle de execução — Entrega v2 (skill refactor-arch 1.2)

Arquivo de acompanhamento item a item da revisão pós-avaliação. Atualizado a cada etapa concluída.

Legenda: ✅ concluído · 🔄 em andamento · ⏳ pendente · ⚠️ atenção/bloqueio

## Contexto

Solicitação do avaliador (entrega v1):

> No ecommerce-api-legacy, a Fase 3 rodou com a opção de manter o contrato e deixou três CRITICAL do próprio relatório abertos: as rotas de relatório financeiro e de exclusão de usuário continuam sem autenticação, o checkout continua sem verificar a senha da conta existente e o gateway simulado continua aprovando como PAID qualquer cartão que começa com "4". Ajuste a skill para que a opção de manter o contrato não possa deixar CRITICAL ou HIGH sem correção, acrescente ao playbook um padrão que resolva de fato o pagamento simulado (o P-09 hoje só isola esse código) e rode a skill de novo nesse projeto.

Decisões do usuário para a v2:

| Tema | Decisão |
|---|---|
| Pergunta de contrato (P3) | 1. Refatorar (recomendado, padrão) · 2. Manter contrato* · 3. Híbrido (mantém contrato em MEDIUM/LOW, corrige CRITICAL/HIGH com mudança mínima) |
| Asterisco da opção 2 | Permitida com aviso: mostra quantos CRITICAL/HIGH ficam sem correção e exige segunda confirmação; veredito "com ressalvas de segurança" |
| Prova | Testes de unidade/integração no framework existente + execução local dos endpoints com credenciais geradas pela própria aplicação |
| Pagamento simulado | Novo padrão P-20: gateway por configuração, recusa por padrão, provedor mock só por configuração explícita fora de produção |
| Execuções | 3 projetos a partir do código-fonte original, respondendo "Refatorar" nos 3 |
| Evidências | Mesmo formato `E-nn` da v1; entrega v1 arquivada em `historico/entrega-v1/` |

## Fase 0 — Preservar a entrega v1

| # | Item | Status | Observação |
|---|---|---|---|
| 0.1 | Criar branch `entrega-v2` a partir de `main` (a772d66) | ✅ | |
| 0.2 | Criar tag local `entrega-v1` em a772d66 | ✅ | push só na Fase 5 |
| 0.3 | Mover `reports/` e `validacoes/` para `historico/entrega-v1/`; copiar README | ✅ | `git mv` (histórico preservado) |
| 0.4 | Criar `historico/entrega-v1/LEIA-ME.md` | ✅ | |
| 0.5 | Commit do arquivamento | ✅ | `296406f` |

## Fase 1 — Skill versão 1.2

| # | Item | Status | Observação |
|---|---|---|---|
| 1.1 | `SKILL.md` | ✅ | regra 6 (testes de prova em qualquer opção), nova regra 10 (piso de segurança), P3/P4 e segunda confirmação na Fase 2, reauditoria conta CRITICAL/HIGH |
| 1.2 | `07-politica-comandos-aprovacoes.md` (P3 com 3 opções, P4 execução local) | ✅ | P3: Refatorar · Manter contrato* · Híbrido; segunda confirmação (§4.2); §5 execução local autenticada |
| 1.3 | `05-playbook-refatoracao.md` (matriz, P-09, novo P-20, P-05) | ✅ | matriz de 3 colunas; P-09 remete ao P-20; P-20 com antes/depois Node e Python e provas |
| 1.4 | `02-catalogo-antipatterns.md` (SEC-14) | ✅ | SEC-14 corrigido por P-20; checagem final (g): todo CRITICAL/HIGH com correção prevista |
| 1.5 | `06-protocolo-validacao.md` (testes de prova, execução local autenticada) | ✅ | V4 = execução local autenticada (§5.1); T4 em qualquer opção; veredito "com ressalvas" |
| 1.6 | `03-template-relatorio.md` | ✅ | versão 1.2 / catálogo 1.1; tabela de contrato por opção; seção "Execução local autenticada"; residuais CRITICAL/HIGH em destaque |
| 1.7 | `01-analise-projeto.md` (inventário de autenticação/seed) | ✅ | |
| 1.8 | Revisão de coerência (sem "Opção 1/Opção 2" remanescente) | ✅ | busca por "Opção 1/2", "sondagem ad hoc" e "só na Opção" = vazia |
| 1.9 | Revisão independente da skill por subagente | ✅ | 0 bloqueantes, 7 importantes, 11 menores — todos aplicados: exceção do diretório temporário na classe X; status `ALTERADO (correção F-xxx, sem contrato)`; P-20 com lista branca de ambiente, sem mock padrão, prefixos filtrados, `Map` de provedores e testes extras; CRITICAL/HIGH novo fora do escopo ⇒ pergunta (sem reversão); "parcial" conta como sem correção; P4 = Não ⇒ veredito qualificado; pré-condição de prova generalizada; ressalva como sufixo; ordem das opções; variante de credencial no payload no P-05; catálogo 1.2 |
| 1.10 | Copiar para os 3 projetos e conferir com `diff -r` | ✅ | `git diff --no-index` vazio entre as 3 cópias |
| 1.11 | Commit da skill 1.2 | ✅ | ver registro |

## Fase 2 — Restaurar o código-fonte original

| # | Item | Status | Observação |
|---|---|---|---|
| 2.1 | Restaurar os 3 projetos a partir de 5303107 | ✅ | `git rm -r` + `git checkout 5303107`; diretórios residuais só com `__pycache__` removidos |
| 2.2 | Reaplicar a skill 1.2 nos 3 projetos | ✅ | `git checkout HEAD -- <projeto>/.claude` (commit da skill 1.2) |
| 2.3 | Conferir suítes no original (23 / 8 / 25) e diff só da skill | ✅ | 23 passed · 8 pass · 25 passed; `git diff 5303107` fora de `.claude/` vazio |
| 2.4 | Commit da restauração | ✅ | `146f7d9` |

## Fase 3 — Executar a skill nos 3 projetos

| # | Item | Status | Observação |
|---|---|---|---|
| 3.1 | P1 code-smells-project — Fases 1 e 2 (pausa) | ✅ | Run id 20261116-195523; 31 findings (9 C / 6 H / 10 M / 6 L); P3 com 3 opções e asterisco "3 CRITICAL e 0 HIGH ficarão sem correção" |
| 3.2 | P1 — respostas e Fase 3 | ✅ | respostas `1A 2A 3A 4A`; na Fase 3: lote C `1A` (checkpoint + worktree temporária) e design de autenticação `2A` (token assinado no `/login`). Veredito VALIDADO (V1+V4); 0 CRITICAL/HIGH residuais; testes 23 → 51 (28 de prova: 9 unidade, 19 integração, todos vermelhos no original); execução local autenticada com 52 requisições (E-03 × E-07) |
| 3.3 | P1 — commit | ✅ | ver registro |
| 3.4 | P1 — validação independente (subagente) | ✅ | APROVADO com ressalvas não bloqueantes ([validação](validacoes/validacao-project-1_2026-11-16_v3.md)): 51 passed reexecutado; 28 provas vermelhas no original; app subida com credenciais geradas (401 sem token, 200 com token, `/admin/query` 404); 31 referências de linha conferidas. Ressalvas: `Infinity`/`NaN` em `POST /produtos` ⇒ 500; README do projeto não atualizado; fragmentos de segredo antigo em E-08 (saída de assert, mantida sem edição para preservar a evidência bruta); cabeçalho E-nn incompleto em E-03/E-06/E-07 |
| 3.5 | P2 ecommerce-api-legacy — Fases 1 e 2 (pausa) | ✅ | Run id 20261116-213657; 25 findings (6 C / 7 H / 7 M / 5 L); pagamento simulado (F-002, SEC-14) com correção P-20 em todas as opções; asterisco de Manter contrato*: "1 CRITICAL (F-003) e 1 HIGH (F-008) ficarão sem correção; exige segunda confirmação" |
| 3.6 | P2 — respostas e Fase 3 | ✅ | respostas `1A 2A 3A 4A`; lote C aprovado; autenticação admin por `ADMIN_API_KEY` (nega tudo sem a variável). Veredito VALIDADO (V1+V3+V4); 0 CRITICAL/HIGH residuais; testes 8 → 33 (25 de prova: 18 unidade, 7 integração); execução local autenticada com 21 requisições (E-04 × E-08), 0 divergentes |
| 3.7 | P2 — commit | ✅ | ver registro |
| 3.8 | P2 — validação independente (subagente) | 🔄 | |
| 3.9 | P3 task-manager-api — Fases 1 e 2 (pausa) | ✅ | Run id 20261116-214549; 28 findings (7 C / 4 H / 11 M / 6 L); asterisco de Manter contrato*: "3 CRITICAL (F-002, F-006, F-007) e 0 HIGH ficarão sem correção"; execução interrompida por limite de uso da API e retomada em 2026-11-18 |
| 3.10 | P3 — respostas e Fase 3 | 🔄 | respostas `1A 2A 3A 4A` |
| 3.11 | P3 — commit | ⏳ | |
| 3.12 | P3 — validação independente (subagente) | ⏳ | |

## Fase 4 — Documentação

| # | Item | Status | Observação |
|---|---|---|---|
| 4.1 | README: seção "Revisão pós-avaliação (entrega v2)" e resultados atualizados | ⏳ | |
| 4.2 | Timeline: passos 13+ | ⏳ | |
| 4.3 | Verificação de links e números | ⏳ | |
| 4.4 | Commit da documentação | ⏳ | |

## Fase 5 — Envio

| # | Item | Status | Observação |
|---|---|---|---|
| 5.1 | Push da branch `entrega-v2` e da tag `entrega-v1` (requer confirmação do usuário) | ⏳ | |
| 5.2 | Abrir PR para `main` | ⏳ | |

## Registro de execução

| Data/hora | Evento |
|---|---|
| 2026-11-16 | Fase 0: branch `entrega-v2`, tag `entrega-v1`, arquivamento (`296406f`) |
| 2026-11-16 | Fase 1: skill 1.2 editada, revisada por subagente independente, ajustada e copiada para os 3 projetos (`20f9e72`) |
| 2026-11-16 | Fase 2: código original restaurado e suítes conferidas (`146f7d9`) |

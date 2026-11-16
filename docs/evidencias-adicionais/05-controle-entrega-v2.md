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
| 0.1 | Criar branch `entrega-v2` a partir de `main` (a772d66) | ⏳ | |
| 0.2 | Criar tag local `entrega-v1` em a772d66 | ⏳ | |
| 0.3 | Mover `reports/` e `validacoes/` para `historico/entrega-v1/`; copiar README | ⏳ | |
| 0.4 | Criar `historico/entrega-v1/LEIA-ME.md` | ⏳ | |
| 0.5 | Commit do arquivamento | ⏳ | |

## Fase 1 — Skill versão 1.2

| # | Item | Status | Observação |
|---|---|---|---|
| 1.1 | `SKILL.md` | ⏳ | |
| 1.2 | `07-politica-comandos-aprovacoes.md` (P3 com 3 opções, P4 execução local) | ⏳ | |
| 1.3 | `05-playbook-refatoracao.md` (matriz, P-09, novo P-20, P-05) | ⏳ | |
| 1.4 | `02-catalogo-antipatterns.md` (SEC-14) | ⏳ | |
| 1.5 | `06-protocolo-validacao.md` (testes de prova, execução local autenticada) | ⏳ | |
| 1.6 | `03-template-relatorio.md` | ⏳ | |
| 1.7 | `01-analise-projeto.md` (inventário de autenticação/seed) | ⏳ | |
| 1.8 | Revisão de coerência (sem "Opção 1/Opção 2" remanescente) | ⏳ | |
| 1.9 | Revisão independente da skill por subagente | ⏳ | |
| 1.10 | Copiar para os 3 projetos e conferir com `diff -r` | ⏳ | |
| 1.11 | Commit da skill 1.2 | ⏳ | |

## Fase 2 — Restaurar o código-fonte original

| # | Item | Status | Observação |
|---|---|---|---|
| 2.1 | Restaurar os 3 projetos a partir de 5303107 | ⏳ | |
| 2.2 | Reaplicar a skill 1.2 nos 3 projetos | ⏳ | |
| 2.3 | Conferir suítes no original (23 / 8 / 25) e diff só da skill | ⏳ | |
| 2.4 | Commit da restauração | ⏳ | |

## Fase 3 — Executar a skill nos 3 projetos

| # | Item | Status | Observação |
|---|---|---|---|
| 3.1 | P1 code-smells-project — Fases 1 e 2 (pausa) | ⏳ | |
| 3.2 | P1 — respostas e Fase 3 | ⏳ | |
| 3.3 | P1 — commit | ⏳ | |
| 3.4 | P1 — validação independente (subagente) | ⏳ | |
| 3.5 | P2 ecommerce-api-legacy — Fases 1 e 2 (pausa) | ⏳ | |
| 3.6 | P2 — respostas e Fase 3 | ⏳ | |
| 3.7 | P2 — commit | ⏳ | |
| 3.8 | P2 — validação independente (subagente) | ⏳ | |
| 3.9 | P3 task-manager-api — Fases 1 e 2 (pausa) | ⏳ | |
| 3.10 | P3 — respostas e Fase 3 | ⏳ | |
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

# Entrega v1 — arquivada

Esta pasta guarda a primeira entrega do desafio, como foi avaliada. Ela foi arquivada porque a skill foi revisada (versão 1.2) e reexecutada nos 3 projetos a partir do código-fonte original.

## Identificação

| Item | Valor |
|---|---|
| Tag git | `entrega-v1` (commit `a772d66`, merge do PR #5) |
| Versão da skill | `refactor-arch 1.1` · Catálogo 1.0 |
| Código refatorado | commits `bbaa786` (code-smells-project), `6e7fcc5` (ecommerce-api-legacy), `51acdfb` (task-manager-api) |
| Código original usado nas execuções | commit `5303107` |

Para ver o repositório exatamente como foi entregue:

```bash
git checkout entrega-v1
```

## Conteúdo

| Caminho | O que é |
|---|---|
| [README-entrega-v1.md](README-entrega-v1.md) | README da entrega v1 (links relativos apontam para a estrutura original; use a tag para navegá-los) |
| [reports/](reports/) | Relatórios `audit-project-{1,2,3}.md` e evidências `E-nn` das execuções da skill 1.1 |
| [validacoes/](validacoes/) | Validações independentes de cada execução (v1 e v2 do projeto 1, projetos 2 e 3) |

## Motivo da revisão

Solicitação do avaliador:

> No ecommerce-api-legacy, a Fase 3 rodou com a opção de manter o contrato e deixou três CRITICAL do próprio relatório abertos: as rotas de relatório financeiro e de exclusão de usuário continuam sem autenticação, o checkout continua sem verificar a senha da conta existente e o gateway simulado continua aprovando como PAID qualquer cartão que começa com "4". Ajuste a skill para que a opção de manter o contrato não possa deixar CRITICAL ou HIGH sem correção, acrescente ao playbook um padrão que resolva de fato o pagamento simulado (o P-09 hoje só isola esse código) e rode a skill de novo nesse projeto.

O que mudou na entrega v2 está descrito no [README](../../README.md) da raiz, seção "Revisão pós-avaliação (entrega v2)", e o passo a passo em [05-controle-entrega-v2.md](../../docs/evidencias-adicionais/05-controle-entrega-v2.md).

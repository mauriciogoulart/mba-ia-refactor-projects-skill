# 06 — Protocolo de validação e evidências (Fase 3)

Define **como provar** que a aplicação continua funcionando e **como mostrar ao usuário** que a prova é real. Complementa `07-politica-comandos-aprovacoes.md` (quem pode rodar o quê).

## 1. Princípios

1. **Só recursos do projeto** (decisão D5): testes, scripts, targets, configs, CI e coleções/exemplos de requisição que **já existem**. Não crie scripts, coleções ou helpers no projeto. Não adicione ferramenta de teste que o projeto não declare. **Exceções:** (a) a skill adiciona/atualiza testes (unidade ou integração), no framework e no diretório de testes que o projeto já usa e sem dependência nova, **apenas para comprovar** correções — cada `CT-xx` aplicado e cada correção CRITICAL/HIGH, em qualquer opção de contrato (seção 8.9); (b) a execução local autenticada (seção 5.1) usa requisições geradas a partir de arquivos temporários **fora** do projeto.
2. **Comparar com o baseline**: tudo que for medido depois é comparado ao que foi medido **antes** de editar, com o mesmo comando.
3. **Evidência real ou nada**: cada ✓ aponta um `E-nn` produzido por chamada de ferramenta desta sessão. Execução pulada = `NÃO EXECUTADO`. Nunca preencha resultado por inferência.
4. **Compilar, subir, testar rodam sempre**, sem confirmação (classe B), em qualquer modo. Só instalação/ambiente (C) e destrutivos (D) dependem de aprovação.
5. **Testes podem ser adaptados, nunca "para passar"**: a refatoração e os contratos aprovados exigem atualizar testes; o que é proibido é editar, remover, enfraquecer ou pular um teste só para ele passar. O teste alterado deve manter a intenção e continuar validando de forma equivalente ou mais forte. Política completa na seção 8.
6. **Segredos mascarados** em toda evidência.

## 2. Plano de validação (montado na Fase 2, executado na Fase 3)

Tabela do relatório (seção "Plano de validação"), a partir do inventário da Fase 1:

| Degrau | Disponível? | Comando (origem, classe) | Observação |
|---|---|---|---|
| V1 Testes do projeto | sim/não | `<cmd>` (arquivo:linha, B) | tipo(s), nº aproximado |
| V2 Script de verificação do projeto | sim/não | `<cmd>` | lint/check/CI |
| V3 Boot + requisições existentes | sim/não | boot `<cmd>` + coleção/curl `<arquivo>` | rotas cobertas |
| V4 Execução local autenticada | depende de P4 | boot com ambiente de teste + requisições com credenciais geradas pela aplicação | seção 5.1; baseline e final |
| V5 Estático | sempre | compilar/importar (B) | — |
| Pré-requisitos | | `<cmd instalação>` (C) | se ausentes |
| Testes afetados previstos | | testes que dependem de módulos movidos, autenticação, seed ou campos alterados | classe T1/T2/T4 (seção 8) |
| Prova prevista (`CT-xx` aplicados e correções CRITICAL/HIGH) | | teste novo de unidade/integração + execução local autenticada / não comprovável | seção 8.9 |
| Não exercitável | | rotas/fluxos e motivo | admin/destrutivas, banco externo, etc. |

## 3. Escada de validação

Tente **sempre o degrau mais alto disponível** e, quando útil, vários (V1 e V3 juntos dão mais confiança). Declare o degrau alcançado e por que não foi mais alto.

| Degrau | O que é | Fonte | Força |
|---|---|---|---|
| **V1** | Suíte de testes automatizados do projeto (unidade/integração/e2e) | comando do projeto (manifesto/config/CI) | Alta |
| **V2** | Script/target de verificação do projeto (`check`, `verify`, `lint`, etapas de CI) | idem | Média-alta |
| **V3** | Boot por comando documentado + coleção/exemplos **existentes** (`.http`, Postman, OpenAPI, `curl` de scripts/CI/README) executados | recursos do projeto | Média |
| **V4** | Execução local autenticada: boot com ambiente de teste e banco descartável + requisições criadas por você, autenticadas com credenciais geradas pela própria aplicação, cobrindo as rotas da Superfície de ataque (seção 5.1) | efêmero; **só** se P4 = Sim | Média |
| **V5** | Estática: o código compila/importa; rotas registram | toolchain da stack (classe B) | Baixa |

**Veredito:**
- `VALIDADO (V1)` / `VALIDADO (V1+V3)` / `VALIDADO (V1+V4)`: testes passaram **e** (quando aplicável) o boot e as rotas responderam como no baseline ou como no contrato aprovado.
- Sufixo `COM RESSALVAS DE SEGURANÇA (CRITICAL/HIGH sem correção: <F-xxx>)`: acrescentado a **qualquer** veredito quando o usuário confirmou deixar CRITICAL/HIGH sem correção (`07`, seção 4.2). Ex.: `VALIDADO (V1+V4) COM RESSALVAS DE SEGURANÇA (...)`, `VALIDADO PARCIALMENTE (...) COM RESSALVAS DE SEGURANÇA (...)`.
- Qualificador `(V4 não executada)` quando P4 = "Não" em serviço HTTP.
- `VALIDADO PARCIALMENTE (<degraus>; não exercitado: <lista>)`.
- `NÃO VALIDADO (<motivo>)`.
Sem V1 nem V3, nunca escreva "a aplicação continua funcionando" sem o qualificador "validação limitada (V4/V5)".

## 4. Protocolo (ordem fixa)

```
Passo 0   Pré-voo
          - A: git status; registrar Run id (relógio do sistema); descobrir SO/shell
          - verificar dependências instaladas (A: pip show/ls node_modules/--version)
          - C (conforme modo): checkpoint (K-00) e instalação de dependências ausentes
          - pasta de evidências: reports/evidence/project-{N}/{Run id}/
Passo 0b  BASELINE (código ORIGINAL, antes da primeira edição) — classe B
          - rodar V1/V2 → E-01...
          - rodar V3 (boot + requisições existentes) → E-0x; registrar status + chaves de cada rota
          - V4 (execução local autenticada, seção 5.1) se P4 permitir — no código original, em cópia
            descartável fora do projeto; registrar a mesma bateria que será repetida no final
          - baseline vermelho (testes já falham) ⇒ avisar o usuário, registrar "falhas pré-existentes"
            e continuar só se o usuário concordar; a comparação passa a ser "não piorou"
Passos 1..n  aplicar padrões do playbook na ordem canônica; após cada bloco: V5 (compila/importa)
Passo V   VALIDAÇÃO FINAL: repetir exatamente os mesmos comandos → E-nn; montar tabelas antes/depois
Passo R   REAUDITORIA: reaplicar o catálogo ao código novo; "No anti-patterns remaining" só se zero residuais
          (senão listar residuais com o motivo); contar CRITICAL/HIGH residuais — com Refatorar/Híbrido
          devem ser zero: residual de correção aprovada que não funcionou ⇒ tratar como falha (abaixo);
          CRITICAL/HIGH novo, fora do escopo aprovado ⇒ PERGUNTAR (incluir novo C-xx ou segunda
          confirmação), nunca reverter por isso; com Manter contrato* confirmado, listar em destaque
Falha     até 2 tentativas de correção por problema; persistindo ⇒ reverter ao checkpoint e relatar
          (reversão total só em regressão funcional; correção que não eliminou o finding sem quebrar nada
          ⇒ reverter só aquele padrão ou manter e declarar o residual, perguntando ao usuário)
Limpeza   encerrar processos iniciados; liberar portas; registrar arquivos criados fora do código-fonte
```

Reversão: com git, volte ao estado do checkpoint apenas por meios **seguros** (branch/stash do checkpoint criado por você; `git reset --hard`/`clean` são classe X). Sem git, restaure da cópia de checkpoint. Se não houver como reverter com segurança, **pare e pergunte**.

## 5. Subir e parar a aplicação (V3/V4)

1. Use o comando de boot **descoberto** na Fase 1 (README/script/CI/entry point), em **segundo plano** (run in background), com timeout. Nunca presuma a porta: leia-a do código/config/coleção.
2. **Prontidão**: aguarde até (a) o log mostrar linha de "listening/running/Started" **ou** (b) a porta responder à rota de saúde/raiz, com tentativas curtas (ex.: 20 × 0,5 s). Capture as primeiras linhas do log como prova de boot.
3. Execute a bateria (coleção/exemplos existentes; e a execução local autenticada V4 se permitida — seção 5.1).
4. **Sempre encerre o processo que você iniciou**, inclusive em falha, e confirme que a porta foi liberada. Porta já ocupada ⇒ reporte e use outra porta **somente** se o projeto permitir configurá-la por ambiente/argumento; **nunca** mate processo que você não iniciou.
5. Windows × Unix: detecte o shell; use a sintaxe correta (variáveis de ambiente, encerrar processo, redirecionamento). Não presuma bash.
6. Banco local do projeto: se subir a aplicação alterar arquivos de dados existentes (seed que apaga), é classe D — trate antes (copie o banco para fora ou pergunte).

### 5.1 Execução local autenticada (V4)

Mostra as rotas funcionando em execução real, com autenticação feita pelos mecanismos da **própria aplicação**. Só com P4 = Sim (`07`, seção 4.1).

1. **Ambiente efêmero:** banco descartável (memória, arquivo em diretório temporário ou cópia do projeto fora da árvore, como as fixtures de teste costumam fazer), porta descoberta, variáveis de ambiente de teste. Nunca o banco existente do projeto.
2. **Credenciais geradas pela aplicação:** gere valores aleatórios por execução para as variáveis de seed/credencial que a aplicação lê (ex.: senha do admin de seed), suba a aplicação e obtenha o token pelo endpoint de login dela. No código original sem esse mecanismo, use os dados de seed já versionados no projeto ou o cadastro público da própria API. Nunca dados reais. Senhas e tokens mascarados (4 caracteres + `***`).
3. **Integrações externas:** use o provedor mock/sandbox da própria aplicação, ativado por configuração de teste (ex.: P-20 com `PAYMENT_PROVIDER=mock`); nunca chame serviço externo.
4. **Bateria:** para cada rota da Superfície de ataque, as variações que se aplicam: sem credencial; credencial inválida (rotas protegidas); credencial válida do perfil adequado; perfil sem permissão (quando houver perfis); escrita com payload sintético; rota destrutiva só contra o banco descartável desta execução. Inclua o caminho de pagamento sem provedor configurado quando houver P-20.
5. **Baseline e final:** rode a mesma bateria no código original (cópia descartável) e no refatorado, quando viável. A diferença mostra o efeito das correções (ex.: `antes 200 sem credencial → depois 401`; `com credencial 200 → 200`).
6. **Evidência:** scripts temporários fora do projeto; saída em `E-nn-<baseline|final>-execucao-local.log`, no formato da seção 7, com uma linha por requisição (método, rota, credencial usada, status, chaves do corpo, tempo); tabela "Execução local autenticada" no anexo (`03`, seção 4). Encerre os processos e confirme a porta liberada.

## 6. Regras de segurança da bateria de requisições

- Baseline e validação usam **as mesmas** requisições, na mesma ordem.
- Rotas marcadas administrativas/destrutivas e qualquer `DELETE` **não** entram automaticamente. Se um recurso do projeto (script/coleção) as contém, trate a requisição como classe D (pergunta individual) ou marque `NÃO EXERCITADA (rota destrutiva)`.
- Escritas (POST/PUT) vindas de recursos do projeto: só se o banco for local/descartável; senão `NÃO EXERCITADA (motivo)`.
- Registre por rota: método, caminho, status, **chaves** do JSON de resposta (não o conteúdo sensível), tempo.
- Rotas com mudança de contrato aprovada aparecem como `ALTERADO (aprovado)`. Mudança de **resultado** causada por correção compatível aprovada (mesma rota, status e formato já existentes, ex.: pagamento recusado sem provedor pelo P-20) aparece como `ALTERADO (correção F-xxx, sem contrato)` e precisa de prova. Qualquer outra diferença é `DIVERGENTE` e **conta como falha**.
- A comparação antes/depois usa o **mesmo ambiente de teste** nos dois lados (ex.: provedor mock ativo quando houver P-20); chamadas que provam a correção (ex.: checkout sem provedor configurado) são registradas à parte, como prova.

## 7. Formato de evidência (`E-nn`)

Cada execução vira um bloco no relatório **e** um arquivo bruto em `reports/evidence/project-{N}/{Run id}/E-nn-<slug>.log` (escreva a saída capturada, com segredos mascarados, usando a ferramenta de escrita; não crie nada dentro do projeto).

```
### E-02 · <descrição> (<baseline|após refatoração>)
Comando:      <literal>                         Diretório: <cwd>
Origem:       <K-nn · arquivo:linha onde foi descoberto> · Classe <B> · Autorização: <automática (classe B)|lote aprovado|individual aprovada>
Início/Fim:   <ISO 8601> → <ISO 8601> (duração <s>)        Exit code: <n>
Ambiente:     <runtime e versões relevantes>
Resultado:    <passed X | failed Y | skipped Z>   (baseline E-01: <...>)
Saída (início e fim; segredos mascarados):
  <~15 primeiras linhas>
  [... N linhas omitidas ...]
  <~15 últimas linhas>
Bruto:        reports/evidence/project-{N}/{Run id}/E-02-<slug>.log
Artefatos:    <junit.xml, cobertura, screenshots, vídeos, traces — somente os gerados pelo projeto/runner>
Integridade:  testes alterados/adicionados: <0 | n — ver "Alterações em testes" / "Testes adicionados">  (verificado por: <git diff, ou snapshots em tests-before/ se não versionados>)
```

**E-00 — evidência da Fase 1.** Na Fase 2 (passo 9 do `SKILL.md`), junto do relatório, grave `reports/evidence/project-{N}/{Run id}/E-00-fase1-analise.txt` com: o bloco `PHASE 1: PROJECT ANALYSIS` **literal**; a lista dos arquivos-fonte contados (caminho e linhas) e o método de contagem; as rotas encontradas (método, caminho, arquivo:linha); o inventário de validação; os comandos descobertos (com classe). Segredos mascarados. O checklist da Fase 1 cita `E-00`. Não altera o formato do relatório.

Artefatos adicionais, quando houver ajuste/criação de testes: `tests-before/<caminho>` (cópia do original), `E-nn-diff-testes.patch` (diff unificado) e as execuções vermelha/verde da seção 8.9.

Para o usuário **ver e crer** que rodou:
1. Comando literal, diretório, horários, duração, exit code.
2. Contagens do próprio runner e comparação com o baseline: o **nº de testes não pode cair** e `skipped` não pode subir sem explicação.
3. Saída bruta salva em arquivo (não só resumo).
4. Artefatos que o projeto já gera (relatório HTML, junit, cobertura, screenshots/vídeos/traces de Playwright/Cypress se configurados) são **coletados e referenciados**; não force a geração instalando algo novo.
5. **Screenshot (opcional)**: se o projeto serve UI web e o agente tem ferramenta de navegador, capture a página principal servida (classe B, host local); salve em `E-nn-<slug>.png` na pasta de evidências. Para APIs puras, o equivalente é a transcrição do terminal (item 3) e a tabela de rotas.
6. **Anti-fabricação**: cada ✓ do bloco `Validation` e do checklist cita um `E-nn`; evidência só existe se saiu de uma chamada de ferramenta real; comando não executado aparece como `NÃO EXECUTADO (motivo)`.
7. Ao final, imprima um resumo compacto (`Resumo da validação`) e o caminho da pasta de evidências.

## 8. Política de alteração de testes

**8.1 Princípio.** Testes podem e, muitas vezes, devem mudar numa refatoração. O que é proibido é alterá-los **só para passar**. Um teste alterado precisa continuar fazendo sentido e validando corretamente a mesma intenção.

**8.2 Quando é permitido alterar:** (a) a refatoração moveu módulos, funções, imports ou fixtures que o teste usa; (b) uma mudança de contrato **aprovada** (`CT-xx`) alterou o comportamento que o teste afirma; (c) é necessária mudança de configuração/ambiente de teste (variável de ambiente, banco temporário, credencial de seed vinda do ambiente).

**8.3 Classes**

| Classe | O que é | Regra |
|---|---|---|
| **T1 mecânica** | imports, caminhos, fixture/setup, credencial de teste, autenticação necessária | asserções **idênticas** |
| **T2 contrato** | a asserção muda porque o contrato aprovado mudou | a nova asserção expressa o novo contrato **de forma explícita** (ex.: com token ⇒ 200 e sem token ⇒ 401), preferindo manter a asserção original no cenário válido |
| **T3 proibida** | remover ou comentar teste/asserção; `skip`/`xfail`/`skipif`; afrouxar o esperado (200 → "200 ou 500"); `assert True`; engolir exceção; mockar o objeto sob teste; reduzir os dados que exercitam a regra; mudar o esperado sem `CT-xx` correspondente | **nunca**, nem sob pedido |
| **T4 novo** | teste adicionado (unidade ou integração) para provar um `CT-xx` aplicado ou uma correção CRITICAL/HIGH, em qualquer opção | seção 8.9 |

**8.4 "Continua fazendo sentido" — verifique por teste alterado:** mesmo nome/cenário/intenção; nº de asserções ≥ o original; cada asserção original mantida ou substituída por equivalente/mais forte (justifique); o teste ainda **pode falhar** se o comportamento sob teste regredir (depende do código real, não de um valor copiado da nova saída sem análise); o esperado vem do contrato aprovado, não do que o código passou a retornar.

**8.5 Procedimento**
1. **Regressão primeiro:** se um teste falha após refatorar, investigue se é regressão (corrija o código) ou consequência de `CT-xx` aprovado. Só então adapte o teste.
2. **Snapshot** do arquivo original em `reports/evidence/project-{N}/{Run id}/tests-before/<caminho>` **antes** de editar (permite diff mesmo sem git ou com testes não versionados).
3. Edite o mínimo necessário.
4. Gere o diff unificado e grave `E-nn-diff-testes.patch`.
5. Reexecute o teste alterado **e** a suíte completa; compare com o baseline (nº de testes **não cai**; `skipped` **não sobe** sem explicação).
6. Registre em "Alterações em testes" (`03`, seção 4).

**8.6 Aprovação.** Ajustes T1/T2/T4 **rastreáveis** a `C-xx`/`CT-xx` já aprovados não geram pergunta extra (a aprovação do escopo/contrato os cobre; os previstos aparecem em "Testes afetados" na Fase 2). **Pergunte** (`Ajustar o teste` · `Manter e registrar a falha`) apenas se: (i) o ajuste não é rastreável a mudança aprovada; (ii) exigiria reescrever a maior parte das asserções do teste; (iii) o teste parece ter bug próprio. T3 nunca.

**8.7 Integridade final.** A lista de testes alterados/adicionados deve ser **igual** à registrada (com git: `git diff` nos caminhos de teste; sem git ou não versionados: compare com `tests-before/`). Divergência ⇒ reverta o ajuste não registrado e refaça a validação.

**8.8 Manter contrato\*.** Não há ajuste de contrato em testes; só T1 mecânico (módulos/fixtures movidos, ambiente de teste: credencial de seed, provedor mock) e testes novos T4 que comprovem as correções CRITICAL/HIGH compatíveis (ex.: hash de senha, pagamento recusado sem provedor).

**8.9 Comprovação das correções (`CT-xx` aplicados e CRITICAL/HIGH).** Cada `CT-xx` aplicado (Refatorar/Híbrido) e cada correção CRITICAL/HIGH (qualquer opção) precisa de evidência produzida pela própria refatoração:
1. **Teste novo ou atualizado** (T2/T4) no framework e no diretório de testes existentes, sem nova dependência, rastreado a `CT-xx`/`F-xxx`. Use **unidade** quando a regra é isolável (gateway de pagamento, hash de senha, validação, autorização) e **integração** quando o efeito é na rota (status, campos, acesso). Exemplos: sem credencial ⇒ 401; credencial inválida ⇒ 401; sem perfil ⇒ 403; credencial válida ⇒ comportamento esperado; rota removida ⇒ 404/405; campo ausente na resposta; entrada inválida ⇒ 400/404/409.
2. **Execução verde** no código refatorado (`E-nn`).
3. **Prova de sensibilidade quando viável:** executar o teste novo contra o **checkpoint do código original** (cópia fora do projeto ou worktree do checkpoint, classe B na cópia); ele deve **falhar** lá. Registre a execução vermelha (`E-nn`). Sem checkpoint utilizável, declare "sensibilidade não verificada".
4. **Execução local autenticada** (seção 5.1, se P4 = Sim) complementa os testes, mostrando as mesmas provas em execução real. **Sem framework de testes**, ela é a prova (chamada sem credencial ⇒ 401, com credencial ⇒ sucesso etc., com `E-nn`). Sem ambos, o item fica `NÃO VALIDADO` (declarado, e avisado ao usuário antes de aplicar — `07`, seção 4.1).
5. Preencha a tabela antes/depois com a coluna **"Prova"** (`E-nn`) e a seção "Testes adicionados" do anexo.

## 9. Casos especiais

- **Sem nenhum teste/coleção:** V1–V3 indisponíveis ⇒ a execução local autenticada (P4) passa a ser o principal degrau; sem permissão, validação em V5 com veredito `VALIDADO PARCIALMENTE (V5)` ou `NÃO VALIDADO`; reforce TST-01 como recomendação. Não introduza framework de testes novo: sem framework, a prova das correções vem da execução local autenticada (seção 8.9, item 4).
- **Projeto não-HTTP** (CLI, biblioteca, worker): "boot" = executar o ponto de entrada com argumento de ajuda/versão ou o exemplo do README; "endpoints" = funções/comandos públicos exercitados por testes existentes. Marque o item do checklist "Endpoints originais respondem" como `N/A (não é serviço HTTP)` com motivo.
- **Dependência externa** (banco/serviço que não é local): não conecte; valide estaticamente e por testes que usem mocks/containers locais já definidos no projeto; registre o limite.
- **Dependências ausentes:** classe C; sem aprovação, a validação cai para V5 e isso é declarado.
- **Aplicação com seed que sobrescreve dados:** copie/aponte para banco descartável antes (se o projeto permitir por variável) ou trate como D.
- **Testes lentos/travados:** aplique timeout; registre `TIMEOUT` com a saída parcial como evidência; não ignore silenciosamente.

## 10. Checklist de saída da Fase 3

- [ ] Baseline registrado antes da primeira edição (E-01…).
- [ ] Validação final com os **mesmos** comandos (E-nn…).
- [ ] Tabela antes/depois de rotas e de testes.
- [ ] Testes alterados/adicionados somente os registrados (T1/T2/T4), com snapshot, diff, justificativa, reexecução e prova de sensibilidade dos testes de prova (ou "não verificada" declarada).
- [ ] Execução local autenticada registrada no baseline e no final (`E-nn-*-execucao-local.log`) ou `NÃO EXECUTADA (motivo)`.
- [ ] CRITICAL/HIGH residuais = 0 (Refatorar/Híbrido) ou listados com a segunda confirmação do usuário (Manter contrato\*/rejeição).
- [ ] `E-00` gravado na Fase 2 e citado no checklist da Fase 1.
- [ ] Processos encerrados e portas liberadas.
- [ ] Reauditoria executada; residuais listados.
- [ ] Todos os ✓ do checklist e do bloco `Validation` referenciam `E-nn`.

# Timeline de execução do desafio

Passo a passo seguido para resolver o desafio, com os artefatos gerados em cada etapa.

1. Comecei com a análise do desafio como um todo, visando entender o objetivo e o formato de execução.

2. Análise manual -> feita utilizando IA com outro modelo mais simples, devido à falta de conhecimento nas linguagens.
   Gerado o relatório [01-relatorio-issues-analise-manual.md](01-relatorio-issues-analise-manual.md).

3. Antes de iniciar a criação da skill em si, fiz uma análise de como os projetos podem ser executados e se já estavam funcionando, criando scripts para automatizar os testes com IA, para validar se os resultados de antes e depois das alterações são os mesmos.
   Gerado o relatório [02-relatorio-analise-execucao-testes.md](02-relatorio-analise-execucao-testes.md).

4. Iniciei uma análise de como criar a skill e de quais decisões técnicas arquiteturais tomar para conseguir atender os requisitos.
   Gerado o documento [03-analise-arquitetural-skill.md](03-analise-arquitetural-skill.md).

5. Ainda antes de criar a skill, pensei em como comprovar que o sistema continua funcionando após as alterações, de forma que a skill procure no projeto instruções sobre como testar, scripts auxiliares etc.

   Sobre testes e validação se continua funcionando:
   configurar a skill para que verifique se há testes de unidade, de integração,
   instruções de como executar o projeto e testar,
   eventuais scripts para subir o sistema ou validar etc.;
   precisamos que, de alguma forma, a skill tenha a habilidade de validar que tudo segue funcionando,
   e que consiga demonstrar com evidências reais como validou, seja com print de tela (se houver Playwright ou outra ferramenta),
   comprovação dos testes ou outra forma que permita ao usuário ver e entender que os testes foram efetivamente executados.

6. Rodada de entrevistas/conversas com IA para refinar o escopo antes de criar a skill. Exemplo:

   ```
   <consideracoes>
   1) Sobre testes e validação se continua funcionando,
   precisamos que a skill verifique se tem testes de unidade, de integração,
   instruções de como executar o projeto e testar,
   eventuais scripts de subir sistema ou de como validar, etc,
   precisamos que de alguma forma, a skill tenha habilidade de validar que segue tudo funcionando,
   e que ela consiga demonstrar com evidencias reais de como validou, seja com print de tela se tiver playright ou outra ferramenta,
   comprovação dos testes, alguma forma que o usuário possa ver e entender que os testes foram efetivamente executados.

   2) Precisamos que a skill siga o solicitado no readme do desafio, considerando a nomenclatura e regras definidas no readme.

   3) NAO CONSIDERE os demais arquivos existentes na pasta de trabalho alem do gerado na sua analise,
   precisamos ser imparcial, e atuar como algum dev/qa novo iniciando no projeto.

   4) A skill nao deve servir apenas para os projetos citados, ela deve ser agnostica a tecnologia ou projeto, os projetos de exemplo sao apenas para validacao,
   o minimo esperado é atender apenas estes projetos, mas precisamos de uma skill capaz de executar em qualquer projeto.
   </consideracoes>
   ```

7. Gerado um plano de ação. Foi tomada a decisão de ter opções de múltipla escolha para o usuário responder em casos de dúvida (como manter ou remover endpoints com issues etc.), e a skill foi criada utilizando o Claude Code.
   Plano de ação gerado: [04-plano-acao-criacao-skill.md](04-plano-acao-criacao-skill.md).

8. Executada a skill no projeto `code-smells-project` para validação. Passou em todos os itens, mas a revisão gerou alguns pontos de atenção.
   [validacoes/validacao-project-1_2026-11-05_v1.md](validacoes/validacao-project-1_2026-11-05_v1.md)

9. Executada a segunda versão da skill no projeto `code-smells-project` para validação. Passou em todos os itens, sem considerações ou pontos de atenção bloqueantes.
   [validacoes/validacao-project-1_2026-11-05_v2.md](validacoes/validacao-project-1_2026-11-05_v2.md)

10. Executada a segunda versão da skill no projeto `ecommerce-api-legacy` para validação. Passou em todos os itens, com uma ressalva relacionada à opção que escolhi manualmente ao ser perguntado: manter os endpoints atuais, sem quebrar o contrato, para demonstrar que a skill permite escolher.
    [validacoes/validacao-project-2_2026-11-06_v2.md](validacoes/validacao-project-2_2026-11-06_v2.md)

11. Executada a segunda versão da skill no projeto `task-manager-api` para validação. Passou em todos os itens, sem pontos de atenção bloqueantes.
    [validacoes/validacao-project-3_2026-11-06_v2.md](validacoes/validacao-project-3_2026-11-06_v2.md)

12. Exemplo de prompt utilizado para validar o resultado da refatoração de cada projeto com base nas evidências geradas pela skill:

    ```
    <contexto>
    Estou fazendo o desafio "Criação de Skills — Refatoração Arquitetural Automatizada" conforme o readme deste projeto.
    Criei a skill e executei no projeto "task-manager-api", preciso validar se o resultado da execução atende os itens a seguir.

    Relatório: reports/audit-project-3.md
    Evidências: reports/evidence/project-3/20261106-140715/
    </contexto>
    <criterios de aceite>
    A skill deve atingir os seguintes mínimos em todos os 3 projetos:
    Critério	Requisito
    Fase 1 detecta stack corretamente	OBRIGATÓRIO (3/3 projetos)
    Fase 2 encontra >= 5 findings	OBRIGATÓRIO (3/3 projetos)
    Fase 2 inclui pelo menos 1 CRITICAL ou HIGH	OBRIGATÓRIO (3/3 projetos)
    Fase 3 aplicação funciona após refatoração	OBRIGATÓRIO (3/3 projetos)
    </criterios de aceite>
    <Checklist de Validação>
    ### Fase 1 — Análise
    - [ ] Linguagem detectada corretamente
    - [ ] Framework detectado corretamente
    - [ ] Domínio da aplicação descrito corretamente
    - [ ] Número de arquivos analisados condiz com a realidade
    ### Fase 2 — Auditoria
    - [ ] Relatório segue o template definido nos arquivos de referência
    - [ ] Cada finding tem arquivo e linhas exatos
    - [ ] Findings ordenados por severidade (CRITICAL → LOW)
    - [ ] Mínimo de 5 findings identificados
    - [ ] Detecção de APIs deprecated incluída (se aplicável)
    - [ ] Skill pausa e pede confirmação antes da Fase 3
    ### Fase 3 — Refatoração
    - [ ] Estrutura de diretórios segue padrão MVC
    - [ ] Configuração extraída para módulo de config (sem hardcoded)
    - [ ] Models criados para abstrair dados
    - [ ] Views/Routes separadas para visualização ou roteamento
    - [ ] Controllers concentram o fluxo da aplicação
    - [ ] Error handling centralizado
    - [ ] Entry point claro
    - [ ] Aplicação inicia sem erros
    - [ ] Endpoints originais respondem corretamente
    </Checklist de Validação>
    ```

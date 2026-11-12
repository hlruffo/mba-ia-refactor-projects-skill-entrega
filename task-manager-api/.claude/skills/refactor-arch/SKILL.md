---
name: refactor-arch
description: Audita e refatora APIs legadas para MVC com confirmação humana.
---

# refactor-arch

Use esta skill para analisar uma codebase backend e conduzir uma refatoração arquitetural segura, agnóstica de linguagem e framework. Nunca invente achados: cada finding deve citar arquivo e linhas verificáveis.

## Contrato de execução

- Trabalhe somente na raiz do projeto alvo.
- Leia os arquivos de referência desta skill antes da auditoria.
- Preserve endpoints, contratos HTTP e comportamento funcional, salvo correção de segurança explicitamente documentada.
- Nunca exponha valores de credenciais; use `[REDACTED]` em relatórios e logs.
- Não modifique arquivos durante as Fases 1 e 2.
- A Fase 2 termina com uma pergunta explícita: `Proceed with refactoring (Phase 3)? [y/n]`.
- Só execute a Fase 3 após uma resposta afirmativa inequívoca.

## FASE 1 — PROJECT ANALYSIS

1. Identifique arquivos-fonte, linguagem, runtime, framework, gerenciador de dependências e banco.
2. Detecte a arquitetura atual: entry points, rotas, modelos, serviços, acesso a dados e integrações.
3. Conte arquivos analisados e registre o domínio inferido somente quando sustentado pelo código ou README.
4. Imprima um resumo com `Language`, `Framework`, `Dependencies`, `Domain`, `Architecture` e `Source files`.

## FASE 2 — ARCHITECTURE AUDIT REPORT

1. Leia `references/anti-pattern-catalog.md`, `references/report-template.md` e os demais guias.
2. Cruze o código com o catálogo, ordenando findings por CRITICAL, HIGH, MEDIUM e LOW.
3. Cada finding deve conter: ID, severidade, título, arquivo, linha inicial/final, evidência não sensível, descrição, impacto e recomendação.
4. Inclua APIs deprecated quando existirem; se não houver, declare `não aplicável` com a busca realizada.
5. Gere o relatório em `reports/audit-<project>.md` sem alterar código.
6. Mostre totais por severidade e o total geral.
7. Pare e solicite confirmação exatamente antes da Fase 3.

## FASE 3 — MVC REFACTORING

Após confirmação:

1. Crie uma cópia/backup local ou use o controle de versão existente antes de alterações.
2. Aplique o playbook de forma incremental e mantenha o contrato das rotas.
3. Separe Models (persistência e entidades), Controllers/Services (casos de uso), Views/Routes (HTTP), configuração e tratamento de erros.
4. Remova segredos hardcoded, dados sensíveis das respostas e logs de cartão/senha.
5. Use queries parametrizadas e KDF seguro para senhas quando aplicável.
6. Centralize configuração em ambiente/config e mantenha `.env.example` sem segredos.
7. Valide sintaxe, importação, boot da aplicação, health check e endpoints originais com dados de teste não sensíveis.
8. Atualize o relatório com a estrutura antes/depois, alterações e evidências reais de validação.
9. Não declare sucesso se um endpoint não foi exercitado ou se o boot falhar.

## Saída obrigatória

- Resumo da análise.
- Relatório de auditoria estruturado.
- Confirmação humana registrada antes da Fase 3.
- Estrutura MVC antes/depois.
- Checklist de validação com comandos e resultados reais.
- Limitações e riscos remanescentes.

# Architecture Audit — ecommerce-api-legacy

- Generated at: 2026-11-12T17:20:14-03:00
- Stack: JavaScript, Node.js, Express 4, SQLite (`sqlite3`)
- Files analyzed: 6 total — 3 source files (`src/app.js`, `src/AppManager.js`, `src/utils.js`) plus `package.json`, README, and `api.http`
- Architecture before: entry point initializes a process-global in-memory database and `AppManager` combines schema/seeds, routes, SQL, business rules, logging, and HTTP responses. Configuration and utilities share a module.
- Domain: checkout and course enrollments, supported by routes, table names, seed records, and API examples.

## Summary

- CRITICAL: 4
- HIGH: 2
- MEDIUM: 3
- LOW: 1
- Total: 10

## Findings

### [CRITICAL] AP-001 — Credenciais e chave de gateway no código-fonte
- File: `ecommerce-api-legacy/src/utils.js:1-6`
- Evidence: `config` contém valores literais para credenciais de infraestrutura e uma chave de gateway; valores omitidos como `[REDACTED]`.
- Description: Configuração sensível está versionada junto com valores operacionais, sem leitura de ambiente.
- Impact: Credenciais podem ser recuperadas do repositório e reutilizadas contra serviços associados.
- Recommendation: Remover os literais e carregar configuração por variáveis de ambiente; fornecer apenas nomes/documentação em `.env.example`.
- Deprecated API: não aplicável; busca em `src` por APIs conhecidas deprecadas do Node/Express/SQLite não encontrou uso explícito.

### [CRITICAL] AP-005 — Hash de senha caseiro sem salt ou KDF
- File: `ecommerce-api-legacy/src/utils.js:17-23`
- Evidence: `badCrypto` repete Base64 e trunca o resultado em 10 caracteres.
- Description: A função não usa uma função de derivação de chave para senha, salt aleatório ou verificação segura.
- Impact: Senhas armazenadas podem ser adivinhadas rapidamente e entradas diferentes podem colidir após truncamento.
- Recommendation: Usar `crypto.scrypt` com salt aleatório por usuário e armazenar salt e resultado em formato verificável.
- Deprecated API: não aplicável.

### [CRITICAL] AP-006 — Cartão e chave de pagamento registrados em log
- File: `ecommerce-api-legacy/src/AppManager.js:43-46`
- Evidence: a linha 45 interpola o dado `cc` e `config.paymentGatewayKey` na mensagem enviada a `console.log`; valores omitidos como `[REDACTED]`.
- Description: O fluxo de checkout registra dados de cartão e credencial de integração.
- Impact: Saídas de processo e coletores de log podem expor dados de pagamento e credenciais.
- Recommendation: Remover os dados sensíveis da mensagem; registrar apenas um identificador de operação não sensível.
- Deprecated API: não aplicável.

### [CRITICAL] AP-004 — Relatório financeiro sem controle de acesso
- File: `ecommerce-api-legacy/src/AppManager.js:80-129`
- Evidence: a rota `GET /api/admin/financial-report` retorna relatório sem checar autenticação ou autorização.
- Description: Um caminho explicitamente administrativo está disponível publicamente no código analisado.
- Impact: Qualquer cliente que alcance a API pode consultar receitas e dados derivados de matrículas.
- Recommendation: Exigir autorização administrativa antes de expor o relatório e testar requisições não autorizadas.
- Deprecated API: não aplicável.

### [HIGH] AP-003 — Módulo combina transporte, persistência e regras de negócio
- File: `ecommerce-api-legacy/src/AppManager.js:25-138`
- Evidence: `setupRoutes` declara handlers Express que validam entrada, consultam e escrevem SQLite, determinam aprovação de pagamento e montam respostas.
- Description: Rotas e casos de uso não estão separados de acesso a dados.
- Impact: Mudanças em HTTP, persistência e checkout ficam acopladas e difíceis de verificar isoladamente.
- Recommendation: Separar routes/controllers, services e repositories, com dependências explícitas.
- Deprecated API: não aplicável.

### [HIGH] AP-014 — Configuração e estado global misturados em utilitários
- File: `ecommerce-api-legacy/src/utils.js:1-15`
- Evidence: o módulo combina configuração operacional, cache mutável e funções auxiliares.
- Description: Configuração e estado de cache são inicializados globalmente durante importação.
- Impact: Testes e instâncias da aplicação compartilham estado implícito, e os segredos não têm fronteira de configuração.
- Recommendation: Centralizar configuração em módulo validado e remover/substituir estado global por dependências de escopo da aplicação.
- Deprecated API: não aplicável.

### [MEDIUM] AP-008 — Consultas repetidas em cascata no relatório
- File: `ecommerce-api-legacy/src/AppManager.js:89-126`
- Evidence: para cada curso consulta matrículas; para cada matrícula consulta usuário e pagamento individualmente.
- Description: O número de consultas cresce com cursos e matrículas.
- Impact: Relatório pode degradar com o volume de dados e sua lógica de callbacks concorrentes fica mais difícil de manter.
- Recommendation: Buscar dados necessários com consultas em lote ou JOIN parametrizado no repository.
- Deprecated API: não aplicável.

### [MEDIUM] AP-009 — Validação insuficiente de dados de checkout e exclusão
- File: `ecommerce-api-legacy/src/AppManager.js:28-36, 66-71, 131-134`
- Evidence: checkout apenas verifica truthiness de quatro campos, aceita `pwd` ausente com senha padrão, e o id de exclusão é enviado diretamente à camada SQL sem validação de formato.
- Description: Não há validação explícita de tipos, formato de e-mail, tamanho, senha ou identificador.
- Impact: Entradas malformadas são aceitas até a persistência/regra posterior e contas podem receber credencial previsível.
- Recommendation: Validar schemas e rejeitar dados inválidos; não atribuir senha padrão a novos usuários.
- Deprecated API: não aplicável.

### [MEDIUM] AP-010 — Erros de gravação ignorados em relatório e auditoria
- File: `ecommerce-api-legacy/src/AppManager.js:57-60, 92-107`
- Evidence: callback da inserção de auditoria ignora `err`; consultas de matrícula, usuário e pagamento seguem sem tratar erros.
- Description: Falhas de persistência podem resultar em resposta de sucesso ou resposta parcial sem indicação clara.
- Impact: Chamadores recebem resultado inconsistente e falhas operacionais ficam ocultas.
- Recommendation: Propagar erros específicos ao service e tratá-los em middleware centralizado com resposta pública segura.
- Deprecated API: não aplicável.

### [LOW] AP-012 — Estado e importações sem uso observável
- File: `ecommerce-api-legacy/src/utils.js:10, 25`
- Evidence: `totalRevenue` é inicializado e exportado, mas não é utilizado nos arquivos-fonte; `globalCache` não tem leitura nos arquivos-fonte analisados.
- Description: Há estado/utilidade exportados sem consumidor visível no projeto fonte analisado.
- Impact: Aumenta ruído e sugere comportamento sem efeito claro.
- Recommendation: Remover após confirmar ausência de consumidores externos ou encapsular apenas se houver uso comprovado.
- Deprecated API: não aplicável.

## Fase 1 — resumo da análise

- Language: JavaScript (CommonJS)
- Framework: Express 4
- Dependencies: `express`, `sqlite3`; runtime requerido: Node.js (versão não declarada no `package.json`)
- Domain: checkout e matrículas de cursos
- Architecture: aplicação monolítica com inicialização e rotas acopladas a `AppManager`, persistência SQLite em memória e utilitários globais
- Source files: 3

## Confirmation Gate

`Proceed with refactoring (Phase 3)? [y/n]`

Human confirmation: afirmativa já fornecida pelo usuário na solicitação de 2026-11-12, antes da execução da Fase 3.

## Refactoring and validation

- Before: `src/app.js` abria o servidor durante a importação; `src/AppManager.js` reunia schema, seeds, rotas, SQL e regras; `src/utils.js` misturava segredos, cache e hash caseiro.
- After: `src/config`, `src/database`, `src/routes`, `src/controllers`, `src/services`, `src/repositories` e `src/middleware` separam configuração, infraestrutura, HTTP, casos de uso e consultas. `src/app.js` exporta uma factory; `src/server.js` inicializa e encerra o processo.
- Compatibility/security changes: os caminhos `POST /api/checkout`, `GET /api/admin/financial-report` e `DELETE /api/users/:id` foram mantidos. O relatório administrativo agora exige `Authorization: Bearer <ADMIN_API_TOKEN>` e responde `503` se não houver token configurado; checkout exige campos válidos e senha explícita; exclusão retorna `404` para id inexistente e remove matrículas/pagamentos por chaves estrangeiras em cascata.
- Secrets: os valores literais foram removidos; `.env.example` contém nomes e placeholders. Configuração é carregada de `process.env`; nenhum arquivo `.env` é lido automaticamente. Credenciais de banco/SMTP sem qualquer consumidor no código SQLite foram descartadas; a chave de gateway é mantida apenas como configuração de ambiente. Cartão, token administrativo e chave do gateway não são registrados.
- Passwords: `crypto.scrypt` com salt aleatório de 16 bytes e chave de 64 bytes substitui o hash caseiro; o valor armazenado mantém salt e derivação para verificação futura.
- Deprecated API: não aplicável. Busca executada em `src`/`package.json` por `deprecated`, `.removeListener(`, `new Buffer(`, `process.binding(` e `domain.create(`; sem ocorrências.
- Boot: **PASS** — `npm test` inicia `src/server.js` como subprocesso em porta local temporária (`PORT=0`), recebe evento `server_started`, e o processo encerra com `SIGTERM` no teardown.
- Health: **PASS** — `GET /health` retorna `200` e `{"status":"ok"}`.
- Endpoint checks: **PASS** — `POST /api/checkout` aprovado retorna `200` com matrícula; cartão recusado retorna `400`; checkout inválido retorna `400`; `GET /api/admin/financial-report` sem token retorna `401` e com token retorna `200` e dados seeded; `DELETE /api/users/1` retorna `200`, e o relatório confirma limpeza das matrículas; id de exclusão inválido retorna `400`. O teste também confirma que cartão, token e chave de teste não aparecem na saída do processo.
- Test command/result: `npm test` — 1 teste de integração aprovado, 0 falhas; processo de teste encerrado com código `0`. `find src test -type f -name '*.js' -print0 | xargs -0 -n1 node --check` e `git diff --check` — sem erros.
- Initial sandbox observation: o primeiro boot de teste foi bloqueado por `listen EPERM` no bind de rede do sandbox. O teste final foi executado com permissão para bind local e passou em `127.0.0.1`.
- Remaining risks: o pagamento ainda é uma simulação que decide pelo prefixo do cartão e não integra um gateway; `PAYMENT_GATEWAY_KEY` está apenas disponível na configuração e não é usada pelo fluxo atual. Configurar `ADMIN_API_TOKEN` antes de habilitar o relatório. Bancos SQLite persistentes criados por uma versão anterior não têm migração formal para as novas constraints; o padrão preservado continua sendo `:memory:`.

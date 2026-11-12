# Guidelines de arquitetura MVC

## Model

Representa entidades, persistência e consultas parametrizadas. Não conhece HTTP, headers, status codes, logs de credenciais ou objetos de request.

## View/Routes

Declara rotas, extrai entrada, chama o controller e transforma o resultado em resposta HTTP. Não contém SQL nem regra de negócio.

## Controller/Service

Orquestra casos de uso, valida invariantes e coordena Models e integrações por dependências explícitas. Não deve criar conexões globais escondidas.

## Configuração

Carrega ambiente em módulo próprio, valida campos obrigatórios e fornece defaults seguros. Segredos ficam fora do código e nunca aparecem em respostas.

## Erros e observabilidade

Use tratamento centralizado, mensagens públicas seguras e logs estruturados sem dados pessoais, senhas, cartões, tokens ou stack traces para o cliente.

## Compatibilidade

Mantenha métodos, caminhos, códigos e formatos existentes quando não forem inseguros. Quando uma correção de segurança mudar o contrato, documente a mudança e teste o novo comportamento.

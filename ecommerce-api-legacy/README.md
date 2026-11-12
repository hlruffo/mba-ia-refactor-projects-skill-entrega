# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
cp .env.example .env
set -a && . ./.env && set +a
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e carrega dados de demonstração no boot. Configure `ADMIN_API_TOKEN` com um valor aleatório antes de habilitar o relatório financeiro; sem ele, a aplicação sobe e esse endpoint responde `503`. O exemplo de ambiente contém somente placeholders.

`PAYMENT_GATEWAY_KEY` é lida da configuração de ambiente para futura integração; o fluxo atual simula a decisão do pagamento e não envia nem registra essa chave. O cartão é validado para o fluxo de demonstração e nunca é armazenado ou incluído em logs.

Exemplos de requisições estão em `api.http`.

## Testes

```bash
npm test
```

Os testes usam o runner nativo do Node.js e iniciam o servidor em uma porta temporária.

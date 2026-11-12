'use strict';

function loadConfig(env = process.env) {
  const port = Number(env.PORT || 3000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('PORT must be an integer between 0 and 65535');
  return Object.freeze({
    port,
    host: env.HOST || '127.0.0.1',
    databasePath: env.DATABASE_PATH || ':memory:',
    adminApiToken: env.ADMIN_API_TOKEN || '',
    paymentGatewayKey: env.PAYMENT_GATEWAY_KEY || ''
  });
}

module.exports = { loadConfig };

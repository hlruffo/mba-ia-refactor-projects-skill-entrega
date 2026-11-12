'use strict';

const express = require('express');
const { createApiRouter } = require('./routes');

function createApp({ db, config }) {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '16kb' }));
  app.get('/health', (req, res) => res.status(200).json({ status: 'ok' }));
  app.use('/api', createApiRouter({ db, config }));
  app.use((error, req, res, next) => {
    if (res.headersSent) return next(error);
    if (error instanceof SyntaxError && error.status === 400 && 'body' in error) return res.status(400).json({ error: 'Invalid JSON' });
    const status = Number.isInteger(error.status) && error.status >= 400 && error.status < 500 ? error.status : 500;
    if (status === 500) console.error(JSON.stringify({ event: 'request_failed', method: req.method, path: req.path }));
    return res.status(status).json({ error: status === 500 ? 'Internal server error' : error.message });
  });
  return app;
}

module.exports = { createApp };

'use strict';

const { loadConfig } = require('./config');
const { openDatabase, initializeDatabase } = require('./database');
const { createApp } = require('./app');

async function startServer() {
  const config = loadConfig();
  const db = openDatabase(config.databasePath);
  await initializeDatabase(db);
  const server = createApp({ db, config }).listen(config.port, config.host, () => {
    console.log(JSON.stringify({ event: 'server_started', port: server.address().port }));
  });
  const shutdown = () => server.close(() => db.close(() => process.exit(0)));
  process.once('SIGINT', shutdown);
  process.once('SIGTERM', shutdown);
  return { server, db };
}

if (require.main === module) {
  startServer().catch((error) => {
    console.error(JSON.stringify({ event: 'startup_failed', message: error.message }));
    process.exitCode = 1;
  });
}

module.exports = { startServer };

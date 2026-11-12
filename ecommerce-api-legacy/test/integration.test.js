'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');

test('boot, health and primary API endpoints', async (t) => {
  const testToken = 'test-admin-token-only';
  const testGatewayKey = 'test-gateway-key-only';
  const serverProcess = spawn(process.execPath, [path.join(__dirname, '..', 'src', 'server.js')], {
    cwd: path.join(__dirname, '..'),
    env: { ...process.env, PORT: '0', DATABASE_PATH: ':memory:', ADMIN_API_TOKEN: testToken, PAYMENT_GATEWAY_KEY: testGatewayKey },
    stdio: ['ignore', 'pipe', 'pipe']
  });

  let output = '';
  let startupLine = '';
  serverProcess.stdout.setEncoding('utf8');
  serverProcess.stderr.setEncoding('utf8');
  serverProcess.stdout.on('data', (chunk) => {
    output += chunk;
    startupLine ||= chunk.split('\n').find((line) => line.includes('server_started')) || '';
  });
  serverProcess.stderr.on('data', (chunk) => { output += chunk; });

  const waitForStartup = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Server startup timed out. Output: ${output}`)), 5000);
    const poll = () => {
      if (startupLine) {
        clearTimeout(timer);
        try { resolve(JSON.parse(startupLine)); } catch (error) { reject(error); }
      } else if (serverProcess.exitCode !== null) {
        clearTimeout(timer);
        reject(new Error(`Server exited before startup (${serverProcess.exitCode}). Output: ${output}`));
      } else setTimeout(poll, 20);
    };
    poll();
  });

  let exitPromise;
  t.after(async () => {
    if (serverProcess.exitCode === null && !serverProcess.killed) {
      exitPromise = new Promise((resolve) => serverProcess.once('exit', resolve));
      serverProcess.kill('SIGTERM');
      await Promise.race([exitPromise, new Promise((resolve) => setTimeout(resolve, 3000))]);
    }
    assert.notEqual(serverProcess.exitCode, null, 'server should terminate after SIGTERM');
  });

  const started = await waitForStartup;
  const baseUrl = `http://127.0.0.1:${started.port}`;
  const health = await fetch(`${baseUrl}/health`);
  assert.equal(health.status, 200);
  assert.deepEqual(await health.json(), { status: 'ok' });

  const unauthorized = await fetch(`${baseUrl}/api/admin/financial-report`);
  assert.equal(unauthorized.status, 401);

  const reportResponse = await fetch(`${baseUrl}/api/admin/financial-report`, {
    headers: { authorization: `Bearer ${testToken}` }
  });
  assert.equal(reportResponse.status, 200);
  const initialReport = await reportResponse.json();
  assert.equal(initialReport.length, 2);
  assert.equal(initialReport[0].course, 'Clean Architecture');
  assert.equal(initialReport[0].revenue, 997);

  const checkoutResponse = await fetch(`${baseUrl}/api/checkout`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ usr: 'Test Buyer', eml: 'buyer@example.test', pwd: 'a-test-password', c_id: 2, card: '4111111111111111' })
  });
  assert.equal(checkoutResponse.status, 200);
  const checkout = await checkoutResponse.json();
  assert.equal(checkout.msg, 'Sucesso');
  assert.ok(Number.isInteger(checkout.enrollment_id));

  const invalidCheckout = await fetch(`${baseUrl}/api/checkout`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ usr: 'Invalid', eml: 'not-an-email', pwd: 'short', c_id: 2, card: '4111' })
  });
  assert.equal(invalidCheckout.status, 400);

  const declinedCheckout = await fetch(`${baseUrl}/api/checkout`, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ usr: 'Declined Buyer', eml: 'declined@example.test', pwd: 'a-test-password', c_id: 2, card: '5111111111111111' })
  });
  assert.equal(declinedCheckout.status, 400);

  const deleteResponse = await fetch(`${baseUrl}/api/users/1`, { method: 'DELETE' });
  assert.equal(deleteResponse.status, 200);
  const missingDelete = await fetch(`${baseUrl}/api/users/not-an-id`, { method: 'DELETE' });
  assert.equal(missingDelete.status, 400);
  const reportAfterDelete = await fetch(`${baseUrl}/api/admin/financial-report`, {
    headers: { authorization: `Bearer ${testToken}` }
  });
  assert.equal(reportAfterDelete.status, 200);
  const reportWithoutDeletedUser = await reportAfterDelete.json();
  assert.deepEqual(reportWithoutDeletedUser[0].students, []);
  assert.equal(reportWithoutDeletedUser[0].revenue, 0);

  assert.ok(!output.includes('4111111111111111'), 'card number must not be logged');
  assert.ok(!output.includes(testToken), 'admin token must not be logged');
  assert.ok(!output.includes(testGatewayKey), 'gateway key must not be logged');
});

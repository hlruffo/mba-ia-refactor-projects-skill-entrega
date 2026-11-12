'use strict';

const { timingSafeEqual } = require('node:crypto');

function createAdminAuth(config) {
  return (req, res, next) => {
    if (!config.adminApiToken) return res.status(503).json({ error: 'Admin authentication is not configured' });
    const authorization = req.get('authorization') || '';
    const suppliedBuffer = Buffer.from(authorization.startsWith('Bearer ') ? authorization.slice(7) : '');
    const expectedBuffer = Buffer.from(config.adminApiToken);
    if (expectedBuffer.length !== suppliedBuffer.length || !timingSafeEqual(expectedBuffer, suppliedBuffer)) return res.status(401).json({ error: 'Unauthorized' });
    next();
  };
}

module.exports = { createAdminAuth };

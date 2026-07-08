#!/usr/bin/env node
// Lightweight simulated host helper for CI e2e tests.
// No external dependencies — uses Node built-in http.

const http = require('http');
const { randomBytes } = require('crypto');
const url = require('url');

const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 5001;
const APP_PORT = process.env.APP_PORT ? parseInt(process.env.APP_PORT, 10) : 5000;

const ops = {}; // operation_id -> { polls, state, provider }
const tokenToOp = {}; // operation_authorization -> operation_id
const rate = {}; // ip -> {count, reset}

function sendJSON(res, status, obj, origin) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  if (origin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  }
  res.end(JSON.stringify(obj));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', (c) => (raw += c.toString()));
    req.on('end', () => {
      if (!raw) return resolve(null);
      try {
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });
}

function checkRate(ip) {
  const now = Date.now();
  const windowMs = 60 * 1000; // 1 minute
  const limit = 30; // requests per minute
  if (!rate[ip] || rate[ip].reset <= now) {
    rate[ip] = { count: 0, reset: now + windowMs };
  }
  rate[ip].count += 1;
  if (rate[ip].count > limit) return false;
  return true;
}

function runtimeProfile() {
  return {
    helper_version: 'simulated-helper',
    state: 'ready',
    runtime: {
      engine: 'simulated',
      gpu: 'off',
      app_port: APP_PORT,
      package_flavor: 'test'
    },
    capabilities: {
      provider_tls_repair: false,
      podman_provider_repair: false,
      max_active_operations: 1
    }
  };
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const origin = req.headers['origin'] || null;
  const ip = req.socket.remoteAddress || 'unknown';

  // Basic rate limiting
  if (parsed.pathname !== '/health' && !checkRate(ip)) {
    return sendJSON(res, 429, { message: 'rate_limited' }, origin);
  }

  if (req.method === 'OPTIONS') {
    // Reply to preflight
    res.statusCode = 204;
    if (origin) {
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    }
    return res.end();
  }

  if (req.method === 'GET' && parsed.pathname === '/health') {
    return sendJSON(res, 200, runtimeProfile(), origin);
  }

  if (req.method === 'POST' && parsed.pathname === '/operations/provider-tls-repair') {
    let data;
    try {
      data = await readBody(req);
    } catch (e) {
      return sendJSON(res, 400, { state: 'rejected_operation_authorization', message: 'Invalid JSON body' }, origin);
    }

    if (!data || typeof data !== 'object') {
      return sendJSON(res, 400, { state: 'rejected_unexpected_field', message: 'Request must be JSON object' }, origin);
    }

    const allowed = new Set(['provider', 'confirmation', 'operation_authorization']);
    const extra = Object.keys(data).filter((k) => !allowed.has(k));
    if (extra.length) {
      return sendJSON(res, 400, { state: 'rejected_unexpected_field', message: 'Unexpected fields', fields: extra }, origin);
    }

    const provider = String(data.provider || '').trim().toLowerCase();
    if (!['google', 'azure'].includes(provider)) {
      return sendJSON(res, 400, { state: 'rejected_unknown_provider', message: 'Unknown provider' }, origin);
    }

    if (data.confirmation !== 'repair_tls_and_restart') {
      return sendJSON(res, 400, { state: 'rejected_confirmation', message: 'Invalid confirmation value' }, origin);
    }

    const op_auth = data.operation_authorization;
    if (typeof op_auth !== 'string' || !/^[A-Za-z0-9_-]{32,128}$/.test(op_auth)) {
      return sendJSON(res, 400, { state: 'rejected_operation_authorization', message: 'Invalid operation_authorization token' }, origin);
    }

    // Idempotency: if token was seen, return existing operation
    if (tokenToOp[op_auth]) {
      const existing = tokenToOp[op_auth];
      return sendJSON(res, 200, { operation_id: existing, state: 'existing' }, origin);
    }

    const operation_id = randomBytes(16).toString('hex');
    tokenToOp[op_auth] = operation_id;
    ops[operation_id] = { polls: 0, state: 'planned', provider };

    return sendJSON(res, 202, { operation_id, state: 'planned' }, origin);
  }

  // GET /operations/:id
  if (req.method === 'GET' && parsed.pathname && parsed.pathname.startsWith('/operations/')) {
    const parts = parsed.pathname.split('/').filter(Boolean);
    const opId = parts[1];
    if (!opId || !ops[opId]) {
      return sendJSON(res, 410, { state: 'operation_expired' }, origin);
    }

    const op = ops[opId];
    op.polls += 1;
    if (op.polls === 1) {
      op.state = 'active';
      return sendJSON(res, 200, { operation_id: opId, state: 'active', classification: 'active', terminal: false }, origin);
    }
    op.state = 'ready';
    return sendJSON(res, 200, { operation_id: opId, state: 'ready', classification: 'terminal_success', terminal: true }, origin);
  }

  // Not found
  sendJSON(res, 404, { message: 'not_found' }, origin);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Simulated helper listening on http://127.0.0.1:${PORT}`);
});

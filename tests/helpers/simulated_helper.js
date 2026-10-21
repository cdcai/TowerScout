#!/usr/bin/env node
// Lightweight simulated host helper for CI e2e tests.
// No external dependencies — uses Node built-in http.

const http = require('http');
const { randomBytes } = require('crypto');
const url = require('url');

const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 5001;
const APP_PORT = process.env.APP_PORT ? parseInt(process.env.APP_PORT, 10) : 5000;
const allowedOrigins = new Set([
  `http://localhost:${APP_PORT}`,
  `http://127.0.0.1:${APP_PORT}`
]);
const allowedStartAuthorizations = new Set([
  `TEST_LOCALHOST_${'L'.repeat(32)}`,
  `TEST_LOOPBACK_${'R'.repeat(32)}`
]);
const allowedProbeAuthorizations = new Set([
  `PROBE_${'Y'.repeat(40)}`
]);

const ops = {}; // operation_id -> { polls, state, provider }
const tokenToOp = {}; // operation_authorization -> operation_id
const rate = {}; // ip -> {count, reset}

function sendJSON(res, status, obj, origin) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Pragma', 'no-cache');
  if (origin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader(
      'Access-Control-Allow-Headers',
      'Content-Type, X-TowerScout-Operation-Authorization'
    );
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
      engine: 'docker',
      gpu: 'off',
      app_port: APP_PORT,
      package_flavor: 'test'
    },
    capabilities: {
      provider_tls_repair: true,
      podman_provider_repair: false,
      max_active_operations: 1
    }
  };
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const origin = req.headers['origin'] || null;
  const ip = req.socket.remoteAddress || 'unknown';

  if (origin && !allowedOrigins.has(origin)) {
    return sendJSON(res, 403, { state: 'rejected_origin' });
  }

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
      res.setHeader(
        'Access-Control-Allow-Headers',
        'Content-Type, X-TowerScout-Operation-Authorization'
      );
    }
    return res.end();
  }

  if (req.method === 'GET' && parsed.pathname === '/health') {
    if (
      !allowedProbeAuthorizations.has(
        req.headers['x-towerscout-operation-authorization']
      )
    ) {
      return sendJSON(res, 401, {
        state: 'rejected_operation_authorization'
      }, origin);
    }
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
    if (
      typeof op_auth !== 'string' ||
      !allowedStartAuthorizations.has(op_auth)
    ) {
      return sendJSON(res, 401, { state: 'rejected_operation_authorization', message: 'Invalid operation_authorization token' }, origin);
    }

    // Idempotency: if token was seen, return existing operation
    if (tokenToOp[op_auth]) {
      const existing = tokenToOp[op_auth];
      const op = ops[existing];
      return sendJSON(res, 409, {
        operation_id: existing,
        operation_type: 'provider_tls_repair',
        provider: op.provider,
        state: op.state,
        accepted: true,
        existing_operation: true,
        execution_enabled: true,
        current_step: op.state,
        classification: op.state === 'ready' ? 'terminal_success' : 'active',
        terminal: op.state === 'ready',
        next_action: op.state === 'ready' ? 'retry_provider_validation' : 'poll_existing_operation',
        status_authorization: {
          operation_type: 'provider_tls_repair',
          scope: 'operation_status',
          expires_at: '2999-01-01T00:00:00Z',
          authorization: op.statusAuthorization
        }
      }, origin);
    }

    const operation_id = randomBytes(16).toString('hex');
    tokenToOp[op_auth] = operation_id;
    const statusAuthorization = randomBytes(32).toString('base64url');
    ops[operation_id] = {
      polls: 0,
      state: 'planned',
      provider,
      statusAuthorization
    };

    return sendJSON(res, 202, {
      operation_id,
      operation_type: 'provider_tls_repair',
      provider,
      state: 'planned',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'worker_start',
      classification: 'pending',
      terminal: false,
      next_action: 'await_controlled_execution',
      status_authorization: {
        operation_type: 'provider_tls_repair',
        scope: 'operation_status',
        expires_at: '2999-01-01T00:00:00Z',
        authorization: statusAuthorization
      }
    }, origin);
  }

  // GET /operations/:id
  if (req.method === 'GET' && parsed.pathname && parsed.pathname.startsWith('/operations/')) {
    const parts = parsed.pathname.split('/').filter(Boolean);
    const opId = parts[1];
    if (!opId || !ops[opId]) {
      return sendJSON(res, 410, { state: 'operation_expired' }, origin);
    }

    const op = ops[opId];
    if (
      req.headers['x-towerscout-operation-authorization'] !==
      op.statusAuthorization
    ) {
      return sendJSON(res, 401, {
        state: 'rejected_operation_authorization'
      }, origin);
    }
    op.polls += 1;
    if (op.polls === 1) {
      op.state = 'active';
      return sendJSON(res, 200, {
        operation_id: opId,
        operation_type: 'provider_tls_repair',
        provider: op.provider,
        state: 'runtime_starting',
        accepted: true,
        existing_operation: false,
        execution_enabled: true,
        current_step: 'runtime_starting',
        classification: 'active',
        terminal: false,
        next_action: 'poll_existing_operation'
      }, origin);
    }
    op.state = 'ready';
    return sendJSON(res, 200, {
      operation_id: opId,
      operation_type: 'provider_tls_repair',
      provider: op.provider,
      state: 'ready',
      accepted: true,
      existing_operation: false,
      execution_enabled: true,
      current_step: 'readiness_wait',
      classification: 'terminal_success',
      terminal: true,
      next_action: 'retry_provider_validation'
    }, origin);
  }

  // Not found
  sendJSON(res, 404, { message: 'not_found' }, origin);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Simulated helper listening on http://127.0.0.1:${PORT}`);
});

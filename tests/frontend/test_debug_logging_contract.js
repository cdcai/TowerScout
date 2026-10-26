#!/usr/bin/env node
/**
 * Debug Logging Contract Test - TASK-048
 *
 * Purpose:
 * - Prevent raw console.log calls from creeping back into app source/template code
 * - Verify the page bootstraps the TowerScout debug logger
 * - Verify the logger exposes an always-on info/status channel for the in-app output panel
 * - Verify the Settings screen routes the existing debug toggle through the logger
 *
 * Usage:
 *   node tests/frontend/test_debug_logging_contract.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '../..');
const TEMPLATE_PATH = path.join(ROOT, 'webapp/templates/towerscout.html');
const SETTINGS_PATH = path.join(ROOT, 'webapp/js/src/settings.js');
const SRC_ROOT = path.join(ROOT, 'webapp/js/src');

function listSourceFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      return listSourceFiles(fullPath);
    }

    if (!entry.isFile() || path.extname(entry.name) !== '.js') {
      return [];
    }

    return [fullPath];
  });
}

function findRawConsoleLogs(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split(/\r?\n/);
  const matches = [];

  lines.forEach((line, index) => {
    if (line.includes('console.log(')) {
      matches.push(`${path.relative(ROOT, filePath)}:${index + 1}`);
    }
  });

  return matches;
}

function assertContains(filePath, expected, description, failures) {
  const content = fs.readFileSync(filePath, 'utf8');
  if (!content.includes(expected)) {
    failures.push(`${description} missing in ${path.relative(ROOT, filePath)}`);
  }
}

function main() {
  const failures = [];
  const filesToCheck = [TEMPLATE_PATH, ...listSourceFiles(SRC_ROOT)];

  for (const filePath of filesToCheck) {
    if (path.basename(filePath) === 'towerscout.js') {
      continue;
    }

    failures.push(...findRawConsoleLogs(filePath));
  }

  assertContains(
    TEMPLATE_PATH,
    'window.TowerScoutLogger = {',
    'Template logger bootstrap',
    failures
  );

  assertContains(
    TEMPLATE_PATH,
    'info(...args)',
    'Template info logger',
    failures
  );

  assertContains(
    SETTINGS_PATH,
    'window.TowerScoutLogger.setDebugMode(enabled)',
    'Settings debug toggle logger integration',
    failures
  );

  if (failures.length > 0) {
    console.error('Debug logging contract FAILED');
    failures.forEach(failure => console.error(` - ${failure}`));
    process.exit(1);
  }

  console.log('Debug logging contract PASSED');
}

if (require.main === module) {
  main();
}

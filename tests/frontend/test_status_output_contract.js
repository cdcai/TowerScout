#!/usr/bin/env node
/**
 * TASK-080 in-app status/output panel contract.
 *
 * Verifies normal debug-off status messages identify the active imagery or
 * geocoding provider while distinguishing provider services from the local
 * TowerScout detection model.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '../..');
const SEARCH_PATH = path.join(ROOT, 'webapp/js/src/ui/search.js');

function assertIncludes(content, expected, failures) {
  if (!content.includes(expected)) {
    failures.push(`Missing expected status contract text: ${expected}`);
  }
}

function assertExcludes(content, unexpected, failures) {
  if (content.includes(unexpected)) {
    failures.push(`Stale non-provider-aware status text remains: ${unexpected}`);
  }
}

function main() {
  const failures = [];
  const content = fs.readFileSync(SEARCH_PATH, 'utf8');

  assertIncludes(content, 'function getProviderDisplayName(provider)', failures);
  assertIncludes(content, 'function getDetectionWorkflowDescription(provider)', failures);
  assertIncludes(content, 'Azure Maps', failures);
  assertIncludes(content, 'Google Maps', failures);
  assertIncludes(content, 'local TowerScout detection model', failures);
  assertIncludes(content, 'Estimating tile count using ${getProviderDisplayName', failures);
  assertIncludes(content, 'Starting cooling tower detection using ${getDetectionWorkflowDescription', failures);
  assertIncludes(content, 'using ${getProviderDisplayName(getActiveDetectionProvider())} imagery', failures);
  assertIncludes(content, 'imagery/geocoding', failures);

  assertExcludes(content, "TowerScoutLogger.info('Estimating tile count for the selected search area...')", failures);
  assertExcludes(content, 'TowerScoutLogger.info("Estimating tile count for the selected search area...")', failures);
  assertExcludes(content, "TowerScoutLogger.info('Starting cooling tower detection...')", failures);
  assertExcludes(content, 'TowerScoutLogger.info("Starting cooling tower detection...")', failures);

  if (failures.length > 0) {
    console.error('Status output contract FAILED');
    failures.forEach(failure => console.error(` - ${failure}`));
    process.exit(1);
  }

  console.log('Status output contract PASSED');
}

if (require.main === module) {
  main();
}

#!/usr/bin/env node
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { buildBundle } = require('../../webapp/build.js');

const output = path.join(__dirname, '../../webapp/js/towerscout.js');
buildBundle();
const first = fs.readFileSync(output);
buildBundle();
const second = fs.readFileSync(output);
assert.deepStrictEqual(second, first, 'Identical source produced different bundle bytes');
assert.match(first.toString('utf8'), /Source SHA-256: [a-f0-9]{64}/);
console.log('Task-105 bundle reproducibility passed');

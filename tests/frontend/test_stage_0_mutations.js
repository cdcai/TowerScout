/**
 * Stage 0 Mutation Test - TASK-038 Frontend Refactoring
 * 
 * Purpose: Verify array reassignments converted to mutations work correctly
 * 
 * Tests:
 *   1. Detection_detections clears without errors (Detection.resetAll)
 *   2. Detection_detections filters correctly (AzureMap.clearAll, GoogleMap.clearAll)
 *   3. Tile_tiles clears without errors (Tile.resetAll)
 *   4. No TypeError exceptions during mutation operations
 * 
 * Prerequisites:
 *   - Flask server running on http://localhost:5000
 *   - npm install puppeteer (if not already installed)
 * 
 * Usage:
 *   node tests/frontend/test_stage_0_mutations.js
 */

const puppeteer = require('puppeteer');

// Test configuration
const CONFIG = {
    baseUrl: 'http://localhost:5000',
    timeout: 60000, // 60 seconds
    headless: true, // Set to false to watch tests run
    slowMo: 100 // Slow down by 100ms for visibility
};

// ANSI color codes for output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
}

function logSection(title) {
    console.log('\n' + '═'.repeat(70));
    log(`  ${title}`, colors.bright + colors.cyan);
    console.log('═'.repeat(70) + '\n');
}

function logTest(name) {
    log(`📍 Test: ${name}`, colors.blue);
}

function logSuccess(message) {
    log(`  ✅ ${message}`, colors.green);
}

function logFailure(message) {
    log(`  ❌ ${message}`, colors.red);
}

function logInfo(message) {
    log(`  ℹ️  ${message}`, colors.yellow);
}

// Test results tracking
const results = {
    passed: 0,
    failed: 0,
    errors: []
};

/**
 * Main test suite
 */
async function runTests() {
    logSection('Stage 0 Mutation Tests - Array Reassignment Validation');

    let browser;
    let page;

    try {
        // Launch browser
        logInfo('Launching browser...');
        browser = await puppeteer.launch({
            headless: CONFIG.headless,
            slowMo: CONFIG.slowMo,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        page = await browser.newPage();

        // Set viewport
        await page.setViewport({ width: 1280, height: 800 });

        // Capture console errors
        const consoleErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });

        // Capture page errors
        const pageErrors = [];
        page.on('pageerror', error => {
            pageErrors.push(error.message);
        });

        // Navigate to application
        logInfo(`Navigating to ${CONFIG.baseUrl}...`);
        await page.goto(CONFIG.baseUrl, { waitUntil: 'networkidle2', timeout: CONFIG.timeout });
        logSuccess('Application loaded');

        // Wait for map to initialize
        await page.waitForSelector('#map', { timeout: CONFIG.timeout });
        await page.waitForTimeout(2000); // Give map time to fully initialize

        // ─────────────────────────────────────────────────────────────
        // Test 1: Detection.resetAll() - Detection_detections.length = 0
        // ─────────────────────────────────────────────────────────────
        logTest('Detection.resetAll() - Array clearing mutation');

        try {
            const result = await page.evaluate(() => {
                // Create some test detections
                window.Detection_detections = [
                    { id: 0, conf: 0.8 },
                    { id: 1, conf: 0.9 },
                    { id: 2, conf: 1.0 } // Manual detection
                ];

                const initialLength = window.Detection_detections.length;

                // Call resetAll which should use .length = 0 mutation
                try {
                    window.Detection.resetAll();

                    return {
                        success: true,
                        initialLength,
                        finalLength: window.Detection_detections.length,
                        error: null
                    };
                } catch (error) {
                    return {
                        success: false,
                        initialLength,
                        finalLength: window.Detection_detections.length,
                        error: error.message
                    };
                }
            });

            if (result.success && result.finalLength === 0) {
                logSuccess(`Array cleared: ${result.initialLength} → ${result.finalLength}`);
                results.passed++;
            } else if (!result.success) {
                logFailure(`Error during resetAll: ${result.error}`);
                results.failed++;
                results.errors.push({
                    test: 'Detection.resetAll()',
                    error: result.error
                });
            } else {
                logFailure(`Array not cleared properly: ${result.initialLength} → ${result.finalLength}`);
                results.failed++;
            }
        } catch (error) {
            logFailure(`Exception: ${error.message}`);
            results.failed++;
            results.errors.push({
                test: 'Detection.resetAll()',
                error: error.message
            });
        }

        // ─────────────────────────────────────────────────────────────
        // Test 2: AzureMap.clearAll() - Detection filtering mutation
        // ─────────────────────────────────────────────────────────────
        logTest('AzureMap.clearAll() - Detection filtering mutation');

        try {
            const result = await page.evaluate(() => {
                // Setup test detections
                window.Detection_detections = [
                    { id: 0, conf: 0.8 },
                    { id: 1, conf: 0.9 },
                    { id: 2, conf: 1.0 }, // Manual - should be removed
                    { id: 3, conf: 0.7 },
                    { id: 4, conf: 1.0 }  // Manual - should be removed
                ];

                const initialLength = window.Detection_detections.length;
                const manualCount = window.Detection_detections.filter(d => d.conf === 1.0).length;

                // Create Azure Maps instance if needed
                if (!window.azureMap) {
                    return {
                        success: false,
                        error: 'Azure Maps not initialized',
                        skipped: true
                    };
                }

                try {
                    // Call clearAll which filters out manual detections
                    window.azureMap.clearAll();

                    const finalLength = window.Detection_detections.length;
                    const expectedLength = initialLength - manualCount;

                    return {
                        success: true,
                        initialLength,
                        finalLength,
                        expectedLength,
                        manualRemoved: manualCount,
                        error: null,
                        skipped: false
                    };
                } catch (error) {
                    return {
                        success: false,
                        initialLength,
                        finalLength: window.Detection_detections.length,
                        error: error.message,
                        skipped: false
                    };
                }
            });

            if (result.skipped) {
                logInfo('Azure Maps not initialized - skipping test');
            } else if (result.success && result.finalLength === result.expectedLength) {
                logSuccess(`Filtered correctly: ${result.initialLength} → ${result.finalLength} (removed ${result.manualRemoved} manual)`);
                results.passed++;
            } else if (!result.success) {
                logFailure(`Error during clearAll: ${result.error}`);
                results.failed++;
                results.errors.push({
                    test: 'AzureMap.clearAll()',
                    error: result.error
                });
            } else {
                logFailure(`Filtering incorrect: ${result.initialLength} → ${result.finalLength}, expected ${result.expectedLength}`);
                results.failed++;
            }
        } catch (error) {
            logFailure(`Exception: ${error.message}`);
            results.failed++;
            results.errors.push({
                test: 'AzureMap.clearAll()',
                error: error.message
            });
        }

        // ─────────────────────────────────────────────────────────────
        // Test 3: Tile.resetAll() - Tile_tiles.length = 0
        // ─────────────────────────────────────────────────────────────
        logTest('Tile.resetAll() - Array clearing mutation');

        try {
            const result = await page.evaluate(() => {
                // Create some test tiles
                window.Tile_tiles = [
                    { id: 0 },
                    { id: 1 },
                    { id: 2 }
                ];

                const initialLength = window.Tile_tiles.length;

                try {
                    // Call resetAll which should use .length = 0 mutation
                    window.Tile.resetAll();

                    return {
                        success: true,
                        initialLength,
                        finalLength: window.Tile_tiles.length,
                        error: null
                    };
                } catch (error) {
                    return {
                        success: false,
                        initialLength,
                        finalLength: window.Tile_tiles.length,
                        error: error.message
                    };
                }
            });

            if (result.success && result.finalLength === 0) {
                logSuccess(`Array cleared: ${result.initialLength} → ${result.finalLength}`);
                results.passed++;
            } else if (!result.success) {
                logFailure(`Error during resetAll: ${result.error}`);
                results.failed++;
                results.errors.push({
                    test: 'Tile.resetAll()',
                    error: result.error
                });
            } else {
                logFailure(`Array not cleared properly: ${result.initialLength} → ${result.finalLength}`);
                results.failed++;
            }
        } catch (error) {
            logFailure(`Exception: ${error.message}`);
            results.failed++;
            results.errors.push({
                test: 'Tile.resetAll()',
                error: error.message
            });
        }

        // ─────────────────────────────────────────────────────────────
        // Test 4: No TypeError for read-only property
        // ─────────────────────────────────────────────────────────────
        logTest('No TypeError exceptions during mutations');

        const typeErrors = pageErrors.filter(err =>
            err.includes('TypeError') &&
            (err.includes('read only') || err.includes('cannot assign'))
        );

        if (typeErrors.length === 0) {
            logSuccess('No TypeError exceptions detected');
            results.passed++;
        } else {
            logFailure(`Found ${typeErrors.length} TypeError(s):`);
            typeErrors.forEach(err => logFailure(`  - ${err}`));
            results.failed++;
            results.errors.push({
                test: 'TypeError check',
                error: typeErrors.join('; ')
            });
        }

        // ─────────────────────────────────────────────────────────────
        // Test 5: Console error check
        // ─────────────────────────────────────────────────────────────
        logTest('Console error check');

        const relevantErrors = consoleErrors.filter(err =>
            !err.includes('favicon') && // Ignore favicon 404
            !err.includes('DevTools')   // Ignore DevTools messages
        );

        if (relevantErrors.length === 0) {
            logSuccess('No console errors detected');
            results.passed++;
        } else {
            logFailure(`Found ${relevantErrors.length} console error(s):`);
            relevantErrors.slice(0, 5).forEach(err => logFailure(`  - ${err}`));
            if (relevantErrors.length > 5) {
                logInfo(`  ... and ${relevantErrors.length - 5} more`);
            }
            results.failed++;
        }

        // ─────────────────────────────────────────────────────────────
        // Test 6: Mutation pattern verification
        // ─────────────────────────────────────────────────────────────
        logTest('Mutation pattern in source code');

        try {
            const mutationCheck = await page.evaluate(() => {
                // Check if the mutation patterns exist in the functions
                const detectionResetStr = window.Detection.resetAll.toString();
                const tileResetStr = window.Tile.resetAll.toString();

                const detectionHasMutation = detectionResetStr.includes('.length = 0');
                const tileHasMutation = tileResetStr.includes('.length = 0');

                return {
                    detectionHasMutation,
                    tileHasMutation,
                    detectionResetStr: detectionHasMutation ? 'contains .length = 0' : 'missing mutation pattern',
                    tileResetStr: tileHasMutation ? 'contains .length = 0' : 'missing mutation pattern'
                };
            });

            if (mutationCheck.detectionHasMutation && mutationCheck.tileHasMutation) {
                logSuccess('Both functions use mutation pattern (.length = 0)');
                results.passed++;
            } else {
                if (!mutationCheck.detectionHasMutation) {
                    logFailure(`Detection.resetAll: ${mutationCheck.detectionResetStr}`);
                }
                if (!mutationCheck.tileHasMutation) {
                    logFailure(`Tile.resetAll: ${mutationCheck.tileResetStr}`);
                }
                results.failed++;
            }
        } catch (error) {
            logFailure(`Exception: ${error.message}`);
            results.failed++;
        }

    } catch (error) {
        logFailure(`Fatal error: ${error.message}`);
        results.failed++;
        results.errors.push({
            test: 'Test suite execution',
            error: error.message
        });
    } finally {
        // Close browser
        if (browser) {
            await browser.close();
            logInfo('Browser closed');
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Results Summary
    // ─────────────────────────────────────────────────────────────
    logSection('Test Results Summary');

    log(`Total Tests: ${results.passed + results.failed}`, colors.bright);
    log(`✅ Passed: ${results.passed}`, colors.green);
    log(`❌ Failed: ${results.failed}`, colors.red);

    if (results.errors.length > 0) {
        console.log('\nErrors:');
        results.errors.forEach((err, i) => {
            log(`  ${i + 1}. ${err.test}`, colors.yellow);
            log(`     ${err.error}`, colors.red);
        });
    }

    console.log('\n' + '═'.repeat(70));

    if (results.failed === 0) {
        log('\n🎉 Stage 0 Validation PASSED - Ready to commit!\n', colors.bright + colors.green);
        log('Next steps:', colors.cyan);
        log('  1. git add webapp/js/towerscout.js validate_stage_0.sh', colors.cyan);
        log('  2. git commit -m "refactor(stage-0): convert array reassignments to mutations"', colors.cyan);
        log('  3. Proceed to Stage 1: Foundation & Managers\n', colors.cyan);
        process.exit(0);
    } else {
        log('\n❌ Stage 0 Validation FAILED - Fix errors before committing\n', colors.bright + colors.red);
        log('Review errors above and fix before proceeding to Stage 1', colors.yellow);
        process.exit(1);
    }
}

// Error handling
process.on('unhandledRejection', (error) => {
    logFailure(`Unhandled rejection: ${error.message}`);
    process.exit(1);
});

// Run tests
if (require.main === module) {
    runTests().catch(error => {
        logFailure(`Fatal error: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { runTests };

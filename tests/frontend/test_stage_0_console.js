/**
 * Stage 0 Console Test - TASK-038 Frontend Refactoring
 * 
 * Purpose: Verify array mutations work correctly
 * 
 * Usage:
 *   1. Open http://localhost:5000 in your browser
 *   2. Open browser console (F12 → Console tab)
 *   3. Copy and paste this entire script
 *   4. Press Enter
 *   5. Review results
 */

(function () {
    // Clear console if available
    if (typeof console.clear === 'function') {
        console.clear();
    }
    console.log('%c═══════════════════════════════════════════════════════════════════', 'color: #667eea; font-weight: bold');
    console.log('%c  Stage 0 Mutation Tests - Array Reassignment Validation', 'color: #667eea; font-weight: bold; font-size: 16px');
    console.log('%c═══════════════════════════════════════════════════════════════════', 'color: #667eea; font-weight: bold');
    console.log('');

    const results = {
        passed: 0,
        failed: 0,
        errors: []
    };

    function logTest(name, passed, message) {
        const icon = passed ? '✅' : '❌';
        const color = passed ? 'color: #28a745; font-weight: bold' : 'color: #dc3545; font-weight: bold';
        console.log(`%c${icon} Test: ${name}`, color);
        console.log(`   ${message}`);
        console.log('');

        if (passed) {
            results.passed++;
        } else {
            results.failed++;
            results.errors.push({ test: name, error: message });
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Test 1: Detection.resetAll() - Detection_detections.length = 0
    // ─────────────────────────────────────────────────────────────
    try {
        // Save original
        const originalDetections = window.Detection_detections;

        // Create test detections
        window.Detection_detections = [
            { id: 0, conf: 0.8, select: () => { } },
            { id: 1, conf: 0.9, select: () => { } },
            { id: 2, conf: 1.0, select: () => { } }
        ];
        const initialLength = window.Detection_detections.length;

        // Call resetAll
        window.Detection.resetAll();

        const finalLength = window.Detection_detections.length;

        if (finalLength === 0) {
            logTest(
                'Detection.resetAll() - Array clearing',
                true,
                `Array cleared successfully: ${initialLength} → ${finalLength}`
            );
        } else {
            logTest(
                'Detection.resetAll() - Array clearing',
                false,
                `Array not cleared: ${initialLength} → ${finalLength} (expected 0)`
            );
        }

        // Restore original
        window.Detection_detections = originalDetections;
    } catch (error) {
        logTest(
            'Detection.resetAll() - Array clearing',
            false,
            `Error: ${error.message}`
        );
    }

    // ─────────────────────────────────────────────────────────────
    // Test 2: Tile.resetAll() - Tile_tiles.length = 0
    // ─────────────────────────────────────────────────────────────
    try {
        // Save original
        const originalTiles = window.Tile_tiles;

        // Create test tiles
        window.Tile_tiles = [
            { id: 0 },
            { id: 1 },
            { id: 2 }
        ];
        const initialLength = window.Tile_tiles.length;

        // Call resetAll
        window.Tile.resetAll();

        const finalLength = window.Tile_tiles.length;

        if (finalLength === 0) {
            logTest(
                'Tile.resetAll() - Array clearing',
                true,
                `Array cleared successfully: ${initialLength} → ${finalLength}`
            );
        } else {
            logTest(
                'Tile.resetAll() - Array clearing',
                false,
                `Array not cleared: ${initialLength} → ${finalLength} (expected 0)`
            );
        }

        // Restore original
        window.Tile_tiles = originalTiles;
    } catch (error) {
        logTest(
            'Tile.resetAll() - Array clearing',
            false,
            `Error: ${error.message}`
        );
    }

    // ─────────────────────────────────────────────────────────────
    // Test 3: Mutation pattern in Detection.resetAll
    // ─────────────────────────────────────────────────────────────
    try {
        const resetAllStr = window.Detection.resetAll.toString();
        const hasMutation = resetAllStr.includes('.length = 0');

        if (hasMutation) {
            logTest(
                'Detection.resetAll() mutation pattern',
                true,
                'Function contains .length = 0 mutation (correct pattern)'
            );
        } else {
            logTest(
                'Detection.resetAll() mutation pattern',
                false,
                'Function missing .length = 0 pattern (still using reassignment?)'
            );
        }
    } catch (error) {
        logTest(
            'Detection.resetAll() mutation pattern',
            false,
            `Error: ${error.message}`
        );
    }

    // ─────────────────────────────────────────────────────────────
    // Test 4: Mutation pattern in Tile.resetAll
    // ─────────────────────────────────────────────────────────────
    try {
        const resetAllStr = window.Tile.resetAll.toString();
        const hasMutation = resetAllStr.includes('.length = 0');

        if (hasMutation) {
            logTest(
                'Tile.resetAll() mutation pattern',
                true,
                'Function contains .length = 0 mutation (correct pattern)'
            );
        } else {
            logTest(
                'Tile.resetAll() mutation pattern',
                false,
                'Function missing .length = 0 pattern (still using reassignment?)'
            );
        }
    } catch (error) {
        logTest(
            'Tile.resetAll() mutation pattern',
            false,
            `Error: ${error.message}`
        );
    }

    // ─────────────────────────────────────────────────────────────
    // Test 5: AzureMap.clearAll() filtering (if initialized)
    // ─────────────────────────────────────────────────────────────
    if (window.azureMap) {
        try {
            const original = window.Detection_detections;

            window.Detection_detections = [
                { id: 0, conf: 0.8, select: () => { } },
                { id: 1, conf: 0.9, select: () => { } },
                { id: 2, conf: 1.0, select: () => { } }, // Manual
                { id: 3, conf: 0.7, select: () => { } },
                { id: 4, conf: 1.0, select: () => { } }  // Manual
            ];
            const initialLength = window.Detection_detections.length;
            const manualCount = window.Detection_detections.filter(d => d.conf === 1.0).length;

            window.azureMap.clearAll();

            const finalLength = window.Detection_detections.length;
            const expectedLength = initialLength - manualCount;

            if (finalLength === expectedLength) {
                logTest(
                    'AzureMap.clearAll() - Detection filtering',
                    true,
                    `Filtered correctly: ${initialLength} → ${finalLength} (removed ${manualCount} manual detections)`
                );
            } else {
                logTest(
                    'AzureMap.clearAll() - Detection filtering',
                    false,
                    `Wrong count: ${initialLength} → ${finalLength}, expected ${expectedLength}`
                );
            }

            window.Detection_detections = original;
        } catch (error) {
            logTest(
                'AzureMap.clearAll() - Detection filtering',
                false,
                `Error: ${error.message}`
            );
        }
    } else {
        console.log('%c⏭️  Skipped: AzureMap.clearAll() - Azure Maps not initialized', 'color: #ffc107');
        console.log('');
    }

    // ─────────────────────────────────────────────────────────────
    // Test 6: GoogleMap.clearAll() filtering (if initialized)
    // ─────────────────────────────────────────────────────────────
    if (window.googleMap) {
        try {
            const original = window.Detection_detections;

            window.Detection_detections = [
                { id: 0, conf: 0.8, select: () => { } },
                { id: 1, conf: 1.0, select: () => { } }, // Manual
                { id: 2, conf: 0.9, select: () => { } }
            ];
            const initialLength = window.Detection_detections.length;
            const manualCount = window.Detection_detections.filter(d => d.conf === 1.0).length;

            window.googleMap.clearAll();

            const finalLength = window.Detection_detections.length;
            const expectedLength = initialLength - manualCount;

            if (finalLength === expectedLength) {
                logTest(
                    'GoogleMap.clearAll() - Detection filtering',
                    true,
                    `Filtered correctly: ${initialLength} → ${finalLength} (removed ${manualCount} manual detections)`
                );
            } else {
                logTest(
                    'GoogleMap.clearAll() - Detection filtering',
                    false,
                    `Wrong count: ${initialLength} → ${finalLength}, expected ${expectedLength}`
                );
            }

            window.Detection_detections = original;
        } catch (error) {
            logTest(
                'GoogleMap.clearAll() - Detection filtering',
                false,
                `Error: ${error.message}`
            );
        }
    } else {
        console.log('%c⏭️  Skipped: GoogleMap.clearAll() - Google Maps not initialized', 'color: #ffc107');
        console.log('');
    }

    // ─────────────────────────────────────────────────────────────
    // Results Summary
    // ─────────────────────────────────────────────────────────────
    console.log('%c═══════════════════════════════════════════════════════════════════', 'color: #667eea; font-weight: bold');
    console.log('%c  Test Results Summary', 'color: #667eea; font-weight: bold; font-size: 16px');
    console.log('%c═══════════════════════════════════════════════════════════════════', 'color: #667eea; font-weight: bold');
    console.log('');

    const total = results.passed + results.failed;
    console.log(`%cTotal Tests: ${total}`, 'font-weight: bold');
    console.log(`%c✅ Passed: ${results.passed}`, 'color: #28a745; font-weight: bold');
    console.log(`%c❌ Failed: ${results.failed}`, 'color: #dc3545; font-weight: bold');
    console.log('');

    if (results.errors.length > 0) {
        console.log('%cErrors:', 'color: #ffc107; font-weight: bold');
        results.errors.forEach((err, i) => {
            console.log(`%c  ${i + 1}. ${err.test}`, 'color: #ffc107');
            console.log(`%c     ${err.error}`, 'color: #dc3545');
        });
        console.log('');
    }

    console.log('%c═══════════════════════════════════════════════════════════════════', 'color: #667eea; font-weight: bold');

    if (results.failed === 0) {
        console.log('%c🎉 Stage 0 Validation PASSED - Ready to commit!', 'color: #28a745; font-weight: bold; font-size: 18px');
        console.log('');
        console.log('%cNext steps:', 'color: #17a2b8; font-weight: bold');
        console.log('%c  1. git add webapp/js/towerscout.js validate_stage_0.sh', 'color: #17a2b8');
        console.log('%c  2. git commit -m "refactor(stage-0): convert array reassignments to mutations"', 'color: #17a2b8');
        console.log('%c  3. Proceed to Stage 1: Foundation & Managers', 'color: #17a2b8');
    } else {
        console.log('%c❌ Stage 0 Validation FAILED - Fix errors before committing', 'color: #dc3545; font-weight: bold; font-size: 18px');
        console.log('');
        console.log('%cReview errors above and fix before proceeding to Stage 1', 'color: #ffc107');
    }

    console.log('%c═══════════════════════════════════════════════════════════════════', 'color: #667eea; font-weight: bold');
})();

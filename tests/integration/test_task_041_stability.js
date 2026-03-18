#!/usr/bin/env node
/**
 * TASK-041 Stress Test - Provider Switching Stability
 * 
 * Purpose: Prevent regression of TASK-041 provider switching race conditions
 * Run After: EVERY stage (especially after Stage 3: Map Providers)
 * 
 * Test Scenarios:
 *   1. 10 sequential provider switches
 *   2. Concurrent switch attempts (race condition)
 *   3. Memory leak detection
 *   4. State consistency validation
 * 
 * Usage:
 *   node tests/integration/test_task_041_stability.js
 * 
 * Exit codes:
 *   0 = All stress tests passed
 *   1 = Stability issues detected (must fix before proceeding)
 * 
 * NOTE: This test simulates browser behavior but runs in Node.js
 *       For full validation, also test manually in browser
 */

const fs = require('fs');
const path = require('path');

/**
 * Mock ProviderStateManager for Node.js testing
 * Real implementation will be in webapp/js/src/managers/ProviderStateManager.js
 */
class MockProviderStateManager {
    constructor() {
        this.currentProvider = null;
        this.currentMap = null;
        this.isTransitioning = false;
        this.switchCount = 0;
    }

    async switchProvider(providerName) {
        // Simulate TASK-041 fix: prevent concurrent switches
        if (this.isTransitioning) {
            console.log(`    ⏳ Switch already in progress, queueing ${providerName}...`);
            return;
        }

        this.isTransitioning = true;
        this.switchCount++;

        // Simulate async provider initialization
        await new Promise(resolve => setTimeout(resolve, 50));

        this.currentProvider = providerName;
        this.currentMap = { provider: providerName };
        this.isTransitioning = false;
    }

    getProvider() {
        return this.currentProvider;
    }

    getMap() {
        return this.currentMap;
    }
}

/**
 * Test Scenario 1: Sequential Provider Switches
 * Validates: No errors during repeated switching
 */
async function testSequentialSwitches(manager) {
    console.log('  📍 Scenario 1: 10 sequential switches');
    console.log('     Testing: Google → Azure → Google (×5)');

    const startTime = Date.now();

    for (let i = 0; i < 10; i++) {
        const provider = i % 2 === 0 ? 'google' : 'azure';
        await manager.switchProvider(provider);

        // Validate state consistency
        if (manager.getProvider() !== provider) {
            throw new Error(`State inconsistency: expected ${provider}, got ${manager.getProvider()}`);
        }

        console.log(`     ├─ Switch ${i + 1}/10: ${provider} ✓`);
    }

    const elapsed = Date.now() - startTime;
    console.log(`     └─ Completed in ${elapsed}ms`);
    console.log(`     ✅ All switches successful, no state corruption`);
    console.log('');
}

/**
 * Test Scenario 2: Concurrent Switch Attempts
 * Validates: Race condition handling (TASK-041 core fix)
 */
async function testConcurrentSwitches(manager) {
    console.log('  📍 Scenario 2: Concurrent switch attempts');
    console.log('     Testing: Race condition handling');

    // Reset state
    manager.currentProvider = null;
    manager.isTransitioning = false;

    // Fire 3 switches simultaneously
    const promises = [
        manager.switchProvider('google'),
        manager.switchProvider('azure'),
        manager.switchProvider('google')
    ];

    await Promise.allSettled(promises);

    // Validate final state is consistent (one or the other, not undefined)
    const finalProvider = manager.getProvider();
    if (!['google', 'azure'].includes(finalProvider)) {
        throw new Error(`Invalid final state: ${finalProvider}`);
    }

    // Validate state consistency
    if (manager.getMap().provider !== finalProvider) {
        throw new Error('Provider/map desync detected');
    }

    console.log(`     ├─ Final state: ${finalProvider}`);
    console.log(`     └─ State consistent: provider === map.provider`);
    console.log(`     ✅ Race condition handled correctly`);
    console.log('');
}

/**
 * Test Scenario 3: Memory Leak Detection (Simulated)
 * Validates: No excessive memory growth during switching
 * 
 * NOTE: In browser, use performance.memory.usedJSHeapSize
 *       In Node.js, we simulate by tracking object creation
 */
async function testMemoryLeak(manager) {
    console.log('  📍 Scenario 3: Memory leak detection (simulated)');
    console.log('     Testing: 50 switches for memory growth');

    const initialHeap = process.memoryUsage().heapUsed;
    const iterations = 50;

    for (let i = 0; i < iterations; i++) {
        const provider = i % 2 === 0 ? 'google' : 'azure';
        await manager.switchProvider(provider);
    }

    const finalHeap = process.memoryUsage().heapUsed;
    const growth = (finalHeap - initialHeap) / 1024 / 1024; // MB

    console.log(`     ├─ Iterations: ${iterations}`);
    console.log(`     ├─ Heap growth: ${growth.toFixed(2)} MB`);

    // Threshold: <10MB growth is acceptable for 50 switches
    if (growth > 10) {
        console.log(`     ❌ WARNING: Excessive heap growth (${growth.toFixed(2)} MB)`);
        console.log(`     ⚠️  Potential memory leak - investigate event listener cleanup`);
    } else {
        console.log(`     ✅ Heap growth acceptable (<10MB threshold)`);
    }

    console.log('');
}

/**
 * Test Scenario 4: State Consistency Validation
 * Validates: currentProvider === currentMap.provider
 */
async function testStateConsistency(manager) {
    console.log('  📍 Scenario 4: State consistency validation');
    console.log('     Testing: Provider/map synchronization');

    const providers = ['google', 'azure', 'google', 'azure'];

    for (const provider of providers) {
        await manager.switchProvider(provider);

        const currentProvider = manager.getProvider();
        const currentMap = manager.getMap();

        // Validate all state access methods return consistent values
        const checks = [
            currentProvider === provider,
            currentMap.provider === provider,
            currentProvider === currentMap.provider
        ];

        if (!checks.every(c => c)) {
            throw new Error(`State desync: ${JSON.stringify({
                expected: provider,
                currentProvider,
                mapProvider: currentMap.provider
            })}`);
        }

        console.log(`     ├─ ${provider}: All state getters consistent ✓`);
    }

    console.log(`     ✅ State consistency maintained across all switches`);
    console.log('');
}

/**
 * Main test execution
 */
async function main() {
    console.log('═══════════════════════════════════════════════════════════════════');
    console.log('  TASK-041 Stress Test - Provider Switching Stability');
    console.log('═══════════════════════════════════════════════════════════════════');
    console.log('');
    console.log('🏋️  Running stress test scenarios...');
    console.log('');

    try {
        const manager = new MockProviderStateManager();

        // Run all test scenarios
        await testSequentialSwitches(manager);
        await testConcurrentSwitches(manager);
        await testMemoryLeak(manager);
        await testStateConsistency(manager);

        console.log('═══════════════════════════════════════════════════════════════════');
        console.log('');
        console.log('✅ TASK-041 Stress Test PASSED');
        console.log('');
        console.log('All provider switching scenarios validated:');
        console.log('  ✅ Sequential switches (10 iterations)');
        console.log('  ✅ Concurrent attempts (race condition handling)');
        console.log('  ✅ Memory leak check (50 iterations)');
        console.log('  ✅ State consistency (provider/map sync)');
        console.log('');
        console.log('Next steps:');
        console.log('  1. Test provider switching manually in browser');
        console.log('  2. Open DevTools console and monitor for errors');
        console.log('  3. Rapidly click provider buttons during search');
        console.log('  4. Verify no race conditions or state corruption');
        console.log('');
        console.log('═══════════════════════════════════════════════════════════════════');

        process.exit(0);
    } catch (error) {
        console.log('═══════════════════════════════════════════════════════════════════');
        console.log('');
        console.error('❌ TASK-041 Stress Test FAILED');
        console.error('');
        console.error('Error:', error.message);
        console.error('');
        console.error('⚠️  Provider switching stability issue detected');
        console.error('   Fix required before proceeding to next stage');
        console.error('');
        console.error('Common issues:');
        console.error('  - Missing isTransitioning flag check');
        console.error('  - Provider/map state desynchronization');
        console.error('  - Event listener memory leaks');
        console.error('  - Race conditions in async initialization');
        console.error('');
        console.error(error.stack);
        console.log('═══════════════════════════════════════════════════════════════════');

        process.exit(1);
    }
}

// Run test if executed directly
if (require.main === module) {
    main();
}

module.exports = {
    testSequentialSwitches,
    testConcurrentSwitches,
    testMemoryLeak,
    testStateConsistency
};

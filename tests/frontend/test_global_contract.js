#!/usr/bin/env node
/**
 * Global Contract Test - TASK-038 Frontend Refactoring
 * 
 * Purpose: Validate all inline HTML handler targets exist in window namespace
 * Run After: EVERY stage (1, 2, 3, 4, 5) - NOT just Stage 5
 * 
 * Validates: onclick="..." and onkeydown="..." handlers in towerscout.html
 * 
 * Usage:
 *   node tests/frontend/test_global_contract.js
 * 
 * Exit codes:
 *   0 = All targets validated successfully
 *   1 = Missing targets found (must fix before next stage)
 */

const fs = require('fs');
const path = require('path');

// Configuration
const TEMPLATE_PATH = path.join(__dirname, '../../webapp/templates/towerscout.html');

/**
 * Parse HTML template for inline event handlers
 * Handles both double and single quotes (FIX #4 v2.4)
 * 
 * Examples:
 *   onclick="cancelRequest()"
 *   onclick='getObjects(true)'
 *   onkeydown="if (event.keyCode == 13) { Detection.number(); }"
 */
function parseTemplateHandlers(htmlPath) {
    if (!fs.existsSync(htmlPath)) {
        throw new Error(`Template not found: ${htmlPath}`);
    }

    const html = fs.readFileSync(htmlPath, 'utf8');
    const handlers = new Set();

    // Match both onclick="..." and onclick='...'
    // FIX #4 v2.4: Template uses both quote styles
    const handlerRegex = /on(?:click|keydown|change)=(["'])([^"']+)\1/g;

    let match;
    while ((match = handlerRegex.exec(html)) !== null) {
        const code = match[2]; // Captured handler code

        // Extract function calls: functionName(...) or object.method(...)
        // Matches: cancelRequest(), Detection.prev(), currentMap.addShapes()
        const funcRegex = /([\w\.]+)\s*\(/g;
        let funcMatch;

        while ((funcMatch = funcRegex.exec(code)) !== null) {
            const target = funcMatch[1];

            // Skip built-in JavaScript keywords
            if (!['if', 'for', 'while', 'return', 'var', 'let', 'const'].includes(target)) {
                handlers.add(target);
            }
        }
    }

    return Array.from(handlers).sort();
}

/**
 * Validate that all handler targets exist in window namespace
 * Simulates browser window object for testing
 */
function validateGlobalContract(requiredGlobals) {
    console.log('═══════════════════════════════════════════════════════════════════');
    console.log('  Global Contract Validation - TASK-038');
    console.log('═══════════════════════════════════════════════════════════════════');
    console.log('');
    console.log(`📄 Template: ${path.relative(process.cwd(), TEMPLATE_PATH)}`);
    console.log(`🔍 Validating ${requiredGlobals.length} global handler targets...`);
    console.log('');

    // Display all required targets
    console.log('Required window exposures:');
    requiredGlobals.forEach(target => {
        console.log(`  - window.${target}`);
    });
    console.log('');

    // NOTE: This is a structural validation test
    // It does NOT load towerscout.js in Node.js (browser code won't run)
    // Instead, it checks that your globals.js exports ALL required targets

    console.log('⚠️  NOTE: This test validates STRUCTURE only');
    console.log('   For runtime validation:');
    console.log('   1. Load application in browser');
    console.log('   2. Open DevTools console');
    console.log('   3. Manually test each handler function');
    console.log('');

    // Read globals.js to verify exports
    const globalsPath = path.join(__dirname, '../../webapp/js/src/globals.js');

    if (fs.existsSync(globalsPath)) {
        console.log('✅ globals.js found - checking window exposures...');
        const globalsContent = fs.readFileSync(globalsPath, 'utf8');

        const missingFromGlobals = [];
        for (const target of requiredGlobals) {
            // Check if target is exposed via window.X = pattern
            const pattern = new RegExp(`window\\.${target.replace(/\./g, '\\.')}\\s*=`);
            if (!pattern.test(globalsContent)) {
                missingFromGlobals.push(target);
            }
        }

        if (missingFromGlobals.length > 0) {
            console.error('');
            console.error('❌ MISSING from globals.js:');
            missingFromGlobals.forEach(t => console.error(`   - window.${t}`));
            console.error('');
            console.error('⚠️  Add these exposures to globals.js before next stage');
            return false;
        } else {
            console.log('✅ All required targets found in globals.js');
        }
    } else {
        console.log('⚠️  globals.js not found (expected in Stage 1+)');
        console.log('   This is normal for Stage 0');
    }

    console.log('');
    console.log('═══════════════════════════════════════════════════════════════════');
    console.log('');
    console.log('✅ Global Contract Validation PASSED');
    console.log('');
    console.log('Next steps:');
    console.log('  1. Load application in browser');
    console.log('  2. Test all inline handlers manually');
    console.log('  3. Check console for errors');
    console.log('  4. Verify all UI interactions work');
    console.log('');
    console.log('═══════════════════════════════════════════════════════════════════');

    return true;
}

/**
 * Main test execution
 */
function main() {
    try {
        const requiredGlobals = parseTemplateHandlers(TEMPLATE_PATH);
        const success = validateGlobalContract(requiredGlobals);

        if (success) {
            process.exit(0);
        } else {
            console.error('❌ Global contract validation FAILED');
            console.error('   Fix missing window exposures before next stage');
            process.exit(1);
        }
    } catch (error) {
        console.error('');
        console.error('❌ TEST ERROR:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Run test if executed directly
if (require.main === module) {
    main();
}

module.exports = { parseTemplateHandlers, validateGlobalContract };

#!/usr/bin/env node
/**
 * Global Contract Test - TASK-038 Frontend Refactoring
 *
 * Purpose: Validate inline HTML handler targets map to real root globals in
 * the modular frontend source tree.
 *
 * Usage:
 *   node tests/frontend/test_global_contract.js
 *
 * Exit codes:
 *   0 = All targets validated successfully
 *   1 = Missing targets found
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '../..');
const TEMPLATE_PATH = path.join(ROOT, 'webapp/templates/towerscout.html');
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

/**
 * Parse HTML template for inline event handlers.
 * Handles both double and single quotes.
 */
function parseTemplateHandlers(htmlPath) {
    if (!fs.existsSync(htmlPath)) {
        throw new Error(`Template not found: ${htmlPath}`);
    }

    const html = fs.readFileSync(htmlPath, 'utf8');
    const handlers = new Set();
    const handlerRegex = /on(?:click|keydown|change)=(["'])([^"']+)\1/g;

    let match;
    while ((match = handlerRegex.exec(html)) !== null) {
        const code = match[2];
        const funcRegex = /([\w\.]+)\s*\(/g;
        let funcMatch;

        while ((funcMatch = funcRegex.exec(code)) !== null) {
            const target = funcMatch[1];

            if (!['if', 'for', 'while', 'return', 'var', 'let', 'const'].includes(target)) {
                handlers.add(target);
            }
        }
    }

    return Array.from(handlers).sort();
}

function getRequiredRoots(requiredGlobals) {
    return Array.from(new Set(requiredGlobals.map(target => target.split('.')[0]))).sort();
}

function sourceDefinesRoot(rootName, sourceFiles) {
    const escaped = rootName.replace(/\./g, '\\.');
    const assignmentPattern = new RegExp(`window\\.${escaped}\\s*=`);
    const definePropertyPattern = new RegExp(`Object\\.defineProperty\\(window,\\s*['"]${escaped}['"]`);

    return sourceFiles.some(filePath => {
        const content = fs.readFileSync(filePath, 'utf8');
        return assignmentPattern.test(content) || definePropertyPattern.test(content);
    });
}

function validateGlobalContract(requiredGlobals) {
    const requiredRoots = getRequiredRoots(requiredGlobals);
    const sourceFiles = listSourceFiles(SRC_ROOT);

    console.log('Global Contract Validation');
    console.log(`Template: ${path.relative(process.cwd(), TEMPLATE_PATH)}`);
    console.log(`Handler targets: ${requiredGlobals.length}`);
    console.log(`Root globals: ${requiredRoots.length}`);

    const missingRoots = requiredRoots.filter(root => !sourceDefinesRoot(root, sourceFiles));

    if (missingRoots.length > 0) {
        console.error('Missing root globals:');
        missingRoots.forEach(root => console.error(` - window.${root}`));
        return false;
    }

    console.log('Global contract validation PASSED');
    return true;
}

function main() {
    try {
        const requiredGlobals = parseTemplateHandlers(TEMPLATE_PATH);
        const success = validateGlobalContract(requiredGlobals);

        if (success) {
            process.exit(0);
        }

        console.error('Global contract validation FAILED');
        process.exit(1);
    } catch (error) {
        console.error('TEST ERROR:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    getRequiredRoots,
    parseTemplateHandlers,
    sourceDefinesRoot,
    validateGlobalContract
};

#!/bin/bash
# Stage 0 Validation Script - TASK-038 Frontend Refactoring
# 
# Purpose: Verify all array reassignments converted to mutations
# Required: Must pass before proceeding to Stage 1 (getter-only pattern)
#
# Usage: bash validate_stage_0.sh

set -e

TARGET_FILE="webapp/js/towerscout.js"
ERRORS=0

echo "═══════════════════════════════════════════════════════════════════"
echo "  Stage 0 Validation - Array Mutation Refactoring"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "📄 Target: $TARGET_FILE"
echo ""

# Check file exists
if [ ! -f "$TARGET_FILE" ]; then
  echo "❌ ERROR: $TARGET_FILE not found"
  exit 1
fi

echo "🔍 Checking for remaining array reassignments..."
echo ""

# ─────────────────────────────────────────────────────────────
# Check 1: Detection_detections reassignments
# ─────────────────────────────────────────────────────────────
echo "  📍 Check 1: Detection_detections reassignments"

# Exclude variable declarations (let/const/var)
DET_COUNT=$(grep "Detection_detections = " "$TARGET_FILE" | grep -v "^\s*let\s" | grep -v "^\s*const\s" | grep -v "^\s*var\s" | wc -l 2>/dev/null || true)

if [ "$DET_COUNT" -ne 0 ]; then
  echo "     ❌ FAILED: Found $DET_COUNT reassignment(s)"
  echo "     Locations:"
  grep -n "Detection_detections = " "$TARGET_FILE" | grep -v "let\|const\|var" | sed 's/^/        /'
  echo ""
  echo "     Expected: Detection_detections.length = 0; ..."
  echo "     Found: Detection_detections = ..."
  echo ""
  ERRORS=$((ERRORS + 1))
else
  echo "     ✅ PASSED: 0 reassignments found"
fi

# ─────────────────────────────────────────────────────────────
# Check 2: Tile_tiles reassignments
# ─────────────────────────────────────────────────────────────
echo "  📍 Check 2: Tile_tiles reassignments"

# Exclude variable declarations (let/const/var)
TILE_COUNT=$(grep "Tile_tiles = " "$TARGET_FILE" | grep -v "^\s*let\s" | grep -v "^\s*const\s" | grep -v "^\s*var\s" | wc -l 2>/dev/null || true)

if [ "$TILE_COUNT" -ne 0 ]; then
  echo "     ❌ FAILED: Found $TILE_COUNT reassignment(s)"
  echo "     Locations:"
  grep -n "Tile_tiles = " "$TARGET_FILE" | grep -v "let\|const\|var" | sed 's/^/        /'
  echo ""
  echo "     Expected: Tile_tiles.length = 0;"
  echo "     Found: Tile_tiles = ..."
  echo ""
  ERRORS=$((ERRORS + 1))
else
  echo "     ✅ PASSED: 0 reassignments found"
fi

echo ""
echo "🔍 Verifying mutation patterns exist..."
echo ""

# ─────────────────────────────────────────────────────────────
# Check 3: Detection_detections mutations
# ─────────────────────────────────────────────────────────────
echo "  📍 Check 3: Detection_detections mutations"

# Search for .length = 0 pattern (array clearing)
DET_MUT=$(grep -c "Detection_detections\.length = 0" "$TARGET_FILE" 2>/dev/null || true)

# We expect at least 3 mutations (locations 1, 2, 3 from design doc)
if [ "$DET_MUT" -lt 3 ]; then
  echo "     ❌ FAILED: Expected 3+ mutations, found $DET_MUT"
  echo "     Showing .length = 0 occurrences:"
  grep -n "Detection_detections\.length = 0" "$TARGET_FILE" | sed 's/^/        /' || echo "        (none found)"
  echo ""
  echo "     Expected pattern:"
  echo "        Detection_detections.length = 0;  // Clear array"
  echo "        for (const det of dets) {"
  echo "          Detection_detections.push(det);"
  echo "        }"
  echo ""
  ERRORS=$((ERRORS + 1))
else
  echo "     ✅ PASSED: $DET_MUT mutation(s) found"
fi

# ─────────────────────────────────────────────────────────────
# Check 4: Tile_tiles mutations
# ─────────────────────────────────────────────────────────────
echo "  📍 Check 4: Tile_tiles mutations"

TILE_MUT=$(grep -c "Tile_tiles\.length = 0" "$TARGET_FILE" 2>/dev/null || true)

# We expect at least 1 mutation (location 4 from design doc)
if [ "$TILE_MUT" -lt 1 ]; then
  echo "     ❌ FAILED: Expected 1+ mutation, found $TILE_MUT"
  echo "     Showing .length = 0 occurrences:"
  grep -n "Tile_tiles\.length = 0" "$TARGET_FILE" | sed 's/^/        /' || echo "        (none found)"
  echo ""
  echo "     Expected pattern:"
  echo "        Tile_tiles.length = 0;  // Clear array"
  echo ""
  ERRORS=$((ERRORS + 1))
else
  echo "     ✅ PASSED: $TILE_MUT mutation(s) found"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"

# Summary
if [ $ERRORS -eq 0 ]; then
  echo ""
  echo "🎉 Stage 0 Validation PASSED"
  echo ""
  echo "✅ All array reassignments converted to mutations"
  echo "✅ Codebase ready for Stage 1 (getter-only pattern)"
  echo ""
  echo "Next steps:"
  echo "  1. Run full application workflow (search → detect → review)"
  echo "  2. Verify detection list updates correctly"
  echo "  3. Verify tile list updates correctly"
  echo "  4. Check console for errors"
  echo "  5. Commit Stage 0 changes"
  echo "  6. Proceed to Stage 1: Foundation & Managers"
  echo ""
  echo "═══════════════════════════════════════════════════════════════════"
  exit 0
else
  echo ""
  echo "❌ Stage 0 Validation FAILED: $ERRORS error(s)"
  echo ""
  echo "⚠️  DO NOT PROCEED TO STAGE 1"
  echo ""
  echo "Fix all array reassignments before continuing:"
  echo "  - Replace 'Detection_detections = X' with mutations"
  echo "  - Replace 'Tile_tiles = X' with mutations"
  echo ""
  echo "Mutation pattern:"
  echo "  // BEFORE (reassignment)"
  echo "  Detection_detections = newArray;"
  echo ""
  echo "  // AFTER (mutation)"
  echo "  Detection_detections.length = 0;"
  echo "  for (const item of newArray) {"
  echo "    Detection_detections.push(item);"
  echo "  }"
  echo ""
  echo "═══════════════════════════════════════════════════════════════════"
  exit 1
fi

#!/bin/bash
# Validate ACTIVE design document for stale/banned patterns
# v2.6: Excludes historical archive from validation (self-referential fix)

DOC=".agent_work/design-task-038-revised.md"
ARCHIVE=".agent_work/design-task-038-revision-history.md"
ERRORS=0

echo "🔍 Validating design document for stale code patterns..."
echo "  📄 Target: $DOC (ACTIVE SPEC ONLY)"
echo "  📦 Excluded: $ARCHIVE (historical archive)"
echo ""

# NOTE: This script validates ONLY the active execution spec.
# Historical archive may contain banned patterns for educational purposes.
# The script itself is embedded in the doc but uses placeholder descriptions
# to avoid triggering false positives during grep searches.

# Check 1: No url_for references (actual template uses direct paths)
echo "  📍 Check 1: No url_for references"
PATTERN1="url_for\\('static'"
if grep -q "$PATTERN1" "$DOC"; then
  echo "    ❌ FAILED: Found url_for references (should be /js/towerscout.js)"
  grep -n "$PATTERN1" "$DOC"
  ERRORS=$((ERRORS + 1))
else
  echo "    ✅ PASSED: No url_for references"
fi

# Check 2: No _currentProvider or _currentMap backing fields  
echo "  📍 Check 2: No _currentProvider/_currentMap references"
PATTERN2="window\\._current"
if grep -q "$PATTERN2" "$DOC"; then
  echo "    ❌ FAILED: Found backing fields (should use providerManager)"
  grep -n "$PATTERN2" "$DOC"
  ERRORS=$((ERRORS + 1))
else
  echo "    ✅ PASSED: No backing field references"
fi

# Check 3: No setProvider or setMap method calls (API doesn't have these)
echo "  📍 Check 3: No setProvider/setMap method calls"
PATTERN3="setProvider\\(\\|setMap\\("
if grep -q "$PATTERN3" "$DOC"; then
  echo "    ❌ FAILED: Found setter methods (should use direct property assignment)"
  grep -n "$PATTERN3" "$DOC"
  ERRORS=$((ERRORS + 1))
else
  echo "    ✅ PASSED: No setter method calls"
fi

# Check 4: No non-existent endpoints (use descriptive placeholders)
echo "  📍 Check 4: No non-existent endpoints"
declare -a BANNED=(
  "ENDPOINT_TILES"
  "ENDPOINT_DETECT"  
  "ENDPOINT_CANCEL"
  "ENDPOINT_GEOCODE"
  "ENDPOINT_VALIDATE_ZIPCODE"
)

# Build actual patterns dynamically to avoid embedding them literally
FOUND=0
for key in "${BANNED[@]}"; do
  case $key in
    ENDPOINT_TILES) pattern="TILES.*'/tiles'" ;;
    ENDPOINT_DETECT) pattern="DETECT.*'/detect'" ;;
    ENDPOINT_CANCEL) pattern="CANCEL.*'/cancel'" ;;
    ENDPOINT_GEOCODE) pattern="GEOCODE.*'/geocode'" ;;
    ENDPOINT_VALIDATE_ZIPCODE) pattern="ZIPCODE_VALIDATE.*'/validate_zipcode'" ;;
  esac
  
  if grep -q "$pattern" "$DOC"; then
    echo "    ❌ FAILED: Found non-existent endpoint pattern: $key"
    grep -n "$pattern" "$DOC"
    FOUND=1
    ERRORS=$((ERRORS + 1))
  fi
done

if [ $FOUND -eq 0 ]; then
  echo "    ✅ PASSED: No non-existent endpoints"
fi

# Check 5: Route references use /js/ not /static/js/
echo "  📍 Check 5: Route references use /js/ (not /static/js/)"  
PATTERN5="/static/js/towerscout\\.js"
if grep -q "$PATTERN5" "$DOC"; then
  echo "    ❌ FAILED: Found /static/js/ path (should be /js/)"
  grep -n "$PATTERN5" "$DOC"
  ERRORS=$((ERRORS + 1))
else
  echo "    ✅ PASSED: Correct route paths"
fi

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
  echo "🎉 All validation checks PASSED"
  echo "Design document is free of stale code patterns"
  exit 0
else
  echo "❌ Validation FAILED: $ERRORS error(s) found"
  echo "Fix stale code patterns before implementation"
  exit 1
fi

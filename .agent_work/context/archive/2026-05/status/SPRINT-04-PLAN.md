# Sprint 04 Plan - Setup Wizard & Code Quality

**Sprint Period**: March 19 - April 4, 2026 (16 days extended)  
**Planning Date**: March 18, 2026  
**Updated Through**: April 1, 2026  
**Sprint Focus**: User Experience Improvements + Code Quality  
**Target Capacity**: 60-75 hours (accommodating additional scope)

---

## 🎯 Sprint Objectives

### Primary Goal
Deliver the Setup Wizard & Settings Screen (TASK-046) to eliminate manual .env editing and provide seamless configuration management.

### Secondary Goals
1. Investigate ISSUE-003 performance with large datasets (discovery phase)
2. Improve application polish through UI formatting updates
3. Simplify console logging for better end-user experience
4. Complete a full-repo stale code and performance audit
5. Clean up legacy code from refactoring efforts using audited findings

---

## Updated Remaining Sequence

**Current sequencing status** (synced April 1, 2026):

1. [x] **TASK-048** - reduced logging/profiling noise and landed debug-mode console gating
2. [x] **ISSUE-003 Follow-Up: Performance Quick Wins** - implemented the bounded, low-risk items from `FURTHER-PERFORMANCE-IMPROVEMENT-INVESTIGATION.md`
3. [x] **TASK-049** - executed the validated low-risk cleanup batch from TASK-050 plus follow-on stale-surface/archive work
4. [ ] **TASK-047** - UI polish remains the only in-sprint implementation task if Sprint 04 resumes before Sprint 05 prep

**Rationale**:
- the further performance investigation recommends removing profiling noise first, then landing quick wins before broader refactors
- TASK-048 already owns the deferred “debug mode gates verbose browser console output” follow-up from TASK-046
- the larger performance ideas remain intentionally deferred until fresh measured profiles exist

---

## 📋 Sprint 04 Tasks

### **Core Feature Development**

#### **TASK-046: Setup Wizard and Settings Screen** ✅ CRITICAL
**Status**: COMPLETED  
**Type**: B (Feature Development)  
**Priority**: CRITICAL  
**Estimated Effort**: 40-50 hours (5-7 days with testing)

**Objective**: Implement first-launch Setup Wizard and in-app Settings Screen for seamless API key management

**Key Features**:
- 🔑 API Key Management (validate and save without text editor)
- 🚀 First-Launch Setup Wizard (guided multi-step flow)
- ⚙️ Settings Modal (in-app configuration updates)
- 🐳 Docker Compatible (host-mounted .env updates)
- 📊 Performance Metrics Display (recent detection stats)
- 🔧 System Controls (debug mode, cache clearing)

**Completion Summary** (March 23, 2026):
- Delivered degraded setup-required boot mode with first-launch setup wizard and in-app settings management
- Implemented `webapp/ts_config.py` plus `/api/config/validate-key`, `/api/config/save-keys`, `/api/config/status`, `/api/config/reset-session`, and `/api/config/performance`
- Delivered frontend modules as `webapp/js/src/setup-wizard.js` and `webapp/js/src/settings.js` within the existing build structure
- Resolved runtime regressions around provider initialization, Azure-only validation, save debouncing, TLS fallback, and single-provider post-setup loading
- Fixed performance-metrics parsing against the real `performance.log` format and hardened secret handling around startup logging and config artifacts
- Deferred the broader “debug mode enables verbose console logging” behavior to TASK-048 while keeping debug-preference persistence in TASK-046

**Implementation Phases**:

**Phase 0: Discovery & Planning (4-6 hours)**
- Review .env management patterns in codebase
- Design backup/rollback strategy for configuration safety
- Validate `python-dotenv` capabilities for dynamic updates
- Identify Flask session requirements for wizard state
- Document technical approach and decision points

**Phase 1: Backend Configuration Module (8-12 hours)**
- Create `ts_config.py` module with ConfigManager class
- Implement .env read/write/validate operations
- Add backup/rollback mechanisms (`.env.backup` timestamped files)
- Implement validation functions for API keys (test requests)
- Create 5 new Flask endpoints:
  - `GET /api/config/status` - Check current configuration state
  - `POST /api/config/validate-key` - Test provider key connectivity
  - `POST /api/config/save-keys` - Write API keys to `.env` with backup
  - `GET /api/config/performance` - Return recent detection metrics
  - `POST /api/config/reset-session` - Clear session and temporary files

**Phase 2: Setup Wizard UI (12-16 hours)**
- Create `webapp/js/src/setup-wizard.js` module
- Implement multi-step wizard flow:
  1. Welcome screen with purpose explanation
  2. API Keys input with validation
  3. Provider selection (Google vs Azure)
  4. Information/tips screen
  5. Completion confirmation
- Add API key validation with visual feedback (<5 seconds)
- Create progress indicator and navigation controls
- Implement blocking behavior (no skip until configuration complete)
- Add setup wizard modal to `webapp/templates/towerscout.html`
- Integrate wizard into `towerscout.py` application startup

**Phase 3: Settings Screen (8-12 hours)**
- Create `webapp/js/src/settings.js` module
- Modal overlay with tabs:
  - **API Keys**: Update provider keys with validation
  - **Performance**: Display recent detection metrics
  - **System**: Cache clearing, debug mode controls
- Provider switching and API key update forms
- Settings persistence via `/api/config/save-keys` endpoint
- Reload configuration without server restart (or show restart message)
- Add settings button to main navigation in `webapp/templates/towerscout.html`

**Phase 4: Testing & Validation (8-12 hours)**
- Integration testing: Complete setup wizard flow
- Settings modal update testing
- API key validation with invalid/valid keys
- Backup/rollback functionality validation
- Edge case testing: Corrupted .env, network failures, permission errors
- User acceptance testing: First-time user experience walkthrough
- Cross-browser testing: Chrome, Firefox, Edge, Safari
- Performance validation: API validation <5s, settings responsiveness <200ms

**Phase 5: Documentation (2-4 hours)**
- Update copilot-instructions.md with new configuration system
- Create user guide for setup wizard and settings screen
- Document .env file format and validation rules
- Update Docker deployment guide (preparation for Sprint 5)

**Success Criteria**:
- [x] Setup wizard blocks application until valid API keys configured
- [x] Users can update API keys via settings without editing files
- [x] API key validation provides clear feedback within 5 seconds
- [x] .env file changes persist with backup/rollback safety
- [x] Zero blocking regressions found in setup/settings runtime flows during TASK-046 closeout
- [ ] Cross-browser compatibility verified
- [x] TASK-046 accepted as complete with the verbose debug-log gating scope explicitly handed off to TASK-048

**Dependencies**:
- ✅ TASK-001 (API Key Security) - COMPLETED (Sprint 01)
- ✅ Error handling system (`ts_errors.py`) - COMPLETED (Sprint 02)
- ✅ Validation utilities (`ts_validation.py`) - COMPLETED (Sprint 02)
- ✅ Frontend modular architecture - COMPLETED (Sprint 03)

**Files to Create**:
- `webapp/ts_config.py` - Configuration management module
- `webapp/js/src/setup-wizard.js` - Setup wizard component
- `webapp/js/src/settings.js` - Settings modal component

**Files to Modify**:
- `webapp/towerscout.py` - Add setup wizard route and configuration check
- `webapp/templates/towerscout.html` - Add settings button and modal container
- `webapp/build.js` - Add new modules to build pipeline
- `.github/copilot-instructions.md` - Document new configuration system

---

### **Performance & Stability**

#### **ISSUE-003: Large Dataset Performance Investigation** 🟡
**Status**: COMPLETED (discovery + targeted Azure fix)  
**Type**: A (Performance - Discovery Phase)  
**Priority**: MEDIUM  
**Estimated Effort**: 2-4 hours (investigation only)

**Objective**: Benchmark performance with 500+ detections and identify optimization opportunities

**Investigation Plan**:
1. **Create Test Dataset** (30 minutes)
   - Generate or collect dataset with 500+ detections
   - Include mix of ML detections and manual towers
   - Vary confidence levels and geographic distribution

2. **Performance Profiling** (1.5-2 hours)
   - Profile detection list rendering performance
   - Profile map marker rendering (Google & Azure Maps)
   - Measure map interaction responsiveness (pan, zoom)
   - Test provider switching with large datasets
   - Document baseline metrics with timestamps

3. **Bottleneck Identification** (30-60 minutes)
   - Analyze browser DevTools performance profiles
   - Identify DOM manipulation bottlenecks
   - Check for memory leaks or excessive reflows
   - Review JavaScript execution time hotspots

4. **Recommendations Report** (30 minutes)
   - Document findings in `.agent_work/context/analysis/ISSUE-003-PERFORMANCE-INVESTIGATION.md`
   - Provide go/no-go recommendation for optimization work
   - Estimate effort for identified improvements
   - Prioritize quick wins vs. major refactoring

**Go/No-Go Criteria**:
- **GO** (implement fixes): Detection list rendering >5 seconds with 500 items
- **NO-GO** (defer to Sprint 5): Acceptable performance, document for future reference

**Potential Optimization Areas** (if investigation warrants):
- Virtual scrolling for detection list (1-2 hours implementation)
- Map marker clustering for dense areas (2-3 hours implementation)
- Lazy loading of detection details (1-2 hours implementation)
- Debouncing of map events (30 minutes implementation)

---

#### **ISSUE-003 Follow-Up: Performance Quick Wins** 🟡
**Status**: COMPLETED  
**Type**: A (Performance Quick Wins)  
**Priority**: MEDIUM-HIGH  
**Estimated Effort**: 3-6 hours

**Objective**: Implement the lowest-risk, highest-signal performance wins from `FURTHER-PERFORMANCE-IMPROVEMENT-INVESTIGATION.md` without opening a broad new optimization initiative.

**Completion Summary** (March 31, 2026):
- Gated `ts_en.py` secondary-classifier debug image dumps behind `TOWERSCOUT_SAVE_EN_DEBUG_IMAGES`
- Collapsed redundant large-result hydration / visibility-update passes in the frontend
- Stopped allocating provider overlay objects for metadata-only tile records by default
- Completed code/build validation plus live browser confirmation of the updated detection flow

**Sequencing Decision**:
- Execute immediately after TASK-048
- Keep scope to quick wins only
- Defer bigger backend/rendering refactors until after fresh phase timings and browser profiles exist

**Initial Scope**:
- Gate or remove `ts_en.py` debug image writes from the normal detection path
- Remove duplicate frontend hydration/visibility passes
- Stop creating provider overlay objects for metadata-only tile records unless review mode actually needs them

**Deferred Until Measured**:
- Async or batched geocoding redesign
- Shared imagery cache for detection downloads
- Clustering, viewport culling, or canvas/WebGL overlay work

**Success Criteria**:
- [x] Debug-only image writes no longer run in the default detection workflow
- [x] Initial large-result hydration avoids redundant visibility/update passes
- [x] Metadata-only tile objects no longer allocate unnecessary provider overlays by default
- [ ] No regressions in search, review, export, or manual tower workflows (left unchecked because the recorded smoke signoff covered the updated detection flow, but not the full workflow matrix)

---

### **Code Quality Improvements**

#### **TASK-047: UI Formatting and Polish** 🟢
**Status**: NOT_STARTED  
**Type**: A (UI/UX Polish)  
**Priority**: MEDIUM  
**Estimated Effort**: 4-8 hours

**Objective**: Implement UI formatting improvements and visual consistency updates

**Sequencing Note**:
- Defer until after TASK-048 and the ISSUE-003 quick-win tranche
- Avoid polishing around rendering/stability paths that are still likely to change

**Scope** (to be defined collaboratively):
- Layout adjustments and spacing improvements
- Typography and font sizing consistency
- Color scheme refinements
- Button styling and visual hierarchy
- Responsive design touch-ups
- Icon and imagery updates
- Loading states and transitions

**Implementation Approach**:
1. **Discovery Session** (1 hour)
   - Review current UI with user
   - Identify specific areas for improvement
   - Prioritize changes by impact and effort
   - Create detailed task list

2. **Implementation** (2-5 hours)
   - Apply CSS updates to `webapp/css/ts_styles.css`
   - Modify HTML templates as needed
   - Test across different screen sizes
   - Validate cross-browser consistency

3. **Review & Refinement** (1-2 hours)
   - User review of changes
   - Iterative adjustments based on feedback
   - Final polish and edge case handling

**Files Likely to Modify**:
- `webapp/css/ts_styles.css` - Primary styling updates
- `webapp/templates/towerscout.html` - HTML structure adjustments
- `webapp/templates/setup.html` - Setup wizard styling (if applicable)

**Success Criteria**:
- [ ] All identified UI improvements implemented
- [ ] Visual consistency across all pages/components
- [ ] Responsive design functions correctly
- [ ] User approval of visual updates
- [ ] No regressions in functionality

---

#### **TASK-048: Console Log Audit and Simplification** 🟢
**Status**: COMPLETED  
**Type**: A (Developer Experience)  
**Priority**: MEDIUM  
**Estimated Effort**: 3-5 hours

**Objective**: Audit and refine browser console log output for better end-user understanding and debugging

**Completion Summary** (March 31, 2026):
- Added an early `TowerScoutLogger` bootstrap in `webapp/templates/towerscout.html`
- Routed app-owned verbose browser logs through debug-gated `TowerScoutLogger.debug(...)`
- Preserved always-on in-app status messaging while keeping browser-console noise low by default
- Added `tests/frontend/test_debug_logging_contract.js` and completed browser smoke testing of startup, provider initialization, detection, cancellation, and debug-mode toggling

**Sequencing Note**:
- This task landed before the ISSUE-003 quick-win tranche so profiling noise was reduced first
- It owns and completes the deferred TASK-046 debug-preference follow-up for gating verbose browser console output

**Implementation Plan**:

**Phase 1: Audit** (1-2 hours)
- Review all `console.log()`, `console.warn()`, `console.error()` statements
- Categorize by purpose: Debug, Info, Warning, Error
- Identify verbose or redundant logging
- Document current logging patterns across modules
- Create inventory of all console output locations

**Phase 2: Simplification Strategy** (30 minutes)
- Define logging levels and when to use each
- Establish message formatting standards
- Decide what should be user-facing vs. developer-only
- Design debug mode toggle for verbose logging
- Plan integration with existing `ts_logging.py` system
- Include the deferred TASK-046 follow-up: make the persisted debug preference actually gate verbose browser console output

**Phase 3: Implementation** (1.5-2 hours)
- Implement debug mode flag (controlled via settings?)
- Standardize message formats across modules
- Remove or conditionalize verbose debug logs
- Improve error message clarity and actionability
- Add helpful context to warnings
- Test console output in various scenarios

**Phase 4: Documentation** (30 minutes)
- Document logging standards for future development
- Update developer guide with logging best practices
- Create troubleshooting guide using console output

**Key Considerations**:
- Balance between helpful debugging and information overload
- Ensure critical errors are always visible
- Make debug mode easily accessible for support scenarios
- Preserve important architectural event logs (provider switching, detection workflow)

**Files to Review**:
- All `webapp/js/src/**/*.js` files for console statements
- `webapp/ts_logging.py` for backend logging patterns
- `webapp/js/src/managers/ErrorHandler.js` for error logging

**Success Criteria**:
- [x] Production console output is clean and user-friendly
- [x] Debug mode provides detailed information when needed
- [x] Error messages are clear and actionable
- [ ] Logging conventions documented (left unchecked because TASK-048 changed runtime behavior and tests, but did not land a separate developer-facing logging guide)
- [x] No sensitive information leaked in console logs

---

#### **TASK-050: Full-Repo Stale Code and Performance Audit** 🟡
**Status**: COMPLETED  
**Type**: C (Architecture / Analysis)  
**Priority**: HIGH  
**Estimated Effort**: 6-10 hours

**Objective**: Perform a full-repository audit to identify stale/orphaned/generated code, test drift, dependency drift, and no-functionality-change performance opportunities.

**Implementation Plan**:

**Phase 1: Structural Inventory and Reference Tracing** (2-3 hours)
- Audit `webapp/`, top-level `tests/`, `webapp/tests/`, `Model/`, `SyntheticData/`, `TowerScoutSite/`, `hosting/`, dependency manifests, and build/config files
- Use `git ls-files`, `rg`, Flask route/template checks, `pytest.ini`, and `webapp/build.js` to determine which surfaces are active vs. unreferenced
- Cross-check runtime requirements against actual imports/usages

**Phase 2: Evidence Scoring and Classification** (2-3 hours)
- Require at least two independent signals before calling anything `confirmed stale`
- Classify each candidate as:
  - `confirmed stale`
  - `generated/backup artifact`
  - `orphaned debug/test surface`
  - `legacy-but-active`
  - `dependency drift`
  - `needs runtime verification`
- Separate removal candidates from preserve-for-now items

**Phase 3: Performance Opportunity Review** (1-2 hours)
- Use existing `webapp/ts_performance.py` instrumentation and static hotspot analysis
- Focus on startup/import cost, bundle size, rendering scale, cache hygiene, dependency footprint, and console/log noise
- Rank findings as `quick win`, `safe refactor`, or `defer`

**Phase 4: Documentation and Handoff** (1 hour)
- Publish findings in `.agent_work/context/analysis/FULL-REPO-STALE-CODE-AND-PERFORMANCE-AUDIT.md`
- Map cleanup work to TASK-049 and performance work to ISSUE-003 / TASK-048
- Update Sprint tracking artifacts so downstream tasks do not repeat discovery work

**Deliverables**:
- Full-repo stale code and performance audit report
- Baseline validation output for pytest collection and unused-code scanning
- Confirmed-safe cleanup batch recommendations
- Follow-on task mapping for cleanup and performance work

**Validation Baseline**:
- `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m pytest --collect-only tests -q`
- `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m flake8 webapp tests --select=F401,F841 --statistics --jobs 1`

---

#### **TASK-049: Legacy Code Cleanup** 🟢
**Status**: COMPLETED  
**Type**: A (Code Quality)  
**Priority**: MEDIUM  
**Estimated Effort**: 4-6 hours

**Objective**: Execute verified cleanup/remediation batches from TASK-050 without removing active or legacy-but-active paths.

**Sequencing Note**:
- Start after TASK-048 and the ISSUE-003 quick-win tranche
- Use cleanup validation as the stability checkpoint before TASK-047 UI polish

**Completion Summary** (March 31, 2026):
- Removed the approved low-risk tracked artifacts: `.coverage`, `.DS_Store`, tracked `webapp/cache/maps/*.cache`, and `webapp/templates/towerscout_backup.html`
- Repaired the pytest collection gate by updating the event-system unit tests, adding test-only lazy secondary-classifier initialization, and quarantining the stale legacy integration harness
- Archived the stale Stage-3 helper scripts and `webapp/tests/` surface under `.agent_work/context/archive/2026-03-task-049-stale-surfaces/`
- Reduced the `flake8 webapp tests --select=F401,F841` baseline from `105/14` to `73/6`
- Handed runtime dependency verification to `TASK-051` and the current integration smoke-test rebuild to `TASK-052`
- `webapp/js/towerscout.original.js` remains explicitly excluded because it is a deliberate rollback/reference artifact and should stay untouched unless a separate rollback/cleanup decision is made
- `webapp/js/src/towerscout.js.stage3.bak` remains deferred because it is local-only and low-value compared with the Sprint 05 pre-containerization work

**Implementation Plan**:

**Phase 1: Intake TASK-050 Findings** (30 minutes)
- Use only candidates marked safe or high-confidence by TASK-050
- Separate low-risk generated artifacts from deeper runtime/test refactors
- Decide first cleanup batch before editing anything

**Phase 2: Safe Removal / Remediation** (1-2 hours)
- Remove confirmed generated artifacts and backup files
- Archive or delete verified stale debug/test surfaces
- Clean up unused imports/locals and dead helper code
- Preserve anything marked `legacy-but-active` or `needs runtime verification`

**Phase 3: Validation** (30-60 minutes)
- Run full test suite: `pytest tests/`
- Execute frontend tests: `tests/frontend/test_stage_0_console.js`
- Perform smoke testing of core workflows:
  - Search and detection
  - Provider switching
  - Manual tower addition
  - Export functionality
- Verify bundle size doesn't increase unexpectedly
- Check for console errors in browser

**Phase 4: Report Update and Next-Batch Planning** (30 minutes)
- Update the audit report with what was actually removed
- Record any false positives or preserve-for-now decisions
- Queue remaining medium-risk items into follow-on tasks instead of forcing one large cleanup pass

**Dependencies**:
- TASK-050 must complete the audit and classify candidates first

**Areas to Focus**:
- Confirmed generated artifacts and backup files
- Verified stale test/debug surfaces
- Unused imports/locals and dead helper code
- Only items validated by TASK-050

**Success Criteria**:
- [x] First cleanup batch is derived from TASK-050 findings, not ad hoc discovery
- [x] Confirmed generated artifacts and dead files removed safely
- [x] Unused imports/locals reduced in touched files
- [ ] Duplicate functions consolidated (left unchecked because TASK-049 did not include duplicate-function consolidation; it stayed scoped to validated artifact cleanup, test-gate repair, and stale-surface archival)
- [ ] All tests passing after cleanup (left unchecked because TASK-049 improved pytest collection and repaired targeted tests, but the replacement for the quarantined legacy integration harness was deferred to TASK-052)
- [ ] No regressions in functionality (left unchecked because TASK-049 validation focused on cleanup baselines and collection/lint checks, not full workflow smoke coverage; broader regression confirmation is still tied to follow-on validation work)
- [x] Documentation updated to reflect removed features (if any)
- [x] Cleaner, more maintainable codebase

---

### **Quick Wins & Tactical Improvements**

#### **Browser Refresh Warning Fix** 🟢
**Status**: NOT_STARTED (carried from Sprint 03)  
**Priority**: LOW (nice-to-have)  
**Estimated Effort**: 2-3 hours

**Objective**: Debug and fix `window.onbeforeunload` handler inconsistencies across browsers

**Implementation**:
- Test current implementation across Chrome, Firefox, Edge, Safari
- Research browser-specific requirements for beforeunload events
- Implement cross-browser compatible solution
- Add fallback messaging strategies
- Document browser compatibility notes in code

**Files to Modify**:
- `webapp/js/src/ui/navigation.js` or `webapp/js/src/globals.js`

---

#### **Error Handling Pattern Standardization** 🟢
**Status**: NOT_STARTED (carried from Sprint 03)  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 hours

**Objective**: Consolidate error handling patterns for consistency

**Implementation**:
- Remove deprecated `fatalError()` function references
- Standardize on `TowerScoutErrorHandler.showFatalError()` usage
- Update all modules to use consistent error handling
- Update documentation with error handling examples
- Add error handling guidelines to developer docs

**Files to Review**:
- All `webapp/js/src/` modules for error handling patterns
- `webapp/js/src/managers/ErrorHandler.js` for consolidation opportunities

---

## 📊 Sprint 04 Execution Timeline

**Sprint Duration**: 16 days (March 19 - April 4, 2026)  
**Extended by**: 2 days to accommodate code quality tasks  
**Target Capacity**: 60-75 hours

### Week 1: March 19-25 (Foundation)
**Focus**: Backend infrastructure and discovery work

- **March 19-20** (Day 1-2): 8-12 hours
  - TASK-046 Phase 0: Discovery & Planning (4-6 hours)
  - ISSUE-003: Performance Investigation (2-4 hours)
  - Parallel execution possible

- **March 21-23** (Day 3-5): 12-18 hours
  - TASK-046 Phase 1: Backend Configuration Module (8-12 hours)
  - TASK-048: Console Log Audit Phase 1 (1-2 hours)
  - TASK-050: Full-Repo Audit Phases 1-2 (2-4 hours)
  - Publish audit findings before cleanup starts

- **March 24-25** (Day 6-7): 12-16 hours
  - TASK-046 Phase 2: Setup Wizard UI - START (first 8-12 hours)
  - Complete by end of Week 1

**Week 1 Total**: 32-46 hours

---

### Week 2: March 26-April 1 (Implementation & Polish)
**Focus**: Feature completion plus stability/performance and cleanup sequencing

- **March 26-28** (Day 8-10): 16-24 hours
  - TASK-046 Phase 2: Setup Wizard UI - COMPLETE (if needed)
  - TASK-046 Phase 3: Settings Screen (8-12 hours)
  - TASK-048: Audit / strategy work and debug-gating approach
  - ISSUE-003 quick-win tranche planning from further investigation findings

- **March 29-30** (Day 11-12): 8-12 hours
  - TASK-048: Console Log Implementation (2-3 hours)
  - ISSUE-003 Follow-Up: Performance Quick Wins (3-6 hours)
  - TASK-049: Cleanup batches derived from TASK-050 (2-4 hours)
  - Browser Refresh Warning Fix (2-3 hours)
  - Error Handling Standardization (2-3 hours)

- **March 31** (Day 13): 6-8 hours
  - TASK-049: Legacy Code Cleanup Phase 4 Validation (1-2 hours)
  - TASK-047: UI work only if stability/performance tranche is complete (1-2 hours)
  - Begin TASK-046 Phase 4: Testing

**Week 2 Subtotal**: 30-44 hours

---

### Week 3: April 1-4 (Testing & Completion)
**Focus**: Comprehensive testing and sprint closeout

- **April 1-3** (Day 13-15): 12-18 hours
  - TASK-046 Phase 4: Testing & Validation (8-12 hours)
    - Integration testing
    - Edge case testing
    - User acceptance testing
    - Cross-browser validation
  - Final validation of all code quality tasks (2-3 hours)
  - Performance benchmarking with cleaned codebase (1-2 hours)

- **April 4** (Day 16): 3-5 hours
  - TASK-046 Phase 5: Documentation (2-4 hours)
  - Sprint 04 Retrospective (1-2 hours)
  - Update task backlogs and prepare Sprint 05 preview

**Week 3 Total**: 15-23 hours

---

### **Sprint 04 Total Effort Estimate**: 60-90 hours
**Target**: 65-75 hours (mid-range, healthy pace)  
**Confidence**: High (based on Sprint 02-03 velocity of 56-61 hours per sprint)

---

## 🎯 Sprint 04 Success Criteria

### Must-Have (Primary Goals)
- [x] Setup wizard functional on first launch, blocks app until configured
- [x] Settings screen accessible and functional for API key updates
- [x] API key validation working with clear feedback (<5 seconds)
- [x] .env file persistence with backup/rollback mechanism
- [ ] Zero regressions in existing functionality (all Sprint 03 features work) (left unchecked because Sprint 04 closeout does not include a full current workflow smoke/regression matrix)
- [x] TASK-046 accepted complete with runtime validation evidence
- [ ] Cross-browser testing complete (Chrome, Firefox, Edge, Safari)

### Should-Have (Secondary Goals)
- [x] ISSUE-003 investigation complete with recommendations
- [x] Bounded ISSUE-003 quick-win tranche completed after TASK-048
- [ ] UI formatting improvements implemented and approved (TASK-047 remains not started)
- [x] Console log output simplified and standardized
- [x] Full-repo stale code/performance audit completed and documented
- [ ] Legacy code cleaned up from audited findings, tests passing (left unchecked because bounded cleanup completed, but the replacement smoke-test baseline is deferred to TASK-052)
- [ ] Browser refresh warning works consistently
- [ ] Error handling patterns fully standardized

### Nice-to-Have (Stretch Goals)
- [x] Quick performance optimizations (if ISSUE-003 identifies easy wins)
- [x] Debug mode toggle for verbose logging
- [ ] Bundle size reduced through code cleanup (current rebuilt bundle remains under the 500 KB target, but it did not shrink)
- [ ] Enhanced developer documentation

---

## 📋 Sprint Health Metrics

### Velocity Tracking
- **Sprint 01**: 32 hours (7 tasks, 90% success rate)
- **Sprint 02**: 61 hours (5 tasks, 100% completion)
- **Sprint 03**: 56 hours (8 tasks, 100% completion, 6 days ahead)
- **Sprint 04 Target**: 65-75 hours (7 major tasks + quick wins)

### Quality Metrics
- Completed Sprint 04 implementation tasks: `TASK-046`, `ISSUE-003`, `ISSUE-003 Follow-Up`, `TASK-048`, `TASK-050`, and `TASK-049`; `TASK-047` remains the only in-sprint implementation task not yet started
- Actual effort within 15% of estimate: pending Sprint 04 closeout
- Zero critical bugs introduced: no blocking regressions recorded in completed task closeouts
- Automated test status: `pytest --collect-only tests -q` repaired to `154 collected`, `0 collection errors`; a current smoke-test baseline is still deferred to `TASK-052`
- Bundle size stays under 500 KB (current rebuilt bundle: `446.1 KB`)
- Documentation updated for all completed task areas

### Risk Indicators
- 🟢 **Low Risk**: Task blocked for >2 days
- 🟡 **Medium Risk**: Effort exceeds estimate by >25%
- 🔴 **High Risk**: Critical bug affecting production features

---

## 🔗 Dependencies & Prerequisites

### External Dependencies
- ✅ `python-dotenv` library (already installed)
- ✅ Flask session management (already configured)
- ✅ Static analysis tools (flake8, ESLint) - verify installed

### Internal Dependencies
- ✅ Error handling system (`ts_errors.py`) - Sprint 02
- ✅ Validation utilities (`ts_validation.py`) - Sprint 02
- ✅ Provider abstraction layer - Sprint 02-03
- ✅ Frontend modular architecture (27 modules) - Sprint 03
- ✅ Frontend state management patterns - Sprint 03

### Known Blockers
- **None identified** - All prerequisites completed in prior sprints

---

## 📝 Definition of Done

### Code Complete
- [ ] All planned features implemented and working
- [ ] No unresolved bugs or regressions
- [x] Code follows established patterns and conventions
- [ ] No TODO comments or temporary hacks remaining
- [x] Bundle built successfully with no errors

### Testing Complete
- [ ] All automated tests passing (pytest + frontend tests)
- [ ] Manual testing completed for all workflows
- [ ] Cross-browser compatibility verified
- [ ] Performance benchmarks within acceptable ranges
- [ ] Edge cases and error scenarios tested

### Documentation Complete
- [ ] User-facing documentation updated (guides, README)
- [ ] Developer documentation updated (copilot-instructions.md)
- [ ] Code comments accurate and helpful
- [x] API changes documented (if applicable)
- [ ] Sprint retrospective completed with lessons learned

### Deployment Ready
- [ ] All changes committed to git with clear messages
- [ ] Feature branch ready for merge (or PR created)
- [x] No sensitive data in code or logs
- [x] Configuration changes documented
- [x] Task backlogs updated for Sprint 05

---

## 🚀 Handoff to Sprint 05

### Expected Deliverables
- ✅ TASK-046: Setup Wizard & Settings fully operational
- ✅ ISSUE-003: Performance investigation report with recommendations
- ✅ TASK-048: Console logging simplified with debug-gated browser output and always-on in-app status messaging
- ✅ TASK-050 / TASK-049: Full-repo audit plus bounded cleanup completed
- ⏳ TASK-047: UI polish remains the only in-sprint implementation task if Sprint 04 resumes before Sprint 05 prep

### Sprint 05 Preview
Based on completed work, Sprint 05 will focus on:
- **TASK-025**: Docker Containerization (leverages TASK-046 configuration UI)
- **TASK-026**: CPU Optimization (may benefit from ISSUE-003 findings)
- **Performance Optimizations**: Implement fixes identified in ISSUE-003 (if needed)
- **TASK-028**: Mobile Responsiveness (build on UI improvements)
- **TASK-051**: Runtime Dependency Verification and Split (validate deployment-sensitive requirements before containerization)
- **TASK-052**: Current Integration Smoke Test Baseline (replace the quarantined legacy harness with a current app-boot and route smoke test)

### Technical Debt Created
Document any shortcuts, deferred polish items, or discovered issues:
- Tag TODO comments with `SPRINT-05` prefix for easy tracking
- Update task backlog with new discoveries
- Note any architectural improvements identified but not implemented

---

## 📚 Reference Documentation

### Task Documents
- [TASK-046 Acceptance Criteria](../tasks/completed/TASK-046-setup-wizard-settings-screen.md)
- [ISSUE-003 Context](.agent_work/context/status/SPRINT-03-RETROSPECTIVE.md)
- [Sprint 03 Retrospective](.agent_work/context/status/SPRINT-03-RETROSPECTIVE.md)

### Technical References
- [Spec-Driven Workflow](.github/instructions/spec-driven-approach.instructions.md)
- [Copilot Instructions](.github/copilot-instructions.md)
- [Task Backlog](.agent_work/task-backlog.md)

### Code Standards
- Frontend: 27-module architecture established in Sprint 03
- Backend: Follow patterns in `ts_*.py` modules
- Testing: Use existing test frameworks and patterns
- Documentation: Maintain inline comments for complex logic

---

## ✅ Sprint 04 Kickoff Checklist (Historical Planning Snapshot)

_Note: this checklist was not maintained as the live source of truth after execution began; `current-tasks.md` and the task documents capture the actual Sprint 04 progress._

- [x] Sprint 03 retrospective completed (March 18, 2026)
- [x] Sprint 03 tasks moved to completed-tasks.md
- [x] Sprint 04 scope finalized with user input
- [x] Sprint 04 planning document created
- [x] TASK-046 task file created with acceptance criteria
- [ ] Sprint 04 branch created: `git checkout -b sprint-04/setup-wizard`
- [x] Team aligned on priorities and timeline
- [x] Development environment ready
- [x] All dependencies verified and installed

---

**Sprint 04 Start Date**: March 19, 2026  
**Sprint 04 End Date**: April 4, 2026  
**Latest Plan Sync**: April 1, 2026  
**Sprint Retrospective Target**: April 4, 2026

**Status**: ⏳ **SPRINT 04 IN PROGRESS** - `TASK-046`, `ISSUE-003`, `ISSUE-003 Follow-Up`, `TASK-048`, `TASK-050`, and `TASK-049` are complete; `TASK-047` plus final closeout items remain

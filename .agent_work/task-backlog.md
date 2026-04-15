# Task Backlog - Future Work Prioritization

**Last Updated**: April 14, 2026  
**Sprint 04 Completed**: March 19 - April 6, 2026  
**Sprint 05 Active**: April 7 - April 25, 2026  
**Next Sprint Planning**: Sprint 06 Prep - April 25, 2026  

---

## 🚀 SPRINT 05 ACTIVE TASKS (Moved to current-tasks.md)

### **TASK-051: Runtime Dependency Verification and Split** 🔴
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md  
**Type**: C (Architecture / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 4-8 hours  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md#task-051-runtime-dependency-verification-and-split) for full details

---

### **TASK-056: First-Run Reliability and Runtime Determinism Hardening** 🔴
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 12-20 hours  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md#task-056-first-run-reliability-and-runtime-determinism-hardening) for full details

---

### **TASK-057: Local YOLO Runtime Ownership and Torch Hub Independence** 🔴
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md  
**Type**: C (Runtime Architecture / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 12-20 hours  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md#task-057-local-yolo-runtime-ownership-and-torch-hub-independence) for full details

---

### **TASK-052: Current Integration Smoke Test Baseline** 🔴
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md  
**Type**: A (Quality / Validation)  
**Priority**: CRITICAL  
**Estimated Effort**: 4-8 hours  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md#task-052-current-integration-smoke-test-baseline) for full details

---

### **TASK-062: Pre-Docker Runtime Cleanup And YOLO Loader Hardening** 🟡
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Priority**: HIGH  
**Estimated Effort**: 6-10 hours  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md) for full details

---

### **TASK-025: Docker Containerization** 🔴
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md  
**Type**: A (Infrastructure)  
**Priority**: HIGH  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md#task-025-docker-containerization) for full details

---

### **TASK-029: Multi-Provider Fallback** 🟡
**Status**: IN_SPRINT_05 - MOVED TO current-tasks.md (stretch goal)  
**Type**: B (Reliability)  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 days (16-24 hours)  
**Target Sprint**: Sprint 05

**See**: [current-tasks.md](./current-tasks.md#task-029-multi-provider-fallback) for full details

---

## 🔧 POST-CONTAINERIZATION RELIABILITY AND ARCHITECTURE FOLLOW-ON

### **TASK-058: Background Detection Jobs and Durable Run State** 🟡
**Status**: NOT_STARTED  
**Type**: C (Architecture / Reliability)  
**Priority**: HIGH  
**Estimated Effort**: 3-5 days (24-40 hours)  
**Target Sprint**: Sprint 06 or Sprint 07

**Objective**: Move long-running detection work out of the request thread and introduce durable run/job state suitable for containerized deployment.

**Issues Addressed**:
- `UT-011` synchronous detection request path blocks long-running ML work
- `UT-015` filesystem sessions and session-persisted paths make deployment state too local
- `UT-016` asyncio download plumbing adds complexity with limited benefit
- follow-on hardening beyond `UT-013` stable session identity

**Requirements**:
- Background job lifecycle for detection start, status, cancellation, and result completion
- Durable job/run identity and shared backing state rather than process-local assumptions
- Clear migration path for progress polling and cancellation
- Explicit handling of temp files, cleanup, and retry semantics outside the request thread

**User Value**: Makes the deployed application more reliable under real long-running workloads and better aligned with containerized execution.

---

### **TASK-059: Backend Layer Decomposition and Logging Consolidation** 🟡
**Status**: NOT_STARTED  
**Type**: C (Architecture / Maintainability)  
**Priority**: HIGH  
**Estimated Effort**: 3-5 days (24-40 hours)  
**Target Sprint**: Sprint 06 or Sprint 07

**Objective**: Reduce change risk in `towerscout.py` by extracting clearer backend layers and completing the migration away from raw `print()` logging in production code paths.

**Issues Addressed**:
- `UT-008` `towerscout.py` remains a high-risk monolith
- remaining work from `UT-009` production request paths still use `print()` instead of structured logging

**Requirements**:
- Extract bounded runtime layers without changing user-facing behavior
- Move detection orchestration, session/state helpers, and route concerns into clearer modules
- Replace remaining production `print()` usage with structured logging in the active backend runtime
- Preserve existing detection behavior and route contracts during the decomposition

**User Value**: Makes future reliability and deployment changes safer and easier to reason about.

---

### **TASK-060: Frontend Build Modernization** 🟡
**Status**: NOT_STARTED  
**Type**: B (Frontend Infrastructure)  
**Priority**: MEDIUM  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 or Sprint 07

**Objective**: Replace the manual ordered-concatenation frontend build with a module-aware bundling workflow.

**Issues Addressed**:
- `UT-012` frontend build still depends on manual ordered concatenation

**Requirements**:
- Adopt a supported bundling workflow with explicit module resolution
- Preserve the current frontend runtime behavior and Flask integration contract
- Document the new dev/build workflow
- Keep generated assets and source ownership clear

**User Value**: Reduces frontend maintenance risk and makes future UI changes easier to validate.

---

### **TASK-061: Coordinated NumPy 2 Runtime Migration** 🟡
**Status**: NOT_STARTED  
**Type**: C (Dependency / Runtime Compatibility)  
**Priority**: MEDIUM  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 07+

**Objective**: Intentionally validate and migrate the runtime stack from the Sprint 05 NumPy 1 containment baseline to a coordinated NumPy 2-compatible stack.

**Issues Addressed**:
- full follow-on resolution path for `UT-005` NumPy 2 compatibility across Shapely and OpenCV

**Requirements**:
- Upgrade Shapely/OpenCV/NumPy together rather than piecemeal
- Revalidate the YOLO and imagery import paths on the upgraded stack
- Re-run first-run and smoke-level proofs against the coordinated dependency set
- Update runtime documentation to reflect the new dependency baseline

**User Value**: Removes the deferred NumPy 1 containment decision and modernizes the runtime stack safely.

---

## 🔴 HIGH PRIORITY - Sprint 06 Candidates

### **TASK-026: CPU Optimization** 🟡
**Status**: NOT_STARTED  
**Type**: C (Performance)  
**Priority**: HIGH  
**Estimated Effort**: 2-3 days (16-24 hours)  
**Target Sprint**: Sprint 06

**Objective**: Optimize detection pipeline for CPU-only deployment scenarios

**Requirements**:
- torch.quantization implementation for model compression
- Hardware detection and batch size optimization
- Progress indicators for CPU processing
- Memory management for 8GB constraints

**Technical Notes**: Apply model quantization, optimize batch sizes for different hardware profiles

**User Value**: Better performance on systems without dedicated GPU hardware

---

## 🟡 MEDIUM PRIORITY - Sprint 06 Candidates

### **TASK-027: Enhanced Error Handling** 🟡
**Status**: NOT_STARTED  
**Type**: A (Infrastructure)  
**Priority**: MEDIUM  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06

**Objective**: Improve user experience with better error messages and recovery

**Requirements**:
- User-friendly error messages for non-technical users
- Graceful degradation for API failures
- Retry mechanisms with exponential backoff
- Error reporting and logging improvements

**Dependencies**: Enhanced logging system ✅ COMPLETED (Sprint 04)

**Notes**: Could include standardization of error handling patterns from Sprint 04 deferred quick win

**User Value**: Better user experience when errors occur, clearer troubleshooting guidance

---

### **TASK-028: Mobile Responsiveness** 🟡
**Status**: NOT_STARTED  
**Type**: B (UI/UX)  
**Priority**: MEDIUM  
**Estimated Effort**: 2 days (16 hours)  
**Target Sprint**: Sprint 06 or Sprint 07

**Objective**: Improve mobile device compatibility for field investigators

**Requirements**:
- Responsive design for tablet/mobile polygon drawing
- Touch-friendly interface elements
- Optimized map controls for small screens
- Progressive loading for mobile networks

**Notes**: Important for field outbreak investigation teams

**User Value**: Enables field investigators to use TowerScout on tablets and mobile devices

---

### **Sprint 04 Deferred Quick Wins** 🟢
**Status**: NOT_STARTED  
**Priority**: LOW-MEDIUM  
**Total Estimated Effort**: 4-6 hours

**Browser Refresh Warning Fix** (2-3 hours)
- Debug `window.onbeforeunload` inconsistencies
- Cross-browser compatibility testing
- Implement reliable solution

**Error Handling Pattern Standardization** (2-3 hours)
- Remove deprecated `fatalError()` references
- Standardize on `TowerScoutErrorHandler`
- Update documentation

**Notes**: Could be absorbed into TASK-027 or completed independently if Sprint 05 has capacity

---

## 🔵 LOW PRIORITY - Backlog

### **Future Enhancement: Advanced Filtering** 🔵
**Type**: B (Feature)  
**Priority**: LOW  
**Estimated Effort**: 3-4 days (24-32 hours)

**Objective**: Add advanced filtering and search capabilities for large result sets

**Ideas**:
- Enhanced confidence threshold controls
- Geographic filtering (distance, administrative boundaries)
- Historical detection tracking
- Batch operations on filtered results
- Saved search areas and filters

**User Value**: Better management of large detection result sets

---

### **Future Enhancement: Performance Dashboard** 🔵
**Type**: A (Monitoring)  
**Priority**: LOW  
**Estimated Effort**: 2 days (16 hours)

**Objective**: Create diagnostic dashboard for troublemaking and optimization

**Ideas**:
- Real-time processing time metrics
- GPU/CPU utilization monitoring
- API usage tracking and quota management
- System health indicators
- Detection accuracy statistics

**User Value**: Better troubleshooting and performance monitoring

---

### **Future Enhancement: User Preferences** 🔵
**Type**: B (UX)  
**Priority**: LOW  
**Estimated Effort**: 1-2 days (8-16 hours)

**Objective**: Add user preference storage and customization

**Ideas**:
- Persistent default map provider selection
- Saved search areas and recent searches
- Custom confidence thresholds per use case
- Interface layout preferences
- Detection notification preferences

**Notes**: Partially addressed by Sprint 04 Settings screen - this would expand those capabilities

**User Value**: More personalized user experience, faster workflow for repeat users

---

## 📅 Sprint Planning Guidelines

### **Sprint Capacity Management**
- **Sprint Duration**: 2-3 weeks (14-21 calendar days, 10-15 working days)
- **Estimated Velocity**: 8-12 days of focused work per sprint
- **Target Hours**: 60-80 hours per sprint (accommodating complexity and validation)

### **Task Selection Criteria**
1. **Dependencies**: Respect task dependencies and prerequisites
2. **Strategic Value**: Prioritize deployment readiness and user-facing improvements
3. **Risk Management**: Balance high-risk architecture work with safe improvements
4. **Validation**: Include adequate testing and validation time
5. **Documentation**: Budget time for proper documentation

### **Sprint 05 Focus**
- Runtime hardening and first-run reliability
- Local YOLO runtime ownership and Torch Hub-independent initialization
- Deployment readiness (containerization)
- Validation infrastructure
- Minimal feature development
- Conservative risk profile

### **Sprint 06 Preview**
- CPU optimization for wider deployment
- Enhanced error handling and reliability
- Optional: Mobile responsiveness or multi-provider fallback completion
- Continue polish and quality improvements

---

## 📊 Historical Sprint Performance

| Sprint | Duration | Tasks | Completion | Bundle Change | Notes |
|--------|----------|-------|------------|---------------|-------|
| Sprint 01 | 14 days | 7/7 (100%) | ✅ Complete | N/A | Foundation work |
| Sprint 02 | 14-21 days | 5/5 (100%) | ✅ Complete | N/A | Architecture work |
| Sprint 03 | 8 days (14 planned) | 8/8 (100%) | ✅ Complete | +40.2 KB | Ahead of schedule |
| Sprint 04 | 19 days (16 planned) | 7/7 core + 1 closeout (100%) | ✅ Complete | +33.3 KB | Extended for stabilization |
| Sprint 05 | 19 days planned | TBD | 🏃 In Planning | TBD | Deployment readiness |

**Trend Analysis**:
- Consistent 100% core task completion across all sprints
- Sprint 03 completed early, Sprint 04 extended - both appropriate for work type
- Bundle size growing but staying under control (currently 446.1 KB vs 500 KB target)
- Strong validation discipline established in Sprint 04

---

## 🎯 Long-Term Roadmap

### **Phase 1: Deployment Readiness (Sprint 04-05)** ✅ In Progress
- ✅ Setup wizard and settings (Sprint 04)
- 🏃 Runtime hardening and local YOLO ownership (Sprint 05)
- 🏃 Runtime dependency verification (Sprint 05)
- 🏃 Integration testing baseline (Sprint 05)
- 🏃 Docker containerization (Sprint 05)

### **Phase 2: Performance and Reliability (Sprint 06-07)**
- CPU optimization
- Enhanced error handling
- Multi-provider fallback
- Mobile responsiveness

### **Phase 3: Advanced Features (Sprint 08+)**
- Advanced filtering and search
- Performance dashboard
- User preferences expansion
- Historical tracking

### **Phase 4: Scale and Polish (Sprint 09+)**
- Large-scale deployment support
- Advanced monitoring
- Additional provider integrations
- Community features

---

## 📝 Notes

**Adding New Tasks**:
1. Use the appropriate template from `task-backlog.md`
2. Assign priority and estimated effort
3. Document dependencies and acceptance criteria
4. Link to related documentation

**Sprint Planning Process**:
1. Review completed sprint retrospective
2. Move completed tasks to `completed-tasks.md`
3. Select 3-5 tasks from backlog based on capacity and priorities
4. Move selected tasks to `current-tasks.md`
5. Update dependencies and estimates
6. Create sprint plan document

**Priority Definitions**:
- 🔴 **CRITICAL**: Blocking issues, security, or hard deadlines
- 🟡 **HIGH**: Important for user experience or strategic goals
- 🟢 **MEDIUM**: Valuable improvements, not immediate blockers
- 🔵 **LOW**: Nice-to-have enhancements, backlog items

---

## 🔗 Related Documentation

- [Current Tasks](./current-tasks.md) - Sprint 05 active work
- [Completed Tasks](./completed-tasks.md) - Historical completion record
- [Sprint 05 Plan](./context/status/SPRINT-05-PLAN.md) - Sprint 05 detailed planning (create at kickoff)
- [Sprint 04 Retrospective](./context/status/SPRINT-04-RETROSPECTIVE.md) - Sprint 04 lessons learned

# TowerScout Local Deployment Requirements

## Executive Summary

This document specifies requirements for transforming TowerScout from a student prototype into a **locally-deployable, user-friendly tool** for cooling tower detection. Requirements are organized using EARS notation and prioritized by Type (A=Quick Fixes, B=Feature Development, C=Architecture Changes).

**DEPLOYMENT MODEL**: **LOCAL DEPLOYMENT** - TowerScout will be deployed on individual user devices (epidemiologists, researchers, health departments) rather than as a hosted service.

**Current State**: Student prototype requiring technical setup  
**Target State**: User-friendly, locally-deployable tool with the merged `TASK-025` Docker-compatible / OCI container baseline, GitHub-first release packaging, and a launcher-first local startup path

**Key Implications**:
- **Authentication eliminated**: Physical access control sufficient for local deployment
- **Enterprise features simplified**: Focus on ease of installation over complex multi-tenant features
- **Hardware compatibility critical**: V1 targets Windows 11/AMD64 CPU-first local use; Podman is the preferred open-source Windows runtime target after release-support gates, Docker Desktop is secondary where licensed/approved, and ARM64, Mac, offline, VDI, shared deployment, and broader runtime hosts remain follow-on targets unless explicitly validated
- **User experience paramount**: No IT support means excellent error messages and setup guidance essential

---

## 🚨 CRITICAL SECURITY REQUIREMENTS (Type C)

### SEC-001: API Key Security
**Priority**: CRITICAL  
**Type**: C  
**EARS**: WHEN the application starts, THE SYSTEM SHALL load API keys from environment variables instead of plain text files  
**Acceptance Criteria**:
- Remove `apikey.txt` from repository
- Implement environment variable loading (`GOOGLE_API_KEY`, `AZURE_MAPS_SUBSCRIPTION_KEY`)
- Add validation for missing API keys with clear error messages
- Update deployment documentation
- Support Azure Key Vault integration for enterprise deployments

### SEC-002: Input Validation
**Priority**: HIGH  
**Type**: C  
**EARS**: WHEN receiving user input, THE SYSTEM SHALL validate and sanitize all polygon coordinates, file uploads, and API parameters  
**Acceptance Criteria**:
- Validate polygon coordinate ranges and formats
- Restrict file uploads to allowed extensions and sizes
- Sanitize all user inputs before processing
- Add rate limiting to prevent abuse

### SEC-003: Error Handling Infrastructure  
**Priority**: HIGH  
**Type**: C  
**Status**: ✅ **COMPLETED**  
**EARS**: WHEN the application encounters errors, THE SYSTEM SHALL provide structured error handling with comprehensive logging  
**Acceptance Criteria**:
- ✅ Implement comprehensive exception hierarchy (8 specialized classes)
- ✅ Add structured logging with automatic rotation (multi-level logs)
- ✅ Create Flask error middleware for standardized JSON responses
- ✅ Implement network resilience with retry logic and exponential backoff
- ✅ Add development validation system for dependency-free testing

### SEC-004: Authentication System
**Status**: ❌ **OBSOLETE FOR LOCAL DEPLOYMENT**  
**Priority**: ~~MEDIUM~~ **ELIMINATED**  
**Type**: C  
**EARS**: ~~WHEN users access the application, THE SYSTEM SHALL provide basic authentication to control access~~ **OBSOLETE**: Local deployment uses physical access control. Authentication adds unnecessary complexity for single-user scenarios.  
**Rationale**: Users run TowerScout on their own devices, eliminating need for user management, login/logout, and admin interfaces.

### SEC-005: Azure Maps Migration
**Priority**: CRITICAL  
**Type**: C  
**Status**: ✅ **COMPLETED - SIMPLIFIED FOR LOCAL DEPLOYMENT**
**EARS**: WHEN the application accesses map services, THE SYSTEM SHALL use Azure Maps instead of Bing Maps with basic API key authentication  
**Acceptance Criteria**:
- ✅ Replace Bing Maps provider with Azure Maps implementation
- ✅ Handle coordinate order transformation (lng,lat vs lat,lng)  
- ~~Implement Azure Key Vault authentication for enterprise deployments~~ **REMOVED**: Over-engineered for local deployment
- ✅ Maintain Google Maps as alternative provider option
- ✅ Validate coordinate accuracy across all providers
- ✅ Remove metadata dependencies (vintage date features)
- ~~Implement provider fallback mechanisms~~ **SIMPLIFIED**: Basic provider selection sufficient for local deployment

---

## 🗺️ MAP PROVIDER REQUIREMENTS (Type C)

### MAP-001: Azure Maps Frontend UI Implementation
**Status**: ✅ **COMPLETED** (TASK-030, January 16, 2026)  
**Priority**: CRITICAL  
**Type**: C  
**EARS**: WHEN users interact with the map interface, THE SYSTEM SHALL provide Azure Maps Web SDK instead of Bing Maps with full functionality  
**Acceptance Criteria**:
- ✅ Replace Bing Maps frontend radio button with Azure Maps option
- ✅ Implement Azure Maps Web SDK integration with complete JavaScript API
- ✅ Add drawing manager for polygon/rectangle creation tools
- ✅ Integrate Azure Maps Search API for location search functionality
- ✅ Maintain coordinate transformation compatibility between frontend and backend
- ✅ Support detection overlay positioning on Azure Maps
- ✅ Ensure cross-browser compatibility and mobile responsiveness
- ✅ Remove all Bing Maps frontend dependencies and references

**Validation**:
- Cross-provider visual consistency achieved (TASK-040, February 11, 2026)
- Geocoding functionality fully operational (TASK-039, February 11, 2026)
- User journey verification completed (TASK-037, February 17, 2026)

---

## 🏗️ INFRASTRUCTURE REQUIREMENTS (Type C)

### INF-001: Error Handling System
**Status**: ✅ **COMPLETED** (TASK-003, ts_errors.py + ts_validation.py)  
**Priority**: HIGH  
**Type**: C  
**EARS**: WHEN errors occur, THE SYSTEM SHALL handle exceptions gracefully and provide meaningful feedback to users  
**Acceptance Criteria**:
- ✅ Add try/catch blocks around all external API calls
- ✅ Implement structured error responses
- ✅ Create error logging with different severity levels
- ✅ Add user-friendly error messages

**Validation**:
- Comprehensive error handling system with custom exception hierarchy
- Input validation utilities for all user inputs
- Centralized error handling across all modules

### INF-002: Logging Infrastructure
**Status**: ✅ **COMPLETED** (ts_logging.py)  
**Priority**: HIGH  
**Type**: C  
**EARS**: THE SYSTEM SHALL implement structured logging for debugging, monitoring, and audit trails  
**Acceptance Criteria**:
- ✅ Replace all print statements with proper logging
- ✅ Add log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Configure log rotation and retention
- ✅ Add request/response logging for API calls

**Validation**:
- Structured logging system implemented across all modules
- Log files written to webapp/logs/ directory
- Configurable log levels and output formats

### INF-003: Testing Framework
**Status**: ✅ **COMPLETED** (TASK-005, Sprint 02 Enhanced)  
**Priority**: HIGH  
**Type**: B  
**EARS**: THE SYSTEM SHALL include comprehensive unit tests to ensure reliability and prevent regressions  
**Acceptance Criteria**:
- ✅ Create `tests/` directory with pytest framework
- ✅ Add unit tests for core modules (ts_maps, ts_imgutil, ts_events)
- ✅ Implement integration tests for Flask routes
- ✅ Add test coverage reporting

**Validation**:
- Comprehensive test suite with unit and integration tests
- Mock objects for external dependencies (API calls, file I/O)
- Test coverage tools configured (pytest-cov)
- Continuous testing workflow established

**Sprint 02 Validation Methodology** (TASK-042, March 4, 2026):  
- ✅ 4-stage manual validation framework established:
  - **Stage 0**: Initialization & Error-Free Load (console clean, provider loaded)
  - **Stage 1**: Location Search & Map Interaction (geocoding, pan/zoom, provider switching)
  - **Stage 2**: Detection Execution (polygon drawing, tile estimation, progress tracking, cancellation)
  - **Stage 3**: Result Review & Export (bidirectional highlighting, confidence filtering, address display)
- ✅ 23 of 23 tests passed, 4 critical bugs fixed during validation
- ✅ Memory leak testing: 20-cycle stress test validated (-0.7% memory change)
- ✅ Cross-provider testing validated visual consistency

---

## 🎨 USER EXPERIENCE REQUIREMENTS (Type B)

### UX-001: Simplified Setup Process
**Status**: 🔄 **UPDATED FOR LOCAL DEPLOYMENT**  
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN new users install TowerScout, THE SYSTEM SHALL provide a streamlined setup process requiring minimal technical knowledge  
**Acceptance Criteria**:
- ✅ Create Docker-compatible / OCI containerization and GitHub Release packaging for simplified deployment (**UPDATED**: Windows 11/AMD64 CPU-first with manifest-managed assets and a GitHub Release ZIP plus GHCR-by-digest package model)
- Auto-bootstrap required model/data assets on first run using a checksummed manifest, with manual/restricted-network bundle fallback
- ✅ Provide setup wizard for initial configuration (**UPDATED**: Integrated into main interface, not separate)
- ✅ Add comprehensive documentation with screenshots
- ~~Support both standard API keys and Azure Key Vault configuration~~ **SIMPLIFIED**: Standard API keys only for local deployment

**Sprint 02 Enhancement** (TASK-038, March 2, 2026):  
- ✅ Frontend split into 27 modular files across 7 directories (managers, boundaries, providers, detection, ui, utils, root)
- ✅ Build system implemented with concatenation-based approach (<2s builds, 319.0 KB bundle)
- ✅ Pre-commit hooks ensure automatic frontend builds
- ✅ 100% backward compatibility maintained with monolithic structure

### UX-002: In-App Configuration
**Status**: 🔄 **UPDATED FOR LOCAL DEPLOYMENT**
**Priority**: MEDIUM  
**Type**: B  
**EARS**: WHEN users need to configure the application, THE SYSTEM SHALL provide a web-based interface for settings management  
**Acceptance Criteria**:
- ✅ Create settings page for API key management (Google Maps, Azure Maps)
- ✅ Add map provider selection interface (Google Maps, Azure Maps)
- ✅ Implement configuration validation and testing for all providers
- ~~Add export/import of configuration settings~~ **REMOVED**: Unnecessary for local single-user deployment
- ~~Support Azure Key Vault configuration for enterprise users~~ **REMOVED**: Over-engineered for local deployment
- ~~Provide migration assistance from legacy Bing Maps configurations~~ **REMOVED**: Not relevant for new local deployments

---

## 🏠 LOCAL DEPLOYMENT REQUIREMENTS (NEW)

### LOC-001: Setup Wizard Integration
**Priority**: CRITICAL  
**Type**: B  
**EARS**: WHEN users first run TowerScout, THE SYSTEM SHALL provide an integrated setup wizard for API key configuration  
**Acceptance Criteria**:
- Implement web-based setup wizard accessible from main interface
- Enable real-time API key validation and testing
- Auto-generate Flask secret key during setup
- Write configuration directly to `.env` file with proper permissions
- Provide clear guidance for obtaining API keys from Google/Azure
- Include provider selection and recommendation
- Support configuration updates through settings interface

### LOC-002: OCI Container Release Package
**Priority**: CRITICAL  
**Type**: C  
**EARS**: WHEN users deploy TowerScout, THE SYSTEM SHALL provide a GitHub Release ZIP package backed by a Docker-compatible / OCI image and Compose-compatible runtime configuration
**Acceptance Criteria**:
- Create Docker-compatible / OCI image targeting the validated AMD64 CPU baseline
- Provide Compose-compatible configuration for the selected runtime host
- Publish user-facing release package through GitHub Releases
- Include quick-start docs, `compose.yaml`, `.env` template, scripts, pinned GHCR image reference by digest, optional OCI archive fallback, asset manifest, checksums, troubleshooting, and recovery guidance
- Treat Podman as the preferred open-source Windows runtime target after release-support gates; `TASK-025` validated the Windows WSL engine path, while `TASK-065` still owns Docker-Desktop-free Compose-provider validation
- Preserve Docker-compatible developer/support path where licensing and endpoint policy allow
- Keep source clone-and-build as a developer/support path, not the default normal-user deployment path
- Do not promise ARM64, Mac, offline, VDI, or shared deployment until separately validated
- Provide `/api/health` and structured `/api/readiness` checks for launcher and validation use, including `starting`, `setup_required`, `degraded`, `ready`, and `fatal` readiness states

### LOC-003: CPU Performance Optimization
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN TowerScout runs on CPU-only systems, THE SYSTEM SHALL provide reasonable performance with clear expectations  
**Acceptance Criteria**:
- Automatic hardware detection (GPU/CPU/Apple Silicon MPS)
- Platform-specific batch size optimization (AMD64: 8-16, ARM64: 4-8, CPU: 4)
- Memory usage optimization for 8GB RAM constraint
- Progress indicators for CPU processing (expected 30-60 seconds)
- Performance documentation visible to users during setup
- Graceful degradation from GPU → MPS → CPU
- Memory cleanup and monitoring to prevent OOM errors

### LOC-004: End-User Error Guidance
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN errors occur, THE SYSTEM SHALL provide actionable guidance for non-technical users  
**Acceptance Criteria**:
- Replace technical stack traces with user-friendly error messages
- Provide "Test Configuration" functionality in setup wizard
- Include troubleshooting steps for common configuration issues
- Add copy-paste solutions for network connectivity problems
- Document platform-specific performance expectations clearly
- Implement configuration validation with helpful error recovery
- Create installation verification checklist

### LOC-005: Optional Model Management
**Priority**: MEDIUM  
**Type**: B  
**EARS**: WHERE advanced users want custom models, THE SYSTEM SHALL support optional volume-based model updates  
**Acceptance Criteria**:
- Default deployment uses manifest-managed release assets with no manual model path setup for normal users
- Advanced users can optionally use the documented assets volume or host-visible asset profile
- Model validation prevents incompatible models from loading
- Rollback capability if custom models fail
- Clear documentation separating basic vs advanced usage
- Model versioning and compatibility checking
- No interference with normal manifest-managed model operation

---

## 🖥️ HARDWARE COMPATIBILITY REQUIREMENTS (NEW)

### HW-001: Cross-Platform Support
**Priority**: CRITICAL  
**Type**: B  
**EARS**: WHEN TowerScout is deployed, THE SYSTEM SHALL work reliably across Intel x86_64, AMD64, and ARM64 architectures  
**Acceptance Criteria**:
- Support Windows, macOS, and Linux operating systems
- Handle architecture-specific PyTorch wheel installation
- Manage platform-specific dependency compilation (GDAL, OpenCV)
- Optimize for Apple Silicon with MPS acceleration
- Provide consistent user experience across platforms
- Document platform-specific installation notes
- Test deployment on representative hardware configurations

### HW-002: Memory Constraint Handling
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN TowerScout runs on memory-constrained systems, THE SYSTEM SHALL operate reliably within 8GB RAM  
**Acceptance Criteria**:
- Monitor memory usage during ML model loading and inference
- Implement batch size reduction for memory-constrained systems
- Clean up model weights between processing sessions
- Provide memory usage feedback to users
- Handle out-of-memory conditions gracefully
- Document minimum and recommended memory requirements
- Test on representative low-memory configurations

### UX-003: Improved Error Feedback
**Priority**: MEDIUM  
**Type**: B  
**EARS**: WHEN operations fail, THE SYSTEM SHALL provide clear, actionable error messages with guidance for resolution  
**Acceptance Criteria**:
- Replace generic error messages with specific descriptions
- Add troubleshooting tips and common solutions
- Implement progress indicators for long-running operations
- Add cancel functionality for user-initiated operations

### UX-004: Mobile Compatibility
**Priority**: LOW  
**Type**: B  
**EARS**: WHEN accessed from mobile devices, THE SYSTEM SHALL provide a responsive interface optimized for smaller screens  
**Acceptance Criteria**:
- Consolidate mobile CSS into main stylesheet
- Implement responsive design for polygon drawing
- Optimize touch interactions for map interface
- Add mobile-specific UI components

---

## 📊 CODE QUALITY REQUIREMENTS (Type A/B)

### CQ-001: Dependency Management
**Priority**: MEDIUM  
**Type**: A  
**EARS**: THE SYSTEM SHALL have properly managed dependencies with clear version specifications  
**Acceptance Criteria**:
- Update `requirements.txt` with missing dependencies
- Pin critical versions (maintain `fiona==1.9.6`)
- Add development dependencies file
- Document dependency rationale

### CQ-002: Code Formatting
**Priority**: LOW  
**Type**: A  
**EARS**: THE SYSTEM SHALL follow consistent code formatting standards  
**Acceptance Criteria**:
- Add black formatter configuration
- Implement flake8 linting rules
- Add pre-commit hooks for code quality
- Format existing codebase

---

## 🚀 PERFORMANCE REQUIREMENTS (Type B)

### PERF-001: CPU Model Support
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN GPU hardware is not available, THE SYSTEM SHALL provide CPU-based model inference with acceptable performance  
**Acceptance Criteria**:
- Implement CPU fallback detection
- Optimize CPU inference performance
- Add performance monitoring and metrics
- Document hardware requirements

**Sprint 02 Performance Benchmarks** (TASK-042, March 4, 2026):  
- ✅ **24 tiles**: ~70 seconds processing, ~158 detections
- ✅ **57 tiles**: ~160 seconds processing, ~430 detections
- ✅ **Mission-Critical Target**: <100 tiles in ~30 seconds (validated in production investigations)
- ✅ **Memory Management**: 20-cycle stress test shows -0.7% memory change (28.6 MB → 28.4 MB)
- ✅ **Frontend Performance**: Build time <2s, bundle size 319.0 KB
- ✅ **Geocoding Limits**: ~370 detections rate limit (expected Azure Maps behavior)

### PERF-002: Concurrent User Support
**Priority**: MEDIUM  
**Type**: B  
**EARS**: WHEN multiple users access the system simultaneously, THE SYSTEM SHALL handle concurrent requests without degradation  
**Acceptance Criteria**:
- Implement proper session isolation
- Add request queuing for GPU resources
- Optimize memory management
- Add load testing validation

---

## 🏭 DEPLOYMENT REQUIREMENTS (Type C)

### DEP-001: Containerization
**Priority**: MEDIUM  
**Type**: C  
**EARS**: THE SYSTEM SHALL support Docker-compatible / OCI deployment for simplified local installation
**Acceptance Criteria**:
- Create production Dockerfile/Containerfile-compatible image definition
- Add Compose-compatible configuration
- Implement `/api/health` and structured `/api/readiness` endpoints
- Document GitHub Release ZIP deployment, pinned GHCR image digest reference, optional OCI archive fallback, selected runtime-host prerequisites, and developer/support clone-build path

### DEP-002: Configuration Management
**Priority**: MEDIUM  
**Type**: C  
**EARS**: THE SYSTEM SHALL support environment-based configuration for different deployment scenarios  
**Acceptance Criteria**:
- Create configuration module
- Support development/staging/production environments
- Add configuration validation
- Document all configuration options

---

## VALIDATION CRITERIA

### Functional Testing
- All existing cooling tower detection capabilities must remain unchanged
- New features must not impact ML model accuracy
- API endpoints must maintain backward compatibility
- Session management must be secure and reliable

### Performance Testing
- Page load times must remain under 3 seconds
- Detection processing must complete within established timeframes
- Memory usage must not exceed current baselines
- CPU fallback must provide reasonable performance

### Security Testing
- No API keys or sensitive data in version control
- All user inputs must be properly validated
- Authentication must prevent unauthorized access
- Session management must be secure

### Usability Testing
- Setup process must be completable by non-technical users
- Error messages must be clear and actionable
- Mobile interface must be fully functional
- Configuration interface must be intuitive

---

## DEPENDENCIES AND CONSTRAINTS

### Technical Constraints
- Must maintain compatibility with existing ML models
- Cannot modify contents of `Model/` folder without approval
- Must support gradual migration from current SystemD setup
- Must maintain Flask framework architecture

### External Dependencies
- Google Maps API availability and pricing
- Azure Maps API availability and pricing
- Azure Key Vault service availability (enterprise deployments)
- Census TIGER data accessibility
- PyTorch framework compatibility
- Azure SDK for Python compatibility

### Resource Constraints
- Development primarily solo with occasional collaboration
- Must maintain cost-effective deployment options
- Limited GPU resources for testing
- Must work within existing infrastructure initially

---

## ACCEPTANCE TESTING STRATEGY

Each requirement will be validated through:

1. **Unit Tests**: Automated testing of individual components
2. **Integration Tests**: End-to-end workflow validation
3. **Security Tests**: Penetration testing and vulnerability scanning
4. **Performance Tests**: Load testing and resource monitoring
5. **User Acceptance Tests**: Real-world usage scenarios

Success criteria must be met before moving to the next phase of development.

---

## 🔙 LEGACY FEATURE REQUIREMENTS (Type B)

### LEG-001: Address Lookup for Detections
**Status**: ✅ **COMPLETED** (TASK-030 January 16, 2026; TASK-039 February 11, 2026)  
**Priority**: CRITICAL  
**Type**: B  
**EARS**: WHEN a cooling tower is detected, THE SYSTEM SHALL automatically retrieve the building address for each detection  
**Additional Requirements**:
- WHEN geocoding fails, THE SYSTEM SHALL provide fallback error handling and retry mechanisms  
- WHEN processing multiple detections, THE SYSTEM SHALL batch geocoding requests to optimize API usage
- WHEN addresses are cached, THE SYSTEM SHALL use cached results to reduce API quota consumption
- WHEN displaying addresses, THE SYSTEM SHALL show fallback text for failed geocoding attempts

**Acceptance Criteria**:
- ✅ Addresses automatically retrieved for all detected cooling towers
- ✅ Multi-provider fallback (Azure Maps Search → Google Geocoding) with error handling
- ✅ Caching system reduces API calls by 60-80% through spatial clustering and Redis/file cache
- ✅ Performance improved 3-4x over current client-side approach
- ✅ Rate limiting prevents API quota exhaustion
- ✅ Integration maintains existing detection workflow without UI disruption

**Validation**:
- Full geocoding functionality restored with emergency fixes (TASK-039)
- All detections show addresses correctly across providers
- Cross-provider compatibility validated (Google Maps + Azure Maps)

**Dependencies**: Environment variables (GOOGLE_API_KEY, AZURE_MAPS_SUBSCRIPTION_KEY), Redis optional  
**Reference**: [TASK-030](completed-tasks.md#sprint-01-feb-4-18-2026), [TASK-039](completed-tasks.md#sprint-01-feb-4-18-2026), [legacy-features.md](legacy-features.md#req-legacy-001-address-lookup-for-detections)

### LEG-002: Interactive Highlighting System
**Status**: ✅ **COMPLETED** (TASK-031, February 11, 2026)  
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN a user clicks on a detection address, THE SYSTEM SHALL highlight the corresponding tower on the map, AND WHEN a user clicks on a map detection, THE SYSTEM SHALL highlight the corresponding address in the results list  
**Additional Requirements**:
- WHEN highlighting occurs, THE SYSTEM SHALL provide visual feedback with distinct styling
- WHEN selections change, THE SYSTEM SHALL clear previous highlights automatically
- WHEN using keyboard navigation, THE SYSTEM SHALL support accessibility requirements

**Acceptance Criteria**:
- ✅ Bidirectional selection between detection list and map markers
- ✅ Visual feedback clearly indicates selected detection with CSS highlighting
- ✅ Selection state properly managed with automatic clearing of previous highlights
- ✅ Keyboard navigation supports accessibility (Tab, Enter, Arrow keys)
- ✅ Performance maintained with large detection sets (>1000 detections)
- ✅ Integration works across all map providers (Google, Azure, Upload)

**Validation**:
- Smooth scrolling implemented for user experience
- Cross-provider compatibility validated
- Integration with details panel (LEG-003) verified

**Dependencies**: LEG-001 (Address Lookup) for address display integration ✅ COMPLETED  
**Reference**: [TASK-031](completed-tasks.md#sprint-01-feb-4-18-2026), [legacy-features.md](legacy-features.md#req-legacy-002-interactive-highlighting-system)

### LEG-003: Enhanced Details Panel
**Status**: ✅ **COMPLETED** (TASK-032, February 11, 2026)  
**Priority**: HIGH  
**Type**: B  
**EARS**: WHEN viewing detection results, THE SYSTEM SHALL display a right-hand panel with tower-specific information including address, confidence level, and image date if available  
**Additional Requirements**:
- WHEN the panel is displayed, THE SYSTEM SHALL maintain responsive design for mobile devices
- WHEN no detection is selected, THE SYSTEM SHALL show helpful guidance in the panel
- WHEN panel content is extensive, THE SYSTEM SHALL provide scrollable content with proper layout

**Acceptance Criteria**:
- ✅ Right-hand panel displays detection details clearly with structured layout
- ✅ Panel shows address, confidence, coordinates, tile info, and metadata
- ✅ Responsive design maintains usability on mobile devices (collapsible on small screens)
- ✅ Panel integrates smoothly with existing UI layout without breaking current functionality
- ✅ Panel updates automatically when detection selection changes
- ✅ Loading states handled gracefully during address lookup

**Validation**:
- Requirements already met by existing implementation
- Integration with interactive highlighting (LEG-002) verified
- Cross-provider functionality validated

**Dependencies**: LEG-001 (Address Lookup) ✅ COMPLETED, LEG-002 (Interactive Highlighting) ✅ COMPLETED  
**Reference**: [TASK-032](completed-tasks.md#sprint-01-feb-4-18-2026), [legacy-features.md](legacy-features.md#req-legacy-003-enhanced-details-panel)

### LEG-004: False Positive Review Mode
**Priority**: MEDIUM  
**Type**: B  
**EARS**: WHEN reviewing detections, THE SYSTEM SHALL provide a dedicated mode for systematic false positive identification  
**Additional Requirements**:
- WHEN in review mode, THE SYSTEM SHALL guide users through detection validation workflow
- WHEN false positives are identified, THE SYSTEM SHALL provide easy flagging and removal mechanisms
- WHEN review is complete, THE SYSTEM SHALL provide summary statistics of flagged detections
- WHEN review sessions are interrupted, THE SYSTEM SHALL persist progress for later completion

**Acceptance Criteria**:
- Dedicated review mode with clear workflow guidance and progress indicators
- Keyboard shortcuts enable efficient review (A/R/S for Accept/Reject/Skip)
- Review progress tracking shows completion status and remaining detections
- Batch operations support efficient large-scale review (select multiple, bulk actions)
- Review sessions persist across page reloads and browser sessions
- Summary statistics show false positive removal impact and accuracy improvements
- Integration maintains existing checkbox functionality for backward compatibility

**Dependencies**: LEG-002 (Interactive Highlighting) for selection system, LEG-003 (Details Panel) for detection information display  
**Reference**: [TASK-033](task-backlog.md#task-033-manual-tower-addition-feature-), [legacy-features.md](legacy-features.md#req-legacy-004-false-positive-review-mode)

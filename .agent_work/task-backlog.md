# Task Backlog - Future Work Prioritization

**Last Updated**: March 16, 2026  
**Sprint 03 Period**: March 11 - March 25, 2026  
**Next Sprint Planning**: March 25, 2026  

---

## 🚀 SPRINT 03 ACTIVE TASKS (Moved to current-tasks.md)

### **TASK-039: Google Maps API Upgrade (ISSUE-005)** 🔴
**Status**: IN_SPRINT_03 - MOVED TO current-tasks.md  
**Type**: C (Architecture - API Migration)  
**Priority**: CRITICAL  
**Estimated Effort**: 8-20 hours  
**Hard Deadline**: April 2026

---

### **TASK-033: Manual Tower Addition Feature** 🟡
**Status**: IN_SPRINT_03 - MOVED TO current-tasks.md  
**Type**: B (Feature Development)  
**Priority**: HIGH  
**Estimated Effort**: 24 hours

---

### **TASK-036: Export System Restoration** 🟡
**Status**: IN_SPRINT_03 - MOVED TO current-tasks.md  
**Type**: B (Feature Development)  
**Priority**: HIGH  
**Estimated Effort**: 16-24 hours

---

## � HIGH PRIORITY - Sprint 04 Planning

### **TASK-046: Setup Wizard and Settings Screen** 🟡
**Status**: NOT_STARTED  
**Type**: B (Feature Development)  
**Priority**: HIGH  
**Estimated Effort**: 5-9 days (1.5-2 weeks with testing)  
**Target Sprint**: Sprint 04  
**Created**: March 16, 2026

**Objective**: Implement first-launch Setup Wizard and in-app Settings Screen for seamless API key management without manual .env file editing

**Requirements**:
- Setup Wizard: Auto-appears on first launch, multi-step flow (Welcome → API Keys → Provider → Info → Complete)
- Settings Screen: In-app modal for API key updates, debug mode toggle, cache management
- API key validation via test requests with success/error indicators
- Docker-compatible .env file persistence with backup/rollback mechanism
- Performance metrics display and resource links to documentation

**Key Features**:
- 🔑 **API Key Management**: Validate and save keys without text editor
- 🚀 **User Onboarding**: Guided setup flow for non-technical users
- ⚙️ **Settings Modal**: In-app configuration management
- 🐳 **Docker Compatible**: Host-mounted .env file updates
- 📊 **Performance Stats**: Recent detection metrics display
- 🔧 **System Controls**: Debug mode toggle, cache clearing

**Technical Components**:
- Backend: `webapp/ts_config.py` module + 5 new Flask API endpoints
- Frontend: Setup Wizard JavaScript (`setup-wizard.js`) + Settings Screen (`settings.js`)
- UI: Modal overlays with mobile-responsive design
- Safety: .env backups, validation, rollback mechanism

**Dependencies**:
- TASK-025 (Docker Containerization) - Volume mount strategy
- TASK-001 (API Key Security) - Environment variable foundation ✅ COMPLETED
- Python `python-dotenv` library (already installed)

**Success Criteria**:
- Users never need to manually edit .env files
- Setup Wizard blocks app until configuration complete
- API key validation via test requests (<5 seconds)
- Settings preserve session state (detections, map view)
- Docker volume mount persistence verified

**Task Document**: [TASK-046-setup-wizard-settings-screen.md](./tasks/TASK-046-setup-wizard-settings-screen.md)

**Notes**: Addresses major UX friction point for non-technical users. Eliminates manual .env file editing requirement. Critical for Docker-based local deployment strategy (TASK-025).

---

## �🟨 MEDIUM PRIORITY - Future Sprints

### **TASK-025: Docker Containerization** 🟡
**Status**: NOT_STARTED  
**Type**: A (Infrastructure)  
**Priority**: MEDIUM  
**Estimated Effort**: 1-2 days
**Target Sprint**: Sprint 3

**Objective**: Create Docker configuration for one-command local deployment

**Requirements**:
- Multi-stage Dockerfile with model weights
- Docker Compose configuration
- Environment variable management
- Platform-specific optimization (AMD64/ARM64)

**Notes**: Enables easier deployment for non-technical users

---

### **TASK-026: CPU Optimization** 🟡
**Status**: NOT_STARTED  
**Type**: C (Performance)  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 days
**Target Sprint**: Sprint 3-4

**Objective**: Optimize detection pipeline for CPU-only deployment scenarios

**Requirements**:
- torch.quantization implementation for model compression
- Hardware detection and batch size optimization
- Progress indicators for CPU processing
- Memory management for 8GB constraints

**Technical Notes**: Apply model quantization, optimize batch sizes for different hardware profiles

---

### **TASK-027: Enhanced Error Handling** 🟡
**Status**: NOT_STARTED  
**Type**: A (Infrastructure)  
**Priority**: MEDIUM  
**Estimated Effort**: 1-2 days
**Target Sprint**: Sprint 4

**Objective**: Improve user experience with better error messages and recovery

**Requirements**:
- User-friendly error messages for non-technical users
- Graceful degradation for API failures
- Retry mechanisms with exponential backoff
- Error reporting and logging improvements

**Dependencies**: Enhanced logging system

---

### **TASK-028: Mobile Responsiveness** 🟡
**Status**: NOT_STARTED  
**Type**: B (UI/UX)  
**Priority**: MEDIUM  
**Estimated Effort**: 2 days
**Target Sprint**: Sprint 4-5

**Objective**: Improve mobile device compatibility for field investigators

**Requirements**:
- Responsive design for tablet/mobile polygon drawing
- Touch-friendly interface elements
- Optimized map controls for small screens
- Progressive loading for mobile networks

**Notes**: Important for field outbreak investigation teams

---

### **TASK-029: Multi-Provider Fallback** 🟡
**Status**: NOT_STARTED  
**Type**: B (Reliability)  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 days
**Target Sprint**: Sprint 5

**Objective**: Implement automatic fallback between map providers for reliability

**Requirements**:
- Automatic provider switching on API failures
- Quality comparison and provider selection logic
- Rate limit handling and quota management
- Transparent failover for users

**Dependencies**: Provider abstraction layer ✅ COMPLETED

---

## 🔵 LOW PRIORITY - Backlog

### **Future Enhancement: Advanced Filtering** 🔵
**Type**: B (Feature)  
**Priority**: LOW  
**Estimated Effort**: 3-4 days

**Objective**: Add advanced filtering and search capabilities for large result sets

**Ideas**:
- Confidence threshold sliders
- Geographic filtering (distance, administrative boundaries)
- Historical detection tracking
- Batch operations on filtered results

---

### **Future Enhancement: Performance Dashboard** 🔵
**Type**: A (Monitoring)  
**Priority**: LOW  
**Estimated Effort**: 2 days

**Objective**: Create diagnostic dashboard for troubleshooting and optimization

**Ideas**:
- Processing time metrics
- GPU/CPU utilization monitoring
- API usage tracking
- System health indicators

---

### **Future Enhancement: User Preferences** 🔵
**Type**: B (UX)  
**Priority**: LOW  
**Estimated Effort**: 1-2 days

**Objective**: Add user preference storage and customization

**Ideas**:
- Default map provider selection
- Saved search areas
- Custom confidence thresholds
- Interface layout preferences

---

## 📅 Sprint Planning Guidelines

### **Capacity Management**
- **Sprint Duration**: 2 weeks (10 working days)
- **Estimated Velocity**: 8-12 days per sprint
- **Buffer Time**: 20% for unexpected issues and technical debt

### **Sprint Composition Strategy**
- **Mix**: 70% feature development (Type B), 20% infrastructure (Type A), 10% architecture (Type C)
- **Risk Balance**: Include 1 low-risk task per sprint for momentum
- **Dependencies**: Ensure prerequisite tasks completed before dependent work

### **Priority Adjustment Triggers**
1. **User Feedback**: Outbreak investigation teams report critical workflow gaps
2. **Technical Debt**: Performance issues impact user experience
3. **External Changes**: API changes require urgent adaptation
4. **Security Issues**: Vulnerabilities discovered requiring immediate attention

### **Sprint Planning Process**
1. **Review Completed Work**: Update effort estimates based on actual completion times
2. **Assess Dependencies**: Verify prerequisite tasks are ready
3. **Capacity Planning**: Consider team availability and external commitments  
4. **Risk Assessment**: Identify potential blockers and mitigation strategies
5. **Sprint Goal Setting**: Define clear success criteria for the sprint

### **Backlog Maintenance**
- **Weekly**: Review and update task priorities based on progress and feedback
- **Bi-weekly**: Detailed effort estimation review and dependency validation
- **Monthly**: Strategic priority adjustment and long-term roadmap alignment

## 🎯 Long-Term Objectives

### **Phase 1: Core Features (Sprints 1-2)**
- Complete address lookup and legacy feature restoration
- Establish stable foundation for outbreak investigation workflows

### **Phase 2: Deployment Ready (Sprints 3-4)**
- Docker containerization and CPU optimization
- Enhanced error handling and mobile responsiveness

### **Phase 3: Advanced Features (Sprints 5-6)**
- Multi-provider reliability and advanced filtering
- Performance monitoring and user customization

### **Success Metrics**
- **User Experience**: Outbreak investigation teams can complete workflows without technical assistance
- **Reliability**: 99%+ uptime for critical detection operations
- **Performance**: <30 seconds processing for <100 tiles on consumer hardware
- **Accessibility**: One-command deployment on Windows/Mac/Linux systems
# Decision Record 010: Local Deployment Strategy Adoption

**Date**: January 5, 2026  
**Status**: Approved  
**Decision Maker**: Development Team + User Feedback  

## Decision

Transform TowerScout deployment model from **hosted service** to **local deployment on individual user devices** (epidemiologists, researchers, health departments). This fundamentally changes architecture priorities from enterprise security and scalability to installation simplicity and broad hardware compatibility.

## Context

TowerScout development began with hosted service assumptions, implementing enterprise-grade features including authentication systems, Azure Key Vault integration, multi-tenant security, and complex provider fallback mechanisms. However, user feedback and deployment analysis revealed that the target audience (epidemiologists, researchers) strongly prefers self-contained, locally-deployed tools.

**User Feedback Drivers**:
- Preference for tools that run on their own devices
- Desire for offline operation after initial setup  
- Reluctance to depend on external hosted services
- Need for simple installation without technical expertise
- Preference for physical access control over logical authentication

## Options Evaluated

### Option A: Continue Hosted Service Model
**Pros**:
- Leverages existing enterprise infrastructure work
- Centralizable updates and maintenance
- Consistent user experience across deployments
- Professional hosting capabilities

**Cons**:
- Complex deployment requiring infrastructure expertise
- Ongoing hosting and maintenance costs
- User dependency on external service availability
- Authentication barriers for simple use cases
- Over-engineered for target audience needs

### Option B: Hybrid Deployment (Both Options)
**Pros**:
- Supports both enterprise and individual users
- Preserves existing enterprise investment
- Flexible deployment options

**Cons**:
- Doubles maintenance complexity
- Splits development focus
- Increases testing and validation requirements
- Confusing user experience with multiple options

### Option C: Local Deployment Only (Selected)
**Pros**:
- Focused development on user priority
- Eliminates hosting complexity and costs  
- Enables offline operation
- Physical access control sufficient for most users
- Simplifies architecture significantly
- Better hardware utilization (user's GPU/CPU)
- One-command Docker deployment possible

**Cons**:
- User devices must meet hardware requirements
- Users responsible for their own updates
- Loss of centralized monitoring capabilities
- Requires broader hardware compatibility testing

## Rationale

**Option C (Local Deployment Only) selected** based on:

1. **User Needs Alignment**: Target users consistently prefer self-contained tools over hosted services
2. **Complexity Reduction**: Eliminates enterprise complexity that provides no value for individual users
3. **Cost Efficiency**: No hosting infrastructure or ongoing operational costs
4. **Security Simplification**: Physical access control sufficient for local deployment scenarios
5. **Performance**: User's hardware often superior to shared hosting resources
6. **Existing Foundation**: Core functionality (Azure Maps, error handling, detection) remains valuable

## Impact

### Architecture Changes
- **Authentication eliminated**: Physical access control replaces logical authentication
- **Configuration simplified**: File-based `.env` configuration instead of enterprise key management
- **User interface enhanced**: Setup wizard and settings management for non-technical users
- **Hardware detection added**: CPU/GPU/MPS detection for diverse local hardware
- **Error handling user-focused**: Non-technical error messages replace technical diagnostics

### Task Prioritization Changes
- **Obsolete Tasks**: TASK-004 (Authentication), TASK-009 (Azure Key Vault), TASK-010 (Multi-Provider Security), TASK-011 (Provider Migration)
- **Simplified Tasks**: TASK-018 (Session Management), TASK-002 (Input Validation), TASK-005 (Testing), TASK-021 (Docker)  
- **New Priorities**: TASK-025 (Setup Wizard), TASK-026 (Multi-Arch Docker), TASK-027 (CPU Optimization), TASK-028 (User Experience), TASK-029 (Model Management)

### Specific Task Modifications Implemented (January 7, 2026)

#### **Azure Maps Migration Section**
- **Removed**: "dual authentication (standard keys + Azure Key Vault)" 
- **Updated**: "standard API keys" only for local deployment
- **Removed**: "Azure Key Vault Integration: Ready for enterprise deployment" from migration complete section

#### **TASK-006: Configuration Management System**
- **Changed**: "web interface for configuration management" → "simple file-based interface"
- **Removed**: Admin panel web interface implementation steps
- **Simplified**: Interface management from "Web interface" → "Simple interface"
- **Maintained**: Core configuration validation and export/import functionality

#### **TASK-012: Map Provider Selection Interface**
- **Removed**: "Legacy Bing" from provider list (Google, Azure only)
- **Changed**: "admin panel" → "simple provider configuration interface"
- **Updated**: "Admin interface manages" → "Simple interface manages"
- **Changed**: "administrators" → "users" for migration progress visibility
- **Simplified**: Configuration management approach for single-user local deployment

#### **Enterprise Features Eliminated**
- **Security Testing**: Removed penetration testing and multi-user load testing requirements
- **Authentication Systems**: Confirmed removal of all authentication dependencies
- **Key Vault Integration**: Eliminated all Azure Key Vault integration references
- **Multi-Tenancy**: Removed admin panels and multi-tenant security considerations

#### **Dependencies Fixed**
- **TASK-018**: Dependency on obsolete TASK-004 (Authentication) removed
- **Configuration Tasks**: Simplified to focus on local deployment configuration management
- **Testing Framework**: Enterprise testing requirements removed or simplified for single-user scenarios

### Development Impact
- **Timeline**: Shortened by eliminating complex enterprise features
- **Focus**: Shifted to user experience and hardware compatibility
- **Testing**: Requires cross-platform and diverse hardware validation
- **Documentation**: User-focused instead of enterprise deployment guides

### Preserved Value
- **Error Handling Infrastructure** (TASK-003): 85% value retention
- **API Security** (TASK-001): 100% value retention  
- **Azure Maps Integration** (TASK-008, TASK-024): 95% value retention
- **Testing Framework** (TASK-005): 60% value retention (simplified)

## Implementation Strategy

### Phase 1: Complete Azure Maps Foundation
- Finish current Azure Maps runtime issue debugging
- Validate stable foundation for local deployment tasks

### Phase 2: Local Deployment Core (NEW)
1. **Setup Wizard Integration** (TASK-025) - API key configuration through web interface
2. **Multi-Architecture Docker** (TASK-026) - AMD64/ARM64 containers with embedded models  
3. **CPU Performance** (TASK-027) - Hardware detection and optimization
4. **User Experience** (TASK-028) - Non-technical error messages and guidance
5. **Model Management** (TASK-029) - Optional advanced features

### Phase 3: Validation & Distribution
- Cross-platform testing
- Docker Hub distribution setup
- User documentation and troubleshooting guides

## Review Criteria

This decision will be reviewed based on:
- **Installation Success Rate**: >95% across target platforms
- **User Satisfaction**: Positive feedback on ease of setup
- **Support Burden**: <20% of users requiring technical assistance
- **Adoption Rate**: Increased usage among target epidemiologist/researcher audience

## Related Decisions

- **Decision 002**: ML Model Protection (unchanged - models remain protected)
- **Decision 003**: Security First Approach (adapted for local deployment context)
- **Decision 006**: Azure Maps Migration (completed - enterprise features removed)
- **Decision 009**: Error Handling Infrastructure (enhanced for end-user guidance)

This decision represents a strategic pivot based on user feedback and practical deployment considerations, transforming TowerScout from an enterprise application to a user-friendly research tool.
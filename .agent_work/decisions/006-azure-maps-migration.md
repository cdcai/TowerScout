# Decision Record 006: Bing Maps to Azure Maps Migration

**Date**: December 10, 2025  
**Status**: Approved  
**Decision Maker**: Development Team  

## Decision

Migrate from Bing Maps to Azure Maps as the primary satellite imagery provider while maintaining Google Maps as an alternative user-selectable option. Implement dual authentication supporting both standard subscription keys and Azure Key Vault integration for enterprise deployments.

## Context

Recent organizational guidance requires adjusting certain elements of development plans to retain testing capabilities during development. Two primary changes were mandated:

1. **Provider Migration**: Replace all Bing Maps instances/connections with Azure Maps
2. **Enterprise Authentication**: Incorporate logic for Azure Key Vault integration alongside standard API key authentication

The current system uses:
- **Bing Maps**: Primary provider via `ts_bmaps.py` with plain text API key storage
- **Google Maps**: Alternative provider via `ts_gmaps.py`  
- **API Keys**: Loaded from environment variables (recent security fix)

## Options Evaluated

### Option A: Direct Bing → Azure Replacement (Selected)
**Pros**:
- Maintains existing dual-provider architecture
- Minimal UI changes required
- Leverages existing Map abstraction layer
- Supports enterprise Key Vault requirements
- Maintains Google Maps as fallback option

**Cons**:
- Requires coordinate system transformation (lng,lat vs lat,lng)
- Loss of metadata features (vintage date)
- Complex Azure SDK integration required
- Extensive validation needed for coordinate accuracy

### Option B: Add Azure Maps as Third Provider
**Pros**:
- No breaking changes to existing providers
- Gradual migration possible
- Lower risk implementation

**Cons**:
- Increased complexity with three providers
- Higher maintenance burden
- Doesn't meet directive to replace Bing Maps
- Additional UI complexity for provider selection

### Option C: Azure Maps Only (Single Provider)
**Pros**:
- Simplified architecture
- Reduced maintenance burden
- Enterprise-focused approach

**Cons**:
- Loss of provider redundancy
- Higher risk if Azure Maps has issues
- Doesn't maintain Google Maps option
- Single point of failure

## Rationale

Option A was selected because:

1. **Compliance**: Directly addresses organizational directive to replace Bing Maps with Azure Maps

2. **Enterprise Integration**: Azure Key Vault support meets enterprise authentication requirements while maintaining standard API key fallback

3. **Risk Management**: Maintaining Google Maps provides provider redundancy and fallback capabilities during migration

4. **Architecture Leverage**: Existing Map abstraction layer (`ts_maps.py`) enables clean provider swapping with minimal core application changes

5. **Coordinate System Handling**: While lng,lat vs lat,lng transformation is complex, it's manageable with proper validation and can be contained within the provider implementation

6. **Testing Continuity**: Dual-provider support ensures testing capabilities remain intact throughout development

## Impact

**Technical Implementation**:
- **New Provider**: Create `ts_azure_maps.py` implementing Map interface
- **Coordinate Transformation**: Handle lng,lat vs lat,lng order reversal with extensive validation
- **Authentication**: Implement `AzureKeyVaultConfig` with `DefaultAzureCredential` fallback chain
- **URL Structure**: Complete reconstruction from Bing's path-based to Azure's query-based API
- **Metadata Loss**: Remove features dependent on imagery vintage dates

**API Changes**:
- **Breaking**: Coordinate order transformation requires validation across all detection workflows
- **Authentication**: New environment variables (`AZURE_MAPS_SUBSCRIPTION_KEY`, `AZURE_KEY_VAULT_URL`)
- **Dependencies**: Add `azure-keyvault-secrets` and `azure-identity` packages
- **Error Handling**: Enhanced authentication error handling and provider fallback

**User Experience**:
- **Provider Selection**: Update UI to offer Google Maps and Azure Maps options
- **Migration**: Provide migration assistance for existing Bing Maps configurations
- **Enterprise**: Support both simple API key and Key Vault authentication methods

**Deployment**:
- **Container Support**: Docker images with Azure SDK and Managed Identity support
- **Configuration**: Environment-based config supporting both authentication methods
- **Documentation**: Comprehensive setup guides for both standard and enterprise deployments

## Implementation Timeline

**Phase 1: Core Provider (1 week)**
- Implement `ts_azure_maps.py` with basic API integration
- Add coordinate system transformation and validation
- Create comprehensive unit tests for coordinate accuracy

**Phase 2: Authentication Integration (1 week)**  
- Implement Azure Key Vault configuration class
- Add fallback authentication chain (Key Vault → Environment → Error)
- Test authentication in both local and container environments

**Phase 3: System Integration (1 week)**
- Integrate Azure Maps into main application
- Implement provider selection UI updates
- Add migration and fallback logic

**Phase 4: Validation & Testing (1 week)**
- ML model accuracy comparison across providers
- Coordinate precision validation
- Load testing with provider failover
- Documentation and deployment testing

## Success Criteria

**Functional Requirements**:
- [ ] Azure Maps provider fully implements Map interface
- [ ] Coordinate transformations maintain geographic accuracy within 1-meter precision
- [ ] Authentication works with both API keys and Azure Key Vault
- [ ] Provider fallback prevents service interruption
- [ ] ML detection accuracy maintained across all providers

**Technical Requirements**:
- [ ] All existing detection workflows function unchanged
- [ ] Container deployment supports Azure Managed Identity
- [ ] API key rotation possible without service restart
- [ ] Provider switching maintains user session state
- [ ] Comprehensive error handling and logging

**Documentation Requirements**:
- [ ] Complete setup documentation for both authentication methods
- [ ] Migration guide for existing Bing Maps deployments
- [ ] Troubleshooting guide for provider and authentication issues
- [ ] Azure Key Vault setup and configuration guide

## Review

This decision will be reviewed after Phase 2 completion (Azure Key Vault integration) to assess:
- Authentication complexity and reliability in different deployment environments
- Coordinate transformation accuracy and ML model impact
- Provider fallback effectiveness and error handling
- Enterprise adoption and Key Vault integration success

Scheduled review date: After TASK-009 completion (Azure Key Vault Integration)

## Dependencies

**Technical Dependencies**:
- Azure SDK for Python compatibility
- Azure Key Vault service availability
- Docker Azure CLI integration for local development
- Managed Identity configuration for production deployments

**Organizational Dependencies**:
- Azure subscription and Key Vault provisioning
- Enterprise authentication policy compliance
- Testing environment Azure resource access
- Production deployment Azure infrastructure
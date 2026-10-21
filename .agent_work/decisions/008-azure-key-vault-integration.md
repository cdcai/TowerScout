# Decision Record 008: Azure Key Vault Integration Architecture

**Date**: December 10, 2025  
**Status**: ❌ **OBSOLETE FOR LOCAL DEPLOYMENT**  
**Decision Maker**: Development Team  
**Superseded By**: [Decision Record 010: Local Deployment Strategy](010-local-deployment-strategy.md)

## ❌ OBSOLETE NOTICE

This decision record is **OBSOLETE** as of January 7, 2026, following the adoption of a local deployment only strategy (Decision Record 010). Azure Key Vault integration is not required for local deployment scenarios where physical access control is sufficient.

**Reason for Obsolescence**: TowerScout deployment model changed from hosted service to local deployment on individual user devices. Enterprise features including Azure Key Vault integration are unnecessary complexity for single-user local deployment scenarios.

**Current Approach**: Standard environment variable configuration via `.env` files as documented in the local deployment strategy.

---

## Original Decision (Now Obsolete)

Implement dual authentication architecture supporting both standard Azure Maps subscription keys via environment variables and enterprise Azure Key Vault integration using `DefaultAzureCredential` with comprehensive fallback mechanisms.

## Context

Enterprise deployment requirements mandate support for Azure Key Vault secret management while maintaining compatibility with standard API key deployment methods. The system must work in multiple deployment scenarios:

**Standard Deployments**:
- Local development with environment variables
- Simple container deployments with API keys
- Cloud deployments without Key Vault access

**Enterprise Deployments**:
- Azure Key Vault centralized secret management
- Managed Identity authentication in Azure containers
- Audit trails and access control for API keys
- Key rotation without application restart

## Options Evaluated

### Option A: Key Vault Only
**Implementation**: Require Azure Key Vault for all deployments
**Pros**:
- Simplified authentication code
- Enhanced security for all deployments
- Consistent secret management approach

**Cons**:
- Blocks local development without Azure setup
- Increases deployment complexity for simple use cases
- Higher barrier to entry for new users
- Additional Azure infrastructure requirements

### Option B: Environment Variables Only  
**Implementation**: Continue using only environment variables
**Pros**:
- Simple deployment model
- No additional Azure dependencies
- Easy local development setup

**Cons**:
- Doesn't meet enterprise Key Vault requirements
- No centralized secret management
- Manual key rotation required
- No audit trails for secret access

### Option C: Dual Authentication with Fallback Chain (Selected)
**Implementation**: Try Key Vault first, fallback to environment variables
```python
def get_azure_maps_key():
    # Try Key Vault if configured
    if os.getenv('AZURE_KEY_VAULT_URL'):
        try:
            return get_from_key_vault('azure-maps-subscription-key')
        except Exception:
            pass
    
    # Fallback to environment variable
    return os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
```

**Pros**:
- Supports both enterprise and standard deployments
- Graceful degradation when Key Vault unavailable
- No deployment method locked out
- Enterprise features available when needed

**Cons**:
- More complex authentication logic
- Multiple failure points to handle
- Additional testing scenarios required

## Rationale

Option C was selected because:

1. **Deployment Flexibility**: Supports the full range of deployment scenarios from local development to enterprise production without blocking any use case

2. **Enterprise Compliance**: Provides Azure Key Vault integration for organizations requiring centralized secret management and audit trails

3. **Development Continuity**: Maintains simple environment variable setup for development and testing, ensuring development workflow remains unblocked

4. **Graceful Degradation**: System continues operating even if Key Vault is temporarily unavailable, preventing single point of failure

5. **Progressive Enhancement**: Organizations can start with simple API keys and upgrade to Key Vault when ready, no migration required

## Implementation Architecture

### Authentication Flow

```python
class AzureKeyVaultConfig:
    def __init__(self, vault_url: str = None):
        self.vault_url = vault_url or os.getenv('AZURE_KEY_VAULT_URL')
        self.credential = DefaultAzureCredential() if self.vault_url else None
        self.client = SecretClient(
            vault_url=self.vault_url, 
            credential=self.credential
        ) if self.vault_url else None
    
    def get_secret(self, secret_name: str, fallback_env_var: str = None) -> str:
        """Get secret from Key Vault with environment variable fallback"""
        
        # Tier 1: Azure Key Vault
        if self.client:
            try:
                secret = self.client.get_secret(secret_name)
                return secret.value
            except Exception as e:
                logger.warning(f"Key Vault unavailable for {secret_name}: {e}")
        
        # Tier 2: Environment variable fallback
        if fallback_env_var:
            env_value = os.getenv(fallback_env_var)
            if env_value:
                return env_value
        
        # Tier 3: Error
        raise EnvironmentError(f"Secret {secret_name} not available via Key Vault or environment variable {fallback_env_var}")
```

### DefaultAzureCredential Chain

The `DefaultAzureCredential` attempts authentication in this order:
1. **EnvironmentCredential**: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
2. **WorkloadIdentityCredential**: Azure Kubernetes workload identity
3. **ManagedIdentityCredential**: Azure VM/Container managed identity  
4. **AzureCliCredential**: Local development with `az login`
5. **AzurePowerShellCredential**: Local development with Azure PowerShell
6. **VisualStudioCodeCredential**: VS Code Azure extension

### Environment Variable Configuration

**Standard Deployment**:
```bash
AZURE_MAPS_SUBSCRIPTION_KEY=your_azure_maps_key_here
```

**Enterprise Deployment**:
```bash
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
AZURE_CLIENT_ID=your_managed_identity_client_id  # Optional: Explicit managed identity
```

**Local Development**:
```bash
# Option 1: Direct API key
AZURE_MAPS_SUBSCRIPTION_KEY=your_dev_key

# Option 2: Key Vault (requires az login)
AZURE_KEY_VAULT_URL=https://dev-vault.vault.azure.net/
```

## Error Handling Strategy

### Authentication Failure Scenarios

**Key Vault Unavailable**:
```python
try:
    key = vault_config.get_secret('azure-maps-subscription-key')
except Exception as e:
    logger.warning(f"Key Vault authentication failed: {e}")
    # Fallback to environment variable
    key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    if not key:
        raise ConfigurationError("No Azure Maps key available")
```

**Network Connectivity Issues**:
- Timeout handling for Key Vault requests
- Retry logic with exponential backoff
- Fallback to cached credentials if available
- Clear error messages for troubleshooting

**Permission Issues**:
- Specific error messages for insufficient Key Vault permissions
- Documentation for required Key Vault access policies
- Fallback to environment variables with security warnings

### Monitoring and Alerting

```python
class AuthenticationMetrics:
    def record_auth_method(self, method: str, success: bool):
        # Record which authentication method was used
        logger.info(f"Authentication method: {method}, Success: {success}")
        
    def record_key_vault_failure(self, error: Exception):
        # Monitor Key Vault failures for alerting
        logger.error(f"Key Vault failure: {error}")
```

## Security Considerations

### Key Vault Access Control

**Required Permissions**:
- `Key Vault Secrets User` role for the application managed identity
- `Get` permission on specific secrets (azure-maps-subscription-key)
- Network access from application subnet to Key Vault

**Security Best Practices**:
- Use managed identity instead of service principal when possible
- Restrict Key Vault network access to application subnets
- Enable Key Vault audit logging
- Implement secret rotation without application restart

### Environment Variable Security

**Standard Deployment Security**:
- Use Azure Container Instances environment variables
- Avoid logging environment variables in application logs
- Use Azure Key Vault references in ARM templates when possible
- Implement secret scanning in CI/CD pipelines

## Deployment Scenarios

### Local Development
```bash
# Method 1: Direct API key (simplest)
export AZURE_MAPS_SUBSCRIPTION_KEY="your_key"

# Method 2: Key Vault (requires az login)
az login
export AZURE_KEY_VAULT_URL="https://dev-vault.vault.azure.net/"
```

### Container Deployment (Standard)
```dockerfile
ENV AZURE_MAPS_SUBSCRIPTION_KEY=""
# Key provided at runtime via docker run -e or docker-compose
```

### Container Deployment (Enterprise)
```dockerfile
ENV AZURE_KEY_VAULT_URL=""
# Managed identity configured at container runtime
```

### Kubernetes Deployment
```yaml
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: towerscout-service-account  # With managed identity
  containers:
  - name: towerscout
    env:
    - name: AZURE_KEY_VAULT_URL
      value: "https://prod-vault.vault.azure.net/"
```

## Testing Strategy

### Unit Tests
```python
class TestAzureAuthentication(unittest.TestCase):
    @patch('azure.keyvault.secrets.SecretClient')
    def test_key_vault_success(self, mock_client):
        # Test successful Key Vault authentication
        
    @patch('azure.keyvault.secrets.SecretClient')
    def test_key_vault_fallback(self, mock_client):
        # Test fallback to environment variables
        
    def test_environment_variable_only(self):
        # Test environment variable authentication
        
    def test_no_authentication_available(self):
        # Test error handling when no auth method works
```

### Integration Tests
- Test authentication in actual Azure environment
- Verify managed identity works in container deployment
- Test Key Vault permissions and network connectivity
- Validate fallback behavior under various failure conditions

### Load Testing
- Test Key Vault performance under load
- Verify credential caching behavior
- Test authentication retry logic
- Monitor Key Vault rate limiting

## Migration Path

### Phase 1: Environment Variable Foundation
- Implement environment variable authentication
- Add configuration validation and error handling
- Test in all deployment scenarios

### Phase 2: Key Vault Integration
- Add Azure SDK dependencies
- Implement `AzureKeyVaultConfig` class  
- Add `DefaultAzureCredential` authentication
- Test fallback mechanisms

### Phase 3: Enterprise Features
- Add audit logging for authentication events
- Implement secret rotation handling
- Add monitoring and alerting
- Document enterprise deployment procedures

## Success Criteria

**Functional Requirements**:
- [ ] Authentication works with environment variables in all scenarios
- [ ] Key Vault authentication works with managed identity
- [ ] Fallback from Key Vault to environment variables functions correctly
- [ ] Clear error messages for all authentication failure scenarios
- [ ] Local development works with both authentication methods

**Security Requirements**:
- [ ] No secrets logged in application logs
- [ ] Key Vault access follows principle of least privilege
- [ ] Managed identity preferred over service principal authentication
- [ ] Secret rotation possible without application restart

**Operational Requirements**:
- [ ] Authentication monitoring and alerting implemented
- [ ] Documentation covers all deployment scenarios
- [ ] Troubleshooting guides for common authentication issues
- [ ] Performance acceptable under production load

## Review

This decision will be reviewed after implementation completion to assess:

**Technical Effectiveness**:
- Authentication reliability across deployment scenarios
- Performance impact of Key Vault integration
- Complexity of troubleshooting authentication issues
- Developer experience with dual authentication setup

**Security Effectiveness**:
- Key Vault integration security posture
- Secret management audit trail quality
- Incident response effectiveness for authentication failures

**Operational Effectiveness**:
- Deployment complexity across different environments
- Monitoring and alerting effectiveness
- Documentation completeness and clarity

**Scheduled Review**: After TASK-009 completion (Azure Key Vault Integration)
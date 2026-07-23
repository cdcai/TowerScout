# Azure Maps Local Setup Guide

## Overview

TowerScout's Azure Maps integration is designed for **local deployment only**, using simple subscription key authentication. This guide explains how to configure Azure Maps for individual users deploying TowerScout on their local devices.

---

## 🔑 **Local Deployment Authentication**

### **Subscription Key Authentication** ⭐ **ONLY METHOD SUPPORTED**

**Best for**: Local deployment on individual user devices (epidemiologists, researchers, health departments)

**Configuration**:
```bash
# .env file
AZURE_MAPS_SUBSCRIPTION_KEY=your_subscription_key_here
```

**How to obtain**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Create an Azure Maps Account (or use existing)
3. Navigate to "Keys and Endpoint" 
4. Copy the Primary Key

**Key Types**:
- **Primary Key**: Use for production
- **Secondary Key**: Use for key rotation without downtime
- Both keys have identical permissions and rate limits

**Security Features**:
- Keys can be regenerated without affecting the other key
- Rate limiting and usage monitoring through Azure Portal
- Stored securely in `.env` file (never committed to version control)

---

## 🏗️ **TowerScout Local Setup Implementation**

### **How Azure Maps Keys Are Accessed**

The application follows this authentication flow:

```python
# 1. Load from environment variables (ts_azure_maps.py)
def __init__(self, subscription_key: str):
    if not subscription_key or not subscription_key.strip():
        raise ConfigurationError("Azure Maps subscription key is required")
    self.subscription_key = subscription_key.strip()

# 2. Validate and initialize (towerscout.py)
def load_api_keys():
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    if azure_key:
        return AzureMaps(azure_key)
    else:
        logger.warning("Azure Maps not available - no subscription key")
        return None

# 3. Use in API calls (ts_azure_maps.py)
def get_url(self, tile):
    url = f"{self.base_url}?api-version={self.api_version}&subscription-key={self.subscription_key}&..."
    return url
```

### **Security Best Practices Implemented**

✅ **Environment Variables**: No hardcoded keys in source code
✅ **Input Validation**: Keys are validated before use  
✅ **Error Handling**: Clear error messages without exposing keys
✅ **Logging**: Keys are never logged or exposed in debugging output

---

## 🏢 **Enterprise vs Individual Key Management**

### **Individual/Development Usage**

```bash
# Simple subscription key approach
AZURE_MAPS_SUBSCRIPTION_KEY=your_personal_subscription_key
DEFAULT_MAP_PROVIDER=azure
```

**Characteristics**:
- Single subscription key for entire application
- Direct billing to personal/company Azure account
- Straightforward setup and management
- Suitable for small teams and development environments

### **Enterprise Usage Options**

#### **Option 1: Centralized Subscription Key** ⭐ **RECOMMENDED**
```bash
# Single enterprise subscription key
AZURE_MAPS_SUBSCRIPTION_KEY=enterprise_subscription_key_from_it_department
DEFAULT_MAP_PROVIDER=azure
```

**Benefits**:
- Centralized billing and cost management
- IT department controls key rotation
- Simple deployment across multiple environments
- No additional authentication complexity

#### **Option 2: Azure Key Vault Integration** 🔒 **MOST SECURE**
```bash
# Key Vault configuration (TASK-009 implementation)
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
AZURE_MAPS_KEY_NAME=towerscout-azure-maps-key
AZURE_MAPS_AUTH_METHOD=keyvault
```

**Benefits**:
- Centralized secret management
- Key rotation without application restart
- Audit trails for key access
- Integration with enterprise security policies

#### **Option 3: Service Principal (AAD)** 🏢 **ENTERPRISE IDENTITY**
```bash
# Azure Active Directory authentication
AZURE_MAPS_AUTH_METHOD=aad
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=towerscout-app-registration
AZURE_CLIENT_SECRET=service-principal-secret
```

**Benefits**:
- Integration with existing identity systems
- Role-based access control
- MFA and conditional access support
- No shared secrets between teams

---

## 📊 **Key Management Comparison**

| Method | Individual | Small Team | Enterprise | Security Level |
|--------|------------|------------|------------|----------------|
| **Subscription Key** | ✅ Perfect | ✅ Good | ⚠️ OK | Medium |
| **Key Vault** | ⚠️ Overkill | ✅ Good | ✅ Excellent | High |
| **AAD Service Principal** | ❌ Too Complex | ⚠️ OK | ✅ Excellent | Very High |
| **SAS Tokens** | ❌ Complex | ⚠️ Special Cases | ✅ Advanced Scenarios | High |

---

## 🔄 **Key Rotation Procedures**

### **Subscription Key Rotation** (Zero Downtime)

```bash
# Phase 1: Add secondary key
AZURE_MAPS_SUBSCRIPTION_KEY=secondary_key_here

# Phase 2: Regenerate primary key in Azure Portal
# Phase 3: Update to new primary key
AZURE_MAPS_SUBSCRIPTION_KEY=new_primary_key_here

# Phase 4: Regenerate secondary key for next rotation
```

### **Automated Key Rotation** (Enterprise)

```python
# Future enhancement for TASK-009
class AzureKeyVaultRotation:
    def rotate_azure_maps_key(self):
        # 1. Generate new key in Azure Maps
        # 2. Store in Key Vault
        # 3. Update application configuration
        # 4. Revoke old key after validation period
        pass
```

---

## 🎯 **Recommendations by Use Case**

### **Individual Developers**
```bash
# Recommended configuration
AZURE_MAPS_SUBSCRIPTION_KEY=your_personal_key
AZURE_MAPS_AUTH_METHOD=subscription_key
DEFAULT_MAP_PROVIDER=azure
```

### **Small Teams (2-10 developers)**
```bash
# Shared subscription key with team Azure account
AZURE_MAPS_SUBSCRIPTION_KEY=team_shared_key
AZURE_MAPS_AUTH_METHOD=subscription_key
DEFAULT_MAP_PROVIDER=azure

# Optional: Basic monitoring
DETAILED_LOGGING=true
LOG_LEVEL=INFO
```

### **Enterprise (10+ users, compliance requirements)**
```bash
# Key Vault integration (requires TASK-009)
AZURE_KEY_VAULT_URL=https://enterprise-vault.vault.azure.net/
AZURE_MAPS_KEY_NAME=towerscout-maps-key
AZURE_MAPS_AUTH_METHOD=keyvault

# Enterprise security settings
SECURE_COOKIES=true
SESSION_TIMEOUT=15
DETAILED_LOGGING=true
LOG_LEVEL=WARNING
```

---

## 🚨 **Security Considerations**

### **Current Implementation Security**
- ✅ Environment variable-based configuration
- ✅ No keys stored in source code
- ✅ Input validation and sanitization
- ✅ Error handling without key exposure
- ✅ HTTPS-only API communications

### **Enterprise Security Enhancements** (Future)
- **Key Vault Integration** (TASK-009): Centralized secret management
- **AAD Integration**: Role-based access control  
- **Network Security**: VNet integration, private endpoints
- **Compliance**: SOC 2, FedRAMP compliance options

### **Development vs Production**

**Development Environment**:
```bash
# Development settings
FLASK_ENV=development
AZURE_MAPS_SUBSCRIPTION_KEY=dev_key_with_lower_limits
MOCK_API_CALLS=false  # Use real APIs for accurate testing
```

**Production Environment**:
```bash
# Production settings  
FLASK_ENV=production
SECURE_COOKIES=true
AZURE_MAPS_SUBSCRIPTION_KEY=production_key_with_higher_limits
DETAILED_LOGGING=false  # Avoid logging sensitive data
```

---

## 📈 **Usage Monitoring & Cost Management**

### **Azure Maps Pricing Tiers**

| Tier | Price per 1K Requests | Included Requests/Month |
|------|----------------------|-------------------------|
| **Gen2 S0** | $0.50 | None |
| **Gen2 S1** | $4.00 | 250K |
| **Gen1 S0** | $5.00 | 25K |
| **Gen1 S1** | $5.00 | 125K |

### **Cost Monitoring Configuration**

```bash
# Enable usage tracking
AZURE_MAPS_TRACK_USAGE=true
AZURE_MAPS_COST_ALERTS=true
AZURE_MAPS_MONTHLY_BUDGET=100  # USD

# Performance optimization to reduce costs
AZURE_MAPS_CACHE_TILES=true
AZURE_MAPS_BATCH_REQUESTS=true
```

### **Enterprise Cost Management**

- **Budgets**: Set spending limits in Azure Portal
- **Alerts**: Automated notifications at 50%, 80%, 100% of budget
- **Usage Analytics**: Detailed reporting by application/team
- **Cost Allocation**: Tag resources for department billing

---

## ⚡ **Performance Expectations (Updated March 2026)**

### **Detection Performance Benchmarks** (Validated TASK-042)

Azure Maps as Primary Provider:

| Workload | Duration | Detections | Notes |
|----------|----------|------------|-------|
| **24 tiles** | ~70 seconds | ~158 detections | Typical neighborhood scan |
| **57 tiles** | ~160 seconds | ~430 detections | Mid-size investigation area |
| **<100 tiles** | ~30 seconds (target) | Variable | Mission-critical performance target |

**Performance Breakdown**:
- **Tile Download**: ~30-40% of total time (Azure Maps optimized with 32% improvement)
- **YOLOv5 Detection**: ~40-50% of total time (GPU batch processing)
- **EfficientNet Classification**: ~5-10% of total time (threshold filtering)
- **Geocoding**: ~5-10% of total time (rate limited, see below)

### **Geocoding Performance & Limitations**

**Azure Maps Geocoding**:
- **Rate Limit**: ~370 detections per batch
- **Behavior**: First 370 detections get addresses, additional detections pending
- **Workaround**: If >370 detections expected, consider batch processing or Google Maps provider
- **Impact**: Sprint 02 testing validated most outbreak investigations <370 detections

**Google Maps Geocoding** (Alternative):
- **Rate Limit**: Higher limits but slower response
- **Behavior**: More detections processed per batch
- **Trade-off**: Slower individual requests vs higher volume capacity

### **Memory Management** (Validated TASK-041)

**20-Cycle Stress Test Results**:
- **Baseline Memory**: 28.6 MB
- **After 20 Cycles**: 28.4 MB
- **Change**: -0.7% (memory DECREASED!)
- **Conclusion**: No memory leaks, proper cleanup implemented

**Memory Optimization Techniques**:
- ✅ Clear-and-rebuild pattern for boundaries
- ✅ Mutex-protected state management
- ✅ Automatic timer and event listener cleanup
- ✅ Provider-synchronized boundary management

### **Frontend Performance**

**Build System**:
- **Build Time**: <2 seconds (concatenation-based)
- **Bundle Size**: 319.0 KB (27 modules)
- **Load Time**: <1 second on typical broadband

**User Interface**:
- **Map Rendering**: Instantaneous for <100 boundaries
- **Detection Display**: <500ms for <500 detections
- **Confidence Filtering**: Real-time slider updates
- **Interactive Highlighting**: Bidirectional (marker ↔ list), <100ms

### **Azure Maps Optimization Achievements** (TASK-030)

**Before Sprint 01**:
- Mixed provider performance
- Inefficient tile management
- Visual inconsistencies between providers

**After Sprint 01** (32% Performance Improvement):
- ✅ Optimized tile download with async/await patterns
- ✅ Batch processing for multiple tiles
- ✅ Cached tile reuse
- ✅ Visual parity with Google Maps (transparency, styling)
- ✅ Provider-agnostic boundary synchronization

### **Performance Tuning Recommendations**

**For Small Investigations** (<50 tiles, <100 detections):
```bash
# Use default settings - optimized for speed
DEFAULT_MAP_PROVIDER=azure
AZURE_MAPS_BATCH_REQUESTS=true
```

**For Large Investigations** (>100 tiles, >370 detections):
```bash
# Consider Google Maps for higher geocoding limits
DEFAULT_MAP_PROVIDER=google
# OR use Azure Maps with batch processing acceptance
AZURE_MAPS_BATCH_REQUESTS=true
# Expect multiple batches for >370 detections
```

**For Development/Testing**:
```bash
# Enable detailed performance logging
LOG_LEVEL=DEBUG
AZURE_MAPS_TRACK_USAGE=true
# Monitor Azure Portal usage metrics
```

---

## 🔧 **Troubleshooting Authentication Issues**

### **Common Problems & Solutions**

**1. "Invalid subscription key" errors**:
```bash
# Verify key is correct
curl "https://atlas.microsoft.com/map/static?api-version=2024-04-01&tilesetId=microsoft.imagery&zoom=1&center=0,0&height=256&width=256&subscription-key=$AZURE_MAPS_SUBSCRIPTION_KEY"

# Check for extra spaces/characters
export AZURE_MAPS_SUBSCRIPTION_KEY=$(echo "$AZURE_MAPS_SUBSCRIPTION_KEY" | tr -d '[:space:]')
```

**2. "Rate limit exceeded" errors**:
```bash
# Check current usage in Azure Portal
# Consider upgrading tier or implementing request caching
AZURE_MAPS_CACHE_TILES=true
```

**3. "Authentication method not supported" errors**:
```bash
# Ensure auth method matches your setup
AZURE_MAPS_AUTH_METHOD=subscription_key  # Default method
```

### **Validation Script**

```bash
# Test Azure Maps configuration
cd webapp
python -c "
from ts_azure_maps import AzureMaps
import os
try:
    key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY')
    maps = AzureMaps(key)
    print('✅ Azure Maps configuration valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

### **Common Azure Maps Issues & Resolutions**

**Issue**: "Detections stop at approximately 370 results"
- **Cause**: Azure Maps geocoding rate limit
- **Status**: ⚠️ Expected behavior, not a bug
- **Solution**: 
  - For <370 detections: No action needed
  - For >370 detections: Consider Google Maps provider or accept batch processing
  - Impact documented in TASK-042 validation

**Issue**: "Azure Maps visual appearance differs from Google Maps"
- **Cause**: Provider styling differences
- **Status**: ✅ RESOLVED in Sprint 01 (TASK-040)
- **Solution**: Update to latest improvements branch
- **Fix**: Transparency and styling parity implemented

**Issue**: "Stale boundaries appear in detection results"
- **Cause**: Boundary accumulation bug
- **Status**: ✅ RESOLVED in Sprint 02 (TASK-045)
- **Solution**: Update to latest improvements branch
- **Fix**: Clear-and-rebuild pattern with resetBoundaries()

**Issue**: "Provider switching takes time - app appears frozen"
- **Cause**: No loading indicator during initialization
- **Status**: ⚠️ Known limitation (NEW-ISSUE-006)
- **Workaround**: Wait 1-2 seconds after clicking provider switch
- **Planned Fix**: TASK-048 (Sprint 03) adds loading overlay

**Issue**: "Console shows many deprecation warnings"
- **Cause**: Global variable migration in progress  
- **Status**: ⏳ Expected during Sprint 02-03 transition
- **Impact**: ~150+ warnings during typical session
- **Action**: No action needed - warnings guide refactoring, not errors
- **Timeline**: Complete migration in TASK-046 (Sprint 03)

**Issue**: "Azure Maps tiles don't load"
- **Verification Steps**:
  1. Check AZURE_MAPS_SUBSCRIPTION_KEY in .env
  2. Verify network connectivity to atlas.microsoft.com
  3. Check Azure Portal for key status and quota
  4. Monitor browser console for HTTP 401/403 errors
- **Resolution**: Regenerate key if expired, check billing status

---

## 🎯 **Next Steps & Future Enhancements**

### **Immediate (Current Implementation)**
- ✅ Subscription key authentication working
- ✅ Environment variable configuration
- ✅ Multi-provider support (Google/Azure/Bing)

### **Short Term (TASK-009: Azure Key Vault)**
- 🔄 **Key Vault Integration**: Centralized secret management
- 🔄 **Automatic Key Rotation**: Zero-downtime key updates  
- 🔄 **Enhanced Security**: Enterprise-grade secret protection

### **Medium Term (Future Tasks)**
- 🔄 **AAD Integration**: Azure Active Directory authentication
- 🔄 **SAS Token Support**: Time-limited access tokens
- 🔄 **Multi-Tenant Support**: Per-user API key management

### **Long Term (Enterprise Features)**
- 🔄 **Network Security**: Private endpoint integration
- 🔄 **Compliance**: SOC 2, FedRAMP certification support
- 🔄 **Global Deployment**: Multi-region key management

---

**Azure Maps authentication is production-ready with subscription keys. Enterprise customers should consider TASK-009 (Key Vault Integration) for enhanced security and centralized management.**
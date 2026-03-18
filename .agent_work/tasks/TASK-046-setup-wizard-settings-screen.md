# TASK-046: Setup Wizard and Settings Screen Implementation

**Status**: NOT_STARTED  
**Priority**: HIGH  
**Type**: B (Feature Development)  
**Estimated Effort**: 5-9 days (1.5-2 weeks with testing)  
**Target Sprint**: Sprint 04  
**Created**: March 16, 2026  

---

## Objective

Implement a first-launch Setup Wizard and in-app Settings Screen to enable users to configure API keys, select map providers, and access resources without manually editing .env files. Provide seamless Docker-compatible configuration management with API key validation and persistence.

---

## Context

**Current State**: Users must manually copy `.env.example` to `.env`, edit API keys in text editor, and restart the application. This creates friction for non-technical users and complicates Docker deployment.

**Target State**: User-friendly configuration UI that:
- Auto-appears on first launch when API keys are missing/invalid
- Validates API keys via test requests before saving
- Persists changes to host-mounted .env file (Docker-compatible)
- Provides in-app Settings access for ongoing configuration management
- Never requires users to manually edit .env files

**Dependencies**:
- Python `python-dotenv` library (already installed)
- Docker volume mount pattern (documented in TASK-025)
- Existing `TowerScoutValidator` class for input validation

**Related Tasks**:
- TASK-025 (Docker Containerization) - Volume mount strategy
- TASK-001 (API Key Security) - Environment variable migration complete
- TASK-039 (Google Maps API Upgrade) - Provider management patterns

---

## Requirements (EARS Notation)

### Setup Wizard

**R1**: WHEN the application starts AND no .env file exists OR API keys contain placeholder values, THE SYSTEM SHALL auto-display the Setup Wizard modal and block access to main application until configuration is complete

**R2**: WHERE the Setup Wizard is displayed, THE SYSTEM SHALL present a multi-step guided flow (Welcome → API Keys → Provider Selection → Performance Info → Complete)

**R3**: WHEN users enter API keys in the Setup Wizard, THE SYSTEM SHALL validate keys by making test API requests and display success/error indicators (✅/❌ emoji checkboxes)

**R4**: WHEN users save API keys via Setup Wizard, THE SYSTEM SHALL update the .env file, reload runtime environment variables, and clear the `needs_setup` session flag

**R5**: IF API key validation fails, THEN THE SYSTEM SHALL display clear error message and prevent saving invalid keys

### Settings Screen

**R6**: WHEN users click the settings icon (⚙️) in top navigation, THE SYSTEM SHALL open Settings modal overlay without clearing current session state (detections, map view)

**R7**: WHERE the Settings Screen is displayed, THE SYSTEM SHALL provide sections for: API Keys, Resources (docs/videos), Performance metrics, and System controls (debug mode, clear cache)

**R8**: WHEN users modify API keys in Settings, THE SYSTEM SHALL track dirty state and warn before closing without saving

**R9**: WHEN users save API keys via Settings, THE SYSTEM SHALL validate keys, update .env file, and reload runtime variables without requiring app restart

**R10**: WHEN users enable Debug Mode toggle, THE SYSTEM SHALL persist preference to localStorage and enable verbose browser console logging

**R11**: WHEN users click Clear Cache button, THE SYSTEM SHALL call `/api/config/reset-session` endpoint to clear Flask session and temporary files

### Backend Infrastructure

**R12**: THE SYSTEM SHALL provide backend API endpoint `/api/config/validate-key` that validates API keys by making test requests to Google/Azure APIs

**R13**: THE SYSTEM SHALL provide backend API endpoint `/api/config/save-keys` that safely updates .env file with backup/validation/rollback mechanism

**R14**: THE SYSTEM SHALL provide backend API endpoint `/api/config/status` that returns current configuration state (which keys are configured/valid)

**R15**: THE SYSTEM SHALL create timestamped .env backups before writes (`webapp/.env.backup.{timestamp}`) and maintain maximum 5 backups with auto-cleanup

**R16**: IF .env file write fails OR validation fails after write, THEN THE SYSTEM SHALL rollback to previous backup automatically

### Docker Compatibility

**R17**: WHERE the application runs in Docker container, THE SYSTEM SHALL write .env updates to host-mounted volume (`-v ./webapp/.env:/app/webapp/.env`)

**R18**: WHEN .env file is updated in container, THE SYSTEM SHALL ensure changes persist across container restarts

---

## Acceptance Criteria

### Setup Wizard
- [ ] Auto-appears on first launch when .env missing or contains placeholder keys
- [ ] Blocks app usage until configuration complete (cannot close wizard prematurely)
- [ ] Multi-step flow: Welcome → API Keys → Provider Selection → Performance Info → Complete
- [ ] Google Maps API key input with validation indicator (✅/❌)
- [ ] Azure Maps API key input with validation indicator (✅/❌)
- [ ] Provider preference selection (radio buttons for Google/Azure default)
- [ ] Performance info display shows recent detection statistics
- [ ] "Start Using TowerScout" button appears after successful configuration
- [ ] Successfully saves API keys to .env file
- [ ] Clears `needs_setup` session flag after completion
- [ ] Provides clear error messages for invalid keys
- [ ] Mobile-responsive design matching existing UI patterns

### Settings Screen
- [ ] Accessible via settings icon (⚙️) in top navigation
- [ ] Opens as modal overlay without clearing session state
- [ ] Four sections: API Keys, Resources, Performance, System
- [ ] API Keys section shows masked keys with "Show" toggle
- [ ] Validation indicators (✅/❌) update on Save click
- [ ] Resources section displays documentation links (placeholder URLs initially)
- [ ] Resources section displays video guide links (placeholder URLs initially)
- [ ] Performance section shows recent detection statistics (avg tiles/sec from last 5 sessions)
- [ ] Debug Mode toggle persists to localStorage
- [ ] Clear Cache button successfully clears session and temp files
- [ ] Close button (X) appears in top-right corner
- [ ] Warns before closing with unsaved changes (dirty state detection)
- [ ] Successfully updates .env file without app restart
- [ ] Preserves current detections and map view when opening/closing

### Backend Infrastructure
- [ ] `/api/config/validate-key` endpoint validates Google Maps keys via test request
- [ ] `/api/config/validate-key` endpoint validates Azure Maps keys via test request
- [ ] `/api/config/save-keys` endpoint updates .env file with proper formatting
- [ ] `/api/config/save-keys` endpoint reloads runtime environment variables
- [ ] `/api/config/status` endpoint returns current key configuration state
- [ ] `/api/config/reset-session` endpoint clears Flask session successfully
- [ ] `/api/config/performance` endpoint returns recent detection statistics
- [ ] .env backup created before every write operation
- [ ] Maximum 5 backups maintained (auto-cleanup oldest)
- [ ] Rollback mechanism works when validation fails
- [ ] Rate limiting applied to validation endpoints (prevent abuse)
- [ ] All inputs sanitized via `TowerScoutValidator` class

### Docker Compatibility
- [ ] .env updates persist across container restarts
- [ ] Volume mount pattern documented: `-v ./webapp/.env:/app/webapp/.env`
- [ ] Container user has write permissions to mounted .env
- [ ] Integration tested in Docker environment

### Error Handling
- [ ] Invalid API key format shows clear error message
- [ ] Failed API validation shows provider-specific error
- [ ] File write errors trigger rollback with user notification
- [ ] Network errors during validation show retry option
- [ ] AJAX failures display user-friendly error messages
- [ ] All errors integrate with existing `TowerScoutErrorHandler`

### Performance
- [ ] API key validation completes within 5 seconds
- [ ] .env file write/reload completes within 2 seconds
- [ ] Settings modal opens instantly (<500ms)
- [ ] No noticeable performance impact on main application

---

## Implementation Plan

### Phase 1: Backend Infrastructure (1-2 days)

**Step 1.1: Create API Key Management Module** (`webapp/ts_config.py`)
```python
def validate_api_key(provider: str, key: str) -> dict:
    """Validate API key by making test request to provider API.
    
    Returns:
        {
            'valid': bool,
            'message': str,  # Success or error message
            'provider': str,
            'tested_at': datetime
        }
    """

def update_env_file(updates: dict) -> bool:
    """Safely update .env file with backup/validation/rollback.
    
    Args:
        updates: Dict of key-value pairs to update
        
    Returns:
        True if successful, False otherwise
    """

def get_env_status() -> dict:
    """Get current environment configuration status.
    
    Returns:
        {
            'google': {'configured': bool, 'valid': bool},
            'azure': {'configured': bool, 'valid': bool},
            'needs_setup': bool
        }
    """

def get_recent_performance_stats() -> dict:
    """Query recent session history for performance metrics.
    
    Returns:
        {
            'avg_tiles_per_second': float,
            'session_count': int,
            'last_updated': datetime
        }
    """
```

**Implementation Details**:
- Use existing `rate_limiter` for validation request throttling
- Store performance stats in Flask session or lightweight SQLite DB
- Preserve .env file comments and formatting when updating
- Use file locking to prevent concurrent write corruption

**Step 1.2: Create Flask Endpoints** (in `webapp/towerscout.py`)

Add 5 new endpoints around line 1500:

```python
@app.route('/api/config/validate-key', methods=['POST'])
def validate_api_key_endpoint():
    """Validate API key via test request"""
    # Rate limiting check
    # Input validation via TowerScoutValidator
    # Call ts_config.validate_api_key()
    # Return JSON response with validation result

@app.route('/api/config/save-keys', methods=['POST'])
def save_api_keys():
    """Save API keys to .env and reload runtime vars"""
    # Validate all keys first
    # Backup current .env
    # Update .env file
    # Reload environment variables
    # Clear needs_setup flag
    # Return success/error

@app.route('/api/config/status', methods=['GET'])
def get_config_status():
    """Get current configuration state"""
    # Return ts_config.get_env_status()

@app.route('/api/config/reset-session', methods=['POST'])
def reset_session():
    """Clear Flask session and temp files"""
    # Clear session data
    # Remove temp directories
    # Return success

@app.route('/api/config/performance', methods=['GET'])
def get_performance_stats():
    """Get recent detection performance stats"""
    # Return ts_config.get_recent_performance_stats()
```

**Step 1.3: Add .env File Safety Checks**
- Create backup before every write: `webapp/.env.backup.{timestamp}`
- Validate .env syntax after write (can be parsed by dotenv)
- Rollback to previous backup if validation fails
- Auto-cleanup: keep only 5 most recent backups

**Deliverables**:
- `webapp/ts_config.py` (new file, ~300 lines)
- 5 new endpoints in `webapp/towerscout.py`
- Unit tests in `tests/unit/test_config.py`

---

### Phase 2: Setup Wizard UI (2-3 days)

**Step 2.1: Create Setup Wizard HTML Template**

Add to `webapp/templates/towerscout.html` (after existing modal overlays):

```html
<!-- Setup Wizard Modal -->
<div id="setup_wizard_div" class="modal-overlay" style="display:none;">
    <div class="modal-container setup-wizard">
        <!-- Progress Indicator -->
        <div class="wizard-progress">
            <span class="step active" data-step="1">1. Welcome</span>
            <span class="step" data-step="2">2. API Keys</span>
            <span class="step" data-step="3">3. Provider</span>
            <span class="step" data-step="4">4. Info</span>
            <span class="step" data-step="5">5. Done</span>
        </div>
        
        <!-- Step 1: Welcome -->
        <div class="wizard-step" data-step="1">
            <h2>Welcome to TowerScout</h2>
            <p>Let's get you set up in just a few steps...</p>
            <button class="btn btn-primary" onclick="SetupWizard.nextStep()">Get Started</button>
        </div>
        
        <!-- Step 2: API Keys -->
        <div class="wizard-step" data-step="2" style="display:none;">
            <h2>Configure API Keys</h2>
            <div class="form-group">
                <label>Google Maps API Key:</label>
                <input type="password" id="wizard_google_key" class="form-control" />
                <span class="validation-indicator" id="google_key_status"></span>
            </div>
            <div class="form-group">
                <label>Azure Maps API Key:</label>
                <input type="password" id="wizard_azure_key" class="form-control" />
                <span class="validation-indicator" id="azure_key_status"></span>
            </div>
            <button class="btn btn-secondary" onclick="SetupWizard.prevStep()">Back</button>
            <button class="btn btn-primary" onclick="SetupWizard.validateAndNext()">Next</button>
        </div>
        
        <!-- Step 3: Provider Selection -->
        <div class="wizard-step" data-step="3" style="display:none;">
            <h2>Choose Default Provider</h2>
            <div class="provider-selection">
                <label><input type="radio" name="default_provider" value="google" checked> Google Maps</label>
                <label><input type="radio" name="default_provider" value="azure"> Azure Maps</label>
            </div>
            <button class="btn btn-secondary" onclick="SetupWizard.prevStep()">Back</button>
            <button class="btn btn-primary" onclick="SetupWizard.nextStep()">Next</button>
        </div>
        
        <!-- Step 4: Performance Info & Tutorial -->
        <div class="wizard-step" data-step="4" style="display:none;">
            <h2>Performance & Usage Guide</h2>
            <p>Detection processing times vary based on hardware...</p>
            <div class="performance-info">
                <p><strong>Typical Performance:</strong></p>
                <ul>
                    <li>50 tiles ≈ 15 seconds (GPU)</li>
                    <li>100 tiles ≈ 30 seconds (GPU)</li>
                    <li>CPU processing: ~4x slower</li>
                </ul>
            </div>
            <button class="btn btn-secondary" onclick="SetupWizard.prevStep()">Back</button>
            <button class="btn btn-primary" onclick="SetupWizard.nextStep()">Next</button>
        </div>
        
        <!-- Step 5: Complete -->
        <div class="wizard-step" data-step="5" style="display:none;">
            <h2>Setup Complete!</h2>
            <p>✅ API keys configured and validated</p>
            <p>✅ Default provider selected</p>
            <p>You're ready to start detecting cooling towers.</p>
            <button class="btn btn-primary" onclick="SetupWizard.complete()">Start Using TowerScout</button>
        </div>
    </div>
</div>
```

**Step 2.2: Create Setup Wizard CSS**

Add to `webapp/css/ts_styles.css`:

```css
/* Setup Wizard Styles */
.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 3000;
}

.modal-container.setup-wizard {
    background: #1a1a2e;
    padding: 40px;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.wizard-progress {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #16213e;
}

.wizard-progress .step {
    font-size: 14px;
    color: #808080;
}

.wizard-progress .step.active {
    color: #4a9eff;
    font-weight: bold;
}

.wizard-step {
    min-height: 300px;
}

.validation-indicator {
    font-size: 24px;
    margin-left: 10px;
}

.provider-selection label {
    display: block;
    margin: 15px 0;
    padding: 15px;
    border: 2px solid #16213e;
    border-radius: 8px;
    cursor: pointer;
}

.provider-selection label:hover {
    border-color: #4a9eff;
}
```

Mobile styles in `webapp/css/ts_styles_mobile.css`:

```css
@media (max-width: 768px) {
    .modal-container.setup-wizard {
        padding: 20px;
        width: 95%;
    }
    
    .wizard-progress {
        flex-direction: column;
        gap: 10px;
    }
}
```

**Step 2.3: Create Setup Wizard JavaScript**

Create `webapp/js/src/setup-wizard.js`:

```javascript
/**
 * Setup Wizard - First-launch configuration flow
 */
const SetupWizard = (function() {
    let currentStep = 1;
    let validatedKeys = {
        google: false,
        azure: false
    };
    
    function init() {
        // Check if setup needed via /api/config/status
        // Show wizard if needs_setup flag is true
    }
    
    function showStep(stepNumber) {
        // Hide all steps
        // Show specified step
        // Update progress indicator
        currentStep = stepNumber;
    }
    
    function nextStep() {
        if (currentStep < 5) {
            showStep(currentStep + 1);
        }
    }
    
    function prevStep() {
        if (currentStep > 1) {
            showStep(currentStep - 1);
        }
    }
    
    async function validateAndNext() {
        // Get API keys from inputs
        // Call /api/config/validate-key for each
        // Update validation indicators
        // If all valid, proceed to next step
        // If invalid, show error message
        
        const googleKey = document.getElementById('wizard_google_key').value;
        const azureKey = document.getElementById('wizard_azure_key').value;
        
        // Validate Google key
        if (googleKey) {
            const googleValid = await validateKey('google', googleKey);
            validatedKeys.google = googleValid;
            updateIndicator('google_key_status', googleValid);
        }
        
        // Validate Azure key
        if (azureKey) {
            const azureValid = await validateKey('azure', azureKey);
            validatedKeys.azure = azureValid;
            updateIndicator('azure_key_status', azureValid);
        }
        
        // Require at least one valid key
        if (validatedKeys.google || validatedKeys.azure) {
            nextStep();
        } else {
            TowerScoutErrorHandler.showError('Please provide at least one valid API key');
        }
    }
    
    async function validateKey(provider, key) {
        try {
            const response = await fetch('/api/config/validate-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, key })
            });
            const result = await response.json();
            return result.valid;
        } catch (error) {
            console.error('Validation error:', error);
            return false;
        }
    }
    
    function updateIndicator(elementId, isValid) {
        const indicator = document.getElementById(elementId);
        indicator.textContent = isValid ? '✅' : '❌';
        indicator.style.color = isValid ? '#4CAF50' : '#f44336';
    }
    
    async function complete() {
        // Save API keys via /api/config/save-keys
        // Save provider preference to localStorage
        // Hide wizard
        // Reload page to initialize with new config
        
        const googleKey = document.getElementById('wizard_google_key').value;
        const azureKey = document.getElementById('wizard_azure_key').value;
        const provider = document.querySelector('input[name="default_provider"]:checked').value;
        
        try {
            const response = await fetch('/api/config/save-keys', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    google_api_key: googleKey,
                    azure_maps_subscription_key: azureKey
                })
            });
            
            if (response.ok) {
                localStorage.setItem('preferredMapProvider', provider);
                document.getElementById('setup_wizard_div').style.display = 'none';
                location.reload(); // Reload to initialize with new config
            } else {
                throw new Error('Failed to save configuration');
            }
        } catch (error) {
            TowerScoutErrorHandler.showError('Configuration save failed: ' + error.message);
        }
    }
    
    return {
        init,
        nextStep,
        prevStep,
        validateAndNext,
        complete
    };
})();

// Initialize on page load
document.addEventListener('DOMContentLoaded', SetupWizard.init);
```

**Step 2.4: Add Auto-Trigger Logic**

Add to `webapp/towerscout.py` startup checks (around line 50-250):

```python
def check_setup_needed():
    """Check if setup wizard should be displayed"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        return True
    
    # Check for placeholder values
    google_key = os.getenv('GOOGLE_API_KEY', '')
    azure_key = os.getenv('AZURE_MAPS_SUBSCRIPTION_KEY', '')
    
    placeholders = [
        'your_google_maps_api_key_here',
        'your_azure_maps_',
        'your_bing_maps_'
    ]
    
    google_is_placeholder = any(p in google_key.lower() for p in placeholders)
    azure_is_placeholder = any(p in azure_key.lower() for p in placeholders)
    
    # Need setup if both are missing or placeholders
    return (not google_key or google_is_placeholder) and (not azure_key or azure_is_placeholder)

@app.before_request
def check_setup_status():
    """Set needs_setup flag in session"""
    if 'needs_setup' not in session:
        session['needs_setup'] = check_setup_needed()
```

Update Jinja2 template to check flag:

```html
<script>
    // Pass needs_setup flag from Flask session
    window.needsSetup = {{ session.get('needs_setup', False) | tojson }};
    if (window.needsSetup) {
        document.getElementById('setup_wizard_div').style.display = 'flex';
    }
</script>
```

**Deliverables**:
- Setup Wizard HTML in `towerscout.html`
- CSS in `ts_styles.css` and `ts_styles_mobile.css`
- JavaScript in `webapp/js/src/setup-wizard.js`
- Auto-trigger logic in `towerscout.py`
- Frontend tests in `tests/frontend/test_setup_wizard.js`

---

### Phase 3: Settings Screen UI (1-2 days)

**Step 3.1: Create Settings Modal HTML**

Add to `webapp/templates/towerscout.html`:

```html
<!-- Settings Screen Modal -->
<div id="settings_div" class="modal-overlay" style="display:none;">
    <div class="modal-container settings-screen">
        <div class="modal-header">
            <h2>Settings</h2>
            <button class="close-btn" onclick="Settings.close()">×</button>
        </div>
        
        <div class="settings-content">
            <!-- API Keys Section -->
            <section class="settings-section">
                <h3>🔑 API Keys</h3>
                <div class="form-group">
                    <label>Google Maps API Key:</label>
                    <div class="key-input-group">
                        <input type="password" id="settings_google_key" class="form-control" />
                        <button class="btn btn-icon" onclick="Settings.toggleKeyVisibility('google')">👁️</button>
                        <span class="validation-indicator" id="settings_google_status"></span>
                    </div>
                </div>
                <div class="form-group">
                    <label>Azure Maps API Key:</label>
                    <div class="key-input-group">
                        <input type="password" id="settings_azure_key" class="form-control" />
                        <button class="btn btn-icon" onclick="Settings.toggleKeyVisibility('azure')">👁️</button>
                        <span class="validation-indicator" id="settings_azure_status"></span>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="Settings.saveKeys()">Save API Keys</button>
            </section>
            
            <!-- Resources Section -->
            <section class="settings-section">
                <h3>📚 Resources</h3>
                <div class="resource-links">
                    <h4>Documentation:</h4>
                    <ul>
                        <li><a href="#" target="_blank">User Guide</a> (Coming Soon)</li>
                        <li><a href="#" target="_blank">Setup Instructions</a> (Coming Soon)</li>
                        <li><a href="#" target="_blank">API Documentation</a> (Coming Soon)</li>
                    </ul>
                    <h4>Video Guides:</h4>
                    <ul>
                        <li><a href="#" target="_blank">Getting Started</a> (Coming Soon)</li>
                        <li><a href="#" target="_blank">Detection Workflow</a> (Coming Soon)</li>
                        <li><a href="#" target="_blank">Manual Tower Addition</a> (Coming Soon)</li>
                    </ul>
                </div>
            </section>
            
            <!-- Performance Section -->
            <section class="settings-section">
                <h3>⚡ Performance</h3>
                <div class="performance-stats" id="performance_stats_container">
                    <p>Loading performance data...</p>
                </div>
            </section>
            
            <!-- System Section -->
            <section class="settings-section">
                <h3>⚙️ System</h3>
                <div class="system-controls">
                    <div class="control-group">
                        <label>
                            <input type="checkbox" id="debug_mode_toggle" onchange="Settings.toggleDebugMode()" />
                            Enable Debug Mode (verbose console logging)
                        </label>
                    </div>
                    <div class="control-group">
                        <button class="btn btn-warning" onclick="Settings.clearCache()">Clear Cache & Session</button>
                        <p class="help-text">Clears temporary files and resets session data</p>
                    </div>
                </div>
            </section>
        </div>
    </div>
</div>
```

**Step 3.2: Add Settings Button to Navigation**

Add settings button to top navigation in `towerscout.html`:

```html
<div class="top-nav">
    <!-- Existing nav items -->
    <button class="btn btn-icon settings-btn" onclick="Settings.open()" title="Settings">
        ⚙️
    </button>
</div>
```

**Step 3.3: Create Settings Screen JavaScript**

Create `webapp/js/src/settings.js`:

```javascript
/**
 * Settings Screen - In-app configuration management
 */
const Settings = (function() {
    let isDirty = false;
    let originalKeys = {};
    
    async function open() {
        // Load current configuration
        await loadCurrentConfig();
        
        // Load performance stats
        await loadPerformanceStats();
        
        // Load debug mode state from localStorage
        const debugMode = localStorage.getItem('debugMode') === 'true';
        document.getElementById('debug_mode_toggle').checked = debugMode;
        
        // Show modal
        document.getElementById('settings_div').style.display = 'flex';
    }
    
    function close() {
        if (isDirty) {
            if (!confirm('You have unsaved changes. Are you sure you want to close?')) {
                return;
            }
        }
        
        document.getElementById('settings_div').style.display = 'none';
        isDirty = false;
    }
    
    async function loadCurrentConfig() {
        try {
            const response = await fetch('/api/config/status');
            const status = await response.json();
            
            // Load masked keys (show ****...1234 pattern)
            if (status.google.configured) {
                document.getElementById('settings_google_key').placeholder = 'Current key: ****...';
            }
            if (status.azure.configured) {
                document.getElementById('settings_azure_key').placeholder = 'Current key: ****...';
            }
            
            originalKeys = {
                google: document.getElementById('settings_google_key').value,
                azure: document.getElementById('settings_azure_key').value
            };
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }
    
    async function loadPerformanceStats() {
        try {
            const response = await fetch('/api/config/performance');
            const stats = await response.json();
            
            const container = document.getElementById('performance_stats_container');
            container.innerHTML = `
                <p><strong>Recent Detection Performance:</strong></p>
                <p>Average: ${stats.avg_tiles_per_second.toFixed(2)} tiles/second</p>
                <p>Based on ${stats.session_count} recent sessions</p>
                <p class="help-text">Last updated: ${new Date(stats.last_updated).toLocaleString()}</p>
            `;
        } catch (error) {
            console.error('Failed to load performance stats:', error);
            document.getElementById('performance_stats_container').innerHTML = '<p>Performance data unavailable</p>';
        }
    }
    
    function toggleKeyVisibility(provider) {
        const input = document.getElementById(`settings_${provider}_key`);
        input.type = input.type === 'password' ? 'text' : 'password';
    }
    
    async function saveKeys() {
        const googleKey = document.getElementById('settings_google_key').value;
        const azureKey = document.getElementById('settings_azure_key').value;
        
        // Only validate and save if keys were changed
        const keysChanged = googleKey !== originalKeys.google || azureKey !== originalKeys.azure;
        
        if (!keysChanged) {
            alert('No changes to save');
            return;
        }
        
        // Validate keys
        let allValid = true;
        
        if (googleKey) {
            const googleValid = await validateKey('google', googleKey);
            updateIndicator('settings_google_status', googleValid);
            allValid = allValid && googleValid;
        }
        
        if (azureKey) {
            const azureValid = await validateKey('azure', azureKey);
            updateIndicator('settings_azure_status', azureValid);
            allValid = allValid && azureValid;
        }
        
        if (!allValid) {
            alert('❌ API key validation failed. Please check your keys and try again.');
            return;
        }
        
        // Save to backend
        try {
            const response = await fetch('/api/config/save-keys', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    google_api_key: googleKey,
                    azure_maps_subscription_key: azureKey
                })
            });
            
            if (response.ok) {
                alert('✅ API keys updated successfully');
                isDirty = false;
                originalKeys = { google: googleKey, azure: azureKey };
            } else {
                throw new Error('Failed to save configuration');
            }
        } catch (error) {
            TowerScoutErrorHandler.showError('Failed to save API keys: ' + error.message);
        }
    }
    
    async function validateKey(provider, key) {
        try {
            const response = await fetch('/api/config/validate-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, key })
            });
            const result = await response.json();
            return result.valid;
        } catch (error) {
            console.error('Validation error:', error);
            return false;
        }
    }
    
    function updateIndicator(elementId, isValid) {
        const indicator = document.getElementById(elementId);
        indicator.textContent = isValid ? '✅' : '❌';
        indicator.style.color = isValid ? '#4CAF50' : '#f44336';
    }
    
    function toggleDebugMode() {
        const enabled = document.getElementById('debug_mode_toggle').checked;
        localStorage.setItem('debugMode', enabled);
        
        // Update logging level
        if (enabled) {
            console.log('Debug mode enabled - verbose logging active');
        } else {
            console.log('Debug mode disabled');
        }
        
        alert(enabled ? '✅ Debug mode enabled' : '❌ Debug mode disabled');
    }
    
    async function clearCache() {
        if (!confirm('This will clear your session data and temporary files. Continue?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/config/reset-session', {
                method: 'POST'
            });
            
            if (response.ok) {
                alert('✅ Cache and session cleared successfully');
                close();
                location.reload();
            } else {
                throw new Error('Failed to clear cache');
            }
        } catch (error) {
            TowerScoutErrorHandler.showError('Failed to clear cache: ' + error.message);
        }
    }
    
    // Track dirty state
    function trackChanges() {
        const inputs = document.querySelectorAll('#settings_div input');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                isDirty = true;
            });
        });
    }
    
    // Initialize
    function init() {
        trackChanges();
    }
    
    return {
        init,
        open,
        close,
        toggleKeyVisibility,
        saveKeys,
        toggleDebugMode,
        clearCache
    };
})();

// Initialize on page load
document.addEventListener('DOMContentLoaded', Settings.init);
```

**Step 3.4: Create Settings Screen CSS**

Add to `webapp/css/ts_styles.css`:

```css
/* Settings Screen Styles */
.modal-container.settings-screen {
    background: #1a1a2e;
    padding: 0;
    border-radius: 12px;
    max-width: 800px;
    width: 90%;
    max-height: 90vh;
    overflow: hidden;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 30px;
    border-bottom: 2px solid #16213e;
}

.close-btn {
    background: none;
    border: none;
    font-size: 32px;
    color: #fff;
    cursor: pointer;
    line-height: 1;
}

.close-btn:hover {
    color: #f44336;
}

.settings-content {
    padding: 30px;
    overflow-y: auto;
    max-height: calc(90vh - 80px);
}

.settings-section {
    margin-bottom: 40px;
    padding-bottom: 30px;
    border-bottom: 1px solid #16213e;
}

.settings-section:last-child {
    border-bottom: none;
}

.settings-section h3 {
    margin-bottom: 20px;
    color: #4a9eff;
}

.key-input-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.key-input-group .form-control {
    flex: 1;
}

.btn-icon {
    background: #16213e;
    border: none;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 4px;
}

.btn-icon:hover {
    background: #0f3460;
}

.resource-links ul {
    list-style: none;
    padding: 0;
}

.resource-links li {
    margin: 10px 0;
}

.resource-links a {
    color: #4a9eff;
    text-decoration: none;
}

.resource-links a:hover {
    text-decoration: underline;
}

.performance-stats {
    background: #16213e;
    padding: 20px;
    border-radius: 8px;
}

.control-group {
    margin: 20px 0;
}

.control-group label {
    display: flex;
    align-items: center;
    gap: 10px;
}

.help-text {
    font-size: 12px;
    color: #808080;
    margin-top: 5px;
}

.settings-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    font-size: 24px;
}
```

**Deliverables**:
- Settings modal HTML in `towerscout.html`
- Settings button in navigation
- JavaScript in `webapp/js/src/settings.js`
- CSS in `ts_styles.css`

---

### Phase 4: Integration & Testing (1-2 days)

**Step 4.1: Integration Testing**

Test scenarios:

1. **First Launch Flow**:
   - Delete .env file
   - Start application
   - Verify Setup Wizard auto-appears
   - Verify app access blocked until configuration complete
   - Complete wizard with valid keys
   - Verify wizard closes and app becomes usable

2. **Settings Modal Flow**:
   - Click settings icon
   - Verify modal opens without clearing session
   - Update API key
   - Click save
   - Verify validation runs
   - Verify success/error feedback

3. **Docker Persistence**:
   - Run app in Docker with volume mount
   - Update keys via Settings
   - Restart container
   - Verify keys still configured

4. **API Key Validation**:
   - Enter invalid Google key
   - Click save
   - Verify error shown
   - Enter valid Google key
   - Click save
   - Verify success shown

5. **Concurrent Access**:
   - Open app in two browser tabs
   - Update keys in both tabs simultaneously
   - Verify no .env file corruption

**Step 4.2: Error Handling Testing**

Test error scenarios:

- Invalid API key format
- Network error during validation
- .env file write failure
- Disk full scenario
- Permission denied on .env file

**Step 4.3: Performance Testing**

Verify:
- API key validation completes within 5 seconds
- .env file write/reload completes within 2 seconds
- Settings modal opens instantly (<500ms)

**Step 4.4: Update Docker Configuration**

Document in TASK-025 (Docker containerization):

```yaml
# docker-compose.yml
services:
  towerscout:
    build: .
    volumes:
      - ./webapp/.env:/app/webapp/.env  # Host-mounted .env for persistence
      - ./webapp/model_params:/app/model_params
      - ./webapp/uploads:/app/uploads
    env_file:
      - webapp/.env
```

Ensure container user has write permissions:

```dockerfile
# Dockerfile
USER app
RUN chmod 644 /app/webapp/.env  # Allow writes to mounted .env
```

**Step 4.5: Documentation**

Create/update documentation:

1. **User Documentation**:
   - `docs/SETUP_WIZARD_GUIDE.md` - Screenshot walkthrough
   - `docs/SETTINGS_SCREEN_GUIDE.md` - Feature overview

2. **Developer Documentation**:
   - Update `.agent_work/context/guides/MIGRATION_GUIDE.md` with Setup Wizard usage
   - Update `.env.example` with reference to Setup Wizard
   - Add API endpoint documentation to `README.md`

3. **Docker Documentation**:
   - Document volume mount pattern for .env persistence
   - Add troubleshooting section for permission issues

**Deliverables**:
- Integration test suite in `tests/integration/test_setup_wizard.py`
- Frontend test suite in `tests/frontend/test_setup_wizard.js`
- Updated documentation in `docs/` directory
- Docker configuration examples

---

## Technical Architecture

### File Structure

```
webapp/
├── towerscout.py                     # 5 new API endpoints
├── ts_config.py                      # New: API key management module
├── templates/
│   └── towerscout.html               # Modified: Add wizard & settings modals
├── js/
│   └── src/
│       ├── setup-wizard.js           # New: Setup wizard logic
│       └── settings.js               # New: Settings screen logic
└── css/
    ├── ts_styles.css                 # Modified: Add modal styles
    └── ts_styles_mobile.css          # Modified: Add mobile styles

tests/
├── unit/
│   └── test_config.py                # New: Unit tests for ts_config module
├── integration/
│   └── test_setup_wizard.py          # New: Integration tests
└── frontend/
    └── test_setup_wizard.js          # New: Frontend tests

docs/
├── SETUP_WIZARD_GUIDE.md             # New: User guide with screenshots
└── SETTINGS_SCREEN_GUIDE.md          # New: Settings screen guide
```

### API Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/api/config/validate-key` | POST | Validate API key | `{provider, key}` | `{valid, message}` |
| `/api/config/save-keys` | POST | Save API keys | `{google_api_key, azure_maps_subscription_key}` | `{success, message}` |
| `/api/config/status` | GET | Get config status | - | `{google: {}, azure: {}, needs_setup}` |
| `/api/config/reset-session` | POST | Clear session | - | `{success}` |
| `/api/config/performance` | GET | Get perf stats | - | `{avg_tiles_per_second, session_count}` |

### Data Flow

```
User Action → Frontend JavaScript → Flask API Endpoint → ts_config Module → .env File
                                                      ↓
                                               Validation → Provider API
                                                      ↓
                                               Update Runtime Variables
                                                      ↓
                                               Return Success/Error
```

### State Management

**Setup Wizard Flow**:
1. App startup checks `needs_setup` flag via `check_setup_needed()`
2. If true, `session['needs_setup'] = True` set in Flask session
3. Frontend reads flag from Jinja2 template variable
4. Setup Wizard auto-displays and blocks app access
5. After successful configuration, `session['needs_setup'] = False`
6. Wizard closes, page reloads, app becomes usable

**Settings Screen Flow**:
1. User clicks settings icon → Settings modal opens
2. Current config loaded via `/api/config/status`
3. User modifies API keys → `isDirty = true`
4. User clicks Save → Validation runs → .env updates
5. Close button checks `isDirty` state → Confirmation if dirty
6. Session state preserved throughout (no reload needed)

---

## Dependencies & Risks

### Technical Dependencies
- Python `python-dotenv` (already installed) - .env file reading/writing
- Flask session (already configured) - State management
- Existing `TowerScoutValidator` class - Input validation
- Docker volume mount pattern (documented in TASK-025)

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| .env file corruption during write | LOW | HIGH | Backup before write + validation + rollback mechanism |
| Concurrent writes from multiple tabs | MEDIUM | MEDIUM | File locking + session-based mutex |
| API key leakage via browser console | LOW | HIGH | Never log keys, mask in UI, production HTTPS |
| Setup Wizard UX confusion | MEDIUM | MEDIUM | Clear step indicators, helpful error messages, user testing |
| Docker volume mount permission issues | MEDIUM | HIGH | Comprehensive documentation, troubleshooting guide |
| Rate limiting bypass on validation endpoint | LOW | MEDIUM | Use existing rate_limiter with strict limits |

### Performance Impact
- **Minimal**: New endpoints only called on user action (not per-detection)
- **File I/O**: Single .env file write (~1KB) - negligible
- **Validation Requests**: Rate-limited to prevent abuse
- **No impact on core detection workflow**

---

## Success Criteria

### Functional Success
- [ ] Setup Wizard auto-appears on first launch and blocks app until complete
- [ ] Settings modal provides seamless in-app configuration management
- [ ] API keys validated via test requests before saving
- [ ] Changes persist to host-mounted .env file (Docker-compatible)
- [ ] Session state preserved when opening/closing Settings
- [ ] Clear error messages for all failure scenarios

### User Experience Success
- [ ] Non-technical users can configure app without editing text files
- [ ] Configuration process takes <5 minutes from start to finish
- [ ] Mobile-responsive design works on phones/tablets
- [ ] Consistent visual design matching existing application
- [ ] Helpful contextual information (performance stats, resource links)

### Technical Success
- [ ] Zero .env file corruption incidents
- [ ] No security vulnerabilities introduced
- [ ] Performance targets met (validation <5s, save <2s, modal open <500ms)
- [ ] Comprehensive test coverage (unit + integration + frontend)
- [ ] Documentation complete and accurate

### Integration Success
- [ ] Works seamlessly with Docker containerization (TASK-025)
- [ ] No regressions in existing functionality
- [ ] Compatible with TASK-039 Google Maps provider management
- [ ] Integrates cleanly with existing error handling patterns

---

## Validation & Testing

### Unit Tests (`tests/unit/test_config.py`)
```python
def test_validate_api_key_google():
    """Test Google Maps API key validation"""
    
def test_validate_api_key_azure():
    """Test Azure Maps API key validation"""
    
def test_update_env_file():
    """Test .env file update with backup/rollback"""
    
def test_get_env_status():
    """Test environment configuration status detection"""
    
def test_get_recent_performance_stats():
    """Test performance statistics retrieval"""
```

### Integration Tests (`tests/integration/test_setup_wizard.py`)
```python
def test_first_launch_flow():
    """Test Setup Wizard auto-appearance on first launch"""
    
def test_settings_save_flow():
    """Test Settings modal API key save with validation"""
    
def test_env_persistence():
    """Test .env changes persist across Flask app restarts"""
    
def test_docker_volume_mount():
    """Test .env updates work with Docker volume mount"""
```

### Frontend Tests (`tests/frontend/test_setup_wizard.js`)
```javascript
test('Setup Wizard displays on first launch', async () => {
  // Verify modal auto-appears when needs_setup flag is true
});

test('Setup Wizard validates API keys', async () => {
  // Verify validation indicators update correctly
});

test('Settings modal tracks dirty state', async () => {
  // Verify unsaved changes warning appears
});
```

### Manual Verification Checklist
- [ ] First launch: Setup Wizard appears automatically
- [ ] Setup Wizard: All 5 steps navigate correctly
- [ ] Setup Wizard: API key validation works for both providers
- [ ] Setup Wizard: Invalid keys show error, valid keys show success
- [ ] Setup Wizard: Configuration saves to .env correctly
- [ ] Settings button: Opens modal without clearing session
- [ ] Settings modal: Current keys load correctly (masked)
- [ ] Settings modal: Validation runs on save
- [ ] Settings modal: Unsaved changes warning appears
- [ ] Settings modal: Debug mode toggle persists
- [ ] Settings modal: Clear cache button works
- [ ] Docker: Volume mount pattern works correctly
- [ ] Docker: .env changes persist across container restarts
- [ ] Mobile: Responsive design works on phone/tablet
- [ ] Performance: All actions complete within target times

---

## Rollback Plan

If issues arise during implementation:

1. **Backend Module (`ts_config.py`)**:
   - Remove module file
   - Remove endpoint routes from `towerscout.py`
   - Remove endpoint tests

2. **Frontend UI**:
   - Remove Setup Wizard HTML from `towerscout.html`
   - Remove Settings modal HTML from `towerscout.html`
   - Remove JavaScript files (`setup-wizard.js`, `settings.js`)
   - Revert CSS changes

3. **Database/Config**:
   - No database changes required
   - .env backups allow easy rollback

4. **Git Strategy**:
   - Implement in feature branch: `feature/setup-wizard-settings`
   - Merge to main only after complete validation
   - Maintain git tags at each phase completion

---

## Future Enhancements (Post-Sprint 4)

Features deferred for future sprints:

1. **Advanced Settings**:
   - Default confidence threshold configuration (0.3-0.9 range)
   - Preferred export format selection (CSV vs KML default)
   - Tile count warning threshold adjustment
   - Geocoding provider preference (Google vs Azure)

2. **Setup Wizard Improvements**:
   - Video tutorial integration (embedded YouTube)
   - Interactive map preview during provider selection
   - API key cost estimation tool
   - One-click Azure/Google account creation links

3. **Performance Dashboard**:
   - Historical performance trend graph
   - Hardware detection info (GPU vs CPU)
   - Real-time system resource monitoring
   - Optimization recommendations

4. **Multi-Language Support**:
   - Internationalization (i18n) for wizard/settings
   - Language selection in Settings
   - Translated documentation links

5. **Enterprise Features** (if cloud deployment pursued):
   - Multi-user access with role management
   - Audit log for configuration changes
   - Azure Key Vault integration for API keys
   - SSO authentication via Azure AD

---

## Related Documentation

- [Plan Document](../../../memories/session/plan.md) - Detailed implementation strategy
- [TASK-025: Docker Containerization](../task-backlog.md#task-025) - Volume mount requirements
- [TASK-001: API Key Security](../completed-tasks.md#task-001) - Environment variable foundation
- [TASK-039: Google Maps API Upgrade](../current-tasks.md#task-039) - Provider management patterns
- [MIGRATION_GUIDE.md](../context/guides/MIGRATION_GUIDE.md) - User setup instructions (to be updated)

---

## Version History

- **v1.0** (March 16, 2026) - Initial task document created based on user requirements and architectural analysis

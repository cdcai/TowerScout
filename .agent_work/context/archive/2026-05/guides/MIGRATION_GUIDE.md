# TowerScout API Key Security Migration Guide

## 🚨 URGENT: API Key Security Fix

This migration addresses a **CRITICAL SECURITY VULNERABILITY** where API keys were stored in plain text files. All deployments must be updated immediately.

---

## 📋 Migration Overview

**What Changed:**
- API keys now loaded from environment variables instead of `apikey.txt`
- Flask secret key now required as environment variable
- Added comprehensive configuration management
- Enhanced error handling for missing configuration

**Impact:**
- **Existing deployments will not start** without environment configuration
- **No functionality changes** - all cooling tower detection features preserved
- **Improved security** - no secrets in source code or file system

---

## 🔧 Migration Steps

### Step 1: Install Updated Dependencies

```bash
cd webapp/
pip install -r requirements.txt
```

**New dependency:** `python-dotenv==1.0.0` for environment variable loading

### Step 2: Create Environment Configuration

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual values:**
   ```bash
   # Required API Keys
   GOOGLE_API_KEY=your_actual_google_maps_api_key_here
   BING_API_KEY=your_actual_bing_maps_api_key_here
   
   # Required Flask Secret Key (generate a new one!)
   FLASK_SECRET_KEY=your_64_character_secret_key_here
   
   # Application Settings
   FLASK_ENV=production
   FLASK_DEBUG=false
   DEFAULT_MAP_PROVIDER=google
   ```

3. **Generate a secure Flask secret key:**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Step 3: Migrate API Keys from Old Format

If you have an existing `apikey.txt` file:

1. **Extract your keys:**
   ```bash
   # View your current keys (DO NOT SHARE THIS OUTPUT)
   cat apikey.txt
   ```

2. **Copy keys to .env file:**
   - First line → `GOOGLE_API_KEY=`
   - Second line → `BING_API_KEY=`

3. **Secure the old file:**
   ```bash
   # Remove the insecure file
   rm apikey.txt
   ```

### Step 4: Update File Permissions

```bash
# Secure the environment file
chmod 600 .env
chown $(whoami):$(whoami) .env
```

### Step 5: Test the Migration

```bash
# Test that the application starts correctly
python towerscout.py
```

**Expected output:**
```
Loading environment variables...
Google API key loaded successfully
Bing API key loaded successfully
Flask secret key configured
Torch cuda: is/is not available
Starting Flask application...
```

**If you see errors:**
- `Configuration Error: GOOGLE_API_KEY environment variable is required` → Check your .env file
- `Configuration Error: FLASK_SECRET_KEY environment variable is required` → Generate and add secret key
- `ModuleNotFoundError: No module named 'dotenv'` → Run `pip install -r requirements.txt`

---

## 🐳 Docker Deployment Migration

### Option 1: Environment File

```dockerfile
# In your docker-compose.yml
services:
  towerscout:
    build: .
    env_file:
      - webapp/.env
    volumes:
      - ./webapp/model_params:/app/model_params
      - ./webapp/uploads:/app/uploads
```

### Option 2: Environment Variables

```dockerfile
# In your docker-compose.yml
services:
  towerscout:
    build: .
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - BING_API_KEY=${BING_API_KEY}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - FLASK_ENV=production
```

---

## 🔧 SystemD Service Migration

If you're using the systemd service from `hosting/towerscout.service`:

1. **Update the service file:**
   ```ini
   [Unit]
   Description=TowerScout Cooling Tower Detection Service
   After=network.target
   
   [Service]
   Type=simple
   User=towerscout
   WorkingDirectory=/path/to/TowerScout/webapp
   EnvironmentFile=/path/to/TowerScout/webapp/.env
   ExecStart=/path/to/venv/bin/python towerscout.py
   Restart=always
   RestartSec=3
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Reload and restart:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart towerscout
   sudo systemctl status towerscout
   ```

---

## 🛡️ Security Best Practices

### ✅ Do This:
- **Generate unique secret keys** for each deployment
- **Use strong API keys** with minimal required permissions
- **Set file permissions** to 600 for .env files
- **Never commit** .env files to version control
- **Rotate keys regularly** (quarterly recommended)
- **Monitor API usage** to detect unauthorized access

### ❌ Never Do This:
- Store API keys in source code files
- Commit .env files to git repositories
- Share API keys in chat, email, or documentation
- Use default or example secret keys in production
- Deploy without HTTPS in production environments

---

## 🔍 Troubleshooting

### Application Won't Start

**Error:** `Configuration Error: GOOGLE_API_KEY environment variable is required`
- **Solution:** Check that `.env` file exists and contains `GOOGLE_API_KEY=your_key_here`
- **Verify:** `cat .env | grep GOOGLE_API_KEY`

**Error:** `Configuration Error: FLASK_SECRET_KEY environment variable is required`
- **Solution:** Generate a secret key and add to .env file
- **Command:** `python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"`

**Error:** `ModuleNotFoundError: No module named 'dotenv'`
- **Solution:** Install updated dependencies
- **Command:** `pip install -r requirements.txt`

### Map Provider Issues

**Error:** API key validation errors from Google/Bing
- **Check:** API key has correct permissions
- **Required for Google:** Maps JavaScript API, Maps Static API, Places API
- **Required for Bing:** Bing Maps API with imagery access

### Permission Issues

**Error:** Permission denied reading .env file
- **Solution:** Fix file permissions
- **Command:** `chmod 600 .env && chown $(whoami) .env`

---

## 📞 Emergency Rollback

If you need to temporarily rollback while troubleshooting:

1. **Create a temporary apikey.txt file:**
   ```bash
   echo "your_google_api_key" > apikey.txt
   echo "your_bing_api_key" >> apikey.txt
   ```

2. **Checkout the previous version:**
   ```bash
   git checkout HEAD~1 -- webapp/towerscout.py
   ```

3. **Fix the issue, then re-apply the security fix:**
   ```bash
   git checkout HEAD -- webapp/towerscout.py
   ```

**⚠️ WARNING:** The rollback creates the same security vulnerability. Use only for emergency troubleshooting and re-apply the fix immediately.

---

## ✅ Migration Verification Checklist

- [ ] `.env` file created with all required variables
- [ ] `.env` file permissions set to 600
- [ ] Application starts without errors
- [ ] Can detect cooling towers (functionality test)
- [ ] No `apikey.txt` file in working directory
- [ ] Docker/systemd service updated (if applicable)
- [ ] Old insecure files removed
- [ ] Team members notified of new configuration requirements

---

## 📚 Additional Resources

- **Environment Variable Best Practices:** [12factor.net/config](https://12factor.net/config)
- **Flask Security Guide:** [flask.palletsprojects.com/security](https://flask.palletsprojects.com/security/)
- **Google Maps API Security:** [developers.google.com/maps/api-security-best-practices](https://developers.google.com/maps/api-security-best-practices)

---

## 🆘 Support

If you encounter issues during migration:

1. **Check the logs** for specific error messages
2. **Verify environment variables** are loaded correctly
3. **Test API keys** work with curl/browser
4. **Review file permissions** on .env file
5. **Consult troubleshooting section** above

For additional support, create an issue with:
- Complete error message
- Your deployment method (Docker/systemd/manual)
- Output of `python --version` and `pip list`
- Confirmation that .env file exists and has correct permissions
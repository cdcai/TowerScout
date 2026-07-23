# Node.js Installation Guide for TowerScout Stage 1+

## Why Node.js is Required

Starting with **Stage 1**, the refactoring workflow uses:
- **Build Script** (`webapp/build.js`) - Concatenates modular source files into `towerscout.js`
- **Automated Tests** - Puppeteer-based browser testing
- **Pre-commit Hook** - Auto-rebuilds bundle when source files change

## Installation Steps (Windows)

### Option 1: Official Node.js Installer (Recommended)

**1. Download Node.js LTS**
- Visit: https://nodejs.org/
- Download: **LTS (Long Term Support)** version - Currently v20.x or v22.x
- Choose: **Windows Installer (.msi)** - 64-bit

**2. Run Installer**
- Double-click downloaded `.msi` file
- Click "Next" through wizard
- ✅ **Important**: Check "Automatically install necessary tools" (includes npm)
- Accept default installation path: `C:\Program Files\nodejs\`
- Click "Install"

**3. Restart Git Bash**
- Close all Git Bash terminals
- Open new Git Bash terminal
- Node.js will now be in PATH

**4. Verify Installation**
```bash
node --version    # Should show: v20.x.x or v22.x.x
npm --version     # Should show: v10.x.x or similar
```

### Option 2: Windows Package Manager (Alternative)

If you have Windows Package Manager (winget):
```powershell
winget install OpenJS.NodeJS.LTS
```

Then restart terminal and verify.

---

## Post-Installation Steps

### 1. Install TowerScout Dependencies
```bash
cd /c/Users/bg90/TowerScout
npm install
```

**Expected output:**
```
added 124 packages in 45s
```

This installs:
- `puppeteer` (~350MB including Chromium browser)
- Other test dependencies

### 2. Test Build Script
```bash
node webapp/build.js
```

**Expected output (Stage 0):**
```
ERROR: Source directory not found: webapp/js/src/
NOTE: This is expected in Stage 0 - src/ will be created in Stage 1
```

### 3. Verify Pre-commit Hook
```bash
git status
# Should show clean state or remaining task file updates
```

The pre-commit hook will now properly detect Node.js and run builds.

---

## Troubleshooting

### "node: command not found" after install

**Problem**: Git Bash doesn't see new PATH  
**Solution**: 
1. Close **ALL** Git Bash windows
2. Open **new** Git Bash
3. Try: `node --version` again

### npm install fails with permission errors

**Problem**: Missing admin rights  
**Solution**: Run Git Bash as Administrator, then `npm install`

### Build script fails with "MODULE_ORDER not defined"

**Problem**: Old cached version  
**Solution**: Hard refresh browser (Ctrl+Shift+R) after rebuild

---

## Stage 1 Readiness Checklist

Before beginning Stage 1, verify:
- [ ] `node --version` shows v16+ 
- [ ] `npm --version` shows v8+
- [ ] `npm install` completed successfully
- [ ] `webapp/build.js` file exists (already created ✅)
- [ ] Git Bash restarted after Node.js install

---

## Next Steps After Installation

Once Node.js is installed and verified:

1. **Update task file** with Node.js installation completion
2. **Begin Stage 1** - Create foundation files (8 hours)
3. **Run build script** - Concatenate modules
4. **Validate** - Run global contract + endpoint tests
5. **Commit** - Stage 1 changes

---

## Current Status

- ✅ Stage 0: Complete (array mutations committed)
- ⏳ Node.js: Installation in progress
- 🎯 Stage 1: Ready to begin after Node.js verified

**Installation time**: ~5-10 minutes  
**Next session**: Stage 1 foundation files (8 hours estimated)

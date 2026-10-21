# UTF-8 Encoding Configuration Guide

**Date**: April 7, 2026  
**Purpose**: Ensure all documentation and text files use UTF-8 encoding across all platforms

## Overview

TowerScout now enforces UTF-8 encoding at multiple levels to ensure consistent handling of text files, especially documentation that may contain addresses with special characters (accents, non-ASCII characters, etc.).

## Configuration Layers

### 1. Git Configuration (`.gitattributes`)

The `.gitattributes` file ensures Git handles text files consistently across Windows, macOS, and Linux:

```gitattributes
# Documentation explicitly UTF-8
*.md text eol=lf working-tree-encoding=UTF-8
*.txt text eol=lf working-tree-encoding=UTF-8

# All text files use LF line endings
* text=auto eol=lf
```

**What this does:**
- Forces LF line endings (no CRLF issues on Windows)
- Explicitly marks documentation files as UTF-8
- Prevents binary files from being corrupted

### 2. Editor Configuration (`.editorconfig`)

Already in place - sets UTF-8 for all files:

```ini
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
```

### 3. VS Code Workspace Settings (`.vscode/settings.json`)

Enforces UTF-8 in the editor:

```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\n"
}
```

**What this does:**
- Prevents VS Code from using Windows-1252 or other encodings
- Disables automatic encoding detection (enforces UTF-8)
- Uses LF line endings consistently

### 4. Python Code (`webapp/*.py`)

All file operations now explicitly specify UTF-8:

```python
# ❌ OLD (platform-dependent encoding)
with open(filename, "w") as f:
    f.write(content)

# ✅ NEW (explicit UTF-8)
with open(filename, "w", encoding="utf-8") as f:
    f.write(content)
```

**Files Fixed:**
- `towerscout.py` line 2749 (label files)
- `towerscout.py` line 2771 (XML files)
- `towerscout.py` line 2821 (contents.txt with address data)

## Why This Matters

### Problem Without UTF-8 Enforcement

On Windows, Python's default encoding is often `cp1252` (Windows Latin-1), not UTF-8. This causes:

1. **Address Data Issues**: Addresses with accents (e.g., "São Paulo", "Montréal") get corrupted
2. **Documentation Issues**: Markdown files with special characters render incorrectly
3. **Export Issues**: CSV/KML exports with international addresses fail or display incorrectly
4. **Platform Inconsistency**: Files created on Windows break on Linux/macOS and vice versa

### Example Failure Scenario

```python
# Without encoding="utf-8" on Windows
with open("contents.txt", "w") as f:
    f.write(json.dumps({"address": "São Paulo, Brazil"}))

# Result: "S├úo Paulo" (cp1252 encoding saved, UTF-8 read)
```

## Verification

### Check Current File Encoding

**In VS Code:**
- Look at bottom-right status bar
- Should show "UTF-8" (not "Windows-1252" or "ASCII")

**From Command Line:**
```bash
file -bi <filename>
# Should show: charset=utf-8
```

### Check Git Configuration

```bash
git check-attr text working-tree-encoding -- "*.md"
# Should show: working-tree-encoding: UTF-8
```

### Test Python File Operations

```python
import sys
import locale

# Check default encoding
print(f"Default encoding: {locale.getpreferredencoding()}")
print(f"stdout encoding: {sys.stdout.encoding}")
# Should print: UTF-8 (not cp1252 or ASCII)
```

## Coding Standards Going Forward

### ✅ Required: Explicit Encoding for All File Operations

```python
# Reading
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Writing
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Reading CSV
with open(path, "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

# Writing CSV
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
```

### ❌ Forbidden: Implicit Encoding

```python
# DON'T - platform-dependent!
with open(path, "r") as f:  # ❌ Missing encoding
    content = f.read()
```

### Exception: Binary Files

Binary operations should use `"rb"` or `"wb"` mode (no encoding parameter):

```python
# Binary files (images, model weights, etc.)
with open("model.pt", "rb") as f:
    data = f.read()
```

## CI/CD Integration

### Lint Check (Future)

Add to CI pipeline:

```bash
# Check for file operations without explicit encoding
grep -rn "open.*['\"]w['\"].*) as" webapp/*.py
```

### Pre-commit Hook (Optional)

```bash
#!/bin/bash
# Reject commits with open() calls missing encoding
git diff --cached --name-only | grep '\.py$' | while read file; do
    if git diff --cached "$file" | grep -E "open\([^)]*['\"]w['\"][^)]*\) as" | grep -v "encoding="; then
        echo "❌ File operation missing encoding in: $file"
        exit 1
    fi
done
```

## Troubleshooting

### Issue: VS Code Shows Wrong Encoding

**Solution:**
1. Click encoding in status bar (bottom-right)
2. Select "Reopen with Encoding" → "UTF-8"
3. If content is garbled, file was already corrupted - restore from Git

### Issue: Git Shows Line-Ending Warnings

```
warning: LF will be replaced by CRLF
```

**Solution:**
```bash
# Re-normalize line endings
git add --renormalize .
git commit -m "Normalize line endings to LF"
```

### Issue: Python Still Uses Wrong Encoding

**Diagnosis:**
```python
import locale
print(locale.getpreferredencoding(False))
```

**Solution:**
Set environment variable:
```bash
# Windows PowerShell
$env:PYTHONIOENCODING = "utf-8"

# Windows CMD
set PYTHONIOENCODING=utf-8

# Linux/macOS
export PYTHONIOENCODING=utf-8
```

Or in code:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## References

- Python PEP 597: https://peps.python.org/pep-0597/ (explicit encoding recommended)
- Git attributes: https://git-scm.com/docs/gitattributes
- EditorConfig: https://editorconfig.org/
- VS Code encoding: https://code.visualstudio.com/docs/editor/codebasics#_file-encoding-support

## Audit History

- **April 7, 2026**: Initial configuration
  - Created `.gitattributes`
  - Updated `.vscode/settings.json`
  - Fixed 3 file operations in `towerscout.py`
  - Added `encoding="utf-8"` to all text file operations

## Maintenance

- **Monthly**: Audit new file operations for missing encoding
- **Per PR**: Review any new `open()` calls in Python code
- **Per sprint**: Verify encoding configuration still in place after large refactors

@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0import-assets.ps1" %*

@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0import-tls-ca.ps1" %*

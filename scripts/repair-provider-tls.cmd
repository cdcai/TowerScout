@echo off
setlocal

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0repair-provider-tls.ps1" %*
exit /b %ERRORLEVEL%

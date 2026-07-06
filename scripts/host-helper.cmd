@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0host-helper.ps1" %*
exit /b %ERRORLEVEL%

@echo off
setlocal

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-towerscout.ps1" %*
exit /b %ERRORLEVEL%

@echo off
setlocal
start "TowerScout Host Helper (Gate 1)" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0host-helper.ps1" %*
exit /b %ERRORLEVEL%

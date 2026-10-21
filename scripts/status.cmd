@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0status.ps1" %*

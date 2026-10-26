@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0logs.ps1" %*

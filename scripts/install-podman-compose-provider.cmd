@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-podman-compose-provider.ps1" %*

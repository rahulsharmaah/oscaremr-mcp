@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_oscar_emr_mcp_windows.ps1"
echo.
pause

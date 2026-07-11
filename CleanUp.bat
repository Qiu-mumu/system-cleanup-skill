@echo off
title CleanUp
echo Step 1: pip cache
pip cache purge
echo Step 2: npm cache
npm cache clean --force
echo Step 3: NVIDIA shader cache
if exist "%USERPROFILE%\.cache\DXCache" (del /f /s /q "%USERPROFILE%\.cache\DXCache\*.*")
echo Step 4: Temp files
del /f /s /q "%TEMP%\*.*"
echo Step 5: Recycle Bin
powershell -Command Clear-RecycleBin -Force
echo Done.
pause
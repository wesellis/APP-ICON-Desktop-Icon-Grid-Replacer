@echo off
title ICON - Desktop Icon Grid Replacer
color 0A

:MENU
cls
echo ===============================================
echo    ICON - Desktop Icon Grid Replacer v1.0
echo         By Wesley Ellis
echo ===============================================
echo.
echo What would you like to do?
echo.
echo  1. Setup (First time configuration)
echo  2. Replace Desktop Icons (Auto - no confirmation)
echo  3. Replace Desktop Icons (Interactive - review each)
echo  4. List Desktop Items
echo  5. Remove UAC/Shortcut Overlays
echo  6. Restore Default Overlays
echo  7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto SETUP
if "%choice%"=="2" goto REPLACE_AUTO
if "%choice%"=="3" goto REPLACE_INTERACTIVE
if "%choice%"=="4" goto LIST
if "%choice%"=="5" goto REMOVE_OVERLAYS
if "%choice%"=="6" goto RESTORE_OVERLAYS
if "%choice%"=="7" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:SETUP
cls
echo ===============================================
echo    Setup Wizard
echo ===============================================
echo.
if exist "dist\ICON.exe" (
    dist\ICON.exe --setup
) else (
    python icon_replacer.py --setup
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:REPLACE_AUTO
cls
echo ===============================================
echo    Replace Desktop Icons (Auto Mode)
echo ===============================================
echo.
echo This will automatically replace ALL desktop icons
echo without asking for confirmation on each one.
echo.
if exist "dist\ICON.exe" (
    dist\ICON.exe --auto
) else (
    python icon_replacer.py --auto
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:REPLACE_INTERACTIVE
cls
echo ===============================================
echo    Replace Desktop Icons (Interactive Mode)
echo ===============================================
echo.
echo This will show you each icon and ask for confirmation
echo before applying it. Type 'y' to apply, 'n' to skip,
echo or 'skip all' to skip the rest.
echo.
if exist "dist\ICON.exe" (
    dist\ICON.exe
) else (
    python icon_replacer.py
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:LIST
cls
echo ===============================================
echo    Desktop Items List
echo ===============================================
echo.
if exist "dist\ICON.exe" (
    dist\ICON.exe --list
) else (
    python icon_replacer.py --list
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:REMOVE_OVERLAYS
cls
echo ===============================================
echo    Remove UAC/Shortcut Overlays
echo ===============================================
echo.
if exist "dist\ICON.exe" (
    dist\ICON.exe --remove-overlays
) else (
    python icon_replacer.py --remove-overlays
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:RESTORE_OVERLAYS
cls
echo ===============================================
echo    Restore Default Overlays
echo ===============================================
echo.
if exist "dist\ICON.exe" (
    dist\ICON.exe --restore-overlays
) else (
    python icon_replacer.py --restore-overlays
)
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:EXIT
cls
echo.
echo Thank you for using ICON!
echo.
timeout /t 2 >nul
exit

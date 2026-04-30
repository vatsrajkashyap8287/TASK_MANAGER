@echo off
echo ==========================================
echo Railway Connection Diagnostic
echo ==========================================
echo.

echo 1. Checking Internet Connection...
ping -n 1 railway.app >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Can reach railway.app
) else (
    echo ❌ Cannot reach railway.app
    echo Check your internet connection
)
echo.

echo 2. Checking Railway CLI...
where railway >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Railway CLI installed
    railway --version
) else (
    echo ❌ Railway CLI not found
)
echo.

echo 3. Testing Railway API...
curl -s https://backboard.railway.com/graphql/v2 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Can reach Railway API
) else (
    echo ❌ Cannot reach Railway API
    echo Try:
    echo - Disable VPN
    echo - Check Firewall
    echo - Use GitHub + Dashboard method
)
echo.

echo ==========================================
echo Recommendation:
echo Use GitHub + Railway Dashboard method
echo ==========================================
pause
@echo off
REM Creator Growth Radar - One-Click Deploy Script
REM This script helps you deploy to Railway and Vercel

echo.
echo ========================================
echo   Creator Growth Radar - Deployment
echo ========================================
echo.

REM Check if logged into Railway
echo [1/4] Checking Railway login...
railway whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ! Railway login required!
    echo.
    echo Please run: railway login
    echo.
    echo Then re-run this script.
    pause
    exit /b 1
)
echo ✓ Railway logged in

REM Check if logged into Vercel
echo.
echo [2/4] Checking Vercel login...
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ! Vercel login required!
    echo.
    echo Please run: vercel login
    echo.
    echo Then re-run this script.
    pause
    exit /b 1
)
echo ✓ Vercel logged in

REM Get RapidAPI Key
echo.
echo [3/4] RapidAPI Key
echo.
echo Please enter your RapidAPI key (get free key at rapidapi.com):
set /p RAPIDAPI_KEY=
if "%RAPIDAPI_KEY%"=="" (
    echo Error: RapidAPI key is required!
    pause
    exit /b 1
)

REM Deploy Backend to Railway
echo.
echo [4/4] Deploying Backend to Railway...
cd backend
railway link --project creator-growth-radar 2>nul || railway init --project creator-growth-radar
railway variables set RAPIDAPI_KEY=%RAPIDAPI_KEY%
railway up --detach
cd ..

echo.
echo ========================================
echo   Backend Deployed!
echo ========================================
echo.

REM Get Railway URL
for /f "delims=" %%i in ('railway domain') do set RAILWAY_URL=%%i
echo Backend URL: %RAILWAY_URL%

REM Update frontend with backend URL
echo.
echo Updating frontend configuration...
powershell -Command "(Get-Content frontend\app.js) -replace 'https://creator-growth-radar-production.up.railway.app', '%RAILWAY_URL%' | Set-Content frontend\app.js"

REM Deploy Frontend to Vercel
echo.
echo Deploying Frontend to Vercel...
cd frontend
vercel deploy --prod --yes
cd ..

echo.
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Frontend URL: (check Vercel output above)
echo Backend URL: %RAILWAY_URL%
echo.
echo Test your app by visiting the frontend URL!
echo.
pause

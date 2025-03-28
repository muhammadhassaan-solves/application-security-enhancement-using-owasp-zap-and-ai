@echo off
echo =============================================
echo Starting Full ZAP + AI Integration Process...
echo =============================================

REM ---------------------------------------
REM 0. CONFIGURATION
REM Update these variables with your details:
set ZAP_PATH="C:\Program Files\ZAP\Zed Attack Proxy\ZAP.exe"
set API_KEY=Confidential
set TARGET_URL=http://www.itsecgames.com/
set JSON_REPORT_PATH="C:\Users\Ait\Desktop\ZAP-Report.json"
set PYTHON_SCRIPT_FOLDER="C:\Users\Ait\Desktop"

REM ---------------------------------------
REM 1. Start ZAP in daemon mode
echo Starting OWASP ZAP in daemon mode...
start "" %ZAP_PATH% -daemon -port 8080 -config api.key=%API_KEY%
if errorlevel 1 (
    echo Error: Failed to start ZAP. Check the path and try again.
    pause
    exit /b 1
)
echo ZAP started. Waiting 60 seconds for initialization...
timeout /t 60

REM ---------------------------------------
REM 2. Spider the target
echo Triggering spider on target URL (%TARGET_URL%)...
curl -s -o spider_start.json ^
  "http://localhost:8080/JSON/spider/action/scan/?apikey=%API_KEY%&url=%TARGET_URL%&recurse=true&inScopeOnly=false"
if errorlevel 1 (
    echo Error: Failed to trigger spider. Ensure curl is installed and ZAP is running.
    pause
    exit /b 1
)
echo Spider triggered. Checking spider status...

REM Get the spider ID from spider_start.json (usually "0", but we'll assume it’s 0)
set SPIDER_ID=0

REM ---------------------------------------
REM 3. Poll spider status
:spider_wait
curl -s -o spider_status.json ^
  "http://localhost:8080/JSON/spider/view/status/?apikey=%API_KEY%&scanId=%SPIDER_ID%"
findstr /i /c:"100" spider_status.json >nul
if %errorlevel%==0 (
    echo Spider complete.
) else (
    echo Spider still in progress... waiting 15 seconds.
    timeout /t 15
    goto spider_wait
)

REM ---------------------------------------
REM 4. Active Scan the target
echo Triggering active scan on target URL (%TARGET_URL%)...
curl -s -o ascan_start.json ^
  "http://localhost:8080/JSON/ascan/action/scan/?apikey=%API_KEY%&url=%TARGET_URL%&recurse=true&inScopeOnly=false"
if errorlevel 1 (
    echo Error: Failed to trigger active scan.
    pause
    exit /b 1
)
echo Active scan triggered. Checking scan status...

REM Assume scan ID is 0
set SCAN_ID=0

REM ---------------------------------------
REM 5. Poll active scan status
:ascan_wait
curl -s -o ascan_status.json ^
  "http://localhost:8080/JSON/ascan/view/status/?apikey=%API_KEY%&scanId=%SCAN_ID%"
findstr /i /c:"100" ascan_status.json >nul
if %errorlevel%==0 (
    echo Active scan complete.
) else (
    echo Active scan still in progress... waiting 15 seconds.
    timeout /t 15
    goto ascan_wait
)

REM ---------------------------------------
REM 6. Generate JSON report
echo Generating JSON report at %JSON_REPORT_PATH%...
curl -s -o %JSON_REPORT_PATH% ^
  "http://localhost:8080/OTHER/core/other/jsonreport/?apikey=%API_KEY%"
if errorlevel 1 (
    echo Error: Failed to generate JSON report.
    pause
    exit /b 1
)
echo JSON report generated at %JSON_REPORT_PATH%.
timeout /t 5

REM ---------------------------------------
REM 7. Convert JSON report to CSV
echo Converting JSON report to CSV...
python "%PYTHON_SCRIPT_FOLDER%\generate_zap_report.py"
if errorlevel 1 (
    echo Error: generate_zap_report.py failed.
    pause
    exit /b 1
)
echo JSON report converted to CSV.

REM ---------------------------------------
REM 8. Rename CSV columns
echo Renaming columns...
python "%PYTHON_SCRIPT_FOLDER%\rename_columns.py"
if errorlevel 1 (
    echo Error: rename_columns.py failed.
    pause
    exit /b 1
)
echo Columns renamed in CSV.
timeout /t 3

REM ---------------------------------------
REM 9. Run AI-driven testing script
echo Running AI-driven testing script...
python "%PYTHON_SCRIPT_FOLDER%\ai_driven_testing.py"
if errorlevel 1 (
    echo Error: ai_driven_testing.py failed.
    pause
    exit /b 1
)
echo AI-driven testing complete.

echo =============================================
echo Full Integration process complete.
pause

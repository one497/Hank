@echo off
REM Windows 무인 실행 래퍼.
REM 작업 스케줄러에 이 파일을 등록하면 새 DEM이 들어올 때마다 도면이 나온다.
chcp 65001 >nul
setlocal

set "HERE=%~dp0.."
REM 아래 세 줄만 현장에 맞게 고치세요.
set "IN_DIR=%HERE%\입력"
set "OUT_DIR=%HERE%\출력"
set "ARCHIVE_DIR=%HERE%\처리완료"

set "PYTHONPATH=%HERE%;%PYTHONPATH%"
set "PYTHONIOENCODING=utf-8"

python -m terrain2dxf watch "%IN_DIR%" "%OUT_DIR%" ^
    --archive "%ARCHIVE_DIR%" ^
    --once ^
    --ground-filter ^
    --flatten-z ^
    --scale 1/1000 ^
    --log "%OUT_DIR%\자동처리.log"

if errorlevel 1 (
    echo.
    echo 처리 중 오류가 발생했습니다. 위 메시지와 로그 파일을 확인하세요.
    pause
)
endlocal

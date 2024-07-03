@echo off
set /p serial="Enter the serial number: "
set /p count="Enter the number of repetitions: "

:: 반복 횟수에 따라 파일을 생성하고 빌드
for /L %%i in (1,1,%count%) do (
    set "SERIAL_NUM=%serial%%%i"
    call setlocal enabledelayedexpansion
    call echo serial_number = "!SERIAL_NUM!" > serial_config.py
    call python combine_script.py !SERIAL_NUM!
    call set "SERIAL=!SERIAL_NUM!"
    call set "BUILD_DIR=build\exe.win-amd64-3.12"
    call set "TARGET_DIR=build\!SERIAL!"
    call python setup.py build

    :: 생성된 exe 폴더를 serial명으로 변경
    if exist "!TARGET_DIR!" rmdir /S /Q "!TARGET_DIR!"
    ren "!BUILD_DIR!" "!SERIAL!"

    :: build\serial 폴더 내에 assets 폴더 생성
    mkdir "!TARGET_DIR!\assets"

    :: assets 폴더의 모든 파일과 디렉토리를 build\serial\assets 폴더로 복사
    xcopy assets "!TARGET_DIR!\assets\" /E /I /Y

    endlocal
)
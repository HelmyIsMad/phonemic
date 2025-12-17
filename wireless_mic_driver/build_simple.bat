@echo off
echo ========================================
echo Building Wireless Microphone Driver
echo ========================================

echo Setting up Visual Studio environment...

REM Try to find Visual Studio 18 Community first (newer version)
set VS_PATH=C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat
if exist "%VS_PATH%" (
    echo Found Visual Studio 18 Community
    call "%VS_PATH%" x64
    goto :check_compiler
)

REM Try Visual Studio 2022 Community
set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat
if exist "%VS_PATH%" (
    echo Found Visual Studio 2022 Community
    call "%VS_PATH%" x64
    goto :check_compiler
)

REM Try Visual Studio 2022 Professional
set VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat
if exist "%VS_PATH%" (
    echo Found Visual Studio 2022 Professional
    call "%VS_PATH%" x64
    goto :check_compiler
)

REM Try Visual Studio 2019 Community
set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat
if exist "%VS_PATH%" (
    echo Found Visual Studio 2019 Community
    call "%VS_PATH%" x64
    goto :check_compiler
)

echo ERROR: Visual Studio not found!
echo Please install Visual Studio 2022 Community from:
echo https://visualstudio.microsoft.com/vs/community/
echo Make sure to select "Desktop development with C++" workload
pause
exit /b 1

:check_compiler
echo Checking for compiler...
where cl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Compiler not found after setting up Visual Studio!
    echo Make sure C++ development tools are installed.
    pause
    exit /b 1
)
echo Compiler found successfully!

REM Check for CMake
echo Checking for CMake...
where cmake >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CMake not found!
    echo Please install CMake from: https://cmake.org/download/
    pause
    exit /b 1
)

REM Create and enter build directory
if not exist build mkdir build
cd build

echo Configuring with CMake...
cmake -G "Visual Studio 18 2026" -A x64 ..
if %ERRORLEVEL% NEQ 0 (
    echo Trying Visual Studio 2022...
    cmake -G "Visual Studio 17 2022" -A x64 ..
    if %ERRORLEVEL% NEQ 0 (
        echo Trying Visual Studio 2019...
        cmake -G "Visual Studio 16 2019" -A x64 ..
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: CMake configuration failed!
            pause
            cd ..
            exit /b 1
        )
    )
)

echo Building Release version...
cmake --build . --config Release --verbose
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    cd ..
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
dir Release\*.dll
echo.
echo DLL location: %cd%\Release\
echo.
echo Next step: Test with python ..\python\driver_interface.py
echo.

cd ..
pause
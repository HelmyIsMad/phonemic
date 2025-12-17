@echo off
echo ========================================
echo Building Wireless Microphone Driver
echo ========================================

REM Check if Visual Studio is available
where cl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Setting up Visual Studio environment...
    
    REM Try different Visual Studio versions
    if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
        call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    ) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
        call "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" x64
    ) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
        call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    ) else (
        echo ERROR: Visual Studio not found!
        echo Please install Visual Studio 2019 or 2022 with C++ support
        echo Download from: https://visualstudio.microsoft.com/downloads/
        pause
        exit /b 1
    )
)

REM Create build directory
if not exist build mkdir build
cd build

REM Check for CMake
where cmake >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CMake not found!
    echo Please install CMake from: https://cmake.org/download/
    pause
    exit /b 1
)

echo Generating project files with CMake...
cmake -G "Visual Studio 16 2019" -A x64 ..
if %ERRORLEVEL% NEQ 0 (
    echo Trying Visual Studio 2022...
    cmake -G "Visual Studio 17 2022" -A x64 ..
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: CMake configuration failed!
        pause
        exit /b 1
    )
)

echo Building Release version...
cmake --build . --config Release
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Driver DLL location:
dir /b Release\*.dll 2>nul
if %ERRORLEVEL% EQU 0 (
    echo %cd%\Release\
) else (
    echo Build output not found in expected location
)

echo.
echo Next steps:
echo 1. Test the driver with: python ..\python\driver_interface.py
echo 2. Integrate with existing PC client
echo.

cd ..
pause
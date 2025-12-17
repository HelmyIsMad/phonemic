@echo off
echo ========================================
echo Building Wireless Microphone Driver
echo ========================================

REM Always try to set up Visual Studio environment (don't rely on PATH)
echo Setting up Visual Studio environment...

set VCVARSALL_FOUND=0

REM Try Visual Studio 2022 locations (in order of preference)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2022 Enterprise
    call "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2022 Professional
    call "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2022 Community
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2022 Build Tools
    call "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2019 Enterprise
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2019 Professional
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2019 Community
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2019 Build Tools
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
    set VCVARSALL_FOUND=1
)

REM Check if we found and set up Visual Studio
if %VCVARSALL_FOUND%==0 (
    echo.
    echo ERROR: Visual Studio not found in any standard location!
    echo.
    echo Please install one of the following:
    echo - Visual Studio 2022 Community (free): https://visualstudio.microsoft.com/vs/community/
    echo - Visual Studio 2019 Community (free): https://visualstudio.microsoft.com/vs/older-downloads/
    echo - Make sure to select "Desktop development with C++" workload during installation
    echo.
    echo Searched in these locations:
    echo - C:\Program Files\Microsoft Visual Studio\2022\
    echo - C:\Program Files (x86)\Microsoft Visual Studio\2019\
    echo.
    pause
    exit /b 1
)

REM Verify compiler is now available
where cl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Compiler (cl.exe) not found even after setting up Visual Studio environment!
    echo This might indicate an incomplete Visual Studio installation.
    echo Make sure "Desktop development with C++" workload is installed.
    pause
    exit /b 1
)

echo Visual Studio environment set up successfully!

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
cmake -G "Visual Studio 17 2022" -A x64 ..
if %ERRORLEVEL% NEQ 0 (
    echo Trying Visual Studio 2019...
    cmake -G "Visual Studio 16 2019" -A x64 ..
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
cmake_minimum_required(VERSION 3.16)
project(WirelessMicDriver)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Windows-specific settings
if(WIN32)
    # Enable Unicode
    add_definitions(-DUNICODE -D_UNICODE)
    
    # Set Windows version
    add_definitions(-DWINVER=0x0A00 -D_WIN32_WINNT=0x0A00)
    
    # Enable COM support
    add_definitions(-D_ATL_NO_AUTOMATIC_NAMESPACE -D_ATL_CSTRING_EXPLICIT_CONSTRUCTORS)
endif()

# Include directories
include_directories(include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/VirtualAudioDevice.cpp
)

# Header files
set(HEADERS
    include/VirtualAudioDevice.h
)

# Create shared library (DLL)
add_library(WirelessMicDriver SHARED ${SOURCES} ${HEADERS})

# Windows-specific libraries
if(WIN32)
    target_link_libraries(WirelessMicDriver
        ole32
        oleaut32
        uuid
        winmm
        ksuser
        avrt
    )
    
    # Set DLL export definitions
    target_compile_definitions(WirelessMicDriver PRIVATE
        WIRELESS_MIC_DRIVER_EXPORTS
    )
    
    # Set output name
    set_target_properties(WirelessMicDriver PROPERTIES
        OUTPUT_NAME "wireless_mic_driver"
        PREFIX ""
    )
endif()

# Compiler-specific options
if(MSVC)
    # Enable all warnings
    target_compile_options(WirelessMicDriver PRIVATE /W4)
    
    # Enable exception handling
    target_compile_options(WirelessMicDriver PRIVATE /EHsc)
    
    # Optimize for release builds
    target_compile_options(WirelessMicDriver PRIVATE
        $<$<CONFIG:Release>:/O2>
        $<$<CONFIG:Release>:/DNDEBUG>
    )
    
    # Add debug info for debug builds
    target_compile_options(WirelessMicDriver PRIVATE
        $<$<CONFIG:Debug>:/Od>
        $<$<CONFIG:Debug>:/Zi>
        $<$<CONFIG:Debug>:/DEBUG>
    )
endif()

# Installation
install(TARGETS WirelessMicDriver
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(FILES ${HEADERS}
    DESTINATION include
)

# Create build scripts
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/build.bat.in
    ${CMAKE_CURRENT_BINARY_DIR}/build.bat
    @ONLY
)

# Print configuration info
message(STATUS "Building WirelessMicDriver")
message(STATUS "CMAKE_BUILD_TYPE: ${CMAKE_BUILD_TYPE}")
message(STATUS "CMAKE_CXX_COMPILER: ${CMAKE_CXX_COMPILER}")
message(STATUS "Target Platform: ${CMAKE_SYSTEM_NAME}")
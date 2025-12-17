#!/usr/bin/env python3
"""
Python interface for Wireless Microphone Virtual Audio Driver
Provides a bridge between the PC audio client and the native Windows driver
"""

import ctypes
import ctypes.wintypes
import os
import sys
from typing import Optional
import numpy as np

class DriverInterface:
    def __init__(self, dll_path: Optional[str] = None):
        """Initialize the driver interface"""
        self.dll = None
        self.is_initialized = False
        self.is_started = False
        
        # Default DLL path
        if dll_path is None:
            dll_path = self._find_dll_path()
        
        self.dll_path = dll_path
        
    def _find_dll_path(self) -> str:
        """Find the driver DLL in common locations"""
        possible_paths = [
            # Same directory as this script
            os.path.join(os.path.dirname(__file__), "..", "build", "Release", "wireless_mic_driver.dll"),
            os.path.join(os.path.dirname(__file__), "..", "build", "Debug", "wireless_mic_driver.dll"),
            os.path.join(os.path.dirname(__file__), "..", "wireless_mic_driver.dll"),
            # Current working directory
            "wireless_mic_driver.dll",
            # System PATH
            os.path.join(os.environ.get("SYSTEMROOT", "C:\\Windows"), "System32", "wireless_mic_driver.dll"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Could not find wireless_mic_driver.dll. Please build the driver first.")
    
    def load_driver(self) -> bool:
        """Load the driver DLL"""
        try:
            print(f"Loading driver from: {self.dll_path}")
            self.dll = ctypes.CDLL(self.dll_path)
            
            # Define function signatures
            self._define_function_signatures()
            
            print("✅ Driver DLL loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load driver DLL: {e}")
            return False
    
    def _define_function_signatures(self):
        """Define the C function signatures for proper calling"""
        if not self.dll:
            return
        
        # CreateDevice() -> HRESULT
        self.dll.CreateDevice.argtypes = []
        self.dll.CreateDevice.restype = ctypes.wintypes.HRESULT
        
        # StartDevice() -> HRESULT  
        self.dll.StartDevice.argtypes = []
        self.dll.StartDevice.restype = ctypes.wintypes.HRESULT
        
        # StopDevice() -> HRESULT
        self.dll.StopDevice.argtypes = []
        self.dll.StopDevice.restype = ctypes.wintypes.HRESULT
        
        # WriteAudio(data, size) -> HRESULT
        self.dll.WriteAudio.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.wintypes.UINT]
        self.dll.WriteAudio.restype = ctypes.wintypes.HRESULT
        
        # DestroyDevice() -> HRESULT
        self.dll.DestroyDevice.argtypes = []
        self.dll.DestroyDevice.restype = ctypes.wintypes.HRESULT
        
        # IsDeviceReady() -> BOOL
        self.dll.IsDeviceReady.argtypes = []
        self.dll.IsDeviceReady.restype = ctypes.wintypes.BOOL
    
    def initialize(self) -> bool:
        """Initialize the virtual audio device"""
        if not self.dll:
            print("❌ Driver not loaded")
            return False
        
        try:
            print("🔧 Initializing virtual audio device...")
            hr = self.dll.CreateDevice()
            
            if self._check_hresult(hr, "CreateDevice"):
                self.is_initialized = True
                print("✅ Virtual audio device initialized successfully")
                return True
            else:
                print("❌ Failed to initialize virtual audio device")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing device: {e}")
            return False
    
    def start(self) -> bool:
        """Start the virtual audio device"""
        if not self.is_initialized:
            print("❌ Device not initialized")
            return False
        
        try:
            print("🚀 Starting virtual audio device...")
            hr = self.dll.StartDevice()
            
            if self._check_hresult(hr, "StartDevice"):
                self.is_started = True
                print("✅ Virtual audio device started successfully")
                print("🎤 Device should now appear as microphone in Windows!")
                return True
            else:
                print("❌ Failed to start virtual audio device")
                return False
                
        except Exception as e:
            print(f"❌ Error starting device: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the virtual audio device"""
        if not self.is_started:
            return True
        
        try:
            print("🛑 Stopping virtual audio device...")
            hr = self.dll.StopDevice()
            
            if self._check_hresult(hr, "StopDevice"):
                self.is_started = False
                print("✅ Virtual audio device stopped successfully")
                return True
            else:
                print("❌ Failed to stop virtual audio device")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping device: {e}")
            return False
    
    def write_audio(self, audio_data: bytes) -> bool:
        """Write audio data to the virtual device"""
        if not self.is_started:
            return False
        
        try:
            # Convert bytes to ctypes array
            data_size = len(audio_data)
            data_array = (ctypes.c_ubyte * data_size).from_buffer_copy(audio_data)
            
            hr = self.dll.WriteAudio(data_array, data_size)
            return self._check_hresult(hr, "WriteAudio", silent=True)
            
        except Exception as e:
            print(f"❌ Error writing audio data: {e}")
            return False
    
    def write_numpy_audio(self, audio_array: np.ndarray) -> bool:
        """Write numpy audio array to the virtual device"""
        if not self.is_started:
            return False
        
        # Convert numpy array to bytes
        if audio_array.dtype != np.int16:
            # Convert to 16-bit if necessary
            if audio_array.dtype == np.float32 or audio_array.dtype == np.float64:
                audio_array = (audio_array * 32767).astype(np.int16)
            else:
                audio_array = audio_array.astype(np.int16)
        
        audio_bytes = audio_array.tobytes()
        return self.write_audio(audio_bytes)
    
    def is_ready(self) -> bool:
        """Check if the virtual device is ready"""
        if not self.dll:
            return False
        
        try:
            return bool(self.dll.IsDeviceReady())
        except:
            return False
    
    def cleanup(self):
        """Cleanup and destroy the virtual device"""
        try:
            if self.is_started:
                self.stop()
            
            if self.is_initialized and self.dll:
                print("🧹 Destroying virtual audio device...")
                hr = self.dll.DestroyDevice()
                self._check_hresult(hr, "DestroyDevice")
                
            self.is_initialized = False
            self.dll = None
            print("✅ Driver cleanup complete")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def _check_hresult(self, hr: int, function_name: str, silent: bool = False) -> bool:
        """Check Windows HRESULT and return success/failure"""
        success = (hr >= 0)  # SUCCEEDED(hr)
        
        if not silent:
            if success:
                print(f"✅ {function_name} succeeded (HRESULT: 0x{hr:08X})")
            else:
                print(f"❌ {function_name} failed (HRESULT: 0x{hr:08X})")
                self._print_hresult_error(hr)
        
        return success
    
    def _print_hresult_error(self, hr: int):
        """Print human-readable error for HRESULT"""
        common_errors = {
            0x80070005: "E_ACCESSDENIED - Access denied",
            0x8007000E: "E_OUTOFMEMORY - Out of memory", 
            0x80070057: "E_INVALIDARG - Invalid argument",
            0x80004001: "E_NOTIMPL - Not implemented",
            0x80004005: "E_FAIL - Unspecified failure",
            0x80070006: "E_HANDLE - Invalid handle",
            0x88890004: "AUDCLNT_E_NOT_INITIALIZED - Audio client not initialized",
            0x88890003: "AUDCLNT_E_ALREADY_INITIALIZED - Audio client already initialized",
        }
        
        error_msg = common_errors.get(hr & 0xFFFFFFFF, f"Unknown error (0x{hr:08X})")
        print(f"   Error details: {error_msg}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

# Example usage and testing
if __name__ == "__main__":
    print("🎤 Testing Wireless Microphone Virtual Driver")
    print("=" * 50)
    
    with DriverInterface() as driver:
        # Load driver
        if not driver.load_driver():
            sys.exit(1)
        
        # Initialize
        if not driver.initialize():
            sys.exit(1)
        
        # Start
        if not driver.start():
            sys.exit(1)
        
        print("\n🎯 Virtual microphone device should now be available!")
        print("📋 Check Windows Sound Control Panel → Recording devices")
        print("🎤 The device should appear as an audio input")
        
        # Keep running for testing
        try:
            input("\nPress Enter to stop the virtual device...")
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        
        print("🧹 Cleaning up...")
    
    print("✅ Test complete!")
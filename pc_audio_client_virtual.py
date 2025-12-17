#!/usr/bin/env python3
"""
PC Audio Client with Virtual Driver Integration
Uses the custom virtual audio driver for ultra-low latency audio routing
No more Stereo Mix needed - appears as real microphone in Windows!
"""

import socket
import threading
import sys
import argparse
import numpy as np
import time
from typing import Optional

# Import our virtual driver interface
sys.path.append('wireless_mic_driver/python')
try:
    from driver_interface import DriverInterface
except ImportError:
    print("❌ Could not import driver_interface. Make sure the driver is built.")
    print("   Run: cd wireless_mic_driver && build.bat")
    sys.exit(1)

class VirtualMicrophoneClient:
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.is_streaming = False
        
        # Virtual driver interface
        self.driver = None
        
        # Audio configuration (must match Android app)
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
        
        # Network configuration
        self.buffer_size = 1024 * 2  # Smaller for lower latency

    def initialize_driver(self) -> bool:
        """Initialize the virtual audio driver"""
        try:
            print("🔧 Initializing virtual audio driver...")
            self.driver = DriverInterface()
            
            # Load and initialize the driver
            if not self.driver.load_driver():
                return False
            
            if not self.driver.initialize():
                return False
            
            if not self.driver.start():
                return False
            
            print("✅ Virtual microphone driver ready!")
            print("🎤 Check Windows Sound Settings → Input devices")
            print("📋 The virtual microphone should now be available!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing driver: {e}")
            return False

    def connect(self, host: str, port: int) -> bool:
        """Connect to phone's audio server"""
        try:
            print(f"📱 Connecting to {host}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # Connection timeout
            self.socket.connect((host, port))
            
            # Configure socket for audio streaming
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16384)  # Small buffer for low latency
            self.socket.settimeout(0.1)  # Short timeout for audio data
            
            self.is_connected = True
            print("✅ Connected to phone successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def start_streaming(self):
        """Start audio streaming from phone to virtual microphone"""
        if not self.is_connected:
            print("❌ Not connected to phone")
            return
        
        if not self.driver or not self.driver.is_ready():
            print("❌ Virtual driver not ready")
            return

        print("🎵 Starting audio streaming...")
        print("🎤 Phone audio will now appear as microphone input in Windows!")
        print("📢 Apps can select this as their microphone input device")
        print("🛑 Press Ctrl+C to stop")

        self.is_streaming = True
        
        try:
            while self.is_connected and self.is_streaming:
                # Receive audio data from phone
                try:
                    data = self.socket.recv(self.buffer_size)
                    if not data:
                        print("📱 Phone disconnected")
                        break
                    
                    # Write directly to virtual microphone driver
                    success = self.driver.write_audio(data)
                    if not success:
                        print("⚠️ Failed to write to virtual device")
                        
                except socket.timeout:
                    # Timeout is normal, continue
                    continue
                except ConnectionResetError:
                    print("📱 Phone connection lost")
                    break
                except Exception as e:
                    print(f"📡 Network error: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        finally:
            self.stop()

    def stop(self):
        """Stop streaming and cleanup"""
        print("🧹 Cleaning up...")
        
        self.is_connected = False
        self.is_streaming = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        if self.driver:
            self.driver.cleanup()
            self.driver = None
        
        print("✅ Cleanup complete")

    def test_driver_only(self):
        """Test the virtual driver without phone connection"""
        print("🧪 Testing virtual driver (no phone connection)...")
        
        if not self.initialize_driver():
            return False
        
        print("✅ Virtual microphone driver is working!")
        print("🎤 Check Windows Sound Control Panel → Recording devices")
        print("📋 You should see the virtual microphone device")
        print("\n🎯 To test with apps:")
        print("  1. Open Discord/Teams/OBS/etc.")
        print("  2. Go to audio settings")
        print("  3. Select the virtual microphone as input")
        print("  4. Connect your phone to stream audio")
        
        try:
            input("\nPress Enter to stop the test...")
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        
        return True

def show_usage():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("🎤 VIRTUAL MICROPHONE CLIENT")
    print("="*60)
    print("\n🚀 QUICK START:")
    print("1. Build the driver:")
    print("   cd wireless_mic_driver")
    print("   build.bat")
    print("\n2. Test driver only:")
    print("   python pc_audio_client_virtual.py --test-driver")
    print("\n3. Connect to phone:")
    print("   python pc_audio_client_virtual.py <PHONE_IP>")
    print("   Example: python pc_audio_client_virtual.py 192.168.1.100")
    print("\n🎯 WHAT THIS DOES:")
    print("- Creates a REAL virtual microphone in Windows")
    print("- No Stereo Mix needed!")
    print("- Ultra-low latency (~50-100ms total)")
    print("- Works with ANY Windows application")
    print("\n📋 APPS CAN USE IT AS:")
    print("- Discord: Input Device")
    print("- OBS: Audio Input Capture") 
    print("- Teams/Zoom: Microphone")
    print("- Any app: Select as microphone input")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Virtual Microphone Client with Custom Driver')
    parser.add_argument('host', nargs='?', help='Phone IP address')
    parser.add_argument('--port', '-p', type=int, default=8888, help='Port number')
    parser.add_argument('--test-driver', '-t', action='store_true', help='Test virtual driver only')
    parser.add_argument('--help-usage', action='store_true', help='Show detailed usage guide')
    
    args = parser.parse_args()
    
    if args.help_usage:
        show_usage()
        return 0
    
    client = VirtualMicrophoneClient()
    
    try:
        if args.test_driver:
            # Test driver without phone connection
            success = client.test_driver_only()
            return 0 if success else 1
        
        if not args.host:
            print("❌ Please provide phone IP address")
            print("Usage: python pc_audio_client_virtual.py <PHONE_IP>")
            print("Or test driver: python pc_audio_client_virtual.py --test-driver")
            print("For help: python pc_audio_client_virtual.py --help-usage")
            return 1
        
        # Initialize virtual driver
        if not client.initialize_driver():
            print("\n💡 TIP: Make sure to build the driver first:")
            print("   cd wireless_mic_driver")
            print("   build.bat")
            return 1
        
        # Connect to phone
        if not client.connect(args.host, args.port):
            return 1
        
        # Start streaming
        client.start_streaming()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        client.stop()

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
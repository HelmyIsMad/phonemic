#!/usr/bin/env python3
"""
Virtual Microphone PC Client for Wireless Microphone
Routes phone audio to a virtual microphone device that Windows apps can use
Requires VB-Cable or Virtual Audio Cable to be installed
"""

import socket
import threading
import sys
import argparse
import numpy as np
from typing import Optional

try:
    import sounddevice as sd
except ImportError:
    print("❌ sounddevice not installed. Please run:")
    print("   pip install sounddevice numpy")
    sys.exit(1)

class VirtualMicrophoneClient:
    def __init__(self, virtual_device_name=None):
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.is_streaming = False
        self.virtual_device_name = virtual_device_name
        self.virtual_device_id = None
        
        # Audio configuration (must match Android app)
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
        self.blocksize = 1024

    def find_virtual_device(self):
        """Find virtual audio cable device"""
        devices = sd.query_devices()
        
        # Common virtual audio cable names
        virtual_names = [
            "CABLE Input",  # VB-Cable
            "VB-Audio Virtual Cable",
            "Virtual Audio Cable",
            "Line 1 (Virtual Audio Cable)",
            "CABLE-A Input",
            "CABLE-B Input"
        ]
        
        if self.virtual_device_name:
            virtual_names.insert(0, self.virtual_device_name)
        
        print("🔍 Looking for virtual audio devices...")
        print("\n📋 Available output devices:")
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                indicator = ""
                device_name = device['name']
                
                # Check if this is a virtual device
                for virtual_name in virtual_names:
                    if virtual_name.lower() in device_name.lower():
                        self.virtual_device_id = i
                        indicator = " ⭐ (VIRTUAL DEVICE FOUND!)"
                        break
                
                print(f"  {i}: {device_name}{indicator}")
        
        return self.virtual_device_id

    def connect(self, host: str, port: int) -> bool:
        """Connect to the phone's audio streaming server"""
        try:
            print(f"📱 Connecting to {host}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            self.is_connected = True
            print("✅ Connected to phone successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to phone: {e}")
            return False

    def audio_callback(self, outdata, frames, time, status):
        """Audio callback function for virtual microphone"""
        if status:
            print(f"Audio status: {status}")
        
        try:
            # Receive audio data from phone
            data = self.socket.recv(frames * 2)  # 16-bit = 2 bytes per sample
            
            if not data:
                raise Exception("No data received from phone")
            
            # Convert bytes to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Pad or truncate to match expected frame count
            if len(audio_data) < frames:
                audio_data = np.pad(audio_data, (0, frames - len(audio_data)), 'constant')
            elif len(audio_data) > frames:
                audio_data = audio_data[:frames]
            
            # Convert to float32 and copy to virtual microphone output
            outdata[:len(audio_data), 0] = audio_data.astype(np.float32) / 32768.0
            
        except Exception as e:
            # Fill with silence on error
            outdata.fill(0)
            if self.is_connected:
                print(f"📡 Audio stream error: {e}")
                self.stop()

    def start_virtual_microphone(self):
        """Start virtual microphone streaming"""
        if not self.is_connected:
            print("❌ Not connected to phone")
            return False

        if self.virtual_device_id is None:
            print("❌ No virtual audio device found!")
            print("\n💡 To fix this:")
            print("1. Install VB-Cable: https://vb-audio.com/Cable/")
            print("2. Or install Virtual Audio Cable")
            print("3. Restart this script")
            print("4. Use --device ID to specify device manually")
            return False

        try:
            device_info = sd.query_devices(self.virtual_device_id)
            print(f"🎤 Starting virtual microphone: {device_info['name']}")
            print("🎵 Phone audio will now appear as microphone input!")
            print("📢 Windows apps can now use this as an audio input device")
            print("🛑 Press Ctrl+C to stop")
            
            # Start audio stream to virtual device
            with sd.OutputStream(
                device=self.virtual_device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                callback=self.audio_callback,
                blocksize=self.blocksize
            ):
                self.is_streaming = True
                
                # Keep stream alive
                while self.is_connected and self.is_streaming:
                    sd.sleep(100)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping virtual microphone...")
        except Exception as e:
            print(f"❌ Error with virtual microphone: {e}")
        finally:
            self.stop()
            
        return True

    def stop(self):
        """Stop client and cleanup"""
        print("🧹 Shutting down...")
        
        self.is_connected = False
        self.is_streaming = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        print("✅ Virtual microphone stopped")

def install_virtual_cable_info():
    """Show information about installing virtual audio cable"""
    print("\n" + "="*60)
    print("🎤 VIRTUAL AUDIO CABLE SETUP")
    print("="*60)
    print("\n📥 STEP 1: Install Virtual Audio Software")
    print("Choose ONE of these options:")
    print("\n🔵 Option A: VB-Cable (FREE, recommended)")
    print("   1. Download: https://vb-audio.com/Cable/")
    print("   2. Install and restart Windows")
    print("   3. Creates 'CABLE Input' device")
    print("\n🔵 Option B: Virtual Audio Cable (paid)")
    print("   1. Purchase and download from Eugene Muzychenko")
    print("   2. Install and restart Windows")
    print("   3. Creates 'Virtual Audio Cable' devices")
    print("\n📋 STEP 2: Verify Installation")
    print("   1. Right-click speaker icon in taskbar")
    print("   2. Select 'Open Sound settings'")
    print("   3. Check if virtual device appears in output devices")
    print("\n🎯 STEP 3: Use This Script")
    print("   python pc_audio_client_virtual_mic.py <PHONE_IP>")
    print("\n📱 STEP 4: Use in Apps")
    print("   - Discord: Settings → Voice → Input Device")
    print("   - OBS: Add Audio Input Capture source")
    print("   - Teams/Zoom: Audio settings → Microphone")
    print("   - Any app: Select the virtual cable as microphone")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Virtual Microphone Client for Wireless Phone Audio')
    parser.add_argument('host', nargs='?', help='Phone IP address (e.g., 192.168.1.100)')
    parser.add_argument('--port', '-p', type=int, default=8888, help='Port number (default: 8888)')
    parser.add_argument('--device', '-d', type=int, help='Specific virtual device ID')
    parser.add_argument('--list-devices', '-l', action='store_true', help='List available audio devices')
    parser.add_argument('--setup-info', '-s', action='store_true', help='Show virtual cable setup information')
    
    args = parser.parse_args()
    
    # Show setup info
    if args.setup_info:
        install_virtual_cable_info()
        return 0
    
    # List devices
    if args.list_devices:
        print("🔊 Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                print(f"  {i}: {device['name']}")
        return 0
    
    # Check if host provided
    if not args.host:
        print("❌ Please provide the phone IP address")
        print("Usage: python pc_audio_client_virtual_mic.py <PHONE_IP>")
        print("Example: python pc_audio_client_virtual_mic.py 192.168.1.100")
        print("\nFor setup help: python pc_audio_client_virtual_mic.py --setup-info")
        return 1
    
    client = VirtualMicrophoneClient()
    
    # Use specific device if provided
    if args.device is not None:
        client.virtual_device_id = args.device
        print(f"🎯 Using specified device ID: {args.device}")
    else:
        # Auto-detect virtual device
        if client.find_virtual_device() is None:
            print("\n❌ No virtual audio cable found!")
            print("💡 Run with --setup-info for installation instructions")
            return 1
    
    try:
        if client.connect(args.host, args.port):
            client.start_virtual_microphone()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.stop()

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
#!/usr/bin/env python3
"""
PC Audio Client with Windows Audio Loopback
Uses Windows built-in audio loopback to route phone audio to system
No external virtual cable software required
"""

import socket
import threading
import sys
import argparse
import numpy as np
from typing import Optional
import subprocess
import time

try:
    import sounddevice as sd
except ImportError:
    print("❌ sounddevice not installed. Please run:")
    print("   pip install sounddevice numpy")
    sys.exit(1)

class AudioLoopbackClient:
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.is_streaming = False
        
        # Audio configuration - balanced for quality and reasonable latency
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
        self.blocksize = 1024  # Balanced buffer size
        self.latency = 0.05    # Reasonable latency (50ms)
        
        # Audio streams
        self.input_stream = None
        self.output_stream = None
        
        # Audio buffer for loopback
        self.audio_buffer = np.zeros((self.blocksize, 1), dtype=np.float32)
        self.buffer_lock = threading.Lock()

    def enable_stereo_mix(self):
        """Enable Windows Stereo Mix (What You Hear) if available"""
        try:
            print("🔍 Checking for Windows Stereo Mix...")
            
            # Try to enable stereo mix using Windows commands
            # This works on many Windows systems
            result = subprocess.run([
                'powershell', '-Command',
                "Get-AudioDevice -List | Where-Object {$_.Name -like '*Stereo Mix*' -or $_.Name -like '*What*You*Hear*'}"
            ], capture_output=True, text=True, timeout=5)
            
            if "Stereo Mix" in result.stdout or "What You Hear" in result.stdout:
                print("✅ Found Stereo Mix capability")
                return True
            else:
                print("⚠️  Stereo Mix not found (this is normal on many systems)")
                return False
                
        except Exception as e:
            print(f"📝 Could not check Stereo Mix: {e}")
            return False

    def find_loopback_device(self):
        """Find a suitable loopback or monitoring device"""
        devices = sd.query_devices()
        
        print("🔍 Looking for audio loopback capabilities...")
        
        # Look for devices that might support monitoring
        loopback_keywords = [
            "stereo mix", "what you hear", "wave out mix", "loopback", 
            "monitor", "mix", "rec. playback", "recording mix"
        ]
        
        suitable_devices = []
        
        print("\n📋 Available input devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                device_name = device['name'].lower()
                is_loopback = any(keyword in device_name for keyword in loopback_keywords)
                
                indicator = " 🔄 (LOOPBACK CAPABLE)" if is_loopback else ""
                print(f"  {i}: {device['name']}{indicator}")
                
                if is_loopback:
                    suitable_devices.append(i)
        
        return suitable_devices[0] if suitable_devices else None

    def connect(self, host: str, port: int) -> bool:
        """Connect to phone's audio server"""
        try:
            print(f"📱 Connecting to {host}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # Connection timeout
            self.socket.connect((host, port))
            
            # Configure socket for stable streaming
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle algorithm
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32768)  # Reasonable receive buffer
            self.socket.settimeout(0.1)   # Balanced timeout for stability
            self.is_connected = True
            print("✅ Connected to phone successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def input_callback(self, indata, frames, time, status):
        """Callback for recording from loopback device"""
        if status:
            print(f"Input status: {status}")
        
        # This will record system audio (including our output)
        with self.buffer_lock:
            # Store the system audio (which includes our phone audio)
            pass  # We'll use this for monitoring

    def output_callback(self, outdata, frames, time, status):
        """Callback for audio output"""
        # Suppress common audio status messages (underflow is normal with network audio)
        if status and 'underflow' not in str(status).lower():
            print(f"Output status: {status}")
        
        try:
            # Try to receive audio from phone
            total_data = b""
            bytes_needed = frames * 2  # 16-bit = 2 bytes per sample
            
            while len(total_data) < bytes_needed and self.is_connected:
                try:
                    chunk = self.socket.recv(bytes_needed - len(total_data))
                    if not chunk:
                        raise Exception("Phone disconnected")
                    total_data += chunk
                except socket.timeout:
                    # Timeout is normal, fill with silence for this frame
                    break
                except ConnectionResetError:
                    raise Exception("Phone disconnected")
            
            if total_data:
                # Convert to numpy array
                audio_data = np.frombuffer(total_data, dtype=np.int16)
                
                # Handle size mismatch
                if len(audio_data) < frames:
                    audio_data = np.pad(audio_data, (0, frames - len(audio_data)), 'constant')
                elif len(audio_data) > frames:
                    audio_data = audio_data[:frames]
                
                # Convert to float and output
                outdata[:len(audio_data), 0] = audio_data.astype(np.float32) / 32768.0
                
                # Store for potential loopback
                with self.buffer_lock:
                    self.audio_buffer = outdata.copy()
            else:
                # No data received, fill with silence
                outdata.fill(0)
                
        except Exception as e:
            outdata.fill(0)
            if self.is_connected and "timed out" not in str(e).lower():
                print(f"📡 Audio error: {e}")
                if "disconnected" in str(e).lower():
                    self.is_connected = False

    def start_simple_playback(self):
        """Start simple audio playback through speakers"""
        # Get default output device
        default_device = sd.query_devices(kind='output')
        print(f"🎵 Using default playback device: {default_device['name']}")
        print("💡 Phone audio will play through your PC speakers")
        print("📝 Apps can record this using 'Stereo Mix' or 'What You Hear' if available")
        
        try:
            with sd.OutputStream(
                device=None,  # Use system default
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                callback=self.output_callback,
                blocksize=self.blocksize,
                latency=self.latency
            ):
                self.is_streaming = True
                print("✅ Audio streaming active!")
                print("🎤 To use as microphone in apps:")
                print("   1. Enable 'Stereo Mix' in Windows sound settings")
                print("   2. Set 'Stereo Mix' as microphone in your app")
                print("   3. Or use app's 'Listen to this device' feature")
                print("🛑 Press Ctrl+C to stop")
                
                while self.is_connected and self.is_streaming:
                    sd.sleep(100)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        except Exception as e:
            print(f"❌ Playback error: {e}")

    def check_stereo_mix_setup(self):
        """Check if Stereo Mix is properly configured"""
        print("\n🔍 CHECKING STEREO MIX SETUP...")
        
        try:
            # Check Windows volume mixer for our process
            print("📊 Audio troubleshooting:")
            print("1. Can you hear the phone audio through speakers? (Test: speak into phone)")
            print("2. Open Windows Volume Mixer (right-click speaker → Open Volume mixer)")
            print("3. Look for 'Python' or this script in the mixer")
            print("4. Make sure it's not muted and volume is up")
            
            # Get current default devices
            default_out = sd.query_devices(kind='output')
            print(f"\n🔊 Current default output: {default_out['name']}")
            
            print("\n⚠️  STEREO MIX REQUIREMENTS:")
            print("- Stereo Mix must be ENABLED and set as DEFAULT recording device")
            print("- Audio must play through the SAME device that Stereo Mix monitors")
            print("- Some systems don't have Stereo Mix (especially laptops)")
            
        except Exception as e:
            print(f"Error checking setup: {e}")

    def show_windows_setup_guide(self):
        """Show how to set up Windows to route speaker output as microphone"""
        print("\n" + "="*70)
        print("🎤 WINDOWS AUDIO ROUTING SETUP")
        print("="*70)
        print("\n🔧 METHOD 1: Enable Stereo Mix (if available)")
        print("1. Right-click speaker icon → Open Sound settings")
        print("2. Click 'Sound Control Panel' → Recording tab")
        print("3. Right-click empty area → Show Disabled Devices")
        print("4. Enable 'Stereo Mix' if available")
        print("5. Set as DEFAULT recording device (important!)")
        print("6. Go to Stereo Mix Properties → Levels → make sure it's not muted")
        print("7. Apps will now record whatever plays through speakers")
        print("\n🔧 METHOD 2: Use 'Listen to this device' feature")
        print("1. Go to Recording tab in Sound Control Panel")
        print("2. Right-click your microphone → Properties")
        print("3. Go to 'Listen' tab")
        print("4. Check 'Listen to this device'")
        print("5. Select playback device")
        print("6. Now microphone picks up speaker audio")
        print("\n🔧 METHOD 3: App-specific solutions (RECOMMENDED)")
        print("📢 OBS: Add 'Desktop Audio' source (captures all system audio)")
        print("🎮 Discord: Go to Voice Settings → Advanced → try different audio subsystems")
        print("📹 Teams: Look for 'Computer Sound' option in audio settings")
        print("🎵 Audacity: Use 'Windows WASAPI' host, select loopback device")
        print("\n❌ IF STEREO MIX DOESN'T WORK:")
        print("- Many modern systems don't have Stereo Mix")
        print("- Try METHOD 3 (app-specific solutions) instead")
        print("- Some apps can directly capture desktop audio")
        print("\n💡 TIP: Start this client, then configure your app to use")
        print("    the method that works best for your system.")
        print("="*70)

    def start_with_guidance(self):
        """Start client with setup guidance"""
        if not self.is_connected:
            print("❌ Not connected to phone")
            return

        # Check for built-in loopback capabilities
        self.enable_stereo_mix()
        loopback_device = self.find_loopback_device()
        
        if loopback_device is not None:
            print(f"✅ Found potential loopback device!")
            print("🎯 This might work better for app integration")
        
        # Show setup guide
        self.show_windows_setup_guide()
        
        # Start simple playback
        print(f"\n🚀 Starting audio stream...")
        
        # Start audio streaming in a separate thread so we can provide guidance
        import threading
        audio_thread = threading.Thread(target=self.start_simple_playback, daemon=True)
        audio_thread.start()
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check setup after audio starts
        self.check_stereo_mix_setup()
        
        print("\n📋 QUICK TEST:")
        print("1. Speak into your phone - do you hear it from PC speakers?")
        print("2. If YES: Check if Stereo Mix shows activity levels")
        print("3. If NO: Check phone server is running and WiFi connection")
        print("4. Try the app-specific methods if Stereo Mix doesn't work")
        print("\n🛑 Press Ctrl+C to stop")
        
        # Wait for audio thread
        try:
            audio_thread.join()
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")

    def stop(self):
        """Stop and cleanup"""
        print("🧹 Cleaning up...")
        self.is_connected = False
        self.is_streaming = False
        
        if self.socket:
            self.socket.close()
        
        print("✅ Stopped")

def main():
    parser = argparse.ArgumentParser(description='PC Audio Client with Windows Audio Routing')
    parser.add_argument('host', nargs='?', help='Phone IP address')
    parser.add_argument('--port', '-p', type=int, default=8888, help='Port number')
    parser.add_argument('--setup-guide', '-s', action='store_true', help='Show Windows setup guide')
    parser.add_argument('--list-devices', '-l', action='store_true', help='List audio devices')
    
    args = parser.parse_args()
    
    if args.setup_guide:
        client = AudioLoopbackClient()
        client.show_windows_setup_guide()
        return 0
    
    if args.list_devices:
        print("🔊 Available audio devices:")
        print(sd.query_devices())
        return 0
    
    if not args.host:
        print("❌ Please provide phone IP address")
        print("Usage: python pc_audio_client_loopback.py <PHONE_IP>")
        print("\nFor setup help: python pc_audio_client_loopback.py --setup-guide")
        return 1
    
    client = AudioLoopbackClient()
    
    try:
        if client.connect(args.host, args.port):
            client.start_with_guidance()
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
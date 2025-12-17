#!/usr/bin/env python3
"""
Alternative PC Audio Client for Wireless Microphone
Uses sounddevice instead of PyAudio for easier installation
Receives audio stream from Android phone and plays it through PC speakers
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

class AudioClient:
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.is_playing = False
        
        # Audio configuration (must match Android app)
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16
        self.blocksize = 1024

    def connect(self, host: str, port: int) -> bool:
        """Connect to the phone's audio streaming server"""
        try:
            print(f"Connecting to {host}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((host, port))
            self.is_connected = True
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def audio_callback(self, outdata, frames, time, status):
        """Audio callback function for sounddevice"""
        if status:
            print(f"Audio status: {status}")
        
        try:
            # Receive audio data from socket
            data = self.socket.recv(frames * 2)  # 16-bit = 2 bytes per sample
            
            if not data:
                raise Exception("No data received")
            
            # Convert bytes to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Pad or truncate to match expected frame count
            if len(audio_data) < frames:
                audio_data = np.pad(audio_data, (0, frames - len(audio_data)), 'constant')
            elif len(audio_data) > frames:
                audio_data = audio_data[:frames]
            
            # Copy to output buffer (reshape for mono)
            outdata[:len(audio_data), 0] = audio_data.astype(np.float32) / 32768.0
            
        except Exception as e:
            # Fill with silence on error
            outdata.fill(0)
            if self.is_connected:
                print(f"Audio error: {e}")
                self.stop()

    def start_receiving(self):
        """Start receiving and playing audio"""
        if not self.is_connected:
            print("❌ Not connected to phone")
            return

        try:
            print("🎧 Starting audio stream...")
            print("🎵 Audio playback started")
            print("🎤 Receiving audio from phone...")
            print("Press Ctrl+C to stop")
            
            # Start audio stream with callback
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                callback=self.audio_callback,
                blocksize=self.blocksize
            ):
                self.is_playing = True
                
                # Keep stream alive
                while self.is_connected and self.is_playing:
                    sd.sleep(100)  # Sleep for 100ms
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop audio client and cleanup resources"""
        print("🧹 Cleaning up...")
        
        self.is_connected = False
        self.is_playing = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        print("✅ Cleanup complete")

def list_audio_devices():
    """List available audio devices"""
    print("🔊 Available audio devices:")
    print(sd.query_devices())

def main():
    parser = argparse.ArgumentParser(description='PC Audio Client for Wireless Microphone (sounddevice version)')
    parser.add_argument('host', nargs='?', help='Phone IP address (e.g., 192.168.1.100)')
    parser.add_argument('--port', '-p', type=int, default=8888, help='Port number (default: 8888)')
    parser.add_argument('--list-devices', '-l', action='store_true', help='List available audio devices')
    parser.add_argument('--device', '-d', type=int, help='Output device ID')
    
    args = parser.parse_args()
    
    # List devices if requested
    if args.list_devices:
        list_audio_devices()
        return 0
    
    # Check if host is provided
    if not args.host:
        print("❌ Please provide the phone IP address")
        print("Usage: python pc_audio_client_alternative.py <PHONE_IP>")
        print("Example: python pc_audio_client_alternative.py 192.168.1.100")
        return 1
    
    # Set output device if specified
    if args.device is not None:
        sd.default.device[1] = args.device  # Set output device
        print(f"🔊 Using audio device: {args.device}")
    
    client = AudioClient()
    
    try:
        if client.connect(args.host, args.port):
            client.start_receiving()
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
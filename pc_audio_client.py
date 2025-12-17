#!/usr/bin/env python3
"""
PC Audio Client for Wireless Microphone
Receives audio stream from Android phone and plays it through PC speakers
"""

import socket
import pyaudio
import threading
import sys
import argparse
from typing import Optional

class AudioClient:
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.is_connected = False
        self.is_playing = False
        
        # Audio configuration (must match Android app)
        self.sample_rate = 44100
        self.channels = 1
        self.format = pyaudio.paInt16
        self.chunk_size = 1024

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

    def start_audio_playback(self):
        """Initialize audio playback stream"""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            self.is_playing = True
            print("🎵 Audio playback started")
        except Exception as e:
            print(f"❌ Failed to start audio playback: {e}")
            raise

    def audio_receiver_thread(self):
        """Thread function to receive and play audio data"""
        if not self.socket or not self.stream:
            return

        print("🎧 Listening for audio data...")
        
        try:
            while self.is_connected and self.is_playing:
                # Receive audio data
                data = self.socket.recv(self.chunk_size * 2)  # 16-bit = 2 bytes per sample
                
                if not data:
                    print("📡 No more data received")
                    break
                
                # Play audio data
                self.stream.write(data)
                
        except socket.timeout:
            print("⏰ Connection timeout")
        except ConnectionResetError:
            print("📱 Phone disconnected")
        except Exception as e:
            print(f"❌ Error receiving audio: {e}")
        finally:
            self.stop()

    def start_receiving(self):
        """Start receiving audio in a separate thread"""
        if not self.is_connected:
            print("❌ Not connected to phone")
            return

        try:
            self.start_audio_playback()
            
            # Start audio receiving thread
            receiver_thread = threading.Thread(target=self.audio_receiver_thread, daemon=True)
            receiver_thread.start()
            
            print("🎤 Receiving audio from phone...")
            print("Press Ctrl+C to stop")
            
            # Keep main thread alive
            receiver_thread.join()
            
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
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        self.audio.terminate()
        print("✅ Cleanup complete")

def main():
    parser = argparse.ArgumentParser(description='PC Audio Client for Wireless Microphone')
    parser.add_argument('host', help='Phone IP address (e.g., 192.168.1.100)')
    parser.add_argument('--port', '-p', type=int, default=8888, help='Port number (default: 8888)')
    
    args = parser.parse_args()
    
    client = AudioClient()
    
    try:
        if client.connect(args.host, args.port):
            client.start_receiving()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
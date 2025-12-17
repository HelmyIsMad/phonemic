#!/usr/bin/env python3
"""
Setup script for PC Audio Client
Installs required dependencies and tests audio system
"""

import subprocess
import sys
import platform

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def test_audio_system():
    """Test if audio system is working"""
    print("🔊 Testing audio system...")
    try:
        import pyaudio
        
        # Test audio initialization
        audio = pyaudio.PyAudio()
        
        # Get default output device
        default_output = audio.get_default_output_device_info()
        print(f"🎵 Default audio output: {default_output['name']}")
        
        # Test if we can open an audio stream
        test_stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            output=True,
            frames_per_buffer=1024
        )
        test_stream.close()
        audio.terminate()
        
        print("✅ Audio system test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        print("💡 Make sure you have audio drivers installed")
        return False

def show_usage():
    """Show usage instructions"""
    print("\n" + "="*50)
    print("🎤 WIRELESS MICROPHONE - PC CLIENT SETUP COMPLETE")
    print("="*50)
    print("\n📱 PHONE SETUP:")
    print("1. Install and run the Flutter app on your phone")
    print("2. Grant microphone permission")
    print("3. Note the IP address shown in the app (e.g., 192.168.1.100:8888)")
    print("4. Press 'Start Server' on your phone")
    print("\n💻 PC USAGE:")
    print("python pc_audio_client.py <PHONE_IP>")
    print("Example: python pc_audio_client.py 192.168.1.100")
    print("\n🔧 OPTIONS:")
    print("--port, -p    Specify port number (default: 8888)")
    print("\n💡 TIPS:")
    print("- Make sure phone and PC are on the same WiFi network")
    print("- Check firewall settings if connection fails")
    print("- Use Ctrl+C to stop the audio streaming")
    print("="*50)

def main():
    print("🚀 Setting up PC Audio Client...")
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Test audio system
    if not test_audio_system():
        print("⚠️  Audio test failed, but you can still try running the client")
    
    # Show usage instructions
    show_usage()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
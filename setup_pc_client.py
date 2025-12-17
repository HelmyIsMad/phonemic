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
    
    # First try PyAudio
    print("🎵 Trying to install PyAudio...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio==0.2.11"], 
                             capture_output=True)
        print("✅ PyAudio installed successfully!")
        return "pyaudio"
    except subprocess.CalledProcessError:
        print("⚠️  PyAudio installation failed (this is common on Windows)")
    
    # Fall back to sounddevice
    print("🔄 Trying alternative: sounddevice + numpy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sounddevice", "numpy"])
        print("✅ sounddevice installed successfully!")
        return "sounddevice"
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install alternative packages: {e}")
        return None

def test_audio_system(audio_lib):
    """Test if audio system is working"""
    print("🔊 Testing audio system...")
    
    if audio_lib == "pyaudio":
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
            
            print("✅ PyAudio system test passed!")
            return True
            
        except Exception as e:
            print(f"❌ PyAudio test failed: {e}")
            return False
    
    elif audio_lib == "sounddevice":
        try:
            import sounddevice as sd
            import numpy as np
            
            # Get default output device
            default_output = sd.query_devices(kind='output')
            print(f"🎵 Default audio output: {default_output['name']}")
            
            # Test basic functionality
            devices = sd.query_devices()
            print(f"🔊 Found {len(devices)} audio devices")
            
            print("✅ sounddevice system test passed!")
            return True
            
        except Exception as e:
            print(f"❌ sounddevice test failed: {e}")
            return False
    
    else:
        print("❌ No audio library installed")
        return False

def show_usage(audio_lib):
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
    
    if audio_lib == "pyaudio":
        print("✅ Using PyAudio version:")
        print("python pc_audio_client.py <PHONE_IP>")
        print("Example: python pc_audio_client.py 192.168.1.100")
    elif audio_lib == "sounddevice":
        print("✅ Using sounddevice version (recommended for Windows):")
        print("python pc_audio_client_alternative.py <PHONE_IP>")
        print("Example: python pc_audio_client_alternative.py 192.168.1.100")
        print("\n📊 Additional options for sounddevice version:")
        print("--list-devices, -l    List available audio devices")
        print("--device, -d ID       Use specific audio device")
    else:
        print("⚠️  Manual installation required:")
        print("pip install pyaudio  OR  pip install sounddevice numpy")
        print("Then use the appropriate client script")
    
    print("\n🔧 COMMON OPTIONS:")
    print("--port, -p    Specify port number (default: 8888)")
    print("\n💡 TIPS:")
    print("- Make sure phone and PC are on the same WiFi network")
    print("- Check firewall settings if connection fails")
    print("- Use Ctrl+C to stop the audio streaming")
    print("- If you have audio issues, try the alternative client")
    print("="*50)

def main():
    print("🚀 Setting up PC Audio Client...")
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Install requirements
    audio_lib = install_requirements()
    if not audio_lib:
        print("\n❌ Failed to install audio libraries")
        print("💡 Try manual installation:")
        print("   For Windows: pip install sounddevice numpy")
        print("   For Linux/Mac: pip install pyaudio")
        show_usage(None)
        return 1
    
    print(f"📚 Using audio library: {audio_lib}")
    
    # Test audio system
    if not test_audio_system(audio_lib):
        print("⚠️  Audio test failed, but you can still try running the client")
    
    # Show usage instructions
    show_usage(audio_lib)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
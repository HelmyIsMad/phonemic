# 🎤 Wireless Microphone System

A complete wireless microphone solution that turns your phone into a high-quality wireless microphone for your PC using WiFi networking.

## 🌟 Features

- **Real-time audio streaming** from phone microphone to PC
- **Cross-platform Flutter app** for Android devices
- **Multiple PC client options** for different operating systems
- **Windows built-in audio routing** - no external software required
- **Low-latency networking** optimized for audio streaming
- **Professional audio quality** with 44.1kHz sample rate

## 🏗️ System Architecture

```
📱 Phone (Flutter App) → 📡 WiFi Network → 💻 PC (Python Client) → 🎧 Audio Output
```

The system consists of two main components:
1. **Flutter mobile app** that captures microphone audio and streams it over TCP
2. **Python PC client** that receives the audio stream and routes it to Windows audio system

## 📁 Project Structure

```
├── mic_loopback_app/              # Flutter Android app
│   ├── lib/main.dart             # UI and networking logic
│   └── android/                  # Native Android audio implementation
├── pc_audio_client_loopback.py   # PC client with Windows audio routing
├── requirements.txt              # Python dependencies
├── WINDOWS_BUILTIN_SETUP.md     # Windows audio setup guide
└── README.md                     # This file
```

## 🚀 Quick Setup

### Phone Side (Android)
1. **Install Flutter** if not already installed
2. **Build and run the app:**
   ```bash
   cd mic_loopback_app
   flutter run
   ```
3. **Grant microphone permission** when prompted
4. **Note the IP address** shown in the app (e.g., 192.168.1.100:8888)
5. **Press "Start Server"** to begin streaming

### PC Side (Windows)
1. **Install Python dependencies:**
   ```bash
   pip install sounddevice numpy
   ```
2. **Run the PC client:**
   ```bash
   python pc_audio_client_loopback.py <PHONE_IP>
   ```
   Example: `python pc_audio_client_loopback.py 192.168.1.100`

### Windows Audio Setup
1. **Enable Stereo Mix** in Windows Sound Control Panel
2. **Set as default recording device**
3. **Applications can now use it as microphone input**

See `WINDOWS_BUILTIN_SETUP.md` for detailed Windows configuration steps.

## 🛠️ Technical Implementation

### Flutter App Features
- **Native Android audio capture** using AudioRecord API
- **TCP server implementation** for reliable audio streaming  
- **Real-time network discovery** showing device IP address
- **Clean Material Design UI** with server start/stop controls
- **Proper resource management** with automatic cleanup

### PC Client Features
- **Cross-platform audio playback** using sounddevice library
- **Windows audio integration** for microphone routing
- **Network optimization** with TCP_NODELAY and custom buffering
- **Robust error handling** for connection issues and audio dropouts
- **Timeout management** for stable streaming

### Network Protocol
- **TCP streaming** on port 8888 for reliable audio delivery
- **16-bit PCM audio** at 44.1kHz sample rate  
- **Optimized packet sizes** for minimal latency
- **Connection monitoring** with automatic reconnection handling

## 📊 Performance Characteristics

- **Audio Quality:** CD-quality 44.1kHz 16-bit PCM
- **Latency:** ~200-400ms total (typical for WiFi-based solutions)
- **Compatibility:** Android 5.0+ phones, Windows 10+ PCs
- **Network Requirements:** Local WiFi network (both devices on same network)

## 🔧 Advanced Configuration

### Custom Port Usage
```bash
# Use custom port (must match on both phone and PC)
python pc_audio_client_loopback.py <PHONE_IP> --port 9999
```

### Audio Device Selection
```bash
# List available audio devices
python pc_audio_client_loopback.py --list-devices

# Use specific audio device
python pc_audio_client_loopback.py <PHONE_IP> --device 2
```

## 🐛 Troubleshooting

### Connection Issues
- **Ensure both devices are on the same WiFi network**
- **Check firewall settings** - may need to allow port 8888
- **Verify phone shows correct IP address**
- **Try restarting the phone server**

### Audio Issues  
- **Check Windows volume mixer** for the Python process
- **Verify Stereo Mix is enabled and set as default**
- **Test with different applications** (Discord, OBS, etc.)
- **Ensure phone microphone permission is granted**

### Performance Issues
- **Check WiFi signal strength** - weak signal increases latency
- **Close bandwidth-heavy applications** during streaming
- **Try moving closer to WiFi router**

## 🎯 Use Cases

### Perfect For:
- **Content creation** - high-quality wireless microphone for recording
- **Video calls** - better audio quality than built-in laptop mics
- **Streaming** - wireless mic setup for live broadcasts
- **Presentations** - wireless microphone for remote presentations

### Limitations:
- **Real-time gaming** - latency may be too high for competitive gaming
- **Live music performance** - consider professional wireless mic systems
- **Critical applications** - where audio delay cannot be tolerated

## 🔮 Future Enhancements

The project architecture supports several potential improvements:

- **UDP streaming** for lower latency (with packet loss handling)
- **Custom Windows audio driver** for professional-grade latency
- **Multi-device support** for multiple phone inputs
- **Audio effects processing** (noise reduction, EQ, compression)
- **iOS support** with platform-specific optimizations

## 🤝 Contributing

This project demonstrates a complete audio streaming solution with:
- Cross-platform mobile development (Flutter)
- Network programming and audio streaming
- Windows API integration
- Real-time audio processing
- User experience design for technical applications

The codebase is structured for extensibility and can serve as a foundation for more advanced audio streaming applications.

## 📄 License

This project is provided as-is for educational and practical use. The implementation demonstrates modern audio streaming techniques and cross-platform development practices.

---

**Built with:** Flutter, Python, Android NDK, Windows Audio APIs, TCP networking
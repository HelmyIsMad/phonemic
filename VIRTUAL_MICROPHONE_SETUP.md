# 🎤 Virtual Microphone Setup Guide

## What You Need

Your phone's audio needs to appear as a **Windows microphone device** that apps like Discord, OBS, Teams, etc. can use. This requires virtual audio software.

## 🔧 Quick Setup (5 minutes)

### Step 1: Install Virtual Audio Cable

**🔵 VB-Cable (FREE - Recommended)**
1. Download from: https://vb-audio.com/Cable/
2. Install and restart Windows
3. Creates "CABLE Input" device

**OR**

**🔵 Virtual Audio Cable (Paid)**
- More advanced features, multiple cables
- Creates "Virtual Audio Cable" devices

### Step 2: Verify Installation

1. Right-click speaker icon in taskbar
2. Select "Open Sound settings" 
3. You should see the virtual device in output devices list

### Step 3: Use the Virtual Microphone Client

```bash
# Use the new virtual microphone client
python pc_audio_client_virtual_mic.py <PHONE_IP>

# Example
python pc_audio_client_virtual_mic.py 192.168.1.100
```

## 🎯 How It Works

```
Phone Mic → Phone App → WiFi → PC Client → Virtual Cable → Windows Apps
```

1. **Phone** captures microphone audio
2. **WiFi** streams audio to PC
3. **PC Client** receives audio and sends it to virtual cable
4. **Virtual Cable** appears as microphone in Windows
5. **Any Windows app** can select it as audio input

## 📱 Using in Applications

### Discord
1. Settings → Voice & Video
2. Input Device → Select "CABLE Output" or "Virtual Audio Cable"

### OBS Studio
1. Add "Audio Input Capture" source
2. Device → Select virtual cable
3. Phone audio now streams into OBS

### Teams/Zoom/Meet
1. Audio settings
2. Microphone → Select virtual cable device

### Any Other App
Look for microphone/audio input settings and select the virtual cable

## 🛠️ Commands Reference

```bash
# Show setup instructions
python pc_audio_client_virtual_mic.py --setup-info

# List available audio devices
python pc_audio_client_virtual_mic.py --list-devices

# Use specific device ID
python pc_audio_client_virtual_mic.py <PHONE_IP> --device 5

# Connect to phone with custom port
python pc_audio_client_virtual_mic.py <PHONE_IP> --port 9999
```

## 🔍 Troubleshooting

### "No virtual audio cable found"
- Install VB-Cable or Virtual Audio Cable
- Restart Windows after installation
- Run `--list-devices` to verify installation

### "Connection failed"
- Check phone and PC are on same WiFi
- Verify phone shows correct IP address
- Make sure phone server is started

### "Audio choppy or delayed"
- Check WiFi signal strength
- Close other network-heavy applications
- Try different virtual device if multiple available

## 💡 Pro Tips

- **Use VB-Cable** - it's free and works great for most use cases
- **Check Windows volume mixer** - make sure virtual device isn't muted
- **Set as default** - you can set the virtual cable as default mic in Windows
- **Multiple cables** - Virtual Audio Cable (paid) supports multiple channels

## 🎉 Result

Your phone becomes a **professional wireless microphone** that any Windows application can use! Perfect for:
- 📹 Content creation with better audio
- 🎮 Gaming with wireless mic
- 💼 Professional video calls
- 🎵 Recording with phone's high-quality mic
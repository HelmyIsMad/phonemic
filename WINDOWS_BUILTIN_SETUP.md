# 🎤 Windows Built-in Audio Routing (No External Software)

## 🎯 Goal
Make your phone audio usable as microphone input in Windows apps using only built-in Windows features.

## 🔧 Method 1: Stereo Mix (Best if available)

### Step 1: Enable Stereo Mix
1. Right-click speaker icon in taskbar
2. Select "Open Sound settings"
3. Click "Sound Control Panel" (on the right)
4. Go to **Recording** tab
5. Right-click in empty area → **"Show Disabled Devices"**
6. Look for **"Stereo Mix"** or **"What You Hear"**
7. Right-click it → **"Enable"**
8. Right-click it → **"Set as Default Device"**

### Step 2: Use the Loopback Client
```bash
python pc_audio_client_loopback.py <PHONE_IP>
```

### Step 3: Test in Apps
- **Discord**: Input Device → "Stereo Mix"
- **OBS**: Add "Audio Input Capture" → "Stereo Mix"
- **Teams/Zoom**: Microphone → "Stereo Mix"

## 🔧 Method 2: Listen to This Device

### If Stereo Mix isn't available:
1. Go to Sound Control Panel → **Recording** tab
2. Find your actual microphone
3. Right-click → **Properties**
4. Go to **"Listen"** tab
5. Check **"Listen to this device"**
6. Select your speakers as playback device
7. Click OK

### How it works:
- Phone audio plays through speakers
- Microphone picks up speaker audio
- Apps record from microphone (which includes phone audio)

## 🔧 Method 3: App-Specific Solutions

### OBS Studio
- Add **"Desktop Audio"** source
- This captures all system audio including phone stream

### Discord
- Try **"Legacy Audio Subsystem"** in Voice settings
- May better detect audio routing

### Windows Apps (Teams, etc.)
- Look for **"System Audio"** or **"Computer Audio"** options
- Some apps can directly capture desktop audio

## ⚡ Quick Test

1. **Start phone server**
2. **Run**: `python pc_audio_client_loopback.py 192.168.1.100`
3. **Speak into phone** - you should hear it from PC speakers
4. **Open Discord/OBS** and select appropriate input method above
5. **Test** - you should see your phone voice in the app!

## 🐛 Troubleshooting

### "Can't hear phone audio"
- Check PC speaker volume
- Verify phone server is running
- Check WiFi connection

### "Apps can't detect phone as microphone"
- Try Method 1 (Stereo Mix) first
- If not available, use Method 2 (Listen to Device)
- Check app-specific audio settings

### "Audio quality issues"
- Adjust speaker volume (not too loud to avoid feedback)
- Check WiFi signal strength
- Try different audio quality settings in app

## 💡 Pro Tips

- **Volume Control**: Keep speakers at moderate volume to avoid feedback
- **App Settings**: Always check app's audio input settings first
- **Test First**: Use Windows Voice Recorder to test if routing works
- **Default Device**: Setting Stereo Mix as default makes it easier for apps to find

## 🎉 Result

Your phone becomes a wireless microphone using only:
- ✅ Your Python client
- ✅ Your phone server
- ✅ Windows built-in audio features
- ❌ No external software needed!

Perfect for Discord calls, streaming, recording, and any app that needs microphone input!
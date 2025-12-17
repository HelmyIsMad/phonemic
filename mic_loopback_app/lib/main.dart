import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:audio_session/audio_session.dart';
import 'dart:async';
import 'dart:io';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mic Loopback',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MicLoopbackPage(),
    );
  }
}

class MicLoopbackPage extends StatefulWidget {
  const MicLoopbackPage({super.key});

  @override
  State<MicLoopbackPage> createState() => _MicLoopbackPageState();
}

class _MicLoopbackPageState extends State<MicLoopbackPage> {
  static const platform = MethodChannel('com.example.micloopback/audio');
  bool _isStreamingActive = false;
  bool _isPermissionGranted = false;
  String _status = 'Stopped';
  String _ipAddress = 'Getting IP...';
  final int _port = 8888;

  @override
  void initState() {
    super.initState();
    _initializeAudioSession();
    _checkPermission();
    _getDeviceIP();
  }

  Future<void> _getDeviceIP() async {
    try {
      for (var interface in await NetworkInterface.list()) {
        for (var addr in interface.addresses) {
          if (addr.type == InternetAddressType.IPv4 && !addr.isLoopback) {
            setState(() {
              _ipAddress = addr.address;
            });
            return;
          }
        }
      }
      setState(() {
        _ipAddress = 'No network found';
      });
    } catch (e) {
      setState(() {
        _ipAddress = 'Error: ${e.toString()}';
      });
    }
  }

  Future<void> _initializeAudioSession() async {
    try {
      final session = await AudioSession.instance;
      await session.configure(const AudioSessionConfiguration(
        avAudioSessionCategory: AVAudioSessionCategory.playAndRecord,
        avAudioSessionCategoryOptions: AVAudioSessionCategoryOptions.defaultToSpeaker,
        avAudioSessionMode: AVAudioSessionMode.measurement,
      ));
    } catch (e) {
      print('Error initializing audio session: $e');
    }
  }

  Future<void> _checkPermission() async {
    final status = await Permission.microphone.status;
    setState(() {
      _isPermissionGranted = status.isGranted;
    });
    
    if (!_isPermissionGranted) {
      final result = await Permission.microphone.request();
      setState(() {
        _isPermissionGranted = result.isGranted;
      });
    }
  }

  Future<void> _toggleStreaming() async {
    if (!_isPermissionGranted) {
      await _checkPermission();
      if (!_isPermissionGranted) return;
    }

    try {
      if (_isStreamingActive) {
        // Stop streaming
        try {
          await platform.invokeMethod('stopAudioStreaming');
          setState(() {
            _isStreamingActive = false;
            _status = 'Stopped';
          });
        } on PlatformException catch (e) {
          _showErrorDialog('Failed to stop audio streaming: ${e.message}');
        }
      } else {
        // Start streaming
        try {
          await platform.invokeMethod('startAudioStreaming', {'port': _port});
          setState(() {
            _isStreamingActive = true;
            _status = 'Streaming on $_ipAddress:$_port';
          });
        } on PlatformException catch (e) {
          if (e.code == 'UNAVAILABLE') {
            _showInfoDialog('Audio streaming feature not yet implemented on this platform.\n\nThe native Android code needs to be updated to enable network audio streaming.');
          } else {
            _showErrorDialog('Failed to start audio streaming: ${e.message}');
          }
        }
      }
    } catch (e) {
      _showErrorDialog('Error toggling audio stream: $e');
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showInfoDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Info'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    // TODO: Clean up any audio resources
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Wireless Microphone'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Wireless Microphone Server',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: Column(
                children: [
                  Text(
                    'Server Address:',
                    style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 8),
                  SelectableText(
                    '$_ipAddress:$_port',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Connect your PC to this address',
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: _isPermissionGranted ? _toggleStreaming : null,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(200, 60),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                backgroundColor: _isStreamingActive ? Colors.red : Colors.green,
                foregroundColor: Colors.white,
              ),
              child: Text(_isStreamingActive ? 'Stop Server' : 'Start Server'),
            ),
            const SizedBox(height: 40),
            Text(
              'Status: $_status',
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 20),
            if (!_isPermissionGranted)
              const Text(
                'Microphone permission required',
                style: TextStyle(color: Colors.red, fontSize: 16),
              ),
          ],
        ),
      ),
    );
  }
}

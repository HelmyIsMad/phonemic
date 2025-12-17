import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:audio_session/audio_session.dart';
import 'dart:async';

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
  bool _isLoopbackActive = false;
  bool _isPermissionGranted = false;
  String _status = 'Stopped';

  @override
  void initState() {
    super.initState();
    _initializeAudioSession();
    _checkPermission();
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

  Future<void> _toggleLoopback() async {
    if (!_isPermissionGranted) {
      await _checkPermission();
      if (!_isPermissionGranted) return;
    }

    try {
      if (_isLoopbackActive) {
        // Stop streaming
        try {
          await platform.invokeMethod('stopAudioLoopback');
          setState(() {
            _isLoopbackActive = false;
            _status = 'Stopped';
          });
        } on PlatformException catch (e) {
          _showErrorDialog('Failed to stop audio loopback: ${e.message}');
        }
      } else {
        // Start streaming
        try {
          await platform.invokeMethod('startAudioLoopback');
          setState(() {
            _isLoopbackActive = true;
            _status = 'Streaming';
          });
        } on PlatformException catch (e) {
          if (e.code == 'UNAVAILABLE') {
            _showInfoDialog('Audio loopback feature not yet implemented on this platform.\n\nThe native Android/iOS code needs to be added to enable real-time microphone to speaker streaming.');
          } else {
            _showErrorDialog('Failed to start audio loopback: ${e.message}');
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
        title: const Text('Mic Loopback'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Mic to Speaker Loopback',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: _isPermissionGranted ? _toggleLoopback : null,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(200, 60),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                backgroundColor: _isLoopbackActive ? Colors.red : Colors.green,
                foregroundColor: Colors.white,
              ),
              child: Text(_isLoopbackActive ? 'Stop Streaming' : 'Start Streaming'),
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

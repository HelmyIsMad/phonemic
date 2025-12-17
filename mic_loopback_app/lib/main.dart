import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
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
  bool _isLoopbackActive = false;
  bool _isPermissionGranted = false;
  String _status = 'Stopped';

  @override
  void initState() {
    super.initState();
    _checkPermission();
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

  Future<void> _startLoopback() async {
    if (!_isPermissionGranted) {
      await _checkPermission();
      if (!_isPermissionGranted) return;
    }

    if (_isLoopbackActive) return;

    try {
      // TODO: Implement actual audio loopback using platform channels
      // For now, just simulate the loopback state
      setState(() {
        _isLoopbackActive = true;
        _status = 'Running (Simulated)';
      });
      
      _showInfoDialog('Loopback started!\n\nNote: This is currently a UI demo. The actual audio loopback functionality needs to be implemented using platform-specific code or native audio libraries.');
      
    } catch (e) {
      _showErrorDialog('Error starting loopback: $e');
    }
  }

  Future<void> _stopLoopback() async {
    if (!_isLoopbackActive) return;

    try {
      // TODO: Stop actual audio loopback
      setState(() {
        _isLoopbackActive = false;
        _status = 'Stopped';
      });
    } catch (e) {
      _showErrorDialog('Error stopping loopback: $e');
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
              onPressed: _isPermissionGranted && !_isLoopbackActive ? _startLoopback : null,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(200, 60),
                textStyle: const TextStyle(fontSize: 16),
              ),
              child: const Text('Start Loopback'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoopbackActive ? _stopLoopback : null,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(200, 60),
                textStyle: const TextStyle(fontSize: 16),
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              child: const Text('Stop Loopback'),
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

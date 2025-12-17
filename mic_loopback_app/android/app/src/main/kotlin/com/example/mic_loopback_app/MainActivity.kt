package com.example.mic_loopback_app

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import kotlin.concurrent.thread
import java.io.IOException
import java.net.ServerSocket
import java.net.Socket

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example.micloopback/audio"
    private var audioRecord: AudioRecord? = null
    private var isStreaming = false
    private var streamingThread: Thread? = null
    private var serverSocket: ServerSocket? = null
    private var clientSocket: Socket? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "startAudioStreaming" -> {
                    try {
                        val port = call.argument<Int>("port") ?: 8888
                        startAudioStreaming(port)
                        result.success("Audio streaming started on port $port")
                    } catch (e: Exception) {
                        result.error("ERROR", "Failed to start audio streaming: ${e.message}", null)
                    }
                }
                "stopAudioStreaming" -> {
                    try {
                        stopAudioStreaming()
                        result.success("Audio streaming stopped")
                    } catch (e: Exception) {
                        result.error("ERROR", "Failed to stop audio streaming: ${e.message}", null)
                    }
                }
                else -> {
                    result.notImplemented()
                }
            }
        }
    }

    private fun startAudioStreaming(port: Int) {
        if (isStreaming) return

        val sampleRate = 44100
        val channelConfig = AudioFormat.CHANNEL_IN_MONO
        val audioFormat = AudioFormat.ENCODING_PCM_16BIT
        val bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            channelConfig,
            audioFormat,
            bufferSize
        )

        // Start server socket
        serverSocket = ServerSocket(port)
        isStreaming = true

        streamingThread = thread {
            try {
                // Wait for client connection
                clientSocket = serverSocket?.accept()
                val outputStream = clientSocket?.getOutputStream()

                // Start recording
                audioRecord?.startRecording()

                val buffer = ByteArray(bufferSize * 2) // 16-bit = 2 bytes per sample
                while (isStreaming && clientSocket?.isConnected == true) {
                    val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (read > 0) {
                        try {
                            outputStream?.write(buffer, 0, read)
                            outputStream?.flush()
                        } catch (e: IOException) {
                            // Client disconnected
                            break
                        }
                    }
                }
            } catch (e: Exception) {
                // Handle connection errors
            } finally {
                try {
                    clientSocket?.close()
                    audioRecord?.stop()
                } catch (e: Exception) {
                    // Ignore cleanup errors
                }
            }
        }
    }

    private fun stopAudioStreaming() {
        isStreaming = false

        streamingThread?.interrupt()
        streamingThread = null

        try {
            clientSocket?.close()
            serverSocket?.close()
        } catch (e: IOException) {
            // Ignore cleanup errors
        }
        clientSocket = null
        serverSocket = null

        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
    }

    override fun onDestroy() {
        super.onDestroy()
        stopAudioStreaming()
    }
}

package com.example.mic_loopback_app

import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import kotlin.concurrent.thread

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example.micloopback/audio"
    private var audioRecord: AudioRecord? = null
    private var audioTrack: AudioTrack? = null
    private var isRecording = false
    private var recordingThread: Thread? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "startAudioLoopback" -> {
                    try {
                        startAudioLoopback()
                        result.success("Audio loopback started")
                    } catch (e: Exception) {
                        result.error("ERROR", "Failed to start audio loopback: ${e.message}", null)
                    }
                }
                "stopAudioLoopback" -> {
                    try {
                        stopAudioLoopback()
                        result.success("Audio loopback stopped")
                    } catch (e: Exception) {
                        result.error("ERROR", "Failed to stop audio loopback: ${e.message}", null)
                    }
                }
                else -> {
                    result.notImplemented()
                }
            }
        }
    }

    private fun startAudioLoopback() {
        if (isRecording) return

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

        audioTrack = AudioTrack(
            AudioManager.STREAM_MUSIC,
            sampleRate,
            AudioFormat.CHANNEL_OUT_MONO,
            audioFormat,
            bufferSize,
            AudioTrack.MODE_STREAM
        )

        audioRecord?.startRecording()
        audioTrack?.play()

        isRecording = true

        recordingThread = thread {
            val buffer = ShortArray(bufferSize)
            while (isRecording) {
                val read = audioRecord?.read(buffer, 0, bufferSize) ?: 0
                if (read > 0) {
                    audioTrack?.write(buffer, 0, read)
                }
            }
        }
    }

    private fun stopAudioLoopback() {
        isRecording = false

        recordingThread?.interrupt()
        recordingThread = null

        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null

        audioTrack?.stop()
        audioTrack?.release()
        audioTrack = null
    }

    override fun onDestroy() {
        super.onDestroy()
        stopAudioLoopback()
    }
}

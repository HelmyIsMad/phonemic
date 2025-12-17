package com.example.micloopback

import android.Manifest
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    private lateinit var statusText: TextView
    
    private var audioRecord: AudioRecord? = null
    private var audioTrack: AudioTrack? = null
    private var isRecording = false
    private var recordingThread: Thread? = null
    
    private val sampleRate = 44100
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    
    private val requestCodeRecordAudio = 1001
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        setupClickListeners()
        checkPermissions()
    }
    
    private fun initializeViews() {
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
        statusText = findViewById(R.id.statusText)
    }
    
    private fun setupClickListeners() {
        startButton.setOnClickListener {
            if (hasRecordPermission()) {
                startLoopback()
            } else {
                requestRecordPermission()
            }
        }
        
        stopButton.setOnClickListener {
            stopLoopback()
        }
    }
    
    private fun checkPermissions() {
        if (!hasRecordPermission()) {
            requestRecordPermission()
        }
    }
    
    private fun hasRecordPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    private fun requestRecordPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.RECORD_AUDIO),
            requestCodeRecordAudio
        )
    }
    
    private fun startLoopback() {
        if (isRecording) return
        
        try {
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
            updateUI()
            
            recordingThread = thread {
                val buffer = ShortArray(bufferSize)
                while (isRecording) {
                    val read = audioRecord?.read(buffer, 0, bufferSize) ?: 0
                    if (read > 0) {
                        audioTrack?.write(buffer, 0, read)
                    }
                }
            }
            
        } catch (e: Exception) {
            Toast.makeText(this, "Error starting loopback: ${e.message}", Toast.LENGTH_SHORT).show()
            stopLoopback()
        }
    }
    
    private fun stopLoopback() {
        isRecording = false
        
        recordingThread?.interrupt()
        recordingThread = null
        
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        
        audioTrack?.stop()
        audioTrack?.release()
        audioTrack = null
        
        updateUI()
    }
    
    private fun updateUI() {
        runOnUiThread {
            if (isRecording) {
                startButton.isEnabled = false
                stopButton.isEnabled = true
                statusText.text = getString(R.string.status_running)
            } else {
                startButton.isEnabled = true
                stopButton.isEnabled = false
                statusText.text = getString(R.string.status_stopped)
            }
        }
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        when (requestCode) {
            requestCodeRecordAudio -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "Permission granted", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Microphone permission required", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        stopLoopback()
    }
}
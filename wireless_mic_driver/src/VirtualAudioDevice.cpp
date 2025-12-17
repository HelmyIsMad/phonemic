#include "../include/VirtualAudioDevice.h"
#include <iostream>
#include <algorithm>
#include <chrono>

// Global device instance
std::unique_ptr<VirtualAudioDevice> g_virtualDevice;

VirtualAudioDevice::VirtualAudioDevice()
    : m_deviceEnumerator(nullptr)
    , m_virtualDevice(nullptr)
    , m_audioClient(nullptr)
    , m_renderClient(nullptr)
    , m_waveFormat(nullptr)
    , m_bufferFrameCount(0)
    , m_samplesPerSec(SAMPLE_RATE)
    , m_bitsPerSample(BITS_PER_SAMPLE)
    , m_channels(CHANNELS)
    , m_isRunning(false)
    , m_audioBufferSize(0)
    , m_bufferWritePos(0)
    , m_bufferReadPos(0)
{
    LOG_ERROR("VirtualAudioDevice constructor");
}

VirtualAudioDevice::~VirtualAudioDevice()
{
    Cleanup();
    LOG_ERROR("VirtualAudioDevice destructor");
}

HRESULT VirtualAudioDevice::Initialize()
{
    LOG_ERROR("Initializing VirtualAudioDevice...");
    
    HRESULT hr = S_OK;
    
    // Initialize COM
    hr = InitializeCOM();
    CHECK_HR(hr);
    
    // For now, create a simple audio buffer without trying to create virtual device
    // This is a proof-of-concept that can be enhanced later
    
    // Setup audio format
    hr = SetupAudioFormat();
    CHECK_HR(hr);
    
    // Allocate audio buffer (circular buffer for incoming audio)
    m_audioBufferSize = (m_samplesPerSec * m_bitsPerSample * m_channels / 8) * 2; // 2 seconds buffer
    m_audioBuffer = std::make_unique<BYTE[]>(m_audioBufferSize);
    
    LOG_ERROR("VirtualAudioDevice initialized successfully (basic mode)");
    return S_OK;
}

HRESULT VirtualAudioDevice::InitializeAudioClient()
{
    HRESULT hr = m_virtualDevice->Activate(
        __uuidof(IAudioClient),
        CLSCTX_ALL,
        nullptr,
        (void**)&m_audioClient
    );
    CHECK_HR(hr);
    
    return S_OK;
}

HRESULT VirtualAudioDevice::SetupAudioFormat()
{
    // Setup wave format (simplified - no WASAPI dependency)
    m_waveFormat = (WAVEFORMATEX*)CoTaskMemAlloc(sizeof(WAVEFORMATEX));
    if (!m_waveFormat) {
        return E_OUTOFMEMORY;
    }
    
    m_waveFormat->wFormatTag = WAVE_FORMAT_PCM;
    m_waveFormat->nChannels = static_cast<WORD>(m_channels);
    m_waveFormat->nSamplesPerSec = m_samplesPerSec;
    m_waveFormat->wBitsPerSample = static_cast<WORD>(m_bitsPerSample);
    m_waveFormat->nBlockAlign = static_cast<WORD>((m_channels * m_bitsPerSample) / 8);
    m_waveFormat->nAvgBytesPerSec = m_samplesPerSec * m_waveFormat->nBlockAlign;
    m_waveFormat->cbSize = 0;
    
    // Set a reasonable buffer frame count for our virtual device
    m_bufferFrameCount = 1024; // Simple fixed buffer size
    
    LOG_ERROR("Audio format setup complete (basic mode)");
    return S_OK;
}

HRESULT VirtualAudioDevice::Start()
{
    LOG_ERROR("Starting VirtualAudioDevice...");
    
    if (m_isRunning) {
        return S_OK; // Already running
    }
    
    // Start audio processing thread (simplified mode)
    m_isRunning = true;
    m_audioThread = std::thread(&VirtualAudioDevice::AudioThreadProc, this);
    
    LOG_ERROR("VirtualAudioDevice started successfully (basic mode)");
    return S_OK;
}

HRESULT VirtualAudioDevice::Stop()
{
    LOG_ERROR("Stopping VirtualAudioDevice...");
    
    if (!m_isRunning) {
        return S_OK; // Already stopped
    }
    
    // Signal thread to stop
    m_isRunning = false;
    m_bufferCondition.notify_all();
    
    // Wait for thread to finish
    if (m_audioThread.joinable()) {
        m_audioThread.join();
    }
    
    LOG_ERROR("VirtualAudioDevice stopped successfully (basic mode)");
    return S_OK;
}

void VirtualAudioDevice::AudioThreadProc()
{
    LOG_ERROR("Audio thread started");
    
    while (m_isRunning) {
        // Fill audio buffer with data from phone
        FillAudioBuffer();
        
        // Sleep for a short time to avoid busy waiting
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    
    LOG_ERROR("Audio thread stopped");
}

HRESULT VirtualAudioDevice::FillAudioBuffer()
{
    // Simplified buffer processing - just manage the circular buffer
    // In a full implementation, this would feed a virtual audio device
    
    {
        std::lock_guard<std::mutex> lock(m_bufferMutex);
        
        UINT32 availableData = GetBufferedDataSize();
        
        if (availableData > 0) {
            // Process some audio data (simulate consumption)
            UINT32 bytesToProcess = (availableData < 1024) ? availableData : 1024;
            AdvanceReadPosition(bytesToProcess);
            
            // In a real implementation, this data would be sent to Windows audio system
            // For now, we just consume it to prevent buffer overflow
        }
    }
    
    return S_OK;
}

HRESULT VirtualAudioDevice::WriteAudioData(const BYTE* data, UINT32 dataSize)
{
    if (!data || dataSize == 0) {
        return E_INVALIDARG;
    }
    
    {
        std::lock_guard<std::mutex> lock(m_bufferMutex);
        
        UINT32 availableSpace = GetAvailableBufferSpace();
        if (dataSize > availableSpace) {
            // Buffer overflow, advance read position to make space
            UINT32 bytesToSkip = dataSize - availableSpace;
            AdvanceReadPosition(bytesToSkip);
        }
        
        // Write data to circular buffer
        UINT32 bytesToEnd = m_audioBufferSize - m_bufferWritePos;
        if (dataSize <= bytesToEnd) {
            // No wraparound
            memcpy(m_audioBuffer.get() + m_bufferWritePos, data, dataSize);
        } else {
            // Wraparound
            memcpy(m_audioBuffer.get() + m_bufferWritePos, data, bytesToEnd);
            memcpy(m_audioBuffer.get(), data + bytesToEnd, dataSize - bytesToEnd);
        }
        
        AdvanceWritePosition(dataSize);
    }
    
    // Notify audio thread
    m_bufferCondition.notify_one();
    
    return S_OK;
}

// Buffer management methods
UINT32 VirtualAudioDevice::GetAvailableBufferSpace() const
{
    if (m_bufferWritePos >= m_bufferReadPos) {
        return m_audioBufferSize - (m_bufferWritePos - m_bufferReadPos) - 1;
    } else {
        return m_bufferReadPos - m_bufferWritePos - 1;
    }
}

UINT32 VirtualAudioDevice::GetBufferedDataSize() const
{
    if (m_bufferWritePos >= m_bufferReadPos) {
        return m_bufferWritePos - m_bufferReadPos;
    } else {
        return m_audioBufferSize - (m_bufferReadPos - m_bufferWritePos);
    }
}

void VirtualAudioDevice::AdvanceWritePosition(UINT32 bytesWritten)
{
    m_bufferWritePos = (m_bufferWritePos + bytesWritten) % m_audioBufferSize;
}

void VirtualAudioDevice::AdvanceReadPosition(UINT32 bytesRead)
{
    m_bufferReadPos = (m_bufferReadPos + bytesRead) % m_audioBufferSize;
}

void VirtualAudioDevice::Cleanup()
{
    Stop();
    
    if (m_waveFormat) {
        CoTaskMemFree(m_waveFormat);
        m_waveFormat = nullptr;
    }
    
    if (m_renderClient) m_renderClient->Release();
    if (m_audioClient) m_audioClient->Release();
    if (m_virtualDevice) m_virtualDevice->Release();
    if (m_deviceEnumerator) m_deviceEnumerator->Release();
}

bool VirtualAudioDevice::IsDeviceAvailable() const
{
    return m_isRunning;  // Simplified check - just verify if we're running
}

// Static methods
HRESULT VirtualAudioDevice::InitializeCOM()
{
    return CoInitializeEx(nullptr, COINIT_MULTITHREADED);
}

void VirtualAudioDevice::CleanupCOM()
{
    CoUninitialize();
}

std::wstring VirtualAudioDevice::GetDeviceId()
{
    return L"{WirelessMic-Virtual-Device-12345}";
}

// C interface for Python integration
extern "C" {
    __declspec(dllexport) HRESULT CreateDevice()
    {
        try {
            g_virtualDevice = std::make_unique<VirtualAudioDevice>();
            return g_virtualDevice->Initialize();
        }
        catch (...) {
            return E_FAIL;
        }
    }
    
    __declspec(dllexport) HRESULT StartDevice()
    {
        if (!g_virtualDevice) {
            return E_FAIL;
        }
        return g_virtualDevice->Start();
    }
    
    __declspec(dllexport) HRESULT StopDevice()
    {
        if (!g_virtualDevice) {
            return E_FAIL;
        }
        return g_virtualDevice->Stop();
    }
    
    __declspec(dllexport) HRESULT WriteAudio(const BYTE* data, UINT32 size)
    {
        if (!g_virtualDevice) {
            return E_FAIL;
        }
        return g_virtualDevice->WriteAudioData(data, size);
    }
    
    __declspec(dllexport) HRESULT DestroyDevice()
    {
        if (g_virtualDevice) {
            g_virtualDevice.reset();
        }
        VirtualAudioDevice::CleanupCOM();
        return S_OK;
    }
    
    __declspec(dllexport) BOOL IsDeviceReady()
    {
        if (!g_virtualDevice) {
            return FALSE;
        }
        return g_virtualDevice->IsDeviceAvailable() ? TRUE : FALSE;
    }
}
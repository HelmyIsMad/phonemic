#include "../include/VirtualAudioDevice.h"
#include <iostream>
#include <algorithm>

// Global device instance
std::unique_ptr<VirtualAudioDevice> g_virtualDevice;

VirtualAudioDevice::VirtualAudioDevice()
    : m_waveFormat(nullptr)
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
    
    // Create device enumerator
    hr = CoCreateInstance(
        __uuidof(MMDeviceEnumerator),
        nullptr,
        CLSCTX_ALL,
        __uuidof(IMMDeviceEnumerator),
        (void**)&m_deviceEnumerator
    );
    CHECK_HR(hr);
    
    // Get default audio endpoint (we'll use this as a template)
    hr = m_deviceEnumerator->GetDefaultAudioEndpoint(
        eRender,
        eConsole,
        &m_virtualDevice
    );
    CHECK_HR(hr);
    
    // Initialize audio client
    hr = InitializeAudioClient();
    CHECK_HR(hr);
    
    // Setup audio format
    hr = SetupAudioFormat();
    CHECK_HR(hr);
    
    // Allocate audio buffer (circular buffer for incoming audio)
    m_audioBufferSize = (m_samplesPerSec * m_bitsPerSample * m_channels / 8) * 2; // 2 seconds buffer
    m_audioBuffer = std::make_unique<BYTE[]>(m_audioBufferSize);
    
    LOG_ERROR("VirtualAudioDevice initialized successfully");
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
    // Setup wave format
    m_waveFormat = (WAVEFORMATEX*)CoTaskMemAlloc(sizeof(WAVEFORMATEX));
    if (!m_waveFormat) {
        return E_OUTOFMEMORY;
    }
    
    m_waveFormat->wFormatTag = WAVE_FORMAT_PCM;
    m_waveFormat->nChannels = m_channels;
    m_waveFormat->nSamplesPerSec = m_samplesPerSec;
    m_waveFormat->wBitsPerSample = m_bitsPerSample;
    m_waveFormat->nBlockAlign = (m_channels * m_bitsPerSample) / 8;
    m_waveFormat->nAvgBytesPerSec = m_samplesPerSec * m_waveFormat->nBlockAlign;
    m_waveFormat->cbSize = 0;
    
    // Initialize the audio client
    HRESULT hr = m_audioClient->Initialize(
        AUDCLNT_SHAREMODE_SHARED,
        AUDCLNT_STREAMFLAGS_LOOPBACK, // This is key for creating a virtual input
        BUFFER_DURATION_MS * 10000,   // Buffer duration in 100ns units
        0,
        m_waveFormat,
        nullptr
    );
    CHECK_HR(hr);
    
    // Get buffer size
    hr = m_audioClient->GetBufferSize(&m_bufferFrameCount);
    CHECK_HR(hr);
    
    // Get render client
    hr = m_audioClient->GetService(__uuidof(IAudioRenderClient), (void**)&m_renderClient);
    CHECK_HR(hr);
    
    return S_OK;
}

HRESULT VirtualAudioDevice::Start()
{
    LOG_ERROR("Starting VirtualAudioDevice...");
    
    if (m_isRunning) {
        return S_OK; // Already running
    }
    
    // Start the audio client
    HRESULT hr = m_audioClient->Start();
    CHECK_HR(hr);
    
    // Start audio processing thread
    m_isRunning = true;
    m_audioThread = std::thread(&VirtualAudioDevice::AudioThreadProc, this);
    
    LOG_ERROR("VirtualAudioDevice started successfully");
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
    
    // Stop audio client
    if (m_audioClient) {
        m_audioClient->Stop();
    }
    
    LOG_ERROR("VirtualAudioDevice stopped successfully");
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
    if (!m_renderClient) {
        return E_FAIL;
    }
    
    UINT32 numFramesPadding;
    HRESULT hr = m_audioClient->GetCurrentPadding(&numFramesPadding);
    CHECK_HR(hr);
    
    UINT32 numFramesAvailable = m_bufferFrameCount - numFramesPadding;
    if (numFramesAvailable == 0) {
        return S_OK; // Buffer is full
    }
    
    // Get buffer from render client
    BYTE* pData;
    hr = m_renderClient->GetBuffer(numFramesAvailable, &pData);
    CHECK_HR(hr);
    
    // Copy audio data from our circular buffer
    UINT32 bytesToCopy = numFramesAvailable * m_waveFormat->nBlockAlign;
    
    {
        std::lock_guard<std::mutex> lock(m_bufferMutex);
        
        UINT32 availableData = GetBufferedDataSize();
        UINT32 actualBytesToCopy = std::min(bytesToCopy, availableData);
        
        if (actualBytesToCopy > 0) {
            // Handle circular buffer wraparound
            UINT32 bytesToEnd = m_audioBufferSize - m_bufferReadPos;
            if (actualBytesToCopy <= bytesToEnd) {
                // No wraparound
                memcpy(pData, m_audioBuffer.get() + m_bufferReadPos, actualBytesToCopy);
            } else {
                // Wraparound
                memcpy(pData, m_audioBuffer.get() + m_bufferReadPos, bytesToEnd);
                memcpy(pData + bytesToEnd, m_audioBuffer.get(), actualBytesToCopy - bytesToEnd);
            }
            AdvanceReadPosition(actualBytesToCopy);
        } else {
            // No data available, fill with silence
            memset(pData, 0, bytesToCopy);
        }
    }
    
    // Release buffer
    hr = m_renderClient->ReleaseBuffer(numFramesAvailable, 0);
    CHECK_HR(hr);
    
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
    
    m_renderClient.Release();
    m_audioClient.Release();
    m_virtualDevice.Release();
    m_deviceEnumerator.Release();
}

bool VirtualAudioDevice::IsDeviceAvailable() const
{
    return m_audioClient != nullptr && m_isRunning;
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
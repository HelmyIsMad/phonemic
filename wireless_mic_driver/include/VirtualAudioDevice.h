#pragma once

#include <windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <audiopolicy.h>
#include <endpointvolume.h>
#include <devicetopology.h>
#include <functiondiscoverykeys_devpkey.h>
#include <propvarutil.h>
#include <comdef.h>
#include <atlbase.h>
#include <atlcom.h>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>

// Virtual Audio Device Class
class VirtualAudioDevice {
private:
    // COM interfaces
    IMMDeviceEnumerator* m_deviceEnumerator;
    IMMDevice* m_virtualDevice;
    IAudioClient* m_audioClient;
    IAudioRenderClient* m_renderClient;
    
    // Audio format
    WAVEFORMATEX* m_waveFormat;
    UINT32 m_bufferFrameCount;
    UINT32 m_samplesPerSec;
    UINT32 m_bitsPerSample;
    UINT32 m_channels;
    
    // Threading and synchronization
    std::thread m_audioThread;
    std::atomic<bool> m_isRunning;
    std::mutex m_bufferMutex;
    std::condition_variable m_bufferCondition;
    
    // Audio buffer for incoming data from phone
    std::unique_ptr<BYTE[]> m_audioBuffer;
    UINT32 m_audioBufferSize;
    UINT32 m_bufferWritePos;
    UINT32 m_bufferReadPos;
    
    // Device properties
    static constexpr UINT32 SAMPLE_RATE = 44100;
    static constexpr UINT32 BITS_PER_SAMPLE = 16;
    static constexpr UINT32 CHANNELS = 1; // Mono
    static constexpr UINT32 BUFFER_DURATION_MS = 100;

public:
    VirtualAudioDevice();
    ~VirtualAudioDevice();
    
    // Main interface methods
    HRESULT Initialize();
    HRESULT Start();
    HRESULT Stop();
    void Cleanup();
    
    // Audio data methods
    HRESULT WriteAudioData(const BYTE* data, UINT32 dataSize);
    bool IsDeviceAvailable() const;
    
    // Device management
    HRESULT CreateVirtualDevice();
    HRESULT RegisterDevice();
    HRESULT UnregisterDevice();
    
    // Static utility methods
    static HRESULT InitializeCOM();
    static void CleanupCOM();
    static std::wstring GetDeviceId();

private:
    // Internal methods
    HRESULT InitializeAudioClient();
    HRESULT SetupAudioFormat();
    void AudioThreadProc();
    HRESULT FillAudioBuffer();
    
    // Buffer management
    UINT32 GetAvailableBufferSpace() const;
    UINT32 GetBufferedDataSize() const;
    void AdvanceWritePosition(UINT32 bytesWritten);
    void AdvanceReadPosition(UINT32 bytesRead);
};

// Global device instance
extern std::unique_ptr<VirtualAudioDevice> g_virtualDevice;

// C interface for Python integration
extern "C" {
    __declspec(dllexport) HRESULT CreateDevice();
    __declspec(dllexport) HRESULT StartDevice();
    __declspec(dllexport) HRESULT StopDevice();
    __declspec(dllexport) HRESULT WriteAudio(const BYTE* data, UINT32 size);
    __declspec(dllexport) HRESULT DestroyDevice();
    __declspec(dllexport) BOOL IsDeviceReady();
}

// Helper macros
#define SAFE_RELEASE(p) { if (p) { (p)->Release(); (p) = nullptr; } }
#define CHECK_HR(hr) { if (FAILED(hr)) return hr; }
#define LOG_ERROR(msg) OutputDebugStringA(msg "\n")
#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "dxgi.lib")
#pragma comment(lib, "ws2_32.lib")
#pragma comment(linker, "/SUBSYSTEM:windows /ENTRY:mainCRTStartup")

#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <d3d11.h>
#include <dxgi1_2.h>
#include <vector>

#define TARGET_IP "192.168.0.1"
#define TARGET_PORT 8888
#define FRAME_WIDTH 1920
#define FRAME_HEIGHT 1080

class ScreenStreamer {
private:
    ID3D11Device* d3dDevice = nullptr;
    ID3D11DeviceContext* d3dContext = nullptr;
    IDXGIOutputDuplication* deskDupl = nullptr;
    SOCKET streamSocket = INVALID_SOCKET;
    
public:
    bool Initialize() {
        // Initialize Direct3D
        D3D_FEATURE_LEVEL featureLevel;
        HRESULT hr = D3D11CreateDevice(
            nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr,
            0, nullptr, 0, D3D11_SDK_VERSION,
            &d3dDevice, &featureLevel, &d3dContext
        );
        
        if (FAILED(hr)) {
            return false;
        }
        
        // Get DXGI device
        IDXGIDevice* dxgiDevice = nullptr;
        hr = d3dDevice->QueryInterface(__uuidof(IDXGIDevice), (void**)&dxgiDevice);
        if (FAILED(hr)) {
            return false;
        }
        
        // Get DXGI adapter
        IDXGIAdapter* dxgiAdapter = nullptr;
        hr = dxgiDevice->GetParent(__uuidof(IDXGIAdapter), (void**)&dxgiAdapter);
        dxgiDevice->Release();
        if (FAILED(hr)) {
            return false;
        }
        
        // Get output
        IDXGIOutput* dxgiOutput = nullptr;
        hr = dxgiAdapter->EnumOutputs(0, &dxgiOutput);
        dxgiAdapter->Release();
        if (FAILED(hr)) {
            return false;
        }
        
        // Get output1
        IDXGIOutput1* dxgiOutput1 = nullptr;
        hr = dxgiOutput->QueryInterface(__uuidof(IDXGIOutput1), (void**)&dxgiOutput1);
        dxgiOutput->Release();
        if (FAILED(hr)) {
            return false;
        }
        
        // Create desktop duplication
        hr = dxgiOutput1->DuplicateOutput(d3dDevice, &deskDupl);
        dxgiOutput1->Release();
        if (FAILED(hr)) {
            return false;
        }
        
        return true;
    }
    
    bool ConnectToReceiver() {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            return false;
        }
        
        streamSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (streamSocket == INVALID_SOCKET) {
            WSACleanup();
            return false;
        }
        
        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(TARGET_PORT);
        inet_pton(AF_INET, TARGET_IP, &serverAddr.sin_addr);
        
        if (connect(streamSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            closesocket(streamSocket);
            WSACleanup();
            return false;
        }
        
        return true;
    }
    
    void StreamLoop() {
        DXGI_OUTDUPL_FRAME_INFO frameInfo;
        IDXGIResource* desktopResource = nullptr;
        ID3D11Texture2D* desktopTexture = nullptr;
        
        while (true) {
            // Acquire next frame
            HRESULT hr = deskDupl->AcquireNextFrame(100, &frameInfo, &desktopResource);
            
            if (hr == DXGI_ERROR_WAIT_TIMEOUT) {
                continue;
            }
            
            if (FAILED(hr)) {
                Sleep(100);
                continue;
            }
            
            // Get texture
            hr = desktopResource->QueryInterface(__uuidof(ID3D11Texture2D), (void**)&desktopTexture);
            desktopResource->Release();
            
            if (SUCCEEDED(hr)) {
                // Create staging texture for CPU access
                D3D11_TEXTURE2D_DESC texDesc;
                desktopTexture->GetDesc(&texDesc);
                
                texDesc.Usage = D3D11_USAGE_STAGING;
                texDesc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
                texDesc.BindFlags = 0;
                texDesc.MiscFlags = 0;
                
                ID3D11Texture2D* stagingTexture = nullptr;
                hr = d3dDevice->CreateTexture2D(&texDesc, nullptr, &stagingTexture);
                
                if (SUCCEEDED(hr)) {
                    // Copy to staging texture
                    d3dContext->CopyResource(stagingTexture, desktopTexture);
                    
                    // Map staging texture
                    D3D11_MAPPED_SUBRESOURCE mappedResource;
                    hr = d3dContext->Map(stagingTexture, 0, D3D11_MAP_READ, 0, &mappedResource);
                    
                    if (SUCCEEDED(hr)) {
                        // Send frame header (frame size)
                        DWORD frameSize = mappedResource.RowPitch * texDesc.Height;
                        send(streamSocket, (char*)&frameSize, sizeof(frameSize), 0);
                        send(streamSocket, (char*)&texDesc.Width, sizeof(texDesc.Width), 0);
                        send(streamSocket, (char*)&texDesc.Height, sizeof(texDesc.Height), 0);
                        
                        // Send frame data
                        int bytesSent = send(streamSocket, (char*)mappedResource.pData, frameSize, 0);
                        
                        if (bytesSent == SOCKET_ERROR) {
                            d3dContext->Unmap(stagingTexture, 0);
                            stagingTexture->Release();
                            desktopTexture->Release();
                            deskDupl->ReleaseFrame();
                            break;
                        }
                        
                        d3dContext->Unmap(stagingTexture, 0);
                    }
                    
                    stagingTexture->Release();
                }
                
                desktopTexture->Release();
            }
            
            // Release frame
            deskDupl->ReleaseFrame();
            
            Sleep(33); // ~30 FPS
        }
    }
    
    void Cleanup() {
        if (deskDupl) deskDupl->Release();
        if (d3dContext) d3dContext->Release();
        if (d3dDevice) d3dDevice->Release();
        if (streamSocket != INVALID_SOCKET) {
            closesocket(streamSocket);
            WSACleanup();
        }
    }
};

int main() {
    ScreenStreamer streamer;
    
    if (!streamer.Initialize()) {
        Sleep(10000);
        return main(); // Retry initialization
    }
    
    // Keep trying to connect every 10 seconds until successful
    while (!streamer.ConnectToReceiver()) {
        Sleep(10000); // Wait 10 seconds before retry
    }
    
    streamer.StreamLoop();
    streamer.Cleanup();
    
    return 0;
}

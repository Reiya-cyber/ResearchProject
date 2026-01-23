# Get first available camera
$webcam = Get-PnpDevice -PresentOnly -Class Camera,Image |
          Select-Object -First 1 -ExpandProperty FriendlyName

if (-not $webcam) {
    Write-Error "No webcam found."
    exit 1
}

# Go to VLC directory
$tempPath = [System.IO.Path]::GetTempPath()
cd "$tempPath\VLC"

# Launch VLC with detected webcam
.\vlc.exe -I dummy dshow:// :dshow-vdev="$webcam" :dshow-adev=none :dshow-size=1280x720 :dshow-fps=30 --sout "#transcode{vcodec=h264,vb=1500,fps=30}:http{mux=ts,dst=:8080/}" --no-sout-all --sout-keep

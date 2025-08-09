# ScreenServer

ffmpeg.exe -list_devices true -f dshow -i dummy

ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -f mpegts udp://localhost:5000
ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -vf scale=640:480 -r 15 -f mpegts udp://localhost:5000


ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -f mpegts udp://127.0.0.1:5000
ffmpeg.exe -f dshow -i video="OBS Virtual Camera" -f mpegts udp://192.168.1.5:5000

ffmpeg.exe -f dshow -i video="OBS Virtual Camera" -vf scale=640:480 -r 15 -f mpegts udp://localhost:5000


ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -f mpegts - | ffplay.exe -
ffmpeg.exe -f dshow -i video="Integrated Webcam" -f mpegts - | ffplay.exe -


ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -vf scale=640:480 -r 15 -f mpegts tcp://localhost:5000?listen
ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -vf scale=640:480 -r 15 -f mpegts udp://localhost:5000

ffmpeg -f lavfi -i testsrc=size=640x480:rate=30 -f mpegts udp://localhost:5000


ffmpeg.exe -f dshow -i video="Logi C270 HD WebCam" -vf scale=640:480 -r 15 -q:v 5 -f mjpeg udp://192.168.1.50:5000

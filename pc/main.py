import socket
import pyaudio

# Audio config
RATE = 48000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 960  # 20ms @ 48kHz (recommended)

# UDP config
UDP_IP = input("IP: ")
UDP_PORT = 5005

# Audio output (set this to your Virtual Cable output device)
p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=CHUNK
)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening for audio...")

try:
    while True:
        data, _ = sock.recvfrom(CHUNK * 2)  # int16 = 2 bytes
        stream.write(data)
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()

import requests, cv2, time, os, subprocess
import numpy as np
import sounddevice as sd
from datetime import date, datetime
from soundfile import write

start = time.time()

# setting things for later
folder = 'D:/Unitn/Progetti/camera/imgs/'
sd.default.samplerate = 44100
sd.default.channels = 2
url = "http://192.168.0.3:30080/shot.jpg"
seconds = 10800
today = str(date.today()).replace('-', '_')
current_time = datetime.now().strftime("%H_%M")
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
recording = sd.rec(seconds * sd.default.samplerate)
counter = 0
recordingEnd = 0
img_list = []

name = input("Course name?")
filename = name + '_' + today + '_' + current_time + '_final.mp4'
print(filename)

recordingStart = time.time()

while True:
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    cv2.imshow("Android_cam", img)
    counter += 1
    img_list.append(img)

    # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        recordingEnd = time.time()
        sd.stop()
        break

duration = recordingEnd - recordingStart
print(duration)
cv2.destroyAllWindows()
fps = counter / duration
print(counter)

out = cv2.VideoWriter('output.avi', fourcc, fps, (1920, 1080))
for i in range(counter):
    out.write(img_list[i])

# print(recording.shape)
write('output.wav', recording, 44100)

print("wrote recording")

subprocess.run(["ffmpeg", "-loglevel", "panic", "-i", "output.avi", "-c", "copy", "output.mp4"],
               capture_output=True)

print("Converted to mp4")
# print(sd.query_devices(kind='input'))

# cut to duration of video
os.system(f"ffmpeg -loglevel panic -ss 0 -i output.wav -t {duration} -c copy output_cut.wav")

print("Cut audio")

# convert to mp3
third_result = subprocess.run(["ffmpeg",
                               "-loglevel", "panic",
                               "-i", "output_cut.wav",
                               "-vn", "-ar", "44100",
                               "-ac", "2",
                               "-b:a", "192k",
                               "output_cut_r.mp3"])

print("Reformat to mp3")

# increase volume
# third_result = subprocess.run(["ffmpeg",
#                                "-i", "output_reformat.wav",
#                                "-c", "copy",
#                                "-af", '"volume=10dB"',
#                                "output_increased_audio.wav"])

fourth_result = subprocess.run(["ffmpeg",
                                "-loglevel", "panic",
                                "-i", "output_cut_r.mp3",
                                "-i", "output.mp4",
                                "-c", "copy",
                                "output_semi_final.mkv"])

print("Merged video and audio")

subprocess.run(["ffmpeg",
                "-loglevel", "panic",
                "-i", "output_semi_final.mkv", "-c", "copy", filename])

print("Converted to mp4 again")

# subprocess.run(["ffmpeg",
#                 # "-loglevel", "panic",
#                 "-i", "output_final.mp4", "-filter:v", "fps=fps=30", filename],
#                capture_output=True)

# print("To 30 fps")

print(time.time() - start)

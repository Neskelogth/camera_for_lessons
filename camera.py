import requests
import cv2
import numpy as np
from datetime import date, datetime
import os
import sounddevice as sd
from soundfile import write
import subprocess

sd.default.samplerate = 44100
sd.default.channels = 2

# Replace the below URL with your own. Make sure to add "/shot.jpg" at last.
url = "http://192.168.0.5:30080/shot.jpg"
seconds = 10800
fs = 44100

# # name = input("Course name?")
name = 'ML'
today = str(date.today()).replace('-', '_')
current_time = datetime.now().strftime("%H_%M")
print(name + '_' + today + '_' + current_time)

filename = name + '_' + today + '_' + current_time + '.mp4'

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('output.avi', fourcc, 10.0, (1920, 1080))

# first_command = 'ffmpeg -loglevel panic -i output.avi -c copy output.mp4'
# second_command = 'ffmpeg -loglevel panic -i output.mp4 -filter:v fps=fps=30 output_30_fps.mp4'

recording = sd.rec(seconds * fs, samplerate=fs, channels=2)

# While loop to continuously fetching data from the Url
while True:
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    cv2.imshow("Android_cam", img)
    out.write(img)

    #     # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        sd.stop()
        break

cv2.destroyAllWindows()

# print(recording.shape)
write('output.wav', recording, 44100)

print("wrote recording")

subprocess.run(["ffmpeg", "-loglevel", "panic", "-i", "output.avi", "-c", "copy", "output.mp4"],
               capture_output=True)

print("Things done")
print(sd.query_devices(kind='input'))

duration = float(input("Insert duration of video: "))
print(duration)

# cut to duration of video
os.system(f"ffmpeg -loglevel panic -ss 0 -i output.wav -t {duration} -c copy output_cut.wav")

# convert to mp3
third_result = subprocess.run(["ffmpeg",
                               "-i", "output_cut.wav",
                               "-vn", "-ar", "44100",
                               "-ac", "2",
                               "-b:a", "192k",
                               "output_cut_r.mp3"])

# increase volume
# third_result = subprocess.run(["ffmpeg",
#                                "-i", "output_reformat.wav",
#                                "-c", "copy",
#                                "-af", '"volume=10dB"',
#                                "output_increased_audio.wav"])

# ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac output.mp4

fourth_result = subprocess.run(["ffmpeg",
                                "-loglevel", "panic",
                                "-i", "output_cut_r.mp3",
                                "-i", "output.mp4",
                                "-c", "copy",
                                "output_semi_final.mkv"])

subprocess.run(["ffmpeg",
                "-loglevel", "panic",
                "-i", "output_semi_final.mkv", "-c", "copy", "output_final.mp4"],
               capture_output=True)

subprocess.run(["ffmpeg",
                "-loglevel", "panic",
                "-i", "output_final.mp4", "-filter:v", "fps=fps=30", "output_30_fps.mp4"],
               capture_output=True)

# removing temp files
os.remove('output.avi')
os.remove('output.mp4')
os.remove('output_30_fps.mp4')
os.remove('output.wav')
os.remove('output_cut.wav')
os.remove('output_cut_r.mp3')
os.remove('output_semi_final.mkv')


print("done")

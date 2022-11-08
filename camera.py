import os
import subprocess
import time
from datetime import date, datetime
import shutil

import cv2
import numpy as np
import sounddevice as sd
from requests import get
from soundfile import write

start = time.time()

# setting things for later
list_of_files = ['fps.php', 'ffmpeg.php', 'automate.cmd']
folder = 'D:/Unitn/Progetti/camera/imgs/'
sd.default.samplerate = 44100
sd.default.channels = 2
url = "http://192.168.137.18:31080/shot.jpg"
seconds = 10800

today = str(date.today()).replace('-', '_')
current_time = datetime.now().strftime("%H_%M")
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
recording = sd.rec(seconds * sd.default.samplerate)
counter = 0
recordingEnd = 0
i = 0

post_process = input('Wanna post process? (y/n)').lower()
name = input("Course name?")
filename = name + '_' + today + '_' + current_time + '_final.mp4'
print(filename)

folder = folder + name + '/'
print(folder)

if not os.path.exists(folder):

    os.mkdir(folder)
    for file in os.listdir('.'):
        if file in list_of_files:
            print(file)
            shutil.copy2(file, folder)

for file in os.listdir(folder):
    file_path = os.path.join(folder, file)
    if os.path.isfile(file_path) and file.find('.php') == -1:
        os.remove(file_path)

print("Deleted")

print("Starting")
recordingStart = time.time()

while True:
    img_resp = get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    cv2.imshow("Android_cam", img)
    img_name = str(time.time()) + ".jpg"
    cv2.imwrite(folder + img_name, img)
    counter += 1

    # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        recordingEnd = time.time()
        sd.stop()
        break

print("Finished recording")

duration = recordingEnd - recordingStart
print(f"duration in minutes: {duration / 60} and duration in seconds: {duration}")
cv2.destroyAllWindows()
fps = counter / duration
print(f"Framerate: {fps}")
frameDuration = 1 / fps

for file in os.listdir(folder):
    with open(folder + 'names.txt', 'a') as source:
        source.write('file ' + file + '\n')
        source.write(f'duration {frameDuration}\n')
        i += 1
        if i == counter:
            source.write('file ' + file + '\n')

os.chdir(folder)
write('output.wav', recording, 44100)

print("wrote recording")

# cut to duration of video
subprocess.check_call(["ffmpeg",
                       "-i", "output.wav",
                       "-ss", "0",
                       "-t", str(duration),
                       "-c", "copy",
                       "output_cut.wav",
                       "-loglevel", "panic"
                       ])

print("Cut audio")

# convert to mp3
third_result = subprocess.check_call(["ffmpeg",
                                      "-i", "output_cut.wav",
                                      "-vn", "-ar", "44100",
                                      "-ac", "2",
                                      "-b:a", "192k",
                                      "output_cut_r.mp3",
                                      "-loglevel", "panic"])

print("Reformat to mp3")

if post_process == 'y':
    subprocess.check_call(['php', 'ffmpeg.php'])
    subprocess.check_call(['php', 'fps.php'])

print((time.time() - start) / 60)

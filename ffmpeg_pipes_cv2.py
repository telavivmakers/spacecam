
# ffmpeg -y -i http://192.168.0.85:81/stream -ss 0 -vframes 1 -vcodec mjpeg -f image2 tomato.jpg
import os
import tempfile
import subprocess
import cv2
import numpy as np

import Image
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import time
import datetime


# To get this path execute:
#    $ which ffmpeg
FFMPEG_BIN = '/home/user/anaconda3/envs/opencv/bin/ffmpeg'


# To find allowed formats for the specific camera:
#    $ ffmpeg -f v4l2 -list_formats all -i /dev/video3
#    ...
#    [video4linux2,v4l2 @ 0x5608ac90af40] Raw: yuyv422: YUYV 4:2:2: 640x480 1280x720 960x544 800x448 640x360 424x240 352x288 320x240 800x600 176x144 160x120 1280x800
#    ...

def run_ffmpeg():
    ffmpg_cmd = [
        FFMPEG_BIN,
        '-i', 'http://192.168.0.85:81 ',
        '-ss','0',
        '-video_size', '800x600',
        '-pix_fmt', 'bgr24',        # opencv requires bgr24 pixel format
        '-vcodec', 'rawvideo',
        '-f', 'image2pipe',
        '-',                        # output to go to stdout
    ]
    return subprocess.Popen(ffmpg_cmd, stdout = subprocess.PIPE, bufsize=10**8)

def run_cv_window(process):
    while True:
        # read frame-by-frame
        raw_image = process.stdout.read(600*800*3)
        if raw_image == b'':
            raise RuntimeError("Empty pipe")
        
        # transform the bytes read into a numpy array
        frame =  np.frombuffer(raw_image, dtype='uint8')
        frame = frame.reshape((600,800,3)) # height, width, channels
        if frame is not None:
            cv2.imshow('Video', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite("tomatoOut.bmp", frame)
            break
        process.stdout.flush()
    
    cv2.destroyAllWindows()
    process.terminate()
    print(process.poll())

def run():
    ffmpeg_process = run_ffmpeg()
    run_cv_window(ffmpeg_process)

run()

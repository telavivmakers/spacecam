
# ffmpeg -y -i http://192.168.0.85:81/stream -ss 0 -vframes 1 -vcodec mjpeg -f image2 tomato.jpg
import os
import tempfile
import subprocess
import cv2
import numpy as np
import datetime

# To get this path execute:
#    $ which ffmpeg
FFMPEG_BIN = '/home/user/anaconda3/envs/cv2.39/bin/ffmpeg'


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
    avg = None
    while True:
        # read frame-by-frame
        raw_image = process.stdout.read(600*800*3)
        if raw_image == b'':
            raise RuntimeError("Empty pipe")
        
        # transform the bytes read into a numpy array
        frameBuf =  np.frombuffer(raw_image, dtype='uint8')
        frameBuf = frameBuf.reshape((600,800,3)) # height, width, channels
        if frameBuf is not None:
            
        
            gray = cv2.cvtColor(frameBuf, cv2.COLOR_BGR2GRAY)
            #####
            frame = cv2.GaussianBlur(gray, (21, 21), 0)
            #text = "Unoccupied"
            if avg is None:
                avg = frame.copy().astype("float")
                continue
            cv2.accumulateWeighted(frame, avg, 0.5)
            myDelta = cv2.absdiff(frame, cv2.convertScaleAbs(avg))
            thresh = cv2.threshold(myDelta, 5, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
            result = []
            for c in cnts:
                if cv2.contourArea(c) >= 900:
                    result.append(c)
                    #text = "Occupied"

            if result or not ('imgRGB' in locals()):
                #####
                edge = cv2.blur(gray, (3, 3))
                edgeThresh = 40
                edge = cv2.Canny(edge,
                                edgeThresh,
                                edgeThresh * 3,
                                apertureSize=3)
                edge = cv2.dilate(edge, np.ones((3, 3), np.uint8))
                imgRGB = cv2.bitwise_and(frameBuf, frameBuf, mask=edge)
                imgRGB = cv2.cvtColor(imgRGB, cv2.COLOR_BGR2RGB)
                #####
                for c in result:
                    (x, y, w, h) = cv2.boundingRect(c)
                    imgRGB[y:y + h,
                        x:x + w] = np.random.randint(256,
                                                        size=(h, w, 3))
                #### DOWN WITH BIG BROTHER ###
                #cv2.rectangle(imgRGB, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #cv2.rectangle(imgRGB, (x, y), (x + w, y + h), (0, 255, 0), -1)
                #cv2.putText(imgRGB, "{}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                # ts = datetime.datetime.now(datetime.timezone(
                    # 'Asia/Jerusalem')).strftime("%A %d %B %Y %I:%M:%S%p")
                ts = "hi"
                cv2.putText(imgRGB, ts, (10, imgRGB.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 0), 1)
                cv2.imshow('Video', imgRGB)
                                
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

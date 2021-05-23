# spacecam
this is the python code that runs tami ([space.telavivmakers.org](space.telavivmakers.org)) is-anyone-there camera. 

using some opencv for face blurring.

![](https://i.imgur.com/nWtcJ9W.png)

## ESP32-cam
using ffmpeg to read the mjpeg stream from the [9$ cam](https://wiki.idiot.io/esp32-cam_2#ai-thinker), 
pipe it to opencv and route to ...


### gstreamer
gst-launch-1.0 souphttpsrc \
    location=http://192.168.0.85:81 do-timestamp=true \
    ! multipartdemux ! image/jpeg,width=640,height=480 \
    ! matroskamux \
    ! filesink location=mjpeg.mkvD

 gst-launch-1.0 videotestsrc is-live=true ! openh264enc ! mpegtsmux \
  ! hlssink playlist-root=https://your-site.org \
  location=/srv/hls/hlssink.%05d.ts \
  playlist-location=/srv/hls/playlist.m3u8

gst-launch-1.0 souphttpsrc \
    location=http://192.168.0.85:81 do-timestamp=true \
    ! multipartdemux ! image/jpeg,width=640,height=480 \
    ! openh264enc ! mpegtsmux \
    ! hlssink playlist-root=https://your-site.org \
    location=/srv/hls/hlssink.%05d.ts \
    playlist-location=/srv/hls/playlist.m3u8
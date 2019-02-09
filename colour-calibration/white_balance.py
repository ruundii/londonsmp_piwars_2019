import os
import cv2
import time

is_raspberry = os.name != 'nt'

camera_settings = {'resolution' : (640,480),
    'iso':800,
    'brightness': 55,
    'saturation':40,
    'framerate' : 40#,
    #'shutter_speed':15000
                   }

if is_raspberry:
    try:
        from videoutils.video_stream_pi import VideoStream
    except:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))
        from videoutils.video_stream_pi import VideoStream
else:
    try:
        from videoutils.video_stream_webcam import VideoStream
    except:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))
        from videoutils.video_stream_webcam import VideoStream

def main():
    camera = VideoStream(camera_settings=camera_settings)

    camera.start()

    count = 0
    while True:
        image=None
        image, _ = camera.read()
        isBgr = True
        if image is None:
            time.sleep(0.1)
            continue
        print('awb gains:',str(float(camera.camera.awb_gains[0])),',',str(float(camera.camera.awb_gains[1])))
        cv2.putText(image, 'awb gains:'+str(float(camera.camera.awb_gains[0]))+','+str(float(camera.camera.awb_gains[1])), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
        cv2.imshow("Original", image)
        print("exposure_speed:",camera.camera.exposure_speed)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break


if __name__ == '__main__':
    main()
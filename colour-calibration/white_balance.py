import os
import cv2
import time
import numpy as np
import json
from threading import Lock
is_raspberry = os.name != 'nt'

gray_region = [300,220,40,40]
camera = None
current_window_name = "Trackbars"
config_file_lock = Lock()

camera_settings = {'resolution' : (640,480),
    'iso':800,
    'brightness': 55,
    'saturation':40,
    'framerate' : 20#,
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
    global camera
    camera = VideoStream(camera_settings=camera_settings)

    camera.start()
    if is_raspberry:
        camera.camera.awb_mode = 'off'
        camera.camera.awb_gains=(1.6,1.6)
    count = 0
    while True:
        count +=1
        image=None
        image, _ = camera.read()
        isBgr = True
        if image is None:
            time.sleep(0.1)
            continue
        cv2.rectangle(image,(gray_region[0],gray_region[1]),(gray_region[0]+gray_region[2],gray_region[1]+gray_region[3]), (255,0,255), 2, 2)

        gray_area_mean_b = np.mean(image[gray_region[1]:gray_region[1]+gray_region[3],gray_region[0]:gray_region[0]+gray_region[2],0])
        gray_area_mean_g = np.mean(image[gray_region[1]:gray_region[1]+gray_region[3],gray_region[0]:gray_region[0]+gray_region[2],1])
        gray_area_mean_r = np.mean(image[gray_region[1]:gray_region[1]+gray_region[3],gray_region[0]:gray_region[0]+gray_region[2],2])

        # cv2.putText(image, 'awb gains:'+str(float(camera.camera.awb_gains[0]))+','+str(float(camera.camera.awb_gains[1])), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
        cv2.putText(image, 'gray:'+str(int(gray_area_mean_r))+"-"+str(int(gray_area_mean_g))+"-"+str(int(gray_area_mean_b)), (200,350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)
        cv2.imshow("Original", image)
        if(count % 3 ==0):
            if is_raspberry:
                print('awb gains:', str(float(camera.camera.awb_gains[0])), ',', str(float(camera.camera.awb_gains[1])))
                print("exposure_speed:", camera.camera.exposure_speed)
                print("shutter_speed:", camera.camera.shutter_speed)

                # set new awb
                red_gain = float(camera.camera.awb_gains[0])
                blue_gain = float(camera.camera.awb_gains[1])
                if(gray_area_mean_r>gray_area_mean_g+2):
                    #reduce red
                    red_gain = red_gain-0.05
                elif(gray_area_mean_r<gray_area_mean_g-2):
                    #increase red
                    red_gain = red_gain+0.05
                if(gray_area_mean_b>gray_area_mean_g+2):
                    #reduce blue
                    blue_gain = blue_gain-0.05
                elif(gray_area_mean_b<gray_area_mean_g-2):
                    #increase blue
                    blue_gain = blue_gain+0.05

                if((gray_area_mean_r+gray_area_mean_g+gray_area_mean_b)/3<120):
                    #increase exposure
                    camera.camera.shutter_speed =  int(camera.camera.exposure_speed*1.02)
                elif ((gray_area_mean_r+gray_area_mean_g+gray_area_mean_b)/3>136):
                    #decrease exposure
                    camera.camera.shutter_speed = int(camera.camera.exposure_speed / 1.02)

                camera.camera.awb_gains = (red_gain, blue_gain)
                print('new awb gains:', str(float(camera.camera.awb_gains[0])), ',', str(float(camera.camera.awb_gains[1])))


        if cv2.waitKey(5) & 0xFF is ord('q'):
            print('writing camera_config.json')
            with config_file_lock:
                with open('camera_config.json', 'r') as json_config_file:
                    config = json.load(json_config_file)
                config["red_gain"] = float(camera.camera.awb_gains[0])
                config["blue_gain"] = float(camera.camera.awb_gains[1])
                config["shutter_speed"] = camera.camera.exposure_speed
                config["shutter_speed_shortened"] = int(camera.camera.exposure_speed * 0.8)
                with open('camera_config.json', 'w') as json_config_file:
                    json.dump(config, json_config_file, indent=2)
            break


if __name__ == '__main__':
    main()
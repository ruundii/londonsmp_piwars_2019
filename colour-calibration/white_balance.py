import os
import cv2
import time
import numpy as np
import json
from threading import Lock
is_raspberry = os.name != 'nt'

green_region = [300,120,40,40]
red_region = [130,100,40,40]
camera = None
current_window_name = "Trackbars"
config_file_lock = Lock()

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
    global camera
    camera = VideoStream(camera_settings=camera_settings)

    camera.start()
    setup_trackbars()
    adjust_camera()
    count = 0
    while True:
        count +=1
        image=None
        image, _ = camera.read()
        isBgr = True
        if image is None:
            time.sleep(0.1)
            continue
        cv2.rectangle(image,(green_region[0],green_region[1]),(green_region[0]+green_region[2],green_region[1]+green_region[3]), (0,255,0), 2, 2)
        cv2.rectangle(image,(red_region[0],red_region[1]),(red_region[0]+red_region[2],red_region[1]+red_region[3]), (0,0,255), 2, 2)
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        red_h = image_hsv[red_region[1]:red_region[1] + red_region[3], red_region[0]:red_region[0] + red_region[2], 0].copy()
        red_h[red_h<90] += 180
        red_area_mean_h = np.mean(red_h) % 180
        red_area_mean_s = np.mean(image_hsv[red_region[1]:red_region[1]+red_region[3],red_region[0]:red_region[0]+red_region[2],1])
        red_area_mean_v = np.mean(image_hsv[red_region[1]:red_region[1]+red_region[3],red_region[0]:red_region[0]+red_region[2],2])

        green_area_mean_h = np.mean(image_hsv[green_region[1]:green_region[1]+green_region[3],green_region[0]:green_region[0]+green_region[2],0])
        green_area_mean_s = np.mean(image_hsv[green_region[1]:green_region[1]+green_region[3],green_region[0]:green_region[0]+green_region[2],1])
        green_area_mean_v = np.mean(image_hsv[green_region[1]:green_region[1]+green_region[3],green_region[0]:green_region[0]+green_region[2],2])

        # print('awb gains:',str(float(camera.camera.awb_gains[0])),',',str(float(camera.camera.awb_gains[1])))
        # cv2.putText(image, 'awb gains:'+str(float(camera.camera.awb_gains[0]))+','+str(float(camera.camera.awb_gains[1])), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
        cv2.putText(image, 'red:'+str(int(red_area_mean_h))+"-"+str(int(red_area_mean_s))+"-"+str(int(red_area_mean_v)), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.putText(image, 'green:'+str(int(green_area_mean_h))+"-"+str(int(green_area_mean_s))+"-"+str(int(green_area_mean_v)), (10,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Original", image)
        if(count % 10 ==0):
            print("exposure_speed:", camera.camera.exposure_speed)
            with config_file_lock:
                with open('camera_config.json', 'r') as json_config_file:
                    config = json.load(json_config_file)
                config["shutter_speed"] = camera.camera.exposure_speed
                config["shutter_speed_shortened"] = int(camera.camera.exposure_speed*0.8)
                with open('camera_config.json', 'w') as json_config_file:
                    json.dump(config, json_config_file, indent=2)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break

def setup_trackbars():
    red, blue = get_trackbars_config()
    cv2.namedWindow(current_window_name)
    cv2.resizeWindow(current_window_name,640,120)
    cv2.createTrackbar("Red gain", current_window_name, int(red*10), 80, callback)
    cv2.createTrackbar("Blue gain", current_window_name, int(blue*10), 80, callback)

def get_trackbar_values():
    values = []
    values.append(float(cv2.getTrackbarPos("Red gain", current_window_name))/10.0)
    values.append(float(cv2.getTrackbarPos("Blue gain", current_window_name))/10.0)
    return values

def save_trackbar_values():
    trackbar_values = get_trackbar_values()
    with config_file_lock:
        with open('camera_config.json') as json_config_file:
            config = json.load(json_config_file)
        config["red_gain"] = trackbar_values[0]
        config["blue_gain"] = trackbar_values[1]
        with open('camera_config.json', 'w') as json_config_file:
            json.dump(config, json_config_file, indent=2)


def get_trackbars_config():
    with config_file_lock:
        with open('camera_config.json') as json_config_file:
            config = json.load(json_config_file)
    red = config["red_gain"]
    blue = config["blue_gain"]
    return red, blue

def callback(value):
    save_trackbar_values()
    adjust_camera()

def adjust_camera():
    values = get_trackbar_values()
    if is_raspberry:
        camera.camera.awb_mode = 'off'
        camera.camera.awb_gains=(values[0],values[1])


if __name__ == '__main__':
    main()
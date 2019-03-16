import os
import cv2
import time
import numpy as np
import json
from threading import Lock
is_raspberry = os.name != 'nt'

green_region = [500,100,40,40]
red_region = [100,100,40,40]
blue_region = [500,300,40,40]
yellow_region = [100,300,40,40]
gray_region = [300,220,40,40]
camera = None

camera_settings = {'resolution' : (640,480),
    'iso':800,
    'brightness': 55,
    'saturation':40,
    'framerate' : 30,
    'awb_mode' : 'off',
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
    with open('camera_config.json', 'r') as json_config_file:
        config = json.load(json_config_file)
    camera_settings['shutter_speed'] = config['shutter_speed']
    camera_settings['awb_gains'] = (config['red_gain'], config['blue_gain'])

    global camera
    camera = VideoStream(camera_settings=camera_settings)

    camera.start()
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
        cv2.rectangle(image,(blue_region[0],blue_region[1]),(blue_region[0]+blue_region[2],blue_region[1]+blue_region[3]), (255,0,0), 2, 2)
        cv2.rectangle(image,(yellow_region[0],yellow_region[1]),(yellow_region[0]+yellow_region[2],yellow_region[1]+yellow_region[3]), (0,255,255), 2, 2)
        cv2.rectangle(image,(gray_region[0],gray_region[1]),(gray_region[0]+gray_region[2],gray_region[1]+gray_region[3]), (255,0,255), 2, 2)
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        red_h = image_hsv[red_region[1]:red_region[1] + red_region[3], red_region[0]:red_region[0] + red_region[2], 0].copy()
        red_h[red_h<90] += 180
        red_area_mean_h = np.mean(red_h) % 180
        #red_area_mean_h= np.mean(image_hsv[red_region[1]:red_region[1] + red_region[3], red_region[0]:red_region[0] + red_region[2], 0])
        red_area_mean_s = np.mean(image_hsv[red_region[1]:red_region[1]+red_region[3],red_region[0]:red_region[0]+red_region[2],1])
        red_area_mean_v = np.mean(image_hsv[red_region[1]:red_region[1]+red_region[3],red_region[0]:red_region[0]+red_region[2],2])

        green_area_mean_h = np.mean(image_hsv[green_region[1]:green_region[1]+green_region[3],green_region[0]:green_region[0]+green_region[2],0])
        green_area_mean_s = np.mean(image_hsv[green_region[1]:green_region[1]+green_region[3],green_region[0]:green_region[0]+green_region[2],1])
        green_area_mean_v = np.mean(image_hsv[green_region[1]:green_region[1]+green_region[3],green_region[0]:green_region[0]+green_region[2],2])

        blue_area_mean_h = np.mean(image_hsv[blue_region[1]:blue_region[1]+blue_region[3],blue_region[0]:blue_region[0]+blue_region[2],0])
        blue_area_mean_s = np.mean(image_hsv[blue_region[1]:blue_region[1]+blue_region[3],blue_region[0]:blue_region[0]+blue_region[2],1])
        blue_area_mean_v = np.mean(image_hsv[blue_region[1]:blue_region[1]+blue_region[3],blue_region[0]:blue_region[0]+blue_region[2],2])

        yellow_area_mean_h = np.mean(image_hsv[yellow_region[1]:yellow_region[1]+yellow_region[3],yellow_region[0]:yellow_region[0]+yellow_region[2],0])
        yellow_area_mean_s = np.mean(image_hsv[yellow_region[1]:yellow_region[1]+yellow_region[3],yellow_region[0]:yellow_region[0]+yellow_region[2],1])
        yellow_area_mean_v = np.mean(image_hsv[yellow_region[1]:yellow_region[1]+yellow_region[3],yellow_region[0]:yellow_region[0]+yellow_region[2],2])

        gray_area_mean_b = np.mean(image[gray_region[1]:gray_region[1]+gray_region[3],gray_region[0]:gray_region[0]+gray_region[2],0])
        gray_area_mean_g = np.mean(image[gray_region[1]:gray_region[1]+gray_region[3],gray_region[0]:gray_region[0]+gray_region[2],1])
        gray_area_mean_r = np.mean(image[gray_region[1]:gray_region[1]+gray_region[3],gray_region[0]:gray_region[0]+gray_region[2],2])

        # cv2.putText(image, 'awb gains:'+str(float(camera.camera.awb_gains[0]))+','+str(float(camera.camera.awb_gains[1])), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
        cv2.putText(image, 'red:'+str(int(red_area_mean_h))+"-"+str(int(red_area_mean_s))+"-"+str(int(red_area_mean_v)), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.putText(image, 'green:'+str(int(green_area_mean_h))+"-"+str(int(green_area_mean_s))+"-"+str(int(green_area_mean_v)), (340,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(image, 'blue:'+str(int(blue_area_mean_h))+"-"+str(int(blue_area_mean_s))+"-"+str(int(blue_area_mean_v)), (340,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        cv2.putText(image, 'yellow:'+str(int(yellow_area_mean_h))+"-"+str(int(yellow_area_mean_s))+"-"+str(int(yellow_area_mean_v)), (10,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.putText(image, 'gray:'+str(int(gray_area_mean_r))+"-"+str(int(gray_area_mean_g))+"-"+str(int(gray_area_mean_b)), (200,350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)
        cv2.imshow("Original", image)
        if(count % 5 ==0):
            if is_raspberry:
                print('awb gains:', str(float(camera.camera.awb_gains[0])), ',', str(float(camera.camera.awb_gains[1])))
                print("exposure_speed:", camera.camera.exposure_speed)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break



if __name__ == '__main__':
    main()
import cv2
import time
import json
from videoutils.video_stream_webcam import VideoStream

use_webcam = True
current_filter_id = 0
current_window_name = ""


def callback(value):
    save_trackbar_values()

def callback_filter(value):
    setup_trackbars(value)

def setup_trackbars(filter_id = 0):
    global current_filter_id, current_window_name
    filter_name, h_min, h_max, s_min, s_max, v_min, v_max = get_trackbars_config(filter_id)
    cv2.destroyWindow(current_window_name)
    current_filter_id = filter_id
    current_window_name = "Trackbars "+filter_name
    cv2.namedWindow(current_window_name)
    cv2.resizeWindow(current_window_name,640,400)
    cv2.createTrackbar("Filter", current_window_name, filter_id, 5, callback_filter)
    cv2.createTrackbar("H MIN", current_window_name, h_min, 255, callback)
    cv2.createTrackbar("H MAX", current_window_name, h_max, 255, callback)
    cv2.createTrackbar("S MIN", current_window_name, s_min, 255, callback)
    cv2.createTrackbar("S MAX", current_window_name, s_max, 255, callback)
    cv2.createTrackbar("V MIN", current_window_name, v_min, 255, callback)
    cv2.createTrackbar("V MAX", current_window_name, v_max, 255, callback)

def get_trackbars_config(filter_id):
    with open('colour_config.json') as json_config_file:
        config = json.load(json_config_file)
    if filter_id==0:
        name = "Alien Green"
        min = config["alien_hsv_ranges"]["green_min"]
        max = config["alien_hsv_ranges"]["green_max"]
    elif filter_id==1:
        name = "Alien Background"
        min = config["alien_hsv_ranges"]["background_min"]
        max = config["alien_hsv_ranges"]["background_max"]
    elif filter_id==2:
        name = "Sheet Green"
        min = config["colour_sheets_hsv_ranges"]["green_min"]
        max = config["colour_sheets_hsv_ranges"]["green_max"]
    elif filter_id==3:
        name = "Sheet Blue"
        min = config["colour_sheets_hsv_ranges"]["blue_min"]
        max = config["colour_sheets_hsv_ranges"]["blue_max"]
    elif filter_id==4:
        name = "Sheet Red"
        min = config["colour_sheets_hsv_ranges"]["red_min"]
        max = config["colour_sheets_hsv_ranges"]["red_max"]
    elif filter_id==5:
        name = "Sheet Yellow"
        min = config["colour_sheets_hsv_ranges"]["yellow_min"]
        max = config["colour_sheets_hsv_ranges"]["yellow_max"]
    return name, min[0], max[0], min[1], max[1], min[2], max[2]



def get_trackbar_values():
    values = []
    values.append(cv2.getTrackbarPos("H MIN", current_window_name))
    values.append(cv2.getTrackbarPos("H MAX", current_window_name))
    values.append(cv2.getTrackbarPos("S MIN", current_window_name))
    values.append(cv2.getTrackbarPos("S MAX", current_window_name))
    values.append(cv2.getTrackbarPos("V MIN", current_window_name))
    values.append(cv2.getTrackbarPos("V MAX", current_window_name))
    return values

def save_trackbar_values():
    global current_filter_id
    trackbar_values = get_trackbar_values()
    with open('colour_config.json') as json_config_file:
        config = json.load(json_config_file)
    if current_filter_id==0:
        config["alien_hsv_ranges"]["green_min"] = [trackbar_values[0], trackbar_values[2], trackbar_values[4]]
        config["alien_hsv_ranges"]["green_max"] = [trackbar_values[1], trackbar_values[3], trackbar_values[5]]
    elif current_filter_id==1:
        config["alien_hsv_ranges"]["background_min"] = [trackbar_values[0], trackbar_values[2], trackbar_values[4]]
        config["alien_hsv_ranges"]["background_max"] = [trackbar_values[1], trackbar_values[3], trackbar_values[5]]
    elif current_filter_id==2:
        config["colour_sheets_hsv_ranges"]["green_min"] = [trackbar_values[0], trackbar_values[2], trackbar_values[4]]
        config["colour_sheets_hsv_ranges"]["green_max"] = [trackbar_values[1], trackbar_values[3], trackbar_values[5]]
    elif current_filter_id==3:
        config["colour_sheets_hsv_ranges"]["blue_min"] = [trackbar_values[0], trackbar_values[2], trackbar_values[4]]
        config["colour_sheets_hsv_ranges"]["blue_max"] = [trackbar_values[1], trackbar_values[3], trackbar_values[5]]
    elif current_filter_id==4:
        config["colour_sheets_hsv_ranges"]["red_min"] = [trackbar_values[0], trackbar_values[2], trackbar_values[4]]
        config["colour_sheets_hsv_ranges"]["red_max"] = [trackbar_values[1], trackbar_values[3], trackbar_values[5]]
    elif current_filter_id==5:
        config["colour_sheets_hsv_ranges"]["yellow_min"] = [trackbar_values[0], trackbar_values[2], trackbar_values[4]]
        config["colour_sheets_hsv_ranges"]["yellow_max"] = [trackbar_values[1], trackbar_values[3], trackbar_values[5]]
    with open('colour_config.json', 'w') as json_config_file:
        json.dump(config, json_config_file, indent=2)


def main():
    global use_webcam, try_alien_detection, try_sheet_detection
    if use_webcam:
        camera = VideoStream(resolution=(640,480), framerate=20)
        camera.start()

    setup_trackbars()
    count = 0
    while True:
        image=None
        if use_webcam:
            image = camera.read()
            isBgr = True
            #image = adjust_gamma(image)
            #image = normalise_colours(image, False)
            #alien_detector.detect_aliens(image, True)
        else:

            res = cv2.waitKey(20) & 0xFF
            if res == 32:
                print(count)
                count = (count + 1) % 17
            #image = cv2.imread("alienpi\\alien_template.png")
            #image = cv2.imread("alienpi\\frame"+str(count)+".jpg")
            image = cv2.imread("alienpi\\frame18.jpg")
            isBgr = False
            time.sleep(0.1)

        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV if isBgr else cv2.COLOR_RGB2HSV)

        h_min, h_max, s_min, s_max, v_min, v_max = get_trackbar_values()

        if(h_min>h_max):
            mask1 = cv2.inRange(image_hsv, (0, s_min, v_min), (h_max, s_max, v_max))
            mask2 = cv2.inRange(image_hsv, (h_min, s_min, v_min), (180, s_max, v_max))
            mask = mask1+mask2
        else:
            mask = cv2.inRange(image_hsv, (h_min, s_min, v_min), (h_max, s_max, v_max))

        preview = cv2.bitwise_and(image, image, mask=mask)
        cv2.imshow("Preview", preview)
        cv2.imshow("Original", image)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break


if __name__ == '__main__':
    main()
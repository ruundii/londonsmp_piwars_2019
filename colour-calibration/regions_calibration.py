import cv2
import time
import json
import numpy as np

resolution = (640,480)
framerate = 20
use_webcam = True
is_raspberry = True
current_window_name = ""

CHALLENGE_SPEED_LINE = 0
CHALLENGE_LABYRINTH = 1
CHALLENGE_COLOURED_SHEETS = 2

current_challenge_id = CHALLENGE_SPEED_LINE

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


def callback(value):
    save_trackbar_values()

def setup_trackbars():
    global current_window_name
    challenge_name, top, bottom, left, right, cross_line_1, cross_line_2, cross_line_3 = get_trackbars_config(current_challenge_id)
    current_window_name = challenge_name
    cv2.namedWindow(current_window_name)
    cv2.resizeWindow(current_window_name,640,400)
    cv2.createTrackbar("Top", current_window_name, top, resolution[0], callback)
    cv2.createTrackbar("Bottom", current_window_name, bottom, resolution[0], callback)
    cv2.createTrackbar("Left", current_window_name, left, resolution[1], callback)
    cv2.createTrackbar("Right", current_window_name, right, resolution[1], callback)
    if(current_challenge_id==CHALLENGE_SPEED_LINE):
        cv2.createTrackbar("CrossLine1", current_window_name, cross_line_1, resolution[1], callback)
        cv2.createTrackbar("CrossLine2", current_window_name, cross_line_2, resolution[1], callback)
        cv2.createTrackbar("CrossLine3", current_window_name, cross_line_3, resolution[1], callback)

def get_trackbars_config(challenge_id):
    with open('regions_config.json') as json_config_file:
        config = json.load(json_config_file)
    if challenge_id==CHALLENGE_SPEED_LINE:
        name = "Speed Line"
        config = config["speed_line"]
    elif challenge_id==CHALLENGE_LABYRINTH:
        name = "Labyrinth"
        config = config["labyrinth"]
    elif challenge_id==CHALLENGE_COLOURED_SHEETS:
        name = "Colour Corners"
        config = config["colour_sheets"]
    if(challenge_id!=CHALLENGE_SPEED_LINE):
        return name, config["top"],config["bottom"],config["left"],config["right"], None, None, None
    else:
        return name, config["top"], config["bottom"], config["left"], config["right"], config["cross_line_1"], config["cross_line_2"], config["cross_line_3"]



def get_trackbar_values():
    global current_window_name
    values = []
    values.append(cv2.getTrackbarPos("Top", current_window_name))
    values.append(cv2.getTrackbarPos("Bottom", current_window_name))
    values.append(cv2.getTrackbarPos("Left", current_window_name))
    values.append(cv2.getTrackbarPos("Right", current_window_name))
    if(current_challenge_id==CHALLENGE_SPEED_LINE):
        values.append(cv2.getTrackbarPos("CrossLine1", current_window_name))
        values.append(cv2.getTrackbarPos("CrossLine2", current_window_name))
        values.append(cv2.getTrackbarPos("CrossLine3", current_window_name))
    return values

def save_trackbar_values():
    global current_challenge_id
    trackbar_values = get_trackbar_values()
    with open('regions_config.json') as json_config_file:
        config = json.load(json_config_file)
    if current_challenge_id==CHALLENGE_SPEED_LINE:
        config_challenge_section = config["speed_line"]
    elif current_challenge_id==CHALLENGE_LABYRINTH:
        config_challenge_section = config["labyrinth"]
    else:
        config_challenge_section = config["colour_sheets"]
    config_challenge_section["top"]=trackbar_values[0]
    config_challenge_section["bottom"] = trackbar_values[1]
    config_challenge_section["left"] = trackbar_values[2]
    config_challenge_section["right"] = trackbar_values[3]
    if current_challenge_id==CHALLENGE_SPEED_LINE:
        config_challenge_section["cross_line_1"] = trackbar_values[4]
        config_challenge_section["cross_line_2"] = trackbar_values[5]
        config_challenge_section["cross_line_3"] = trackbar_values[6]
    with open('regions_config.json', 'w') as json_config_file:
        json.dump(config, json_config_file, indent=2)


def main():
    global use_webcam, resolution, framerate
    if use_webcam:
        camera = VideoStream(resolution=resolution, framerate=framerate)
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
        if image is None:
            time.sleep(0.1)
            continue

        challenge_name, top, bottom, left, right, cross_line_1, cross_line_2, cross_line_3 = get_trackbars_config(
            current_challenge_id)
        cv2.rectangle(image, (left, top),(len(image[0])-right, len(image)-bottom), (0,255,0), 2)
        if cross_line_1 is not None and cross_line_2 is not None and cross_line_3 is not None:
            cv2.line(image, (0, len(image) - cross_line_1-bottom), (len(image[0]), len(image) - cross_line_1-bottom), (255,0,0), 1)
            cv2.line(image, (0, len(image) - cross_line_2-bottom), (len(image[0]), len(image) - cross_line_2-bottom), (255,0,0), 1)
            cv2.line(image, (0, len(image) - cross_line_3-bottom), (len(image[0]), len(image) - cross_line_3-bottom), (255,0,0), 1)
        cv2.imshow("Preview", image)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            break


if __name__ == '__main__':
    main()
import cv2
import numpy as np
from matplotlib import pyplot as plt

green_lower_bound_hsv = (40,105,20)
green_higher_bound_hsv = (90,255,255)
#green_lower_bound_hsv = (40,60,80)
#green_higher_bound_hsv = (85,255,255)
background_lower_bound_hsv = (0,0,90)
background_higher_bound_hsv = (255,165,255)
green = (0,125,255)

camera = cv2.VideoCapture(0)
camera.set(3, 640)
camera.set(4,480)
#https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
#https://github.com/llSourcell/Object_Detection_demo_LIVE/blob/master/demo.py
#https://pythonprogramming.net/morphological-transformation-python-opencv-tutorial/

def get_alien_contours(image_hsv):
    #frame = imutils.resize(frame, width=600)
    #image_hsv = cv2.medianBlur(image_hsv, 15)
    #image_hsv = cv2.GaussianBlur(image_hsv, (11, 11), 0)
    mask = cv2.inRange(image_hsv, green_lower_bound_hsv, green_higher_bound_hsv)
    #mask = cv2.erode(mask, None, iterations=2)
    #mask = cv2.dilate(mask, None, iterations=2)
    cv2.imwrite("test\\alien_mask_original.jpg", mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cv2.imwrite("test\\alien_mask.jpg", mask)
    # if len(image_hsv)>=480:
    #     cv2.imshow("Mask", mask)

    _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_TC89_L1)
    im3 = cv2.drawContours(image_hsv.copy(), contours, -1, 255, -1)
    if len(image_hsv)>=480:
        cv2.imshow("Contours", im3)
    #preview = cv2.bitwise_and(image_hsv, image_hsv, mask=mask)
    #cv2.imshow("Preview", preview)
    return contours, mask

def __get_template_contour(image_name):
    alien_template = cv2.imread(image_name)
    alien_template_hsv = cv2.cvtColor(alien_template, cv2.COLOR_RGB2HSV)
    alien_template_contours, _ = get_alien_contours(alien_template_hsv)
    return alien_template_contours[0]

def do_surf(image):
    surf = cv2.xfeatures2d.SURF_create(200)
    # find the keypoints with ORB
    kp, des = surf.detectAndCompute(image, None)

    # draw only keypoints location,not size and orientation
    img2 = cv2.drawKeypoints(image, kp, None, color=(0, 255, 0), flags=0)
    plt.imshow(img2), plt.show()


alien_template_with_contour = __get_template_contour("alienpi\\alien_template.png")

def is_alien_contour(contour, image_hsv, image):
    try:
        ellipse = cv2.fitEllipse(contour)
    except:
        print('killing by ellipse constr')
        return False
    ellipseRatio = ellipse[1][1] / ellipse[1][0]

    r = cv2.boundingRect(contour)
    extended_rectange = image_hsv[r[1]:r[1]+r[3],r[0]:r[0]+r[2]]
    cv2.imwrite("test\\test_contour.jpg", extended_rectange)

    #check ellipse radius ratio and hieght
    if ellipseRatio < 1.1 or ellipseRatio > 3 or ellipse[1][1] < 3:
        print('killing by ellipse', ellipse)
        return False

    #check area
    area = cv2.contourArea(contour)
    if area < 15:
        print('killing by area', ellipse)
        return False

    #compare shapes
    likelihood = cv2.matchShapes(contour, alien_template_with_contour, 1, 0)
    if likelihood > 0.5:
        print('killing by shape', ellipse)
        return False

    #check background
    r = cv2.boundingRect(contour)
    y_border = max(int(r[3]/2),15)
    x_border = max(int(r[2] / 2), 15)
    y1 = max(int(r[1])-y_border,0)
    y2 = min(int(r[1]+r[3]) + y_border, 480)
    x1 = max(int(r[0]) - x_border,0)
    x2 = min(int(r[0]+r[2]) + x_border, 640)
    extended_rectange = image_hsv[y1:y2,x1:x2].copy()
    cv2.imwrite("test\\image.jpg", cv2.cvtColor(image_hsv, cv2.COLOR_HSV2RGB))
    cv2.imwrite("test\\extended_rectange.jpg", extended_rectange)
    extended_rectange_orig = image[y1:y2, x1:x2]
    #do_surf(image)
    contours, mask = get_alien_contours(extended_rectange)
    black_img = np.zeros([y2-y1, x2-x1, 1], dtype=np.uint8)
    drawn_contour = cv2.drawContours(black_img, contours, -1, 255, -1)
    cv2.imwrite("test\\drawn_contour.jpg", drawn_contour)
    kernel = np.ones((7, 7), np.uint8)
    drawn_contour_dilated = cv2.dilate(drawn_contour, kernel, iterations=1)
    cv2.imwrite("test\\drawn_contour_dilated.jpg", drawn_contour_dilated)

    background = cv2.bitwise_and(extended_rectange, extended_rectange, mask=cv2.bitwise_not(mask))
    cv2.imwrite("test\\background.jpg", background)
    matching_background = cv2.inRange(background, background_lower_bound_hsv, background_higher_bound_hsv)
    cv2.imwrite("test\\matching_background.jpg", matching_background)
    #matching_background_plus_mask = cv2.drawContours(matching_background, contours, -1, 255, -1)
    matching_background_plus_mask = cv2. bitwise_or(matching_background,drawn_contour_dilated)
    cv2.imwrite("test\\Crop_mask.jpg", matching_background_plus_mask)
    mean = cv2.mean(matching_background_plus_mask)
    if(mean[0]<230):
        print('killing by background', ellipse, mean)
        return False

    #print('likelihood: ', likelihood, ' area:', area, ' height:', ellipse[1][1], ' ellipse ratio:', ellipseRatio, ' mean:',mean[0])
    return True

def detect_aliens(image, is_rgb):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV if is_rgb else cv2.COLOR_BGR2HSV)
    contours, _ = get_alien_contours(image_hsv)
    real_contours_num =0
    for contour in contours:
        if not is_alien_contour(contour, image_hsv, image):
            continue
        ellipse = cv2.fitEllipse(contour)
        image= cv2.ellipse(image, ellipse, green, 2)
        real_contours_num = real_contours_num+1

    print(real_contours_num,":",len(contours))



# while True:
#     ret, image = camera.read()
#     detect_aliens(image, False)
#     if cv2.waitKey(1) & 0xFF is ord('q'):
#         break

#trik - piwars robot
joystick_left_axis = 1
joystick_right_axis = 4

alien_distance_multiplier = 1.0/1.7
alien_distance_offset = 0

motor_module = "processors.motor_xy160d"

green_lower_bound_hsv = (40,95,20)
green_higher_bound_hsv = (90,255,255)

background_lower_bound_hsv = (0,0,90)
background_higher_bound_hsv = (255,255,255)

alien_template = "videoutils/alien_template.png"
camera_calibrations_path = "videoutils/calibrations"
video_stream_module = "videoutils.video_stream_pi"
is_rgb_not_bgr=True
camera_id = "pi640"
resolution = (640, 480)
camera_pov = (120, 100)
framerate = 20

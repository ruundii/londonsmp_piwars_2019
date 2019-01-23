#windows, surface book
green_lower_bound_hsv = (30,105,20)
green_higher_bound_hsv = (80,255,255)

background_lower_bound_hsv = (0,0,150)
background_higher_bound_hsv = (255,165,255)

joystick_left_axis = 1
joystick_right_axis = 3

alien_distance_multiplier = 1.0/2.65
alien_distance_offset = 0.06

motor_module = "processors.motor_stub"

alien_template = "videoutils\\alien_template.png"
camera_calibrations_path = "videoutils\calibrations"
video_stream_module = "videoutils.video_stream_webcam"
camera_id = "surface"
is_rgb_not_bgr=False
resolution = (640, 480)
camera_pov = (120, 100)
framerate = 20

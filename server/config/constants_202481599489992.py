#makeblock
joystick_left_axis = 1
joystick_right_axis = 4

alien_distance_multiplier = 1.0/2.2
alien_distance_offset = 0.1

coloured_sheet_distance_multiplier = 1.0/2.2
coloured_sheet_distance_offset = 0.1

motor_module = "processors.motor_ifx9201sg"

colour_config_name = "config/colour_config_pi.json"
regions_config_name = "config/regions_config_pi.json"

alien_template = "videoutils/alien_template.png"
camera_calibrations_path = "videoutils/calibrations"
video_stream_module = "videoutils.video_stream_pi"

camera_id = "pi640"
is_rgb_not_bgr=True
resolution_aliens = (640,480)
resolution_coloured_sheet = (320, 240)
camera_fov = (120, 100)
framerate = 20

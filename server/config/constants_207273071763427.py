#windows, surface book
joystick_left_axis = 1
joystick_right_axis = 3

alien_distance_multiplier = 1.0/2.65
alien_distance_offset = 0.06

coloured_sheet_distance_multiplier = 1.0/2.65
coloured_sheet_distance_offset = 0.06

motor_module = "processors.motor_stub"

colour_config_name = "config\\colour_config_win.json"
regions_config_name = "config\\regions_config_win.json"

alien_template = "videoutils\\alien_template.png"
camera_calibrations_path = "videoutils\calibrations"
video_stream_module = "videoutils.video_stream_webcam"

camera_id = "surface"
is_rgb_not_bgr=False
camera_settings_aliens = {
    'resolution' : (640,480),
    'framerate' : 30
}
camera_settings_coloured_sheet = {
    'resolution': (640, 480),
    'framerate': 30
}
camera_settings_speed_track = {
    'resolution': (640, 480),
    'framerate': 40
}
camera_fov = (60, 50)
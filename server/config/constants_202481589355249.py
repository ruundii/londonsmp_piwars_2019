#trik - piwars robot
joystick_left_axis = 1
joystick_right_axis = 4

alien_distance_multiplier = 1.0/4.4
alien_distance_offset = 0.05

coloured_sheet_distance_multiplier = 1.0/2.2
coloured_sheet_distance_offset = 0.1

motor_module = "processors.motor_xy160d"

colour_config_name = "config/colour_config_pi.json"
regions_config_name = "config/regions_config_pi.json"
camera_config_name = "config/camera_config.json"

video_log_folder_path = "video_files/"

alien_template = "videoutils/alien_template.png"
camera_calibrations_path = "videoutils/calibrations"
video_stream_module = "videoutils.video_stream_pi"

camera_id = "pi640"
camera_flip = False
is_rgb_not_bgr=True
camera_settings_aliens = {
    'resolution' : (1280,720),
    'resolution_resized' : (320,180),
    'iso':800,
    'awb_mode':'off',
    'brightness': 55,
    'saturation':40,
    'framerate' : 10,
}
camera_settings_coloured_sheet = {
    'resolution' : (320,240),
    'iso':800,
    'awb_mode':'off',
    'brightness': 55,
    'saturation':40,
    'framerate': 30
}
camera_settings_speed_track = {
    'resolution' : (320,240),
    'iso':800,
    'awb_mode':'off',
    'brightness': 75,
    'contrast': 50,
    'saturation':40,
    'framerate': 40,
    'video_denoise':False,
    'shutter_speed_setting':'shutter_speed_shortened'
}
camera_fov = (60, 50)
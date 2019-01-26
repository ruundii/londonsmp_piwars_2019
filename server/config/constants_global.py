alien_image_height_mm = 77
coloured_sheet_height_mm = 200#260

image_processing_tracing_show_original = True
image_processing_tracing_show_region_of_interest = True
image_processing_tracing_show_colour_mask = True
image_processing_tracing_show_background_colour_mask = True
image_processing_tracing_show_detected_objects = True

performance_tracing_robot_camera_detect_aliens = True
performance_tracing_robot_camera_detect_coloured_sheets = True

#importing machine-specific constants
import importlib
from uuid import getnode as get_mac
print('loading ',"config.constants_"+str(get_mac()))
constants_specific = importlib.import_module("config.constants_"+str(get_mac()))

module_dict = constants_specific.__dict__
try:
    to_import = constants_specific.__all__
except AttributeError:
    to_import = [name for name in module_dict if not name.startswith('_')]
globals().update({name: module_dict[name] for name in to_import})


alien_image_height_mm = 77

image_processing_tracing_show_original = True
image_processing_tracing_show_colour_mask = True
image_processing_tracing_show_backgroud_colour_mask = True
image_processing_tracing_show_detected_objects = True

performance_tracing_robot_camera_detect_aliens = True

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


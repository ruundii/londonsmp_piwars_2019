from _thread import start_new_thread
import time
import cv2

class ImageDisplay:
    def __init__(self):
        self.image_display_queue = []
        self.show_images = True
        self.destroy_trigger = False
        start_new_thread(self.__image_display_loop,())

    def set_mode(self, show_images):
        self.show_images = show_images


    def add_image_to_queue(self, window_name, image):
        if(not self.show_images): return
        self.image_display_queue.append((image, window_name))

    def destroy_windows(self):
        self.destroy_trigger = True

    def __image_display_loop(self):
        while True:
            while(len(self.image_display_queue)>0):
                (image, window_name) = self.image_display_queue.pop()
                if image is None:
                    continue
                cv2.imshow(window_name, image)
                cv2.waitKey(1)
            if(self.destroy_trigger):
                if (not self.show_images): return
                self.image_display_queue.clear()
                time.sleep(0.01)
                self.image_display_queue.clear()
                cv2.destroyAllWindows()
                self.destroy_trigger = False

            time.sleep(0.01)

image_display = ImageDisplay()

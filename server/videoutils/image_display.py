from _thread import start_new_thread
import time
import cv2
import queue

class ImageDisplay:
    def __init__(self):
        self.image_display_queue = queue.Queue()
        self.show_images = True
        self.destroy_trigger = False
        start_new_thread(self.__image_display_loop,())

    def set_mode(self, show_images):
        self.show_images = show_images


    def add_image_to_queue(self, window_name, image):
        if(not self.show_images): return
        self.image_display_queue.put((image, window_name, time.time()))

    def destroy_windows(self):
        self.destroy_trigger = True

    def __image_display_loop(self):
        while True:
            if(self.image_display_queue.empty()):
                time.sleep(0.01)
            (image, window_name, t) = self.image_display_queue.get()
            if (time.time()-t)>0.1: continue
            if image is None:
                continue
            cv2.imshow(window_name, image)
            cv2.waitKey(1)
            if(self.destroy_trigger):
                if (not self.show_images): return
                while(not self.image_display_queue.empty()):
                    _,_ = self.image_display_queue.get()
                cv2.destroyAllWindows()
                self.destroy_trigger = False

image_display = ImageDisplay()

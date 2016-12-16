import cv2
import threading
from main import *
from logger import  create_rotating_log
from camera import Camera
import tornado.httpclient
import tornado.web
import tornado.ioloop
from tornado import gen
import time

class StreamHandler(tornado.web.RequestHandler):
    # def __init__(self, application, request, **kwargs):
    #     super(StreamHandler, self).__init__(application, request, **kwargs)
    #     self.headers = {
    #         "Content-Type": "application/json",
    #         "Accept": "application/json",
    #         "Media-Type": "application/json"
    #     }
    #     tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    #     self.http_client = tornado.httpclient.AsyncHTTPClient(max_clients=50)
    #
    # def set_default_headers(self):
    #     self.set_header("Access-Control-Allow-Origin", "*")
    #     self.set_header("Access-Control-Allow-Headers", "x-requested-with, Authorization")
    #     self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
    #
    # def stream(self):
    #     cameras = config_everything_and_get_cameras("config/config.yml", [1, 2], test=False)
    #     for camera in cameras:
    #         camera.configure_streaming()
    #     frame_list = [camera.get_frame() for camera in cameras]  # Fills an array with "None" values
    #     LOGGER.info("Starting the program. Cameras count: %s" % str(len(cameras)))
    #     while True:
    #         for index, camera in enumerate(cameras):
    #             camera.single_capture(test=False)
    #             if camera.get_frame() is not None:
    #                 frame_list[index] = camera.get_frame()
    #             else:
    #                 frame_list[index] = cv2.imread('img/loading.jpg')
    #         cv2.imwrite('t.jpg', get_image_stack(frame_list))
    #         cv2.waitKey(15)
    #         yield (b'--frame\r\n'
    #                b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


    @gen.coroutine
    @tornado.web.asynchronous
    def get(self):
        ioloop = tornado.ioloop.IOLoop.current()
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Connection', 'close')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=--boundarydonotcross')
        self.set_header('Pragma', 'no-cache')
        self.served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross\n"

        cameras = config_everything_and_get_cameras("config/config.yml", [1, 2], test=False)
        print str(len(cameras))
        for camera in cameras:
            camera.configure_streaming()
        frame_list = [camera.get_frame() for camera in cameras]  # Fills an array with "None" values

        while True:
            for index, camera in enumerate(cameras):
                camera.single_capture(test=False)
                if camera.get_frame() is not None:
                    frame_list[index] = camera.get_frame()
                else:
                    frame_list[index] = cv2.imread('img/loading.jpg')
            cv2.imwrite('t.jpg', get_image_stack(frame_list))
            cv2.waitKey(15)
            with open("t.jpg") as f:
                img = f.read()
            interval = 1.0
            if self.served_image_timestamp + interval < time.time():
                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(str(img))
                self.served_image_timestamp = time.time()
                import pdb; pdb.set_trace()
                yield gen.Task(self.flush)
            else:
                yield gen.Task(ioloop.add_timeout, ioloop.time() + interval)



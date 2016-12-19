from flask import Flask, render_template, Response
import cv2
import threading
from main import *
from logger import  create_rotating_log
from camera import Camera
import base64
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()
application = Flask(__name__)

@application.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    LOGGER.info("Starting the program. Cameras count: %s" % str(len(cameras)))
    while True:
        gevent.sleep(0.001)
        for index, camera in enumerate(cameras):
            camera.single_capture(test=False)
            if camera.get_frame() is not None:
                frame_list[index] = camera.get_frame()
            else:
                frame_list[index] = cv2.imread('img/loading.jpg')
        cv2.imwrite('t.jpg', get_image_stack(frame_list))
        cv2.waitKey(15)
        yield ('data: ' + base64.b64encode(open('t.jpg', 'rb').read()) + '\n\n')


@application.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='text/event-stream')

if __name__ == '__main__':
    global cameras
    cameras = config_everything_and_get_cameras("config/config.yml", [1,2], test=False)
    for camera in cameras:
        camera.configure_streaming()
    frame_list = [camera.get_frame() for camera in cameras]  # Fills an array with "None" values
    http_server = WSGIServer(('127.0.0.1', 8001), application.wsgi_app)
    http_server.serve_forever()

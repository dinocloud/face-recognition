from flask import Flask, render_template, Response
import cv2
import threading
from main import *
from logger import  create_rotating_log
from camera import Camera

application = Flask(__name__)

@application.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    cameras = config_everything_and_get_cameras("config/config.yml", [1,2], test=False)
    for camera in cameras:
        camera.configure_streaming()
    frame_list = [camera.get_frame() for camera in cameras]  # Fills an array with "None" values
    LOGGER.info("Starting the program. Cameras count: %s" % str(len(cameras)))
    while True:
        for index, camera in enumerate(cameras):
            camera.single_capture(test=False)
            if camera.get_frame() is not None:
                frame_list[index] = camera.get_frame().tobytes()
            else:
                frame_list[index] = cv2.imread('img/loading.jpg')
        cv2.imwrite('t.jpg', get_image_stack(frame_list))
        cv2.waitKey(15)
        yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@application.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    application.logger.addHandler(create_rotating_log('/var/log/count.log', 'info'))
    application.run(host='0.0.0.0', debug=True, threaded=True)

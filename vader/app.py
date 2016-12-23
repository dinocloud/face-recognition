from flask import Flask, render_template, Response
import cv2
import argparse
from controller import *
from logger import  create_rotating_log
from camera import Camera
import base64
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()
application = Flask(__name__)
cameras = []
frame_list =  []


@application.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    LOGGER.info("Starting the program. Cameras count: %s" % str(len(cameras)))
    while True:
        gevent.sleep(0.01)
        for index, camera in enumerate(cameras):
            camera.single_capture(test=False)
            if camera.get_frame() is not None:
                frame_list[index] = camera.get_frame()
            else:
                frame_list[index] = cv2.imread('img/loading.jpg')
        #cv2.imwrite('t.jpg', get_image_stack(frame_list))
        #cv2.waitKey(15)
        yield ('data: ' + base64.b64encode(cv2.imencode('.jpg',get_image_stack(frame_list))[1]) + '\n\n')


@application.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='text/event-stream')


def setup():
    parser = argparse.ArgumentParser(description='Application arguments')
    parser.add_argument('--tenant', required=True, type=int, help='The id of the tenant to be executed')
    parser.add_argument('--key', required=True, help='The token/key to authenticate to the tenant')
    args = parser.parse_args()
    tenant = args.tenant
    if not validate_tenant(tenant, args.key):
        print 'Tenant and key not valid. Exiting...'
        sys.exit(1)
    global cameras
    cameras = config_everything_and_get_cameras(tenant, test=False)
    for camera in cameras:
        camera.configure_streaming()
    global frame_list
    frame_list = [camera.get_frame() for camera in cameras]  # Fills an array with "None" values


def main(args):
    setup()
    http_server = WSGIServer(('', 8001), application.wsgi_app)
    http_server.serve_forever()


if __name__ == '__main__':
    main(sys.argv)


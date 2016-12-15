import sys

import cv2
import numpy as np
import yaml

from camera import Camera
from database import configure_database_connection
from logger import create_rotating_log


LOGGER = create_rotating_log('/var/log/count.log', 'info')

def get_configuration_from_file(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.load(file)
    return config


def config_database(config):
    LOGGER.info("Trying to configure database")
    db_config = config.get("database")
    LOGGER.debug("Database data. Engine: {engine}. Server: {server}. User: {username}. Password: {password}."
                " Database: {database}".format(engine=db_config.get("engine"), server=db_config.get("server"),
                                                username=db_config.get("username"), password=db_config.get("password"),
                                                database=db_config.get("database")))
    configure_database_connection(db_config.get("engine"), db_config.get("server"), db_config.get("username"),
                                  db_config.get("password"), db_config.get("database"))
    LOGGER.info("Database configured successfully")


def config_logging(config):
    log_config = config.get("logging")
    LOGGER = create_rotating_log(log_config.get("path"), log_config.get("level"))
    LOGGER.debug("Logging configured successfully")


def config_cameras(config, id_cameras):
    cameras = []
    for camera in config.get("cameras", {}):
        id = camera.get("id", 0)
        LOGGER.info("Trying to configure camera: {id}".format(id=str(id)))
        if id not in id_cameras:
            break
        in_area_points = []
        out_area_points = []
        critical_area_points = []
        for in_points in camera.get("in_area", {}):
            in_area_points.append([int(in_points.split(';')[0]), int(in_points.split(';')[1])])
        for out_points in camera.get("out_area", {}):
            out_area_points.append([int(out_points.split(';')[0]), int(out_points.split(';')[1])])
        for crit_points in camera.get("critical_area", {}):
            critical_area_points.append([int(crit_points.split(';')[0]), int(crit_points.split(';')[1])])
        source = camera.get("source", 0)
        description = camera.get("description", "No description")
        max_person_age = camera.get("max_person_age", 5)
        detection_area = camera.get("detection_area", 300)
        LOGGER.debug("Camera {id} data - source: {source} - description: {description} "
                     "- max_person_age: {max_person_age} - detection_area: {detection_area}"
                     .format(id=id, source=source, description=description, max_person_age=max_person_age,
                             detection_area=detection_area))
        cam = Camera(id, source, description, in_area_points, out_area_points, critical_area_points, 0, 0,
                     max_person_age, detection_area)
        cameras.append(cam)
        LOGGER.info("Camera {id} configured successfully !!! ".format(id=str(id)))
    LOGGER.info("All the cameras were successfully configurated")
    return cameras


def config_everything_and_get_cameras(yaml_file, id_cameras, test=False):
    config = get_configuration_from_file(yaml_file)
    # config_logging(config)
    if not test:
        config_database(config)
    cameras = config_cameras(config, id_cameras)
    return cameras


def get_image_stack(frame_list):
    image_stack = frame_list[0]
    stack_tmp = ""
    if len(frame_list) > 1:
        for i in range(1, len(frame_list)):
            if i % 2 == 0:
                if i == len(frame_list) - 1:
                    image_stack = np.concatenate((image_stack, frame_list[i]), axis=0)
                else:
                    stack_tmp = frame_list[i]
            else:
                if i == 1:
                    image_stack = np.concatenate((image_stack, frame_list[i]), axis=1)
                else:
                    stack_tmp = np.concatenate((stack_tmp, frame_list[i]), axis=1)
                    image_stack = np.concatenate((image_stack, stack_tmp), axis=0)
    return image_stack


def start_processing(file, id_cameras=list()):
    cameras = config_everything_and_get_cameras(file, id_cameras)

    for camera in cameras:
        camera.configure_streaming()

    cv2.namedWindow("MySoftware", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

    frame_list = [camera.get_frame() for camera in cameras] #Fills an array with "None" values
    LOGGER.info("Starting the program. Cameras count: %s" % str(len(cameras)))
    while True:
        for index, camera in enumerate(cameras):
            camera.single_capture()
            if camera.get_frame() is not None:
                frame_list[index] = camera.get_frame()
            else:
                frame_list[index] = cv2.imread('img/loading.jpg')
        cv2.imshow("MySoftware", get_image_stack(frame_list))
        k = cv2.waitKey(15) & 0xff
        if k == 27:
            break
    cv2.destroyAllWindows()  # close all openCV windows
    sys.exit(0)

if __name__ == "__main__":
    start_processing("config/config.yml", [1,2])
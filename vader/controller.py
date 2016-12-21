import sys
import cv2
import numpy as np
import yaml

from camera import Camera
from logger import create_rotating_log
from database import full_engine

LOGGER = create_rotating_log('/var/log/count.log', 'info')


def validate_tenant(tenant, key):
    #TODO: This method will validate to an admin API if the tenant is valid
    return True

def get_configuration_from_file(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.load(file)
    return config


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


def get_cameras_from_tenant(id_tenant):
    query = "SELECT id, source, detection_area, max_person_age, source_user, source_password, description FROM cameras WHERE " \
            "id_tenant = {id_tenant}".format(id_tenant=str(id_tenant))
    connection = full_engine.connect()
    result = connection.execute(query)
    cameras = []
    for row in result:
        id = int(row[0])
        source = row[1]
        detection_area = int(row[2])
        max_person_age = int(row[3])
        source_user = row[4]
        source_password = row[5]
        description = row[6]

        #Calculating in_points
        in_points = []
        result_in = connection.execute("SELECT num_order, x_value, y_value FROM points WHERE id_camera = " + str(id) +
                                       " AND id_area = " + str(1) + " ORDER BY num_order")
        for in_row in result_in:
            in_points.append([int(in_row[1]), int(in_row[2])])

        crit_points = []
        result_crit = connection.execute("SELECT num_order, x_value, y_value FROM points WHERE id_camera = " + str(id) +
                                       " AND id_area = " + str(2) + " ORDER BY num_order")
        for crit_row in result_crit:
            crit_points.append([int(crit_row[1]), int(crit_row[2])])

        out_points = []
        result_out = connection.execute("SELECT num_order, x_value, y_value FROM points WHERE id_camera = " + str(id) +
                                       " AND id_area = " + str(3) + " ORDER BY num_order")
        for out_row in result_out:
            out_points.append([int(out_row[1]), int(out_row[2])])

        cam = Camera(id, source, description, in_points, out_points, crit_points, 0, 0,
                     max_person_age, detection_area, source_user, source_password)
        cameras.append(cam)

    return cameras

def config_everything_and_get_cameras(yaml_file, id_tenant, test=False):
    config = get_configuration_from_file(yaml_file)
    # config_logging(config)
    #cameras = config_cameras(config, id_tenant)
    cameras = get_cameras_from_tenant(id_tenant)
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
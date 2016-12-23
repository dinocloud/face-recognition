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


def config_logging(config):
    log_config = config.get("logging")
    LOGGER = create_rotating_log(log_config.get("path"), log_config.get("level"))
    LOGGER.debug("Logging configured successfully")


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
        cam = Camera(id, source, description, in_points, out_points, crit_points, max_person_age, detection_area,
                     source_user, source_password)
        cameras.append(cam)

    return cameras


def config_everything_and_get_cameras(id_tenant, test=False):
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


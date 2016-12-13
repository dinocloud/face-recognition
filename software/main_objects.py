import cv2
import sys
import yaml
from threading import Thread
from camera import Camera
from database import configure_database_connection


def get_configuration_from_file(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.load(file)
    return config


def config_database(config):
    config = config.get("database")
    configure_database_connection(config.get("engine"), config.get("server"), config.get("username"),
                                  config.get("password"), config.get("database"))


def config_cameras(config):
    cameras = []
    for camera in config.get("cameras", {}):
        in_area_points = []
        out_area_points = []
        critical_area_points = []
        for in_points in camera.get("in_area", {}):
            in_area_points.append([int(in_points.split(';')[0]), int(in_points.split(';')[1])])
        for out_points in camera.get("out_area", {}):
            out_area_points.append([int(out_points.split(';')[0]), int(out_points.split(';')[1])])
        for crit_points in camera.get("critical_area", {}):
            critical_area_points.append([int(crit_points.split(';')[0]), int(crit_points.split(';')[1])])
        id = camera.get("id", 0)
        source = camera.get("source", 0)
        description = camera.get("description", "No description")
        max_person_age = camera.get("max_person_age", 5)
        detection_area = camera.get("detection_area", 300)
        cam = Camera(id, source, description, in_area_points, out_area_points, critical_area_points, 0, 0,
                     max_person_age, detection_area)
        cameras.append(cam)

    return cameras


def main(args):
    configuration = get_configuration_from_file("config/config.yml")
    config_database(configuration)
    cameras = config_cameras(configuration)
    threads = []

    for camera in cameras:
        t = Thread(target=camera.start_capture())
        threads.append(t)

    for thread in threads:
        thread.start()

    cv2.waitKey(0)
    cv2.destroyAllWindows()  # close all openCV windows
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
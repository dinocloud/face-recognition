import cv2
import sys
import yaml
from camera import Camera


def config_cameras_from_file(yaml_file):
    cameras = []
    with open(yaml_file, 'r') as file:
        config = yaml.load(file)

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
    cameras = config_cameras_from_file("config/config.yml")
    for camera in cameras:
        camera.start_capture()
    cv2.destroyAllWindows()  # close all openCV windows
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
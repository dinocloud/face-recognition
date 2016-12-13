import numpy as np
import cv2
import sys
from person import Person, MultiPerson
from utils import inside_convex_polygon
from camera import Camera

#Frame dimensions
frame_width = 640.0
frame_height = 480.0

#GEOMETRIC CONSTANTS
IN_LINE_POINTS = [[0, (frame_height * 1 / 4)],[frame_width, (frame_height * 1 / 4)]]
OUT_LINE_POINTS = [[frame_width, (frame_height*3/4)],[0, (frame_height*3/4)]]
CRITICAL_AREA_POINTS = [IN_LINE_POINTS[0],IN_LINE_POINTS[1], OUT_LINE_POINTS[0],OUT_LINE_POINTS[1]]
IN_AREA_POINTS = [[0,0], IN_LINE_POINTS[0], IN_LINE_POINTS[1], [frame_width, 0]]
OUT_AREA_POINTS = [[0, frame_height],  OUT_LINE_POINTS[1],OUT_LINE_POINTS[0], [frame_width, frame_height]]


def main(args):
    cam = Camera(0, "Main camera", IN_AREA_POINTS, OUT_AREA_POINTS, CRITICAL_AREA_POINTS)
    cam.start_capture()
    cv2.destroyAllWindows()  # close all openCV windows
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
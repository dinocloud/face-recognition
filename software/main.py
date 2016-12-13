import numpy as np
import cv2
import sys
from person import Person, MultiPerson
from utils import inside_convex_polygon

#Main variable that opens the video file
capture = cv2.VideoCapture(0)

#Used for noise deletion
background_substractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
kernel_open = np.ones((3, 3), np.uint8)
kernel_close = np.ones((11, 11), np.uint8)

# Main Variables
people = []
person_id = 1
count_in = 0
count_out = 0

#Image processing constants
MAX_PERSON_AGE = 5
DETECTION_AREA = 300
font = cv2.FONT_HERSHEY_SIMPLEX

#Frame dimensions
frame_width = capture.get(3)
frame_height = capture.get(4)

#GEOMETRIC CONSTANTS
IN_LINE_POINTS = [[0, (frame_height * 1 / 4)],[frame_width, (frame_height * 1 / 4)]]
OUT_LINE_POINTS = [[frame_width, (frame_height*3/4)],[0, (frame_height*3/4)]]
CRITICAL_AREA_POINTS = [IN_LINE_POINTS[0],IN_LINE_POINTS[1], OUT_LINE_POINTS[0],OUT_LINE_POINTS[1]]
IN_AREA_POINTS = [[0,0], IN_LINE_POINTS[0], IN_LINE_POINTS[1], [frame_width, 0]]
OUT_AREA_POINTS = [[0, frame_height],  OUT_LINE_POINTS[1],OUT_LINE_POINTS[0], [frame_width, frame_height]]


def draw_person_road(frame):
    """
    Used for drawing people roads
    :param frame: the frame where to place the drawing
    :return: the frame with the draw
    """
    global people
    for i in people:
        if len(i.getTracks()) >= 2:
            pts = np.array(i.getTracks(), np.int32)
            pts = pts.reshape((-1, 1, 2))
            frame = cv2.polylines(frame, [pts], False, i.getRGB())
        if i.getId() == 9:
            print str(i.getX()), ',', str(i.getY())
        cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)
    return frame


def draw_person(frame, cx, cy, x, y, w, h):
    """
    Used for drawing a person dimensions.
    :param frame: the frame where to draw
    :param cx: the x point for the circle
    :param cy: the y point for the circle
    :param x: the x point for the rectangle
    :param y: the y point for the rectangle
    :param w: the width of the rectangle
    :param h: the height of the rectangle
    """
    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3)


def calculate_in_and_out():
    """
    Method that iterates over the persons array and counts how many people are entering and how many are going outside.
    """
    global people
    global count_in
    global count_out
    deletable_index = []
    for index, person in enumerate(people):
        crit_area = False
        in_area = False
        out_area = False
        for track in person.getTracks():
            if inside_convex_polygon((track[0], track[1]), CRITICAL_AREA_POINTS):
                crit_area = True
            if crit_area:
                if inside_convex_polygon((track[0], track[1]), IN_AREA_POINTS):
                    in_area = True
                    break
                if inside_convex_polygon((track[0], track[1]), OUT_AREA_POINTS):
                    out_area = True
                    break
        if crit_area and in_area:
            count_in += 1
            print "Added in person. In: " + str(count_in)
            deletable_index.append(index)
        if crit_area and out_area:
            count_out += 1
            print "Added out person. Out: " + str(count_out)
            deletable_index.append(index)
    people = [person for index, person in enumerate(people) if index not in deletable_index]

def main(args):
    global people
    global person_id
    while capture.isOpened():

        ret, frame = capture.read()  # read a frame

        fgmask = background_substractor.apply(frame)  # Use the substractor
        try:
            ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            # Opening (erode->dilate) para quitar ruido.
            mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernel_open)
            # Closing (dilate -> erode) para juntar regiones blancas.
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
        except:
            # if there are no more frames to show...
            print('EOF')
            break

        # Draw the different areas
        in_area = np.array(IN_AREA_POINTS, np.int32).reshape((-1 ,1 , 2))
        out_area = np.array(OUT_AREA_POINTS, np.int32).reshape((-1, 1, 2))
        critical_area = np.array(CRITICAL_AREA_POINTS, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(frame, [in_area], False, color = (255, 0, 0), thickness=2)
        frame = cv2.polylines(frame, [out_area], False, color=(0, 255, 0), thickness=2)
        frame2 = frame.copy()
        frame2 = cv2.fillPoly(frame2, pts = [critical_area], color = (0, 0, 255))
        opacity = 0.5
        cv2.addWeighted(frame2, opacity, frame, 1 - opacity, 0, frame)
        _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)


        for contour in contours:
            #cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3, 8)
            area = cv2.contourArea(contour)
            if area > DETECTION_AREA:
                #################
                #   TRACKING    #
                #################
                moment = cv2.moments(contour)
                cx = int(moment['m10'] / moment['m00'])
                cy = int(moment['m01'] / moment['m00'])
                x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(contour)

                new_person = True
                for person in people:
                    if abs(x_rect - person.getX()) <= w_rect and abs(y_rect - person.getY()) <= h_rect:
                        # The person is near another one that was already detected
                        new_person = False
                        person.updateCoords(cx, cy)  # Update this person coordinates
                        draw_person(frame, cx, cy, x_rect, y_rect, w_rect, h_rect)
                        break

                if new_person and inside_convex_polygon((cx, cy), CRITICAL_AREA_POINTS):
                    p = Person(person_id, cx, cy, MAX_PERSON_AGE)
                    people.append(p)
                    person_id += 1
                    draw_person(frame, cx, cy, x_rect, y_rect, w_rect, h_rect)
                    print "New person, init points: %s,%s. Total: %s" % (cx, cy, str(len(people)))

        calculate_in_and_out()
        cv2.imshow('Frame', frame)

        # Abort and exit with 'Q' or ESC
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    capture.release()  # release video file
    cv2.destroyAllWindows()  # close all openCV windows
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
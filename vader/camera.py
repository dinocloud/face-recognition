import numpy as np
import cv2
import urllib
import platform
from utils import inside_convex_polygon
from person import Person
from database import save_movement


class Camera:

    AREA_WEIGHT = 1
    CIRCLE_COLOR = (0, 0, 255)
    RECTANGLE_COLOR = (0, 255, 0)
    BACKGROUND_SUBSTRACTOR = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    KERNEL_OPEN = np.ones((3, 3), np.uint8)
    KERNEL_CLOSE = np.ones((11, 11), np.uint8)

    def __init__(self, id, source, description, in_area_points, out_area_points, critical_area_points,
                 count_in=0, count_out=0, max_person_age=5, detection_area=300):
        self.id = id
        self.source = source
        self.description = description
        self.in_area_points = in_area_points
        self.out_area_points = out_area_points
        self.critical_area_points = critical_area_points
        self.count_in = count_in
        self.count_out = count_out
        self.max_person_age = max_person_age
        self.detection_area = detection_area
        self.people = []
        self.person_id = 1
        self.people_detected = {}
        self.frame = None

    def __draw_person_road(self, frame):
        """
        Used for drawing people roads
        :param frame: the frame where to place the drawing
        :return: the frame with the draw
        """
        for person in self.people:
            if len(person.getTracks()) >= 2:
                pts = np.array(person.getTracks(), np.int32)
                pts = pts.reshape((-1, 1, 2))
                frame = cv2.polylines(frame, [pts], False, person.getRGB())
            cv2.putText(frame, str(person.getId()), (person.getX(), person.getY()), Camera.FONT, 0.3, person.getRGB(), 1,
                        cv2.LINE_AA)
        return frame

    def __draw_person(self, frame, cx, cy, x, y, w, h, id=0):
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
        cv2.circle(frame, (cx, cy), 5, Camera.CIRCLE_COLOR, -1)
        cv2.putText(frame, str(id), (cx, cy), Camera.FONT, fontScale=4, color=Camera.CIRCLE_COLOR, thickness=3)
        cv2.rectangle(frame, (x, y), (x + w, y + h), Camera.RECTANGLE_COLOR, 2)
        # cv2.drawContours(frame, cnt, -1, Camera.RECTANGLE_COLOR, 3)

    def __calculate_in_and_out(self):
        """
        Method that iterates over the persons array and counts how many people are entering and how many are going outside.
        """
        deletable_index = []
        for index, person in enumerate(self.people):
            crit_area = False
            in_area = False
            out_area = False
            crit_weight = 0
            in_weight = 0
            out_weight = 0
            for track in person.getTracks():
                if inside_convex_polygon((track[0], track[1]), self.critical_area_points):
                    crit_weight+=1
                    if crit_weight == Camera.AREA_WEIGHT:
                        crit_area = True
                        continue
                if crit_area:
                    if inside_convex_polygon((track[0], track[1]), self.in_area_points):
                        in_weight+=1
                        if in_weight == Camera.AREA_WEIGHT:
                            in_area = True
                            break
                    if inside_convex_polygon((track[0], track[1]), self.out_area_points):
                        out_weight+=1
                        if out_weight == Camera.AREA_WEIGHT:
                            out_area = True
                            break
            if crit_area and in_area and not self.people_detected[person.getId()]:
                self.count_in += 1
                save_movement("in", self.id)
                print "Added in person. Camera: " + str(self.id) + " Id: " + str(person.getId()) + " In: " + str(self.count_in)
                deletable_index.append(index)
                self.people_detected[person.getId()] = True
            if crit_area and out_area and not self.people_detected[person.getId()]:
                self.count_out += 1
                save_movement("out", self.id)
                print "Added out person. Camera: " + str(self.id) + " Id: " + str(person.getId()) + " Out: " + str(self.count_out)
                deletable_index.append(index)
                self.people_detected[person.getId()] = True
        self.people = [person for index, person in enumerate(self.people) if index not in deletable_index]

    def __process_streaming(self, fgmask, kernel_open, kernel_close, test=False):
        try:
            ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            # Opening (erode->dilate) para quitar ruido.
            mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernel_open)
            # Closing (dilate -> erode) para juntar regiones blancas.
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
        except:
            # if there are no more frames to show...
            print('EOF')
            raise
            # Draw the different areas
        frame2 = self.frame.copy()
        in_area = np.array(self.in_area_points, np.int32).reshape((-1, 1, 2))
        out_area = np.array(self.out_area_points, np.int32).reshape((-1, 1, 2))
        critical_area = np.array(self.critical_area_points, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(frame2, [in_area], isClosed=True, color=(255, 0, 0), thickness=2)
        frame = cv2.polylines(frame2, [out_area], isClosed=True, color=Camera.RECTANGLE_COLOR, thickness=2)
        frame2 = cv2.fillPoly(frame2, pts=[critical_area], color=Camera.CIRCLE_COLOR)
        opacity = 0.5
        cv2.addWeighted(frame2, opacity, self.frame, 1 - opacity, 0, self.frame)
        _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        id_moving = []
        for contour in contours:
            # cv2.drawContours(frame, cnt, -1, Camera.RECTANGLE_COLOR, 3, 8)
            area = cv2.contourArea(contour)
            if area > self.detection_area:
                #################
                #   TRACKING    #
                #################
                moment = cv2.moments(contour)
                cx = int(moment['m10'] / moment['m00'])
                cy = int(moment['m01'] / moment['m00'])
                x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(contour)

                new_person = True
                for person in self.people:
                    if abs(x_rect - person.getX()) <= w_rect and abs(y_rect - person.getY()) <= h_rect:
                        # The person is near another one that was already detected
                        new_person = False
                        person.updateCoords(cx, cy)  # Update this person coordinates
                        self.__draw_person(self.frame, cx, cy, x_rect, y_rect, w_rect, h_rect, person.getId())
                        id_moving.append(person.getId())
                        break

                if new_person:  # and inside_convex_polygon((cx, cy), self.critical_area_points):
                    p = Person(self.person_id, cx, cy, self.max_person_age)
                    self.people.append(p)
                    self.people_detected[self.person_id] = False
                    self.person_id += 1
                    self.__draw_person(self.frame, cx, cy, x_rect, y_rect, w_rect, h_rect, p.getId())
                    id_moving.append(p.getId())

        self.people = [person for person in self.people if person.getId() in id_moving]
        # If there aren't people on screen, reset the id
        if len(self.people) == 0:
            self.person_id = 1

        if not test:
            self.__calculate_in_and_out()

    def __start_capture_windows(self):
        """
        DEPRECATED
        """
        background_substractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        kernel_open = np.ones((3, 3), np.uint8)
        kernel_close = np.ones((11, 11), np.uint8)
        self.stream = urllib.urlopen(self.source)
        bytes = ''
        while True:
            bytes += self.stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b + 2]
                bytes = bytes[b + 2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                fgmask = background_substractor.apply(frame)  # Use the substractor
                try:
                    self.__process_streaming(frame, fgmask, kernel_open, kernel_close)
                except:
                    break
                cv2.imshow(self.description, frame)
                k = cv2.waitKey(30) & 0xff
                if k == 27:
                    break


    def __start_capture_linux(self):
        """
        DEPRECATED
        """
        capture = cv2.VideoCapture()
        capture.open(self.source)
        background_substractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        kernel_open = np.ones((3, 3), np.uint8)
        kernel_close = np.ones((11, 11), np.uint8)
        frame_width = capture.get(3)
        frame_height = capture.get(4)
        while capture.isOpened():
            ret, frame = capture.read()  # read a frame
            fgmask = background_substractor.apply(frame)  # Use the substractor
            try:
                self.__process_streaming(frame, fgmask, kernel_open, kernel_close)
            except:
                break
            cv2.imshow(self.description, frame)
            # Abort and exit with 'Q' or ESC
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
        capture.release()  # release video file
        cv2.destroyAllWindows()  # close all openCV windows

    def get_frame(self):
        return self.frame

    def start_capture(self):
        if platform.system().upper() == "WINDOWS":
            self.__start_capture_windows()
        elif platform.system().upper() == "LINUX":
            self.__start_capture_windows()


    def configure_streaming(self):
        self.stream = urllib.urlopen(self.source)
        #self.stream = cv2.VideoCapture(self.source)
        self.bytes = ''

    def single_capture(self, test=False):
        self.bytes += self.stream.read(1024)
        a = self.bytes.find('\xff\xd8')
        b = self.bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = self.bytes[a:b + 2]
            self.bytes = self.bytes[b + 2:]
            self.frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            fgmask = Camera.BACKGROUND_SUBSTRACTOR.apply(self.frame)  # Use the substractor
            self.__process_streaming(fgmask, Camera.KERNEL_OPEN, Camera.KERNEL_CLOSE, test)
            return True
        else:
            return False

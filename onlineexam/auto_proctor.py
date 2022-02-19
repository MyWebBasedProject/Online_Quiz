import cv2
import face_recognition
import dlib
import threading
import numpy as np
import math
import time
import MySQLdb
from onlineexam import socketio, threaded_backend

img_count = 0  # This is count violation images inserted in database.
cap = cv2.VideoCapture(0)  # Reading webcam

detector = dlib.get_frontal_face_detector()  # used to detect face.
# loading shape predictor.
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

violation_done = 0

correct_person = [False]
persons = 0
mobiles = 0
eye_direction = "center"
face_direction = "center"
face_count = 0
canBreak = False


with open("onlineexam\yolov3\coco.names", "r") as f:
    classes_names = [line.strip() for line in f.readlines()]
net = cv2.dnn.readNet("onlineexam\yolov3\yolov3-spp.weights",
                      "onlineexam\yolov3\yolov3-spp.cfg")  # This is our ANN/model
layers_names = net.getLayerNames()
output_layers = [layers_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

imgMridul = face_recognition.load_image_file("onlineexam\images\Mridul.jpg")
imgMridul = cv2.cvtColor(imgMridul, cv2.COLOR_BGR2RGB)
refEncode = face_recognition.face_encodings(imgMridul)[0]

# imgRdj = face_recognition.load_image_file("onlineexam\images\_rdj.jpg")
# imgRdj = cv2.cvtColor(imgRdj, cv2.COLOR_BGR2RGB)
# refEncode = face_recognition.face_encodings(imgRdj)[0]


def insert_Image(backendInstance, message, frame, mydb, violationTime):
    global img_count

    message_path = ''
    for i in message:
        if i == ' ':
            message_path += '_'
        else:
            message_path += i

    path = "static/temp_report/" + \
        str(message_path)+"/" + str(img_count)+".png"
    cv2.imwrite("onlineexam/" + path, frame)
    backendInstance.insert_message(message, path, mydb, violationTime)
    img_count += 1


def check_correct_person():
    global correct_person
    while True:
        correct, frame = cap.read()
        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) == 1:
            face_encodes = face_recognition.face_encodings(
                frame, face_locations)
            correct_person = face_recognition.compare_faces(
                refEncode, face_encodes)
        if cv2.waitKey(3000) & canBreak == True:
            break


def get_midpoint(pointa, pointb):
    return int((pointa.x + pointb.x)/2), int((pointa.y + pointb.y)/2)


def gaze_detection(eyePoint, landmarks, frame, gray):

    eye_region = np.array([(landmarks.part(eyePoint[0]).x, landmarks.part(eyePoint[0]).y),
                           (landmarks.part(eyePoint[1]).x,
                            landmarks.part(eyePoint[1]).y),
                           (landmarks.part(eyePoint[2]).x,
                            landmarks.part(eyePoint[2]).y),
                           (landmarks.part(eyePoint[3]).x,
                            landmarks.part(eyePoint[3]).y),
                           (landmarks.part(eyePoint[4]).x,
                            landmarks.part(eyePoint[4]).y),
                           (landmarks.part(eyePoint[5]).x, landmarks.part(eyePoint[5]).y)], np.int32)

    height, width, channels = frame.shape
    mask = np.zeros((height, width), np.uint8)  # a black screen of size frame

    # draw polygon lines on gray image
    cv2.polylines(mask, [eye_region], True, 255, 1)
    cv2.fillPoly(mask, [eye_region], 255)

    cv2.imshow("poly shape", mask)
    eye = cv2.bitwise_and(gray, gray, mask=mask)  # apply mask on gray image
    eye[mask == 0] = 255

    cv2.imshow("Eye", eye)  # display eye on mask

    min_x = np.min(eye_region[:, 0])
    max_x = np.max(eye_region[:, 0])
    min_y = np.min(eye_region[:, 1])
    max_y = np.max(eye_region[:, 1])
    gray_eye = eye[min_y: max_y, min_x:max_x]

    cv2.imshow("Gray eye", gray_eye)

    _, thresholdm_eye = cv2.threshold(gray_eye, 55, 255, cv2.THRESH_BINARY)

    height, width = thresholdm_eye.shape

    divPart = width/3

    cv2.imshow("Threshold", thresholdm_eye)

    left_side_thres = thresholdm_eye[0:height, 0:int(divPart)]
    left_side_white = cv2.countNonZero(left_side_thres)

    center_side_thres = thresholdm_eye[0:height, int(divPart):2*int(divPart)]
    center_side_white = cv2.countNonZero(center_side_thres)

    right_side_thres = thresholdm_eye[0:height, int(divPart)*2:width]
    right_side_white = cv2.countNonZero(right_side_thres)

    return left_side_white, center_side_white, right_side_white


def get_slopes(pointA, pointB):
    if pointB[1] != pointA[1]:
        return (pointB[0] - pointA[0])/(pointB[1] - pointA[1])

def face_orientation(frame, landmarks):

    global face_direction, img_count

    m1 = get_slopes([landmarks.part(27).x, landmarks.part(27).y], [
                    landmarks.part(30).x, landmarks.part(30).y])

    m2 = get_slopes([landmarks.part(30).x, landmarks.part(30).y], [
                    landmarks.part(33).x, landmarks.part(33).y])

    cv2.arrowedLine(frame, (landmarks.part(30).x, landmarks.part(
        30).y), (landmarks.part(27).x, landmarks.part(27).y), (255, 0, 0))
    cv2.arrowedLine(frame, (landmarks.part(30).x, landmarks.part(
        30).y), (landmarks.part(33).x, landmarks.part(33).y), (255, 0, 0))

    if m1 != None and m2 != None:
        angle_r = math.atan((m2 - m1 / (1 + (m1 * m2))))
        angle_d = round(math.degrees(angle_r))
        angle_d = 180 - angle_d
        cv2.putText(frame, str(angle_d), (300, 100),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
        if angle_d < 160:
            face_direction = 'Face Left Side'
            cv2.putText(frame,'Face Left Side', (100, 100),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            return False
        elif angle_d > 200:
            face_direction = "Face Right Side"
            cv2.putText(frame, "Face Right Side", (100, 100),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            return False
        else:
            face_direction = "center side"
            cv2.putText(frame, "center", (100, 100),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            return True


def gaze_calcualtion(backendInstance, frame, gray, landmarks, mydb):
    global eye_direction
    left_eye = [36, 37, 38, 39, 40, 41]
    right_eye = [42, 43, 44, 45, 46, 47]
    left_l, center_l, right_l = gaze_detection(
        left_eye, landmarks, frame, gray)
    left_r, center_r, right_r = gaze_detection(
        right_eye, landmarks, frame, gray)
    left = left_l + left_r
    center = center_l + center_r
    right = right_l + right_r

    if left < right and left < center:
        eye_direction = "left"
        cv2.putText(frame, "Eye: Left", (50, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
        return False

    elif right < left and right < center:
        eye_direction = "right"
        cv2.putText(frame, "Eye: Right", (50, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)
        return False

    elif center < left and center < right:
        eye_direction = "center"
        cv2.putText(frame, "Eye: Center", (50, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)
        return True


def face_area(frame, x1, y1, x2, y2):
    # cv2.putText(frame, str((y2 - y1) + (x2 - x1)), (300, 300), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255), 3)
    return (y2 - y1)+(x2 - x1)


def detect_person_mobile(backendInstance):
    global persons, mobiles, canBreak, correct_person, violation_done, no_other_violations, no_violation_mobile
    mydb = MySQLdb.connect(host='localhost', user='root', passwd='', db='exam')

    not_doing_person_violation = True
    not_doing_mobile_violation = True

    str_correct_person = True
    start_time_person = 0
    start_time_mobile = 0

    while True:  # and time.time()>(last_time + 3):
        if correct_person[0] == True:
            str_correct_person = True
        else:
            str_correct_person = False
        correct, frame = cap.read()  # normal image capture in RGB format
        if correct:
            frame = cv2.flip(frame, 1)
            # detecting image
            # opencv works in BGR format so we r converting it.
            blob = cv2.dnn.blobFromImage(
                frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            outs = net.forward(output_layers)

            height, width, channels = frame.shape

            confidences = []
            boxes = []
            class_ids = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.3 and (class_id == 0 or class_id == 67):
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2]*width)
                        h = int(detection[3]*height)

                        # Rectangle Coordinates
                        x = int(center_x - w/2)
                        y = int(center_y - h/2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            number_object_detected = len(boxes)

            persons = 0
            mobiles = 0

            for i in range(number_object_detected):
                if i in indexes:
                    if class_ids[i] == 0:
                        persons += 1
                    if class_ids[i] == 67:
                        mobiles += 1

                    x, y, w, h = boxes[i]
                    label = str(classes_names[int(class_ids[i])])
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(
                        frame, label + ": " + str(class_ids[i]), (x, y+40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)

            if persons > 1 and not_doing_person_violation == True:
                violation_done += 1
                start_time_person = time.time()
                not_doing_person_violation = False
                violation_person_image = frame
            elif persons == 1 and not_doing_person_violation == False:
                total_time_person = time.time() - start_time_person
                not_doing_person_violation = True
                insert_Image(backendInstance, 'Multiple Person Detected', violation_person_image , mydb, total_time_person)


            if mobiles != 0 and not_doing_mobile_violation == True:
                violation_done += 1
                start_time_mobile = time.time()
                not_doing_mobile_violation = False
                violation_mobile_image = frame
            elif mobiles == 0 and not_doing_mobile_violation == False:
                total_time_mobile = time.time() - start_time_mobile
                not_doing_mobile_violation = True
                print("mobile violation: " + str(total_time_mobile) )
                insert_Image(backendInstance, 'Mobile Detected', violation_mobile_image, mydb, total_time_mobile)

            cv2.putText(frame, str(face_count), (50, 100),
                        cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 255))
            cv2.imshow("person mobile", frame)
            socketio.emit('detect_person_mobile',
                          (persons, mobiles, str_correct_person))
        if cv2.waitKey(1) & canBreak == True:
            break

def violation(backendInstance):
    # Model
    global violation_done

    not_doing_face_violation = True
    not_doing_wrong_person_violation = True
    not_doing_face_direction_violation = True
    not_doing_eye_direction_violation = True



    mydb = MySQLdb.connect(host='localhost', user='root', passwd='', db='exam')
    start_time = 0
    violation_image = None
    while True:
        correct, frame = cap.read()  # normal image capture in RGB format

        if correct:
            frame = cv2.flip(frame, 1)

            # convert to gray image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)  # apply detector on gray image
            global face_count, persons, eye_direction, face_direction, correct_person
            face_count = len(faces)

            # check Face count and person count
            if face_count == 0 and not_doing_face_violation == True:
                not_doing_face_violation = False
                violation_done += 1
                start_time = time.time()
                violation_image = frame

            elif face_count==1 and persons==1 and not_doing_face_violation == False:
                not_doing_face_violation  = True
                total_time = time.time() - start_time
                insert_Image(backendInstance, 'No Face Detected',violation_image, mydb, total_time)

            elif face_count==1 and persons == 1 and not_doing_face_violation == True:
                # print('no problem')
                face = faces[0]
                x1, y1 = face.left(), face.top()
                x2, y2 = face.right(), face.bottom()
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                face_perimenter = face_area(frame, x1, y1, x2, y2)
                landmarks = predictor(gray, face)

                if correct_person[0]==False and not_doing_wrong_person_violation==True:
                    violation_done += 1
                    start_time = time.time()
                    not_doing_wrong_person_violation = False
                    violation_image = frame
                    # print("wrong person detected")


                elif correct_person[0]==True and not_doing_wrong_person_violation==False:
                    not_doing_wrong_person_violation = True
                    total_time = time.time() - start_time
                    insert_Image(backendInstance, 'Wrong Person', violation_image, mydb, total_time)
                    # print('Wrong person gone')

                elif correct_person[0]==True and not_doing_wrong_person_violation == True:
                   # print("no problem")

                    if face_perimenter > 400 and face_perimenter < 525:
                        face_orientation_check = face_orientation(frame, landmarks)

                        if face_orientation_check==False and not_doing_face_direction_violation == True:
                            not_doing_face_direction_violation= False
                            start_time = time.time()
                            violation_done+=1
                            violation_image = frame
                            violation_msg = face_direction

                        elif face_orientation_check==True and not_doing_face_direction_violation==False:
                            not_doing_face_direction_violation = True
                            total_time = time.time() - start_time
                            insert_Image(backendInstance, violation_msg, violation_image, mydb, total_time)
                            print('Wrong Direction Stopped')

                        elif face_orientation_check==True and not_doing_face_direction_violation == True:
                            print("no problem")
                            gaze_detection_check = gaze_calcualtion(backendInstance, frame, gray, landmarks, mydb)

                            if gaze_detection_check == False and not_doing_eye_direction_violation == True:
                                not_doing_eye_direction_violation = False
                                violation_image = frame
                                violation_done+=1
                                violation_msg = eye_direction
                                start_time = time.time()

                            elif gaze_detection_check == True and not_doing_eye_direction_violation == False:
                                total_time = time.time() - start_time
                                not_doing_eye_direction_violation = True
                                insert_Image(backendInstance, violation_msg, violation_done, mydb, total_time)

                            elif gaze_detection_check == True and not_doing_eye_direction_violation == True:
                                print("no problem")

                    elif face_perimenter < 400:
                        cv2.putText(frame, str("Face too far"), (100, 100),
                                    cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)
                    elif face_perimenter > 525:
                        cv2.putText(frame, str("Face too close"), (100, 100),
                                    cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)

            cv2.putText(frame, "Is correct Person" + str(correct_person), (50, 100),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255))
            cv2.imshow("violations", frame)
            socketio.emit('violation', (face_count,
                                  eye_direction, face_direction))
            socketio.emit('number_of_violation', (violation_done))
            global canBreak
            if cv2.waitKey(1) & canBreak == True:
                break


@socketio.on('violation')
def start_violation():
    backendInstance = threaded_backend.BackendOperations()
    t1 = threading.Thread(target=detect_person_mobile, args=(backendInstance,))
    t2 = threading.Thread(target=violation, args=(backendInstance,))
    t3 = threading.Thread(target=check_correct_person, args=())

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


@socketio.on('close_camera')
def close_camera():
    cap.release()
    cv2.destroyAllWindows()
    global canBreak
    canBreak = True

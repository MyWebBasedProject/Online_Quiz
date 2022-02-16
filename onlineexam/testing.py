import cv2
import face_recognition
import dlib
import threading
import numpy as np
import math, time
import MySQLdb, os
from onlineexam import socketio, backend

img_count = 0
time_gap = 2
cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

violation_done = 0
correct_person = [False]
persons = 0
mobiles = 0
eye_direction = "center"
face_direction = "center"
face_count = 0
canBreak = False


# classes_names = []
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


def insert_Image(backendInstance, message, frame, mydb):
    global img_count

    message_path=''
    for i in message:
        if i==' ':
            message_path+='_'
        else:
            message_path+=i

    path = "static/temp_report/"+ str(message_path)+"/" +str(img_count)+".png"
    print(path)
    print(cv2.imwrite("onlineexam/" + path,frame))
    backendInstance.insert_message(message, path, mydb)
    img_count+=1

def check_correct_person(frame):
    global correct_person
    face_locations = face_recognition.face_locations(frame)
    if len(face_locations) == 1:
        face_encodes = face_recognition.face_encodings(
            frame, face_locations)
        correct_person = face_recognition.compare_faces(
            refEncode, face_encodes)


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
    # cv2.imshow("mask zeros", mask)

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


def face_orientation(backendInstance, frame, landmarks, mydb):

    global face_direction, violation_done, img_count

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
            face_direction = "left side"
            violation_done += 1
            cv2.putText(frame, "Left Side", (100, 100),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            insert_Image(backendInstance,'Face Left Side', frame, mydb)
            return False
        elif angle_d > 200:
            face_direction = "right side"
            violation_done += 1
            cv2.putText(frame, "Right Side", (100, 100),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            insert_Image(backendInstance,'Face Right Side',frame, mydb)
            return False
        else:
            face_direction = "center side"
            cv2.putText(frame, "center", (100, 100),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            return True

def gaze_calcualtion(backendInstance, frame, gray, landmarks, mydb):
    global eye_direction, violation_done
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
        violation_done += 1
        cv2.putText(frame, "Eye: Left", (50, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
        insert_Image(backendInstance, 'Looking Left', frame, mydb)

    elif right < left and right < center:
        violation_done += 1
        eye_direction = "right"
        cv2.putText(frame, "Eye: Right", (50, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)
        insert_Image(backendInstance, 'Looking Right', frame, mydb)

    elif center < left and center < right:
        eye_direction = "center"
        cv2.putText(frame, "Eye: Center", (50, 200),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)


def face_area(frame, x1, y1, x2, y2):
    # cv2.putText(frame, str((y2 - y1) + (x2 - x1)), (300, 300), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255), 3)
    return (y2 - y1)+(x2 - x1)


def detect_person_mobile(backendInstance):
    global persons, mobiles, canBreak, correct_person, violation_done
    last_time = 0
    mydb = MySQLdb.connect(host='localhost', user='root', passwd='', db='exam')
    str_correct_person = True # send message to client weather the person is correct or not.
    while True and time.time()>(last_time + 3):
        if correct_person[0] == True:
            str_correct_person = True
        else:
            str_correct_person = False
        correct, frame = cap.read()  # normal image capture in RGB format
        if correct:
            last_time = time.time()
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
                    label = str(classes_names[class_ids[i]])
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(
                        frame, label + ": " + str(class_ids[i]), (x, y+40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)

            if persons != 1:
                violation_done += 1
                insert_Image(backendInstance, 'Multiple Person Detected', frame, mydb)
            if mobiles != 0:
                violation_done += 1
                insert_Image(backendInstance, 'Mobile Detected', frame, mydb)
            cv2.putText(frame, str(face_count), (50, 100),
                        cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 255))
            cv2.imshow("person mobile", frame)

            if face_count == 1:
                check_correct_person(frame)

            socketio.emit('detect_person_mobile',
                          (persons, mobiles, str_correct_person))
        if cv2.waitKey(3000) & canBreak == True:
            break


def violation(backendInstance):
    # Model
    global violation_done
    last_time = 0
    mydb = MySQLdb.connect(host='localhost', user='root', passwd='', db='exam')
    while True and time.time()> (last_time + time_gap):
        correct, frame = cap.read()  # normal image capture in RGB format

        if correct:
            frame = cv2.flip(frame, 1)
            last_time = time.time()
            # convert to gray image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)  # apply detector on gray image
            global face_count, persons, eye_direction, face_direction
            face_count = len(faces)
            if face_count > 0 and persons == 1:
                for face in faces:  # for each face detected by detector
                    x1, y1 = face.left(), face.top()
                    x2, y2 = face.right(), face.bottom()
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    face_perimenter = face_area(frame, x1, y1, x2, y2)

                    landmarks = predictor(gray, face)

                    if face_count == 1:
                        if face_perimenter > 400 and face_perimenter < 525:
                            cv2.putText(frame, str(correct_person), (50, 100),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255))
                            if correct_person[0]:
                                if face_orientation(backendInstance, frame, landmarks, mydb):
                                    gaze_calcualtion(
                                        backendInstance, frame, gray, landmarks, mydb)
                            else:
                                violation_done += 1
                                cv2.putText(frame, "Wrong Person", (50, 100),
                                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255))
                        elif face_perimenter < 400:
                            cv2.putText(frame, str("Face too far"), (100, 100),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)
                        elif face_perimenter > 525:
                            cv2.putText(frame, str("Face too close"), (100, 100),
                                        cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)
                    elif face_count != 1:
                        cv2.putText(frame, str("Multiple Faces Detected: " + str(face_count)),
                                    (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

                        insert_Image(backendInstance, "Multiple Faces Detected",frame, mydb)

            else:
                violation_done+=1
                cv2.putText(frame, str("No Face Detected"), (50, 100),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                insert_Image(backendInstance, 'No Face Detected', frame, mydb)

            cv2.imshow("violation", frame)
            socketio.emit('violation', (face_count, eye_direction, face_direction))
            socketio.emit('number_of_violation', (violation_done))

        global canBreak
        if cv2.waitKey(2000) & canBreak == True:
            break


@socketio.on('violation')
def start_violation():
    print("start_violation: ")
    backendInstance = backend.BackendOperations()
    t1 = threading.Thread(target=detect_person_mobile, args=(backendInstance,))
    t2 = threading.Thread(target=violation, args=(backendInstance,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


@socketio.on('close_camera')
def close_camera():
    cap.release()
    cv2.destroyAllWindows()
    global canBreak
    canBreak = True

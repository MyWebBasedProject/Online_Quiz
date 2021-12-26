import cv2, time, face_recognition
import simple_websocket
import dlib, numpy as np, math
from flask_socketio import send, emit
from flask import render_template, request
from onlineexam import app, socketio, mydb, backend


check_rate = 1


imgMridul = face_recognition.load_image_file("onlineexam\images\Mridul.jpg")
imgMridul = cv2.cvtColor(imgMridul, cv2.COLOR_BGR2RGB)
refEncode = face_recognition.face_encodings(imgMridul)
def compare_faces(frame):
    if len(face_recognition.face_encodings(frame))!=0:
        encode = face_recognition.face_encodings(frame)[0]
        return face_recognition.compare_faces([refEncode], encode)
    else:
        return False

@app.route("/face_detect", methods=["POST"])
def faceDetect():
    if request.method == "POST":
        return render_template("face_detect.html")


cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")



def get_midpoint(pointa, pointb):
    return int((pointa.x + pointb.x)/2), int((pointa.y + pointb.y)/2)

def nose_area(nosePoint, landmarks):
    nose_region = np.array([(landmarks.part(nosePoint[0]).x,landmarks.part(nosePoint[0]).y),
                                (landmarks.part(nosePoint[1]).x,landmarks.part(nosePoint[1]).y),
                                (landmarks.part(nosePoint[2]).x,landmarks.part(nosePoint[2]).y),
                                (landmarks.part(nosePoint[3]).x,landmarks.part(nosePoint[3]).y),
                                (landmarks.part(nosePoint[4]).x,landmarks.part(nosePoint[4]).y)], np.int32)   
    return nose_region

def gaze_detection(eyePoint, landmarks, frame, gray):
    
    eye_region = np.array([(landmarks.part(eyePoint[0]).x,landmarks.part(eyePoint[0]).y),
                                        (landmarks.part(eyePoint[1]).x,landmarks.part(eyePoint[1]).y),
                                        (landmarks.part(eyePoint[2]).x,landmarks.part(eyePoint[2]).y),
                                        (landmarks.part(eyePoint[3]).x,landmarks.part(eyePoint[3]).y),
                                        (landmarks.part(eyePoint[4]).x,landmarks.part(eyePoint[4]).y),
                                        (landmarks.part(eyePoint[5]).x,landmarks.part(eyePoint[5]).y)], np.int32)
        
    height, width,channels = frame.shape
    mask = np.zeros((height, width), np.uint8) #a black screen of size frame
    # cv2.imshow("mask zeros", mask)

    cv2.polylines(mask, [eye_region], True, 255, 1) #draw polygon lines on gray image
    cv2.fillPoly(mask,[eye_region], 255)

    cv2.imshow("poly shape", mask)
    eye = cv2.bitwise_and(gray, gray, mask=mask) #apply mask on gray image
    eye[mask==0]=255

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
    if pointB[0]!=pointA[0]:
        return (pointB[1] - pointA[1])/(pointB[0] - pointA[0])


def face_orientation(backendInstance, frame, landmarks):
    nose_region = nose_area([27, 28, 29, 30, 33], landmarks)
    # print(np.size(nose_region))
    m1 = get_slopes([landmarks.part(27).x, landmarks.part(27).y], [landmarks.part(30).x, landmarks.part(30).y])
    m2 = get_slopes([landmarks.part(30).x, landmarks.part(30).y], [landmarks.part(33).x, landmarks.part(33).y])
    cv2.polylines(frame, [nose_region], False, (0, 0, 0))
    if m1 != None and m2 != None:
        angle_r = math.atan((m2 - m1 / (1 + (m1 * m2))))
        angle_d = round(math.degrees(angle_r))
        cv2.putText(frame, str(angle_d), (300, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
        if angle_d <= 60 and angle_d > 0:
            cv2.putText(frame, "Left Side", (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            #backendInstance.insert_message('Face Left Side', frame)
            return False
        elif angle_d >= -60 and angle_d < 0:
            cv2.putText(frame, "Right Side", (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            #backendInstance.insert_message('Face Right Side', frame)
            return False
        else:
            cv2.putText(frame, "center", (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)
            return True


def gaze_calcualtion(backenInstance ,frame, gray, landmarks):
    left_eye = [36,37,38,39,40,41]
    right_eye = [42,43,44,45,46,47]
    left_l, center_l, right_l = gaze_detection(left_eye, landmarks, frame, gray)
    left_r, center_r, right_r = gaze_detection(right_eye, landmarks, frame, gray)
    left = left_l + left_r
    center = center_l + center_r
    right = right_l + right_r

    if left < right and left < center:
        cv2.putText(frame, "Left", (50, 200), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
        backenInstance.insert_message('Looking Left', frame)
    elif right < left and right < center:
        cv2.putText(frame, "Right", (50, 200), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 3)
        backenInstance.insert_message('Looking Right', frame)
    elif center < left and center < right:
        cv2.putText(frame, "Center", (50, 200), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 3)

def face_area(frame, x1, y1, x2, y2):
    cv2.putText(frame, str((y2 - y1) + (x2 - x1)), (300, 300), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255), 3)
    return (y2 - y1)+(x2 - x1)

@socketio.on('yolo_event')
def yolo_event():
    # Model
    last_time = 0
    backendInstance = backend.BackendOperations()

    while True:
        correct, frame = cap.read() #normal image capture in RGB format
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #convert to gray image
        faces = detector(gray) # apply detector on gray image
        face_count = len(faces)
        if face_count>0:
            for face in faces: #for each face detected by detector
                x1,y1 = face.left(), face.top()
                x2,y2 = face.right(), face.bottom()
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                face_perimenter = face_area(frame, x1, y1, x2, y2)

                landmarks = predictor(gray, face)
                if face_count==1:
                    if face_perimenter>400 and face_perimenter<525  and time.time() > check_rate+last_time:
                        last_time = time.time()
                        if compare_faces(frame):
                            if face_orientation(backendInstance, frame, landmarks):
                                gaze_calcualtion(backendInstance, frame, gray, landmarks)
                    elif face_perimenter<400:
                        cv2.putText(frame, str("Face too far"), (100,100), cv2.FONT_HERSHEY_TRIPLEX,1,(255,0,0),3)
                    elif face_perimenter>525:
                        cv2.putText(frame, str("Face too close"), (100,100), cv2.FONT_HERSHEY_TRIPLEX,1,(255,0,0),3)
                elif face_count!=1 and time.time() > check_rate+last_time:
                    last_time = time.time()
                    cv2.putText(frame, str("Multiple Faces Detected: " + str(face_count)), (50,100), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 3)
                    #backendInstance.insert_message("Multiple Faces Detected",frame)
        elif time.time()>last_time+check_rate:
            last_time = time.time()
            cv2.putText(frame, str("No Face Detected"), (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
            #backendInstance.insert_message("No Face Detected", frame)
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
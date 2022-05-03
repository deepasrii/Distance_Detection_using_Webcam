from flask import Flask, render_template, request
from flask_socketio import *
import functools
from flask_login import current_user
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import base64
import io
from imageio import imread
import matplotlib.pyplot as plt

app = Flask(__name__)
#cors=CORS(app,resources={r"/api/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")

@socketio.on('connect')
def connected():
    print('connected')


@socketio.on('image')
def index(data_image):
    Known_distance = 58.2
 
    # width of face in the real world or Object Plane
    # centimeter
    Known_width = 14.3

    # Colors
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # defining the fonts
    #fonts = cv2.FONT_HERSHEY_COMPLEX

    # face detector object
    face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    #eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')

    # focal length finder function
    def Focal_Length_Finder(measured_distance, real_width, width_in_rf_image):

        # finding the focal length
        focal_length = (width_in_rf_image * measured_distance) / real_width
        return focal_length

    # distance estimation function
    def Distance_finder(Focal_Length, real_face_width, face_width_in_frame):

        distance = (real_face_width * Focal_Length)/face_width_in_frame

        # return the distance
        return distance


    # reading reference_image from directory
    ref_image = cv2.imread('my.png')

    # find the face width(pixels) in the reference_image
    gray_image = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(gray_image, 1.3, 5)#1.1, 4
    for (x, y , w ,h) in faces:
        face_width = w

    ref_image_face_width = face_data(face_width)

    # get the focal by calling "Focal_Length_Finder"
    # face width in reference(pixels),
    # Known_distance(centimeters),
    # known_width(centimeters)
    Focal_length_found = Focal_Length_Finder(
        Known_distance, Known_width, ref_image_face_width)

    #print(Focal_length_found)

    # show the reference image
    ####cv2.imshow("ref_image", ref_image)

    # initialize the camera object so that we
    # can get frame from it
    #cap = cv2.VideoCapture(0)

    # looping through frame, incoming from
    # camera/video
    #while True:

    # reading the frame from camera
    while(True):
        code1=data_image.partition(',')[2]
        imgdata= base64.b64decode(code1)
        dataBytesIO = io.BytesIO(imgdata)
    
        pimg = Image.open(dataBytesIO)
    
        frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray_image, 1.3, 5)

        for (x, y , w ,h) in faces:
            face_width = w
   
        #frame = pimg
        # calling face_data function to find
        # the width of face(pixels) in the frame
        face_width_in_frame = face_width

        # check if the face is zero then not
        # find the distance
        if face_width_in_frame != 0:

            # finding the distance by calling function
            # Distance distnace finder function need
            # these arguments the Focal_Length,
            # Known_width(centimeters),
            # and Known_distance(centimeters)
            Distance = Distance_finder(
                Focal_length_found, Known_width, face_width_in_frame)

            # draw line as background of text
            #cv2.line(frame, (30, 30), (230, 30), RED, 32)
            #cv2.line(frame, (30, 30), (230, 30), BLACK, 28)

            # Drawing Text on the screen
            #cv2.putText(
                #frame, f"Distance: {round(Distance,2)} CM", (30, 35),
                #fonts, 0.6,WHITE, 1)#GREEN
            d=Distance
            if d<=45:
                #cv2.putText(frame,'too close to screen',(28,80),fonts,0.8,RED,2)
                print('too close to screen')
        #else:
            #cv2.putText(frame,'GooD',(28,80),fonts,0.8,GREEN,2)
     

        # show the frame on the screen
        #cv2.imshow("frame", frame)

        # quit the program if you press 'q' on keyboard
        #if cv2.waitKey(1) == ord("q"):
            #break

    # closing the camera
    ##cap.release()

    # closing the the windows that are opened
    #cv2.destroyAllWindows()
    
    #return jsonify()

    
@socketio.on('client_disconnecting')
def disconnect_details():
    print('user disconnected.')

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=5000)
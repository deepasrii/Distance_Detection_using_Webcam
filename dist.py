from flask import Flask,jsonify,render_template
import cv2
import numpy as np

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/webcam",methods=['GET'])
def distance():
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
    fonts = cv2.FONT_HERSHEY_COMPLEX

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

    def face_data(image):
        face_width = 0  # making face width to zero

        # converting color image ot gray scale image
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detecting face in the image
        faces = face_detector.detectMultiScale(gray_image, 1.3, 5)#1.1, 4

        # looping through the faces detect in the image
        # getting coordinates x, y , width and height

        for (x, y , w ,h) in faces:

            # draw the rectangle on the face
            cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0 , 0), 3)
            '''roi_gray = gray_image[y:y+h, x:x+w]
            roi_color = image[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey ,ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (0, 255, 0), 5)
            #eye_width = ew'''
            face_width = w

        # getting face width in the pixels
        return face_width #eye_width


    # reading reference_image from directory
    ref_image = cv2.imread("my.png")

    # find the face width(pixels) in the reference_image
    ref_image_face_width = face_data(ref_image)

    # get the focal by calling "Focal_Length_Finder"
    # face width in reference(pixels),
    # Known_distance(centimeters),
    # known_width(centimeters)
    Focal_length_found = Focal_Length_Finder(
        Known_distance, Known_width, ref_image_face_width)

    print(Focal_length_found)

    # show the reference image
    ####cv2.imshow("ref_image", ref_image)

    # initialize the camera object so that we
    # can get frame from it
    cap = cv2.VideoCapture(0)

    # looping through frame, incoming from
    # camera/video
    while True:

        # reading the frame from camera
        _, frame = cap.read()

        # calling face_data function to find
        # the width of face(pixels) in the frame
        face_width_in_frame = face_data(frame)

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
            cv2.line(frame, (30, 30), (230, 30), BLACK, 28)

            # Drawing Text on the screen
            cv2.putText(
                frame, f"Distance: {round(Distance,2)} CM", (30, 35),
              fonts, 0.6,WHITE, 1)#GREEN
            d=Distance
            if d<=45:
                cv2.putText(frame,'too close to screen',(28,80),fonts,0.8,RED,2)
            else:
                cv2.putText(frame,'GooD',(28,80),fonts,0.8,GREEN,2)

        # show the frame on the screen
        cv2.imshow("frame", frame)

        # quit the program if you press 'q' on keyboard
        if cv2.waitKey(1) == ord("q"):
            break

    # closing the camera
    cap.release()

    # closing the the windows that are opened
    cv2.destroyAllWindows()
    
    return jsonify()

if __name__=="__main__":
    app.run()

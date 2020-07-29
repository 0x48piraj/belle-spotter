import face_recognition
import cv2
import math
import numpy as np

# performance tweaks
#   1. process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. only detect faces in every other frame of video

def phi(landmarks):
    """
    This dates back to the ancient Greeks, who believed that beauty was defined by a Golden Ratio, also known as the Divine Proportion, or “phi.”
    The Greeks discovered that 1:1.618 was the ideal proportion of two parts of any object, whether a flower petal, a nautilus seashell or the human face.
    According to this formula, a beautiful person’s face is roughly one and a half times longer than it is wide.
    """

    left_face = landmarks[0]['chin'][0]
    right_face = landmarks[0]['chin'][-1]
    bottom_face = landmarks[0]['chin'][8]

    ext_right_eye = landmarks[0]['right_eye'][3]
    int_right_eye = landmarks[0]['right_eye'][0]
    ext_left_eye = landmarks[0]['left_eye'][0]
    int_left_eye = landmarks[0]['left_eye'][3]
    ext_left_nose = landmarks[0]['nose_tip'][0]
    ext_right_nose = landmarks[0]['nose_tip'][-1]
    top_nose = landmarks[0]['nose_bridge'][0]
    bottom_nose = landmarks[0]['nose_tip'][2]

    width_face = math.dist(left_face, right_face)
    phi = round(width_face * 1.618)

    nasion_subnasale = math.dist(top_nose, bottom_nose)
    subnasale_mention = math.dist(bottom_nose, bottom_face)

    # nasion-<a>-subnasale-<b>-mention (a = 3/4 x b) (a = 43%, b = 57%)
    NSM = subnasale_mention / (nasion_subnasale + subnasale_mention)
    _bool_NSM = abs(NSM - 0.57) <= 0.01 # initial scalar (should be adjusted later)

    FWER = math.dist(ext_right_eye, int_right_eye) / width_face # eye - facial width ratio (right eye)
    _bool_FWER = abs(FWER - 0.20) <= 0.01 # initial scalar (should be adjusted later)

    FWNR = math.dist(ext_left_nose, ext_right_nose) / width_face # intercanthal distance - facial width ratio
    _bool_FWNR = abs(FWNR - 0.20) <= 0.01 # initial scalar (should be adjusted later)

    _top_face = tuple(np.subtract(bottom_face, (0, phi))) # ideal top (not actual)
    return _top_face, bottom_face, left_face, right_face, ext_right_eye, ext_left_eye, ext_right_nose, ext_left_nose, top_nose, bottom_nose


# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("barak.webp")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

known_face_encoding = obama_face_encoding

# Initialize some variables
score = 0
face_locations = []
face_encodings = []
results = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        if len(face_locations) > 1 or len(face_locations) == 0:
            print("Too many or too less people...")
            continue
        face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        results = []
        # TODO
        # perform the golden ratio stuff on each of the faces in the frame
        # append the results
        _top_face, bottom_face, left_face, right_face, ext_right_eye, ext_left_eye, ext_right_nose, ext_left_nose, top_nose, bottom_nose = phi(face_landmarks_list)
        match = face_recognition.compare_faces([known_face_encoding], face_encodings[0])

        if True in match:
            score = 100

        result = "Your score: {}%".format(score)
        results.append(result)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), result in zip(face_locations, results):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # test test
        cv2.line(frame, tuple(4 * np.array(bottom_face)), tuple(4 * np.array(_top_face)), (0,0,255), 2)

        landmarks = face_landmarks_list[0]

        # print(landmarks)

        # face mask
        for feature in landmarks.keys():
            pts = 4 * np.array(landmarks[feature])
            cv2.drawContours(frame, [pts], 0, (255,255,255), 2)

        # vertical ratio
        # distance between the lines should be 1/5 each
        cv2.line(frame, tuple(4 * np.array(left_face)), tuple(4 * np.add(left_face, (0,100))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(right_face)), tuple(4 * np.add(right_face, (0,100))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(ext_right_eye)), tuple(4 * np.add(ext_right_eye, (0,100))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(ext_left_eye)), tuple(4 * np.add(ext_left_eye, (0,100))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(ext_right_nose)), tuple(4 * np.add(ext_right_nose, (0,100))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(ext_left_nose)), tuple(4 * np.add(ext_left_nose, (0,100))), (0,0,255), 2)

        # horizontal ratio
        cv2.line(frame, tuple(4 * np.array(top_nose)), tuple(4 * np.add(top_nose, (100,0))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(bottom_nose)), tuple(4 * np.add(bottom_nose, (100,0))), (0,0,255), 2)
        cv2.line(frame, tuple(4 * np.array(bottom_face)), tuple(4 * np.add(bottom_face, (100,0))), (0,0,255), 2)

        # draw a label with the result below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, result, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # display the result
    cv2.imshow('Video', frame)

    # hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
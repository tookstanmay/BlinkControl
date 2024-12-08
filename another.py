import cv2
import numpy as np
import dlib
from math import hypot
from playsound import playsound
import time

# load sounds
sound = "sounds/sound.wav"
left_sound = "sounds/left.wav"
right_sound = "sounds/right.wav"

# we used the detector to detect the frontal face
detector = dlib.get_frontal_face_detector()

# it will dectect the facial landwark points 
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

font = cv2.FONT_HERSHEY_PLAIN

#Keyboard setting 
keyboard = np.zeros((600,1000,3),np.uint8)
#dictionary containing the letters, each one associated with an index.
keys_set_1 = {0: "Q", 1: "W", 2: "E", 3: "R", 4: "T",
              5: "A", 6: "S", 7: "D", 8: "F", 9: "G",
              10: "Z", 11: "X", 12: "C", 13: "V", 14: "<"}

keys_set_2 = {0: "Y", 1: "U", 2: "I", 3: "O", 4: "P",
              5: "H", 6: "J", 7: "K", 8: "L", 9: "_",
              10: "V", 11: "B", 12: "N", 13: "M", 14: "<"}

center_set = {0: "Yes", 1: "No", 2: "Drink Water", 3: "Washroom", 4: "Itching",
              5: "Turn body other side", 6: "fan increase", 7: "fan decrease", 8: "turn off light", 9: "turn on light",
              10: "give food", 11: "call ramesh", 12: "call suresh", 13: "go to sleep", 14: "feeling cold"}

def letter(letter_index, text, letter_light):
    # keys

    x, y = ((letter_index % 5) * 200), (int (letter_index / 5) * 200)

    width, height = 200, 200
    th = 3

    if letter_light == True:
        cv2.rectangle (keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 255, 255), -1)
    else:        
        cv2.rectangle (keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 0, 0), th)

    font_letter = cv2.FONT_HERSHEY_PLAIN
    font_th = 4
    font_scale = 10
    text_size = cv2.getTextSize(text, font_letter, font_scale, font_th)[0]
    width_text, height_text = text_size[0], text_size[1]
    text_x = int((width - width_text) / 2) + x
    text_y = int((height + height_text) / 2) + y

    cv2.putText (keyboard, text, (text_x, text_y), font_letter, font_scale, (255, 0, 0), font_th)

def letter_center(letter_index, text, letter_light):
    # Get the dimensions of the keyboard
    rows, cols, _ = keyboard.shape

    # Center section coordinates
    center_x_start = int(cols / 3)
    center_x_end = 2 * int(cols / 3)
    center_width = center_x_end - center_x_start

    # Define grid dimensions for the center section
    grid_cols = 2  # Two columns
    grid_rows = 8  # Maximum rows

    # Calculate cell width dynamically based on the maximum text length
    font_letter = cv2.FONT_HERSHEY_PLAIN
    font_scale = 1.5
    font_th = 2
    max_text_width = max(cv2.getTextSize(text, font_letter, font_scale, font_th)[0][0] for text in center_set.values())
    cell_width = max(max_text_width + 40, center_width // grid_cols)  # Add padding for aesthetics
    key_height = int(rows / grid_rows)

    # Calculate position of the current key
    x = center_x_start + (letter_index % grid_cols) * max_text_width
    y = (letter_index // grid_cols) * key_height

    th = 3  # Thickness of the border

    # Draw the key rectangle
    if letter_light:
        cv2.rectangle(keyboard, (x + th, y + th), (x + max_text_width - th, y + key_height - th), (255, 255, 255), -1)
    else:
        cv2.rectangle(keyboard, (x + th, y + th), (x + max_text_width - th, y + key_height - th), (255, 0, 0), th)

    # Add text to the rectangle
    text_size = cv2.getTextSize(text, font_letter, font_scale, font_th)[0]
    text_width, text_height = text_size[0], text_size[1]
    text_x = int((max_text_width - text_width) / 2) + x
    text_y = int((key_height + text_height) / 2) + y

    cv2.putText(keyboard, text, (text_x, text_y), font_letter, font_scale, (255, 0, 0), font_th)


def draw_menu():
    rows, cols, _ = keyboard.shape
    th_lines = 4  # Thickness of dividing lines

    # Draw dividing lines
    cv2.line(keyboard, (int(cols / 3) - int(th_lines / 2), 0), (int(cols / 3) - int(th_lines / 2), rows),
             (51, 51, 51), th_lines)
    cv2.line(keyboard, (2 * int(cols / 3) - int(th_lines / 2), 0), (2 * int(cols / 3) - int(th_lines / 2), rows),
             (51, 51, 51), th_lines)

    # Add text labels for each section
    font_scale = 6
    font_thickness = 5
    cv2.putText(keyboard, "LEFT", (50, 300), font, font_scale, (255, 255, 255), font_thickness)
    cv2.putText(keyboard, "C", (int(cols / 3) + 50, 300), font, font_scale, (255, 255, 255), font_thickness)
    cv2.putText(keyboard, "RIGHT", (2 * int(cols / 3) + 50, 300), font, font_scale, (255, 255, 255), font_thickness)


#We create a function that we will need later on to detect the medium point.
#On this function we simply put the coordinates of two points and will return the medium point 
#(the points in the middle between the two points).
def midpoint (p1, p2):
    return int ((p1.x + p2.x)/2), int ((p1.y + p2.y)/2)

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint (facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint (facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    # hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    # ver_line = cv2.line (frame, center_top, center_bottom, (0, 0, 255), 2)

    hor_line_length = hypot ((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_length = hypot ((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_length / ver_line_length
    return ratio

def eyes_contour_points(facial_landmarks):
    left_eye = []
    right_eye = []
    for n in range(36, 42):
        x = facial_landmarks.part(n).x
        y = facial_landmarks.part(n).y
        left_eye.append([x, y])
    for n in range(42, 48):
        x = facial_landmarks.part(n).x
        y = facial_landmarks.part(n).y
        right_eye.append([x, y])
    left_eye = np.array(left_eye, np.int32)
    right_eye = np.array(right_eye, np.int32)
    return left_eye, right_eye

def get_gaze_ratio(eye_points, facial_landmarks):
    # Gaze Detection
    left_eye_region = np.array ([
        (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
        (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
        (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
        (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
        (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
        (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y),
    ], np.int32)        

    height, width, _ = frame.shape
    mask = np.zeros ((height, width), np.uint8)

    cv2.polylines (mask, [left_eye_region], True, 255, 2)
    cv2.fillPoly (mask, [left_eye_region], 255)
    eye = cv2.bitwise_and (gray, gray, mask=mask)

    min_x = np.min (left_eye_region[:, 0])
    max_x = np.max (left_eye_region[:, 0])

    min_y = np.min (left_eye_region[:, 1])
    max_y = np.max (left_eye_region[:, 1])

    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv2.threshold (gray_eye, 70, 255, cv2.THRESH_BINARY)

    height, width = threshold_eye.shape

    left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    left_side_white = cv2.countNonZero (left_side_threshold)
        
    right_side_threshold = threshold_eye[0: height, int(width / 2): width]
    right_side_white = cv2.countNonZero (right_side_threshold)

    gaze_ratio = 0.5

    if right_side_white == 0:
        gaze_ratio = 0
    else:
        gaze_ratio = left_side_white / right_side_white
    
    return gaze_ratio

# Variables to track blinks
last_blink_time = 0
double_blink_detected = False

def detect_double_blink(eye_points, facial_landmarks):
    global last_blink_time, double_blink_detected
    
    # Get the blinking ratio
    blink_ratio = get_blinking_ratio(eye_points, facial_landmarks)

    # Check if the ratio exceeds the threshold (indicating a blink)
    if blink_ratio > 5.5:
        current_time = time.time()
        
        # Check if this blink occurs soon after the last one
        if current_time - last_blink_time <= 0.5:
            double_blink_detected = True
        else:
            double_blink_detected = False
        
        # Update the last blink time
        last_blink_time = current_time
    
    return double_blink_detected


# to open webcab to capture the image
cap = cv2.VideoCapture(0)


#Going to create a white image which is going to be the board where we will put the letters we click from the virtual keyboard.
board = np.zeros((300,1400), np.uint8)
board[:]=255

#Counters
#To count the number of the frames
frames = 0
#The blinking_frames variable will keep track of the frames in a row in which the eyes are blinking.
blinking_frames = 0
letter_index = 0
frames_to_blink = 5
frames_active_letter = 15

#Text and keyboard setting
keyboard_selected = "out"
last_keyboard_selected = "out"
#Text is going to contain all the letter that we will press when we blink our eyes.
text = ""
selected_keyboard_menu = True
keyboard_selection_frames = 0

time.sleep (10)

while True:
    _, frame = cap.read()
    rows, cols, _ = frame.shape
    keyboard[:] = (0,0,0)
    frames += 1
    
    frame = cv2.flip (frame, 1)

    #change the color of the frame captured by webcam to grey
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Draw a white space for loading bar
    frame[rows - 50: rows, 0: cols] = (255, 255, 255)
    
    if selected_keyboard_menu == True:
        draw_menu()
        
    #Keyboard selected
    if keyboard_selected == "left":
        keys_set = keys_set_1
    elif keyboard_selected == "center":
        keys_set = center_set
    else:
        keys_set = keys_set_2

    active_letter = keys_set[letter_index]
    
    # to detect faces from grey color frame
    faces = detector(gray)
    for face in faces:
        
        #to detect the landmarks of a face
        landmarks = predictor(gray, face)
        
        # left_eye,right_eye = eyes_contour_points(landmarks)
        
        # Find blinking ratio of both eyes, detect blinking 
        right_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        left_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
        
        # Eyes color
        #right now colo red around eyes cause we are not blinking them
        # cv2.polylines(frame, [left_eye], True, (0, 0, 255), 2)
        # cv2.polylines(frame, [right_eye], True, (0, 0, 255), 2)
        
        if selected_keyboard_menu is True:
            #Detecting gaze to select left or right keybaord.
            gaze_ratio_left_eye = get_gaze_ratio ([36, 37, 38, 39, 40, 41], landmarks)
            gaze_ratio_right_eye = get_gaze_ratio ([42, 43, 44, 45, 46, 47], landmarks)
            gaze_ratio = (gaze_ratio_left_eye + gaze_ratio_right_eye) / 2
            
            if gaze_ratio < 0.8:
                cv2.putText (frame, "L", (50, 100), font, 2, (0, 0, 255), 3)
                keyboard_selected = "left"
                keyboard_selection_frames += 1

                # If Kept gaze on one side more than 15 frames, move to keyboard
                if keyboard_selection_frames == 15:
                    selected_keyboard_menu = False
                    playsound(left_sound)

                    #set frames count to zero when keyboard is selected.
                    frames = 0
                    keyboard_selection_frames = 0
                    if last_keyboard_selected != keyboard_selected:
                        last_keyboard_selected = keyboard_selected
                        keyboard_selection_frames = 0
            elif gaze_ratio >= 0.8 and gaze_ratio < 1.9:
                cv2.putText (frame, "Centeraaaaaaa", (50, 100), font, 2, (0, 0, 255), 3)
                keyboard_selected = "center"
                keyboard_selection_frames += 1

                if keyboard_selection_frames == 15:
                    selected_keyboard_menu = False
                    playsound (sound=sound)

                    frames = 0
                    keyboard_selection_frames = 0
                    if last_keyboard_selected != keyboard_selected:
                        last_keyboard_selected = keyboard_selected
                        keyboard_selection_frames = 0
            elif gaze_ratio > 1.9:
                cv2.putText (frame, "Right", (50, 100), font, 2, (0, 0, 255), 3)
                keyboard_selected = "right"
                keyboard_selection_frames += 1

                # If Kept gaze on one side more than 15 frames, move to keyboard
                if keyboard_selection_frames == 15:
                    selected_keyboard_menu = False
                    playsound(right_sound)

                    #set frames count to zero when keyboard is selected.
                    frames = 0
                    keyboard_selection_frames = 0
                    if last_keyboard_selected != keyboard_selected:
                        last_keyboard_selected = keyboard_selected
                        keyboard_selection_frames = 0
                            
        else:
            #Detect the blinking to selec the keyboard that is lighting up
            if blinking_ratio > 5.5:
                #cv2.putText(frame, "BLINKING", (50, 150), font, 4, (255, 0, 0),thickness = 3)
                blinking_frames = blinking_frames + 1
                frames = frames -1
                
                #Show green eyes when closed
                # cv2.polylines(frame, [left_eye], True, (0, 255, 0), 2)
                # cv2.polylines(frame, [right_eye], True, (0, 255, 0), 2)
                
                #Typing letters
                if blinking_frames == frames_to_blink:
                    if active_letter != "<" or active_letter != ">":
                        text += active_letter
                    if active_letter == "_":
                        text += " "
                    playsound(sound=sound)
                    selected_keyboard_menu = True
            else:
                blinking_frames = 0   

    #Display letters on the keyboard            
    if selected_keyboard_menu is False:
        if frames == frames_active_letter:
            letter_index += 1
            frames = 0
        if letter_index == 15:
            letter_index = 0
        if keyboard_selected == "center":
            for i in range (15):
                if i == letter_index:
                    light = True
                else:
                    light = False
                letter_center(i, keys_set[i], light)
        else:
            for i in range(15):
                if i == letter_index:
                    light = True
                else:
                    light = False
                letter(i, keys_set[i], light)
    
    
    
    # Show the text we're writing on the board
    cv2.putText(board, text, (80, 100), font, 9, 0, 3)

    # Blinking loading bar
    # percentage_blinking = blinking_frames / frames_to_blink
    # loading_x = int(cols * percentage_blinking)
    # cv2.rectangle(frame, (0, rows - 50), (loading_x, rows), (51, 51, 51), -1)
    
    # cv2.imshow("Frame", frame)
    cv2.imshow("Virtual keyboard", keyboard)
    cv2.imshow("Board", board)    

    key = cv2.waitKey(1)
    #close the webcam when escape key is pressed
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
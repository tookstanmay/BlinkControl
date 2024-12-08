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


def draw_menu(j, light_board):
    rows, cols, _ = keyboard.shape

    # Add text labels for each section
    font_scale = 6
    font_thickness = 5
    section_width = cols // 3

    # Define colors
    active_color = (255, 255, 255)
    default_color = (51, 51, 51) 
    text_color = (0, 0, 0) if light_board else (255, 255, 255)

    # Highlight or keep the section default
    rect_color = active_color if light_board else default_color
    cv2.rectangle(keyboard, (j * section_width, 0), ((j + 1) * section_width, rows), rect_color, -1)

    # Draw the text for each section
    labels = ["L", "C", "R"]
    x_pos = j * section_width + section_width // 2 - 50
    y_pos = rows // 2 + 50
    cv2.putText(keyboard, labels[j], (x_pos, y_pos), font, font_scale, text_color, font_thickness)


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


# to open webcab to capture the image
cap = cv2.VideoCapture(0)


# create a white image which is going to be the board where we will put the letters we click from the virtual keyboard.
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
is_board_selected = False
keyboard_selection_frames = 0
board_types = ["left", "center", "right"]
board_index = 0
menu_frames = 0

while True:
    _, frame = cap.read()
    rows, cols, _ = frame.shape
    keyboard[:] = (0,0,0)
    frames += 1
    menu_frames += 1
    
    frame = cv2.flip (frame, 1)

    #change the color of the frame captured by webcam to grey
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
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
        
        # Find blinking ratio of both eyes, detect blinking 
        right_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        left_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2


        #Detect the blinking to selec the keyboard that is lighting up
        if blinking_ratio > 5.5:
            cv2.putText(frame, "BLINKING", (50, 150), font, 4, (255, 0, 0),thickness = 3)
            blinking_frames = blinking_frames + 1
            frames = frames - 1
            menu_frames = menu_frames - 1

            if is_board_selected == False:
                if blinking_frames == 5:
                    is_board_selected = True
                    keyboard_selected = board_types[board_index]
                    frames = 0
                    letter_index = 0
                    menu_frames = 0
                    board_index = 0
                    playsound (sound=sound)
                    # if keyboard_selected == "left":
                    #     playsound (sound=left_sound)
                    # elif keyboard_selected == "right":
                    #     playsound (sound=right_sound)
                    # else:
                    #     playsound (sound=sound)

            else:    
                #Typing letters
                if blinking_frames == 5:
                    if active_letter != "<" or active_letter != ">":
                        text += active_letter
                    if active_letter == "_":
                        text += " "
                    playsound(sound=sound)
                    is_board_selected = False
                    menu_frames = 0
                    board_index = 0
                    frames = 0
                    letter_index = 0
        else:
            blinking_frames = 0   


    # selecting board
    if is_board_selected == False:
        if menu_frames == 15:
            board_index += 1
            menu_frames = 0
        if board_index == 3:
            board_index = 0
        for j in range (3):
            if j == board_index:
                light_board = True
            else:
                light_board = False
            draw_menu (j, light_board)


    #Display letters on the keyboard            
    if is_board_selected == True:
        if frames == 15:
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
    
    # cv2.imshow("Frame", frame)
    cv2.imshow("Board", board)    
    cv2.imshow("Virtual keyboard", keyboard)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
print (text)
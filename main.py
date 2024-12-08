import cv2
import numpy as np
import dlib
from math import hypot
from playsound import playsound

# load sounds
sound = "sounds/sound.wav"
left_sound = "sounds/left.wav"
right_sound = "sounds/right.wav"

cap = cv2.VideoCapture(0)
board = np.zeros ((500, 500), np.uint8)
board[:] = 255

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
font = cv2.FONT_HERSHEY_PLAIN

# keyboard settings
keyboard = np.zeros ((600, 1000, 3), np.uint8)

key_set_1 = {
    0: "Q", 1: "W", 2: "E", 3: "R", 4: "T",
    5: "A", 6: "S", 7: "D", 8: "F", 9: "G",
    10: "Z", 11: "X", 12: "C", 13: "V", 14: "B"
}

def letter(letter_index, letter_light):
    # keys

    x, y = ((letter_index % 5) * 200), (int (letter_index / 5) * 200)

    text = key_set_1[letter_index]
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

def draw_menu_center():
    rows, cols, _ = keyboard.shape
    th_lines = 4  # Thickness of dividing lines

    # Draw dividing lines for the center section
    cv2.line(keyboard, (int(cols / 3) - int(th_lines / 2), 0), (int(cols / 3) - int(th_lines / 2), rows),
             (51, 51, 51), th_lines)
    cv2.line(keyboard, (2 * int(cols / 3) - int(th_lines / 2), 0), (2 * int(cols / 3) - int(th_lines / 2), rows),
             (51, 51, 51), th_lines)

    # Center section coordinates
    center_x_start = int(cols / 3)
    center_x_end = 2 * int(cols / 3)
    center_width = center_x_end - center_x_start

    # Draw the center area text
    center_set = {
        0: "Yes", 1: "No", 2: "Drink Water", 3: "Washroom", 4: "Itching",
        5: "Turn body other side", 6: "fan increase", 7: "fan decrease",
        8: "turn off light", 9: "turn on light", 10: "give food", 11: "call ramesh",
        12: "call suresh", 13: "go to sleep", 14: "feeling cold"
    }

    # Calculate text placement
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    padding = 20  # Padding between lines
    text_height = cv2.getTextSize("Sample", font, font_scale, font_thickness)[0][1]
    y_start = (rows - (len(center_set) * (text_height + padding))) // 2  # Vertical centering

    for i, text in center_set.items():
        y_position = y_start + i * (text_height + padding)
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_width = text_size[0][0]

        # Ensure text is horizontally centered
        text_x = center_x_start + (center_width - text_width) // 2
        text_y = y_position + text_height

        # Draw the text
        cv2.putText(keyboard, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)


# blinking feature
frames = 0
letter_index = 0
blinking_frames = 0
text = ""

keyboard_selected = "center"
last_keyboard_selected = "center"

while True:
    _, frame = cap.read()
    
    keyboard[:] = (0, 0, 0)
    frames += 1
    frame = cv2.flip (frame, 1)
    # frame = cv2.resize (frame, None, fx=0.5, fy=0.5)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    active_letter = key_set_1[letter_index]

    faces = detector(gray)
    for face in faces:

        landmarks = predictor(gray, face)

        # Find blinking ratio of both eyes, detect blinking 
        right_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        left_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)

        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        if blinking_ratio > 5.5:
            cv2.putText (frame, "Blinking", (50, 150), font, 5, (0, 255, 0))
            blinking_frames += 1
            frames -= 1

            if blinking_frames == 5:
                text += active_letter
                playsound (sound=sound)
        else:
            blinking_frames = 0    

        # elif right_eye_ratio > 5:
        #     cv2.putText (frame, "Blinking", (50, 150), font, 5, (0, 255, 0))
        # elif left_eye_ratio > 5:
        #     cv2.putText (frame, "Blinking", (50, 150), font, 5, (0, 255, 0))


        gaze_ratio_left_eye = get_gaze_ratio ([36, 37, 38, 39, 40, 41], landmarks)
        gaze_ratio_right_eye = get_gaze_ratio ([42, 43, 44, 45, 46, 47], landmarks)
        gaze_ratio = (gaze_ratio_left_eye + gaze_ratio_right_eye) / 2

        # around 1 and 2 for center
        # around > 2 for right
        # around < 0.8 for left

        if gaze_ratio < 0.8:
            cv2.putText (frame, str(gaze_ratio), (50, 100), font, 2, (0, 0, 255), 3)
            # cv2.putText (frame, "L", (50, 100), font, 2, (0, 0, 255), 3)
            keyboard_selected = "left"
            if keyboard_selected != last_keyboard_selected:
                playsound (left_sound)
                last_keyboard_selected = keyboard_selected
        elif gaze_ratio >= 1 and gaze_ratio < 1.4:
            # cv2.putText (frame, "Centeraaaaaaa", (50, 100), font, 2, (0, 0, 255), 3)
            cv2.putText (frame, str(gaze_ratio), (50, 100), font, 2, (0, 0, 255), 3)

        elif gaze_ratio > 1.6:
            # cv2.putText (frame, "Right", (50, 100), font, 2, (0, 0, 255), 3)
            cv2.putText (frame, str(gaze_ratio), (50, 100), font, 2, (0, 0, 255), 3)
            keyboard_selected = "right"
            if keyboard_selected != last_keyboard_selected:
                playsound (right_sound)
                last_keyboard_selected = keyboard_selected

            
        # cv2.putText (frame, str (gaze_ratio), (50, 100), font, 2, (0, 0, 255), 3)

        # put letter
        if frames == 15:
            frames = 0
            letter_index += 1
        
        if letter_index == 15:
            letter_index = 0

        for i in range (15):
            if i == letter_index:
                letter (i, True)
            else:
                letter (i, False)

        # draw_menu_center()

        cv2.putText(board, text, (10, 100), font, 4, 0, 3)

    # cv2.imshow ("Frame", frame)
    cv2.imshow ("Keyboard", keyboard)
    # cv2.imshow ("Board", board)

    key = cv2.waitKey(1)
    if key == 81:
        break

cap.release()
cv2.destroyAllWindows()

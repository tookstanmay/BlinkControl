import cv2
import numpy as np

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


for i in range (15):
    letter (i, True)


cv2.imshow ("keyboard", keyboard)
cv2.waitKey (0)
cv2.destroyAllWindows ()
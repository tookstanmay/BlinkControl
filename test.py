import pyglet
import time

left_sound = pyglet.media.load ("sounds/left.wav")
right_sound = pyglet.media.load ("sounds/right.wav")
left_sound.play()
time.sleep (1)
right_sound.play ()
time.sleep (1)
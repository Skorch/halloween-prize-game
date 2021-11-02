import RPi.GPIO as GPIO 
import time

CL = [0, 131, 147, 165, 175, 196, 211, 248] 
CM = [0, 262, 294, 330, 350, 393, 441, 495] 
CH = [0, 525, 589, 661, 700, 786, 882, 990]
# Frequency of Bass tone in C major
# Frequency of Midrange tone in C major
# Frequency of Treble tone in C major
Buzzer = -1

losing_sound = {
    "notes": [ CL[5],CL[4],CL[3],CL[2],CL[1] ],
    "beats": [ 1,1,1,1,1 ]

}


winning_sound = {
    "notes": [ CH[1],CH[2],CH[3],CH[4],CH[5] ],
    "beats": [ 1,1,1,1,1 ]

}

tick_sounds = [ CH[1],CH[2],CH[3],CH[4],CH[5] ]

mute_sound = False

def start_sound(note):
    if mute_sound:
        return

    Buzz.start(50)
    Buzz.ChangeFrequency(note) 

def stop_sound():
    Buzz.stop()  

def play_sounds(sound):

    if mute_sound:
        return

    notes = sound["notes"]
    beats = sound["beats"]
    Buzz.start(50)   
    for i in range(0, len(notes)): 
        Buzz.ChangeFrequency(notes[i]) # Change the frequency along the song note
        time.sleep(beats[i] * 0.1) # delay a note for beat * 0.5s 
    Buzz.stop()

def setup_buzzer(pin = 25, mute = False):
    global Buzzer, mute_sound
    Buzzer = pin
    mute_sound = mute

    GPIO.setup(Buzzer, GPIO.OUT, initial=GPIO.HIGH)
    # GPIO.setup(Buzzer, GPIO.OUT)
    global Buzz
    Buzz = GPIO.PWM(Buzzer, 440)
# Numbers GPIOs by physical location # Set pins' mode is output
# Assign a global variable to replace GPIO.PWM # 440 is initial frequency.
    # Buzz.start(50)    

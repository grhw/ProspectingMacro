from time import sleep
import numpy as np
import easyocr
import pynput
import utils
import time
import mss

config = utils.get_config()

print("OCR loading... (First time will take longer)")
ss = mss.mss()
ocr = easyocr.Reader(["en"])
print("Done.")

mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()

class states:
    dig = "Collect Deposit"
    shake = "Pan"
    walk = "Walking"

class fullness:
    empty = 0
    between = 1
    full = 2

state = states.walk
nothing_count = 10
is_using_w_instead_of_s = True

def update_state():
    global state,nothing_count
    image = np.array(ss.grab(config["bbox"]["state"]))
    text = ocr.readtext(image,detail=0,allowlist="Collect DepositPan")
    
    last = state
    if text == states.dig:
        state = states.dig
        nothing_count = 10
    elif text == states.shake:
        state = states.shake
        nothing_count = 10
    else:
        nothing_count -= 1
        if nothing_count < 0:
            state = states.walk
    
    print("Text:",text)
    if last != state:
        print("Mode:",state)

dig_cooldown = time.time()
last_dig = time.time()
def dig():
    global dig_cooldown,last_dig
    image = utils.to_pil(ss.grab(config["bbox"]["progress"]))
    
    if utils.is_color(image.getpixel((1,1)),(255,255,255)):
        mouse.release(pynput.mouse.Button.left)
        dig_cooldown = time.time()
    if not utils.is_color(image.getpixel((1,0)),(15,250,0)) and time.time()-dig_cooldown > 1:
        mouse.press(pynput.mouse.Button.left)
        last_dig = time.time()
    
    if time.time()-last_dig > 3:
        print("stuck?")
        last_dig = time.time()
        mouse.release(pynput.mouse.Button.left)

def shake():
    mouse.press(pynput.mouse.Button.left)    
    sleep(1)
    mouse.release(pynput.mouse.Button.left)

def full_state():
    fill = utils.to_pil(ss.grab(config["bbox"]["fill"]))
    w,h = fill.size
    
    if utils.is_color(fill.getpixel((0,0)),(140,140,140)):
        return fullness.empty
    if utils.is_color(fill.getpixel((w-1,0)),(140,140,140)):
        return fullness.full
    return fullness.between

while True:
    sleep(1/144)
    last = state
    if state == states.dig:
        dig()
        if full_state() == fullness.full:
            state = states.walk
    elif state == states.shake:
        shake()
        if full_state() == fullness.empty:
            state = states.walk
    
    if state == states.walk:
        while state != last:
            key = "w" if is_using_w_instead_of_s else "s"
            keyboard.press(key)
            sleep(0.25)
            keyboard.release(key)
            update_state()
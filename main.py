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

dig_cooldown = time.time()
last_dig = time.time()
def update_state():
    global state,nothing_count,is_using_w_instead_of_s,last_dig
    image = np.array(ss.grab(config["bbox"]["state"]))
    text = ocr.readtext(image,detail=0,allowlist="Collect DepositPan")
    
    last = state
    if states.dig in text:
        state = states.dig
        nothing_count = 10
        last_dig = time.time()
    elif states.shake in text:
        state = states.shake
        nothing_count = 10
    else:
        nothing_count -= 1
        if nothing_count < 0:
            state = states.walk
    
    if last != state:
        print("Mode:",state)
        print("Text:",text)

def dig():
    global dig_cooldown,last_dig
    image = utils.to_pil(ss.grab(config["bbox"]["progress"]))
    
    if utils.is_color(image.getpixel((1,7)),(255,255,255)) or utils.is_color(image.getpixel((1,1)),(255,255,255)):
        mouse.release(pynput.mouse.Button.left)
        dig_cooldown = time.time()
        last_dig = time.time()
    if not utils.is_color(image.getpixel((1,0)),(15,250,0)) and time.time()-dig_cooldown > 1:
        mouse.press(pynput.mouse.Button.left)
    
    if time.time()-last_dig > 2:
        print("stuck?")
        last_dig = time.time()
        mouse.release(pynput.mouse.Button.left)
        return True

def shake():
    mouse.press(pynput.mouse.Button.left)    
    sleep(1)
    mouse.release(pynput.mouse.Button.left)

def is_empty():
    shot = ss.grab(config["bbox"]["fill"])
    num = np.array(shot)
    fill = utils.to_pil(shot)
    if utils.is_color(fill.getpixel((0,0)),(140,140,140)):
        prog = ("".join(ocr.readtext(num,detail=0,allowlist="0123456789/."))).split("/")[0]
        print(prog)
        if prog == "0":
            return True

def is_full():
    shot = ss.grab(config["bbox"]["fill"])
    fill = utils.to_pil(shot)
    w,h = fill.size
    if not utils.is_color(fill.getpixel((w-1,1)),(140,140,140)):
        return True
prev_state = None

while True:
    sleep(1/144)

    if state == states.dig:
        if dig():
            if is_full():
                print("Done")
                state = states.walk

    elif state == states.shake:
        shake()
        if is_empty():
            state = states.walk
            #sleep(1)
            #keyboard.press("`")
            #sleep(0.05)
            #keyboard.release("`")
            #mouse.position = (1920+1151,1032)
            #sleep(0.05)
            #mouse.press(pynput.mouse.Button.left)
            #sleep(0.05)
            #mouse.release(pynput.mouse.Button.left)
            #sleep(0.05)
            #keyboard.press("`")
            #sleep(0.05)
            #keyboard.release("`")

    if state == states.walk:
        while state == prev_state or state == states.walk:
            key = "w" if is_using_w_instead_of_s else "s"
            keyboard.press(key)
            sleep(0.25)
            keyboard.release(key)
            update_state()
        print("Done walking")
        is_using_w_instead_of_s = not is_using_w_instead_of_s
    prev_state = state

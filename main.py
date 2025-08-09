from time import sleep
from mss import mss
from PIL import Image
import pynput
import time
import pytesseract

mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()

coords = {
    "progress": {"left": 1522+1920, "top": 608, "width": 100, "height": 531},
    "action_text": {"left": 881+1920, "top": 1255, "width": 802, "height": 72},
    "bar": {"left": 960+1920, "top": 1143, "width": 802, "height": 2}
}

class Modes:
    moving = "Moving"
    digging = "Collect Deposit"
    shaking = "Pan"

tes_config = "--psm 7 --user-patterns tes_modes.txt"
ss = mss()

def is_color(rgb, ref, leniency=15):
    return sum(abs(a-b) for a, b in zip(rgb, ref)) < leniency

def to_pil(sct_img):
    return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

mode = Modes.moving
nothing_count = 15
fill_count = 5

def update_mode():
    global mode, nothing_count, fill_count
    img = to_pil(ss.grab(coords["action_text"]))
    text = pytesseract.image_to_string(img, config=tes_config)

    last_mode = mode
    if Modes.digging in text:
        mode = Modes.digging
        fill_count = 10
        nothing_count = 15
        clocks["dig_duration"] = time.time()
    elif Modes.shaking in text:
        mode = Modes.shaking
        nothing_count = 15
    else:
        nothing_count -= 1
        if nothing_count < 0:
            mode = Modes.moving

    if mode != last_mode:
        print("mode:", mode)
        print("text:", text.strip())

clocks = {
    "dig_cooldown": time.time(),
    "dig_duration": time.time()
}

is_using_w = True

while True:
    last = mode
    if mode == Modes.digging:
        if time.time() - clocks["dig_cooldown"] > 3:
            progress = to_pil(ss.grab(coords["progress"]))
            hit = is_color(progress.getpixel((13, 19)), (255, 255, 255)) or is_color(progress.getpixel((13, 8)), (255, 255, 255))

            if not is_color(progress.getpixel((77,516)),(140,140,140)):
                fill_count -= 1
            if fill_count < 0:
                mode = Modes.moving
            if hit:
                mouse.release(pynput.mouse.Button.left)
                clocks["dig_cooldown"] = time.time()
                fill_count = 10
            elif time.time() - clocks["dig_duration"] > 5:
                mouse.release(pynput.mouse.Button.left)
                print("stuck?")
                clocks["dig_duration"] = time.time()
        sleep(1)
        mouse.release(pynput.mouse.Button.left)

    if mode == Modes.moving:
        print("moving...")
        is_using_w = not is_using_w
        move_key = "w" if is_using_w else "s"
        while mode == Modes.moving or mode == last:
            update_mode()
            if mode != Modes.moving and mode != last:
                break
            keyboard.press(move_key)
            sleep(0.25)
            keyboard.release(move_key)
            sleep(0.25)

    if mode != Modes.digging:
        update_mode()

    sleep(1/144)

import shutil
from PIL import Image
import pywinctl as pwc

def is_color(rgb, ref, leniency=15):
    return sum(abs(a - b) for a, b in zip(rgb, ref)) < leniency

def to_pil(sct_img):
    return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

roblox_names = [
    "Sober",
    "Roblox",
    "Main" # sober alias???
]
def get_roblox_name():
    for i in pwc.getAllTitles():
        if i in roblox_names:
            return i
    for i in pwc.getAllTitles():
        for v in roblox_names:
            if v.lower() in i.lower():
                return i

def get_roblox_bbox():
    name = get_roblox_name()
    print("Found window:",name)
    if name:
        win = pwc.getWindowsWithTitle(name)[0]
        return {
            "left": win.left,
            "top": win.top,
            "width": win.width,
            "height": win.height,
        }

print(get_roblox_bbox())
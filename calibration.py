import json
import os
import shutil
import mss
import utils

ss = mss.mss()

print("\n\n!! Before starting:")
print("-  Hold left click")
print("-  Press escape")
print("-  Release left click")
print("-  Press escape again")
print("-  Press enter here, make sure it isn't blocking gameplay UI (except for quests)")
input("\n\nPress enter when ready\n...")

mon = utils.get_roblox_bbox()
screen = utils.to_pil(ss.grab(mon))
half_w,half_y = round(mon["width"]/2),round(mon["height"]/2)

def calc_fill_bbox():
    vert = screen.crop([half_w-1,0,half_w+1,mon["height"]])
    _,h = vert.size
    top,bottom = 0,0
    
    for i in range(h):
        col = vert.getpixel((1,i))
        if utils.is_color(col,(140,140,140),2):
            if top == 0:
                top = i
            bottom = i
    
    left,right = 0,0
    horz = screen.crop([0,top,mon["width"],bottom])
    w,_ = horz.size
    for i in range(w):
        col = horz.getpixel((i,1))
        if utils.is_color(col,(140,140,140)):
            if left == 0:
                left = i
            right = i
    
    return (left,top,right,bottom)

def get_state(fill):
    return (fill[0]-20,fill[3]+30,fill[2]+20,mon["height"]-100)

def get_progress(right_fill,top_fill):
    right = 0
    left = 0
    top = 0
    
    vert = screen.crop([half_w,0,right_fill,top_fill])
    w,h = vert.size
    
    vert.save("test2.png")
    for y in range(h):
        for x in range(w):
            if utils.is_color(vert.getpixel((x,y)),(15,250,0)):
                if top == 0:
                    top = y
                if left == 0:
                    left = half_w+x
                right = half_w+x

    return (left,top,right,top+40)

fill_bbox = calc_fill_bbox()
progress = get_progress(fill_bbox[2],fill_bbox[1])
state = get_state(fill_bbox)

print("-- Generated Config --")
config = {
    "screen": {
        "width": mon["width"],
        "height": mon["height"],
    },
    "bbox": {
        "progress": progress,
        "fill": fill_bbox,
        "state": state
    }
}

print(config)

print("-- Showing preview...")
os.makedirs("preview/",exist_ok=True)
for key in config["bbox"].keys():
    screen.crop(config["bbox"][key]).save("preview/"+key+".png")

print("\n\n!! Check `preview/` folder.")
print("-  progress.png: Green bar (the top of the dig bar)")
print("-  fill.png: Pan fill")
print("-  state.png: Action text (should say `Collect Deposit`)")
input("\n\nIf everything looks correct, press enter.\nif not, press CTRL+C and try again.\n...")

print("saving...")
with open("calibrated.json","w+") as f:
    f.write(json.dumps(config,indent=4))
shutil.rmtree("preview/")
print("\nDone cleaning! Keep note you will have to do this again if you change resolution.")
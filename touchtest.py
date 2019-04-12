#!/usr/bin/python3



import pygame, time, evdev, select, math, psutil, socket, datetime


Touchscreen = evdev.InputDevice('/dev/input/by-path/platform-3f204000.spi-event')
Touchscreen.grab()

surfaceSize = (480, 320)

print(Touchscreen.capabilities(verbose=True))

x = 500
y = 500
maxx = 0
minx = 999999

maxy = 0
miny = 999999

# Min X = 248
# Max X = 3392
# Min Y = 226
# Max Y = 3959

tftOrig = (248,3959)
tftEnd = (3392,226)
tftDelta = (tftEnd [0] - tftOrig [0], tftEnd [1] - tftOrig [1])
tftAbsDelta = (abs(tftEnd [0] - tftOrig [0]), abs(tftEnd [1] - tftOrig [1]))

def getPixelsFromCoordinates(coords):
    # TODO check divide by 0!
    if tftDelta [0] < 0:
        x = float(tftAbsDelta [0] - coords [0] + tftEnd [0]) / float(tftAbsDelta [0]) * float(surfaceSize [1])
    else:    
        x = float(coords [0] - tftOrig [0]) / float(tftAbsDelta [1]) * float(surfaceSize [1])
    if tftDelta [1] < 0:
        y = float(tftAbsDelta [1] - coords [1] + tftEnd [1]) / float(tftAbsDelta [1]) * float(surfaceSize [0])
    else:        
        y = float(coords [1] - tftOrig [1]) / float(tftAbsDelta [0]) * float(surfaceSize [0])
    return (int(x), int(y))

'''
for event in Touchscreen.read_loop():
    if event.type == evdev.ecodes.EV_KEY:
         print(evdev.categorize(event))
    if event.type == evdev.ecodes.EV_ABS:
        if event.code == 0:
            x = event.value
            if x > maxx:
                maxx = x
            if x < minx:
                minx = x
        elif event.code == 1:
            y = event.value
            if y > maxy:
                maxy = y
            if y < miny:
                miny = y
    #print('X = ' + str(x) + ' | Y = ' + str(y))
    #print(maxy,miny,sep=" - ")
    pxl = getPixelsFromCoordinates((x,y))
    print(pxl,(x,y))
'''
x = 0
y = 0
while True:    
    event = Touchscreen.read_one()
    if event is not None:
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == 0:
                x = event.value
            elif event.code == 1:
                y = event.value
            pxl = getPixelsFromCoordinates((x,y))
            #print(pxl,(x,y))
        if event.type == evdev.ecodes.EV_KEY:
            if event.code == 330 and event.value == 0:
                print(pxl)
                #print(evdev.categorize(event),event.code,event.value,sep=" - ")
    else:
        time.sleep(1)




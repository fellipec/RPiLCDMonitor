#!/usr/bin/python3

##
# Prerequisites:
# A Touchscreen properly installed on your system:
# - a device to output to it, e.g. /dev/fb1
# - a device to get input from it, e.g. /dev/input/touchscreen
##

import pygame, time, evdev, select, math, psutil, socket, datetime, os

# Very important: the exact pixel size of the TFT screen must be known so we can build graphics at this exact format
surfaceSize = (480, 320)

# Note that we don't instantiate any display!
pygame.init()

# The pygame surface we are going to draw onto. 
# /!\ It must be the exact same size of the target display /!\
lcd = pygame.Surface(surfaceSize)

#Touchscreen
Touchscreen = evdev.InputDevice('/dev/input/by-path/platform-3f204000.spi-event')
Touchscreen.grab()

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



# This is the important bit
def refresh():
    # We open the TFT screen's framebuffer as a binary file. Note that we will write bytes into it, hence the "wb" operator
    f = open("/dev/fb1","wb")
    # According to the TFT screen specs, it supports only 16bits pixels depth
    # Pygame surfaces use 24bits pixels depth by default, but the surface itself provides a very handy method to convert it.
    # once converted, we write the full byte buffer of the pygame surface into the TFT screen framebuffer like we would in a plain file:
    f.write(lcd.convert(16,0).get_buffer())
    # We can then close our access to the framebuffer
    f.close()
    # Will not wait. Let the regular code wait for the draw
    #time.sleep(0.1)

# Now we've got a function that can get the bytes from a pygame surface to the TFT framebuffer, 
# we can use the usual pygame primitives to draw on our surface before calling the refresh function.

# Here we just blink the screen background in a few colors with the "Hello World!" text
pygame.font.init()
defaultFont = pygame.font.Font('SourceCodePro-Bold.ttf',25)

lcd.fill((127,127,127))
lcd.blit(defaultFont.render("Hello World!", False, (0, 0, 0)),(0, 0))
refresh()


# Get the stats
def memuse():
    # you can convert that object to a dictionary 
    dvm = dict(psutil.virtual_memory()._asdict())
    return dvm['percent'] 

def ipaddrs():
    af_map = {
        socket.AF_INET: 'IPv4',
        socket.AF_INET6: 'IPv6',
        psutil.AF_LINK: 'MAC',
    }
    adapters = dict()
    for nic, addrs in psutil.net_if_addrs().items():
        addresses = list()       
        for addr in addrs:
            if addr.family == socket.AF_INET:
                addresses.append(addr.address)
        if nic != 'lo':
            adapters[nic] = addresses
    return adapters

def ipaddr(interface):
    ips = ipaddrs()
    value = "0.0.0.0"
    if interface in ips:
        if len(ips[interface]) > 0:
            value = ips[interface][0]
    return value

def uptime():
    raw_timedelta = datetime.timedelta(seconds=time.time() - psutil.boot_time())
    return datetime.timedelta(days=raw_timedelta.days,seconds=raw_timedelta.seconds)

def cpu():
    return psutil.cpu_percent(interval=0, percpu=False)

def cputemp():
    temps = psutil.sensors_temperatures()
    if not temps:
        sys.exit("can't read any temperature")
    for name, entries in temps.items():
        if name == 'cpu-thermal':
            for entry in entries:
               return entry.current


#Buttons
button_size = 96
margin = 10
button_top = surfaceSize[1] - button_size - margin

def button_lft(order):
    return surfaceSize[0] - ((margin + button_size)*order)

def buttonclick(pxl,order):
    if pxl[1] > button_lft(order) and pxl[1] < (button_lft(order)+button_size):
        if pxl[0] > button_top and pxl[0] < (button_top + button_size):
            return True
    return False


# Main Loop

orange = (255,103,0)
yellow = (255,199,0)



Run = True
i = 0
x = 500
y = 500

while Run:
    
    shutdownicon = pygame.image.load('shutdown.png')
    restarticon = pygame.image.load('restart.png')
    fbcpicon = pygame.image.load('fbcp.png')
    exiticon = pygame.image.load('exit.png')
    
    surface = pygame.image.load('background.png')
    lcd.blit(surface,[0,0])
    text_height = defaultFont.size("0")[1] + 2
    lcd.blit(defaultFont.render("IP Ethernet: " + str(ipaddr('eth0')), False,yellow),(0, 0))
    lcd.blit(defaultFont.render("IP Wi-Fi   : " + str(ipaddr('wlan0')), False, yellow),(0, text_height*1))
    lcd.blit(defaultFont.render("CPU        : " + str(cpu()) , False, yellow),(0, text_height*2))
    lcd.blit(defaultFont.render("RAM        : " + str(memuse()) , False, yellow),(0, text_height*3))
    lcd.blit(defaultFont.render("Temperature: " + str(cputemp()) , False, yellow),(0, text_height*4))
    lcd.blit(defaultFont.render("Uptime     : " + str(uptime()) , False, yellow),(0, text_height*5))
    
    
    lcd.blit(shutdownicon,[button_lft(1),button_top])
    lcd.blit(restarticon,[button_lft(2),button_top])
    lcd.blit(fbcpicon,[button_lft(3),button_top])
    lcd.blit(exiticon,[button_lft(4),button_top])

    refresh()

    #Touchscreen 
    event = Touchscreen.read_one()
    if event is not None:
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == 0:
                x = event.value
            elif event.code == 1:
                y = event.value
            pxl = getPixelsFromCoordinates((x,y))
        if event.type == evdev.ecodes.EV_KEY:
            if event.code == 330 and event.value == 0:
                print(pxl)
                if buttonclick(pxl,4): #Exit
                    Run = False
                elif buttonclick(pxl,3): #FBCP
                    Touchscreen.ungrab()
                    os.system('./fbcp')
                    Run = False
                elif buttonclick(pxl,2): #Restart
                    os.system('sudo reboot')  
                    Run = False             
                elif buttonclick(pxl,1): #Shutdown
                    os.system('sudo shutdown')
                    Run = False
                
    else:
        time.sleep(1)


#Clean for exit
lcd.fill((0,0,0))
refresh()
Touchscreen.ungrab()
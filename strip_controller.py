import time
from neopixel import *
from multiprocessing import Process, Pipe
from threading import *

# LED strip configuration:
LED_COUNT      = 240      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


#Transistion Constants
INSTANT = 'instant'
WIPE = 'wipe'

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()

def render(colors=[16777215], transistion=INSTANT, transistion_speed=50.0, renderCounter=0, pixelIndex=0):
	if transistion == INSTANT:
		for i in range(strip.numPixels()):
                	strip.setPixelColor(i, colors[renderCounter%len(colors)])
                	renderCounter = renderCounter + 1
		strip.show()
	elif transistion == WIPE and pixelIndex != strip.numPixels():
		strip.setPixelColor(pixelIndex, colors[renderCounter%len(colors)])
		strip.show()
		Timer(transistion_speed/1000.0, render, args=(colors, transistion, transistion_speed, renderCounter+1, pixelIndex+1)).start()

def brightness(bri=80, fade_speed=50.0):
        currentBrightness = strip.getBrightness()
        increment = 1
        if bri-currentBrightness < 0:
                increment = -1
	
#       while True:
        nextBrightness = currentBrightness + increment
        strip.setBrightness(int(nextBrightness + increment))
        strip.show()
        currentBrightness = nextBrightness
	if currentBrightness != bri:
		Timer(fade_speed/1000.0, brightness, args=(bri, fade_speed)).start()

#Command Map
CMD_MAP = {
	'render': render,
	'brightness': brightness,
}

wait_ms = 50

def run(conn):
	while True:
		command = conn.recv()
		func = CMD_MAP[command['name']]
		func(**command['args'])
		
#def brightness(brightness=80, fade_speed=50):
#	currentBrightness = strip.getBrightness()
#        increment = 1
#        if brightness-currentBrightness < 0:
#                increment = -1
#	while True:
#                nextBrightness = currentBrightness + increment
#                strip.setBrightness(int(nextBrightness + increment))
#                strip.show()
#                currentBrightness = nextBrightness
#                if currentBrightness == brightness:
#                        break
#                time.sleep(fade_speed/1000.0)#

if __name__ == "__main__":
	p_conn, c_conn = Pipe()
	p = Process(target=run, args=(c_conn,))
	p.start()
	colorPallete = [16711680,65535]
#	colorPattern = (colorPallete[0:1]*12).append((colorPallete[1:]*12))
	colorPattern = [colorPallete[0]]*12
	colorPattern.extend([colorPallete[1]]*12)
	pixelMap = colorPattern*10
	p_conn.send({'name': 'render', 'args':{'colors':colorPattern}})
	time.sleep(2)
	while True:
		pixelMap = pixelMap[LED_COUNT-1:] + pixelMap[:LED_COUNT-1]
		p_conn.send({'name': 'render', 'args':{'colors':pixelMap}})
		time.sleep(50.0/1000.0)
	#p_conn.send({'name': 'cycle', 'args':{}})
#	while True:
#		p_conn.send({'name': 'render', 'args':{'colors':[16711680],'transistion':WIPE}})
#		time.sleep(1)
#		p_conn.send({'name': 'render', 'args':{'colors':[65535],'transistion':WIPE}})
#	p_conn.send({'name': 'brightness', 'args':{'bri':20}})
#		time.sleep(1)
	#p_conn.send({'name': 'render', 'args':{'colors':[16711680],'transistion':WIPE}})

from flask import Flask
from flask import request
app = Flask(__name__)

from neopixel import *
import math
import time
import patterns
import inspect
import ast
from multiprocessing import Process, Pipe
from strip_controller import run, WIPE, INSTANT

# LED strip configuration:
#LED_COUNT      = 240      # Number of LED pixels.
#LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
#LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
#LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
#LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
#LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
#LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
#LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering



#strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
#strip.begin()

parent_conn, child_conn = Pipe()
command_loop = Process(target=run, args=(child_conn,))
command_loop.start()

@app.route("/pattern/<functionName>", methods=['POST'])
def executePattern(functionName):
	method_to_call = getattr(patterns, functionName)
	json = request.get_json()
	if method_to_call:
		argspec = inspect.getargspec(method_to_call)
		args = []
		for arg in argspec[0]:
			if arg in json:
				args.append(json[arg])	
		#method_to_call(strip, *args)
	return "done"

@app.route('/exec/<command>', methods=['POST'])
def execCommand(command):
	json = request.get_json()
	args = json['args']
	parent_conn.send({'name': command, 'args': args})
	return "executing command"

#@app.route('/render', methods=['POST'])
#def render():
#	json = request.get_json()
#	args = json['args']
	#colors = json['colors']
	#counter = 0
        #for i in range(strip.numPixels()):
        #        strip.setPixelColor(i, colors[counter%len(colors)])
        #        counter = counter + 1
        #strip.show()
#	parent_conn.send({'name': 'render', 'args': args})
#	return "done"

#@app.route('/brightness', methods=['POST'])
#def changeBrightness():
#	json = request.get_json()
#	args = json['args']
#	brightness = int(json['brightness'])
#	currentBrightness = strip.getBrightness()
#	increment = 1
#	if brightness-currentBrightness < 0:
#		increment = -1
#
#	wait_ns = 50.0
#	if 'wait' in json:
#		wait_ns = float(json['wait'])
#
#	while True:
#		nextBrightness = currentBrightness + increment
#		strip.setBrightness(int(nextBrightness + increment))
#		strip.show()
#		currentBrightness = nextBrightness
#		if currentBrightness == brightness:
#			break
#		time.sleep(wait_ns/1000.0)
#	parent_conn.send({'name': 'brightness', 'args':args})
#	return "done"

if __name__ == '__main__':
    app.run('0.0.0.0')
#parent_conn, child_conn = Pipe()
#p1 = Process(target=strip_controller.run, args=(child_conn,))
#p1.start()
#parent_conn.send([42, None, 'hello'])


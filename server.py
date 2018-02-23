from flask import Flask, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Cheese321!'
socketio = SocketIO(app)

from neopixel import *
import math
import time
import patterns
import inspect
import ast
from multiprocessing import Process, Pipe
from strip_controller import run, getPixels

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

@app.route('/state', methods=['GET'])
def getState():
	pixels = getPixels()
	state = []
	for i in range(pixels.size):
		state.append(pixels[i])
	return jsonify(state)

if __name__ == '__main__':
	socketio.run(app, '0.0.0.0')

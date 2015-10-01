#!/usr/bin/python
"""run.py: Script python para el montaje detector de rayos cósmicos y radiactividad. """

import atexit, gc, subprocess, threading, time
import RPi.GPIO as GPIO

__author__ = "José Ángel Jiménez Vadillo"
__copyright__ = "Copyright 2015, José Ángel Jiménez Vadillo"

__license__ = "GPLv3"
__date__ = "2015-02-21"
__version__ = "1.1"
__maintainer__ = "José Ángel Jiménez Vadillo"
__email__ = "jose.angel.jimenez@gmail.com"
__status__ = "Development"

# Configuration
PLAYER = ["aplay", "-q"]
INPUT_CHANNELS = (7, 8, 25)
LIGHT_CHANNELS = (11, 9, 10)
NUM_CHANNELS = len(INPUT_CHANNELS)
INPUT_RANGE = range(NUM_CHANNELS)
ENABLE_CHANNEL = 24
WAV1 = "bell_long.wav"
WAV2 = "cminor7.wav"
WAV3 = "piano2.wav"

def setup():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  for i in INPUT_CHANNELS:
    GPIO.setup(i, GPIO.IN)
  for i in LIGHT_CHANNELS:
    GPIO.setup(i, GPIO.OUT)
  GPIO.setup(ENABLE_CHANNEL, GPIO.OUT)
  GPIO.output(ENABLE_CHANNEL, 1)
  gc.disable()

@atexit.register
def cleanup():
  for i in LIGHT_CHANNELS:
    GPIO.output(i, 0)
  GPIO.output(ENABLE_CHANNEL, 0)
  GPIO.cleanup()
  print "cleanup()"

# Sets the i-th (0, 1, 2) light to the given state (0, 1)
def set_light(i, state):
  GPIO.output(LIGHT_CHANNELS[i], state)

light_queues = [[], [], []]
def light_on(i):
  light_queues[i].append(1)
  GPIO.output(LIGHT_CHANNELS[i], 1)

def light_off(i):
  light_queues[i].pop()
  if (not light_queues[i]):
    GPIO.output(LIGHT_CHANNELS[i], 0)

def flash(i, seconds):
  light_on(i)
  threading.Timer(seconds, light_off, [i]).start()

def play(filename):
  subprocess.Popen(PLAYER + [filename])

def detect():
  # Local variables
  match = 0
  pattern = []
  history = []

  # Loops while all input channels are inactive
  while(1):
    inputs = [GPIO.input(i) for i in INPUT_CHANNELS]
    if (sum(inputs) < 3):
      break

  # Loops while any input channel is still active
  while (1):
    if (not history or history[len(history) - 1] != inputs):
      history.append(inputs)
    detected = NUM_CHANNELS - sum(inputs)
    if (detected > match):
      match = detected
      pattern = inputs
    inputs = [GPIO.input(i) for i in INPUT_CHANNELS]
    if (sum(inputs) == 3):
      break

  # Returns
  if (match == 1):
    return match, pattern
    print "Single:", history
  elif (match == 2):
    print "Double:", history
  else:
    print "Triple:", history
  return match, pattern

def where(pattern):
  result = []
  for i in range(len(pattern)):
    if (pattern[i] == 0):
      result.append(i)
  return result

# Init
setup()

# Elapsed time in seconds
def t():
  return time.time()

t2 = t()
while(1):
  match, pattern = detect()
  lights = where(pattern)
  # Single
  if (match == 1):
    play(WAV1)
    flash(lights[0], 0.5)
    #print "Single:", pattern
    continue

  # Debugging
  t1 = t2
  t2 = t()
  #print "Double:" if (match == 2) else "Triple:", pattern, t2 - t1
  print t2 - t1

  # Double
  if (match == 2):
    play(WAV2)
    flash(lights[0], 4)
    flash(lights[1], 4)
  # Triple
  else:
    play(WAV3)
    flash(lights[0], 8)
    flash(lights[1], 8)
    flash(lights[2], 8)

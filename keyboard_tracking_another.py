import time
from collections import OrderedDict

from pynput import keyboard
from threading import Thread

key_press_start = {}
key_press_durations = OrderedDict()
key_intervals = OrderedDict()


def on_key_press(key):
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)

    timestamp = time.time()

    if key_str not in key_press_start:
        key_press_start[key_str] = timestamp


def on_key_release(key):
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)

    timestamp = time.time()

    if key_str in key_press_start:
        press_start = key_press_start[key_str]
        duration = timestamp - press_start

        if key_str not in key_press_durations:
            key_press_durations[key_str] = []

        key_press_durations[key_str].append(duration)

        if len(key_intervals) > 0:
            last_release = key_press_start[key_str] #key_intervals[list(key_intervals.keys())[-1]][-1]
            interval = timestamp - last_release
            # if interval > 10:
            #     interval = -interval / 10000000000
            if key_str not in key_intervals:
                key_intervals[key_str] = []
            key_intervals[key_str].append(interval)
        else:
            key_intervals[key_str] = [0.0]

        key_press_start.pop(key_str)


def start_tracking():
    global listener_thread
    listener_thread = Thread(target=run_listener)
    listener_thread.start()


def run_listener():
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()


def stop_tracking():
    durations_copy = OrderedDict(key_press_durations)
    intervals_copy = OrderedDict(key_intervals)

    key_press_start.clear()
    key_press_durations.clear()
    key_intervals.clear()

    return durations_copy, intervals_copy

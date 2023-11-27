import keyboard
import time

key_press_start = {}
key_press_durations = {}
key_intervals = {}


def on_key_press(event):
    key = event.name
    timestamp = time.time()

    if key not in key_press_start:
        key_press_start[key] = timestamp


def on_key_release(event):
    key = event.name
    timestamp = time.time()

    if key in key_press_start:
        press_start = key_press_start[key]
        duration = timestamp - press_start

        if key not in key_press_durations:
            key_press_durations[key] = []

        key_press_durations[key].append(duration)
        key_press_start.pop(key)

        if key in key_intervals:
            last_release = key_intervals[key][-1]
            interval = timestamp - last_release
            key_intervals[key].append(interval)
        else:
            key_intervals[key] = [0.0]


def start_tracking():
    keyboard.hook(on_key_press)
    keyboard.hook(on_key_release)


def stop_tracking():
    keyboard.unhook_all()

    durations_copy = key_press_durations.copy()
    intervals_copy = key_intervals.copy()

    key_press_start.clear()
    key_press_durations.clear()
    key_intervals.clear()

    return durations_copy, intervals_copy

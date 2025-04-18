# Dindo Bot
# Copyright (c) 2018 - 2019 AXeL

import sys
import os
from datetime import datetime
from PIL import Image
from . import parser
import pyautogui, psutil
import time
import socket
import webbrowser
import platform

if platform.system() == 'Windows':
	import win32gui
else:
	from Xlib import display, X, Xatom

# Return active game window(s) list
def get_game_window_list():
	game_window_list = {}
	try:
		if platform.system() == 'Windows':
			def winEnumHandler(hwnd, ctx):
				if win32gui.IsWindowVisible(hwnd):
					window_text = win32gui.GetWindowText(hwnd)
					_, pid = win32gui.GetWindowThreadProcessId(hwnd)
					try:
						exe = psutil.Process(pid).name()
						if exe.lower() in ['dofus.exe']:
							if window_text in game_window_list:
								name = '%s (%d)' % (window_text, len(game_window_list)+1)
							else:
								name = window_text
							game_window_list[name] = hwnd
					except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
						pass

			win32gui.EnumWindows(winEnumHandler, None)
	except Exception as ex:
		print(ex)
	return game_window_list

# Return screen size

def get_screen_size():
	#screen = Gdk.Screen.get_default()
	#return (screen.get_width(), screen.get_height())
	return pyautogui.size()

# Activate a window
def activate_window(window_id):
	if platform.system() == 'Windows':
		win32gui.ShowWindow(window_id, 5)  # SW_SHOW
		win32gui.SetForegroundWindow(window_id)
	else:
		pass

# Return game window decoration height
def get_game_window_decoration_height(window_xid):
    return 0


# Return absolute path
def get_full_path(rel_path):
	dir_of_py_file = os.path.dirname(__file__)
	root_dir = os.path.join(dir_of_py_file, '..')
	relative_path = os.path.join(root_dir, rel_path)
	absolute_path = os.path.abspath(relative_path)
	return absolute_path

# Return internet state
def internet_on(host='8.8.8.8', port=53, timeout=3):
	'''
	Host: 8.8.8.8 (google-public-dns-a.google.com)
	OpenPort: 53/tcp
	Service: domain (DNS/TCP)
	'''
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		#print(ex.message)
		return False

# Return internet state as a string
def print_internet_state(state=None):
	if state is None:
		state = internet_on()
	return 'Internet is ' + ('on' if state else 'off')

# Take a screenshot of given window
def take_window_screenshot(window, save_to='screenshot'):
	if platform.system() == 'Windows':
		pyautogui.screenshot(save_to + '.png')

# Return a screenshot of the game
def screen_game(region, save_to=None):
	x, y, width, height = region
	try:
		raw = root.get_image(x, y, width, height, X.ZPixmap, 0xffffffff)
		screenshot = Image.frombytes('RGB', (width, height), raw.data, 'raw', 'BGRX')
		if save_to is not None:
			screenshot.save(save_to + '.png')
	except:
		filename = save_to + '.png' if save_to is not None else None
		screenshot = pyautogui.screenshot(filename, region)
	return screenshot

# Return pixel color of given x, y coordinates
def get_pixel_color(x, y):
	pixel = screen_game((x, y, 1, 1))
	rgb = pixel.getpixel((0, 0))
	return rgb

# Return date as a string in the given format
def get_date(format='%d-%m-%y'):
	return datetime.now().strftime(format)

# Return time as a string
def get_time():
	return get_date('%H:%M:%S')

# Return date & time as a string
def get_date_time():
	return get_date('%d-%m-%y_%H-%M-%S')

# Return timestamp
def get_timestamp(as_int=True):
	timestamp = time.mktime(datetime.now().timetuple())
	return int(timestamp) if as_int else timestamp

# Save text to file
def save_text_to_file(text, filename, mode='w'):
	file = open(filename, mode)
	file.write(text)
	file.close()

# Return file content
def read_file(filename):
	if os.path.isfile(filename):
		file = open(filename, 'r')
		content = file.read()
		file.close()
		return content
	else:
		return None

# Return platform name
def get_platform():
	return sys.platform

# Checks platform name
def platform_is(platform_name, use_startswith=False):
	if use_startswith:
		return sys.platform.startswith(platform_name)
	else:
		return sys.platform == platform_name

# Return command line arguments
def get_cmd_args():
	return sys.argv[1:]


# Check if position is inside given bounds
def position_is_inside_bounds(pos_x, pos_y, bounds_x, bounds_y, bounds_width, bounds_height):
	if pos_x > bounds_x and pos_x < (bounds_x + bounds_width) and pos_y > bounds_y and pos_y < (bounds_y + bounds_height):
		return True
	else:
		return False

# Fit position coordinates to given destination
def fit_position_to_destination(x, y, window_width, window_height, dest_width, dest_height):
	# new coordinate = old coordinate / (window size / destination size)
	new_x = x / (window_width / float(dest_width))
	new_y = y / (window_height / float(dest_height))
	return (int(new_x), int(new_y))

# Adjust click position
def adjust_click_position(click_x, click_y, window_width, window_height, dest_x, dest_y, dest_width, dest_height):
	# get screen size
	screen_width, screen_height = pyautogui.size()
	if screen_width > window_width and screen_height > window_height:
		# fit position to destination size
		new_x, new_y = fit_position_to_destination(click_x, click_y, window_width, window_height, dest_width, dest_height)
		#print('new_x: %d, new_y: %d, dest_x: %d, dest_y: %d' % (new_x, new_y, dest_x, dest_y))
		# scale to screen
		x = new_x + dest_x
		y = new_y + dest_y
	else:
		x = click_x
		y = click_y
	return (x, y)

# Perform a simple click or double click on x, y position
def perform_click(x, y, double=False):
	old_position = pyautogui.position()
	if double:
		pyautogui.doubleClick(x=x, y=y, interval=0.1)
	else:
		pyautogui.click(x=x, y=y)
	pyautogui.moveTo(old_position)

# Press key
def press_key(key, interval=None):
	if interval is not None:
		time.sleep(interval)
	keys = parser.parse_key(key)
	count = len(keys)
	if count == 1:
		pyautogui.press(keys[0])
	elif count == 2:
		pyautogui.hotkey(keys[0], keys[1])

# Type text
def type_text(text, interval=0.1):
	for c in text:
		if c.isdigit():
			pyautogui.hotkey('shift', c, interval=0.1)
		else:
			pyautogui.press(c)
		time.sleep(interval)

# Scroll to value
def scroll_to(value, x=None, y=None, interval=None):
	if interval is not None:
		time.sleep(interval)
	pyautogui.scroll(value, x, y)

# Create directory(s) if not exist
def create_directory(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

# Check if color matches expected color
def color_matches(color, expected_color, tolerance=0):
	r, g, b = color
	red, green, blue = expected_color
	return (abs(r - red) <= tolerance) and (abs(g - green) <= tolerance) and (abs(b - blue) <= tolerance)

# Return the percentage of a color in an image
def get_color_percentage(image, expected_color, tolerance=10):
	# get image colors
	width, height = image.size
	image = image.convert('RGB')
	colors = image.getcolors(width * height)
	# check if the expected color exist
	expected_color_count = 0
	for count, color in colors:
		if color_matches(color, expected_color, tolerance):
			expected_color_count += count
	# convert to percentage
	if height == 0: height = 1
	if width == 0: width = 1
	percentage = ((expected_color_count / height) / float(width)) * 100
	return round(percentage, 2)

# Return the dominant color in an image & his percentage
def get_dominant_color(image):
	# get image colors
	width, height = image.size
	image = image.convert('RGB')
	colors = image.getcolors(width * height)
	# get dominant color
	count, color = max(colors, key=lambda color: color[0])
	# convert to percentage
	if height == 0: height = 1
	if width == 0: width = 1
	percentage = ((count / height) / float(width)) * 100
	return (color, round(percentage, 2))

# Open given file in text editor
def open_file_in_editor(filename):
	editor = os.getenv('EDITOR')
	if editor:
		os.system('%s %s' % (editor, filename))
	else:
		webbrowser.open(filename)

# Wait for mouse event
def wait_for_mouse_event(event):
	pyautogui.waitForMouseEvent(event)

# Return given coordinates center
def coordinates_center(coords):
	return (coords[0] + int(coords[2] / 2), coords[1] + int(coords[3] / 2))

# Return mouse position
def get_mouse_position():
	return pyautogui.position()

# Return screen size
def get_screen_size():
	return pyautogui.size()

# Move mouse to position
def move_mouse_to(position):
	pyautogui.moveTo(position)


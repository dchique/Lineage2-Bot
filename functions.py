import time
import win32gui
import glob
import numpy as np
import mss

from PIL import ImageOps, Image, ImageGrab
from numpy import *
import time
import cv2
import win32gui
from collections import defaultdict


WINDOW_SUBSTRING = "Lineage"


# Brazenhem algo
def draw_line(x1=0, y1=0, x2=0, y2=0):

    coordinates = []

    dx = x2 - x1
    dy = y2 - y1

    sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
    sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

    if dx < 0:
        dx = -dx
    if dy < 0:
        dy = -dy

    if dx > dy:
        pdx, pdy = sign_x, 0
        es, el = dy, dx
    else:
        pdx, pdy = 0, sign_y
        es, el = dx, dy

    x, y = x1, y1

    error, t = el / 2, 0

    coordinates.append([x, y])

    while t < el:
        #print(error)
        error -= es
        if error < 0:
            error += el
            x += sign_x
            y += sign_y
        else:
            x += pdx
            y += pdy
        t += 1
        coordinates.append([x, y])

    return coordinates


# Smooth move mouse from current pos to xy
def smooth_move(autohotpy, x, y):
    flags, hcursor, (startX, startY) = win32gui.GetCursorInfo()
    coordinates = draw_line(startX, startY, x, y)
    #print('x: {}, y: {}'.format(x,y))
    #print(coordinates[-1])
    x = 0
    for dot in coordinates:
        x += 1
        if x % 2 == 0 and x % 3 == 0:
            pass
            #time.sleep(0.01)
        autohotpy.moveMouseToPosition(dot[0], dot[1])
        #autohotpy.moveMouseToPosition(x, y)

def get_window_info(hwnd):
    # set window info
    window_info = defaultdict(list)
    window_info['hwnd'] = hwnd
    win32gui.EnumWindows(set_window_coordinates, window_info)
    return window_info


# EnumWindows handler
# sets L2 window coordinates
def set_window_coordinates(hwnd, window_info):
    if win32gui.IsWindowVisible(hwnd):
        if WINDOW_SUBSTRING in win32gui.GetWindowText(hwnd):
            if hwnd == window_info['hwnd']:
                rect = win32gui.GetWindowRect(hwnd)
                x = rect[0]
                y = rect[1]
                w = rect[2] - x
                h = rect[3] - y
                window_info['x'] = x
                window_info['y'] = y
                window_info['width'] = w
                window_info['height'] = h
                window_info['name'] = win32gui.GetWindowText(hwnd)
                print('Main HWND: ' + str(hwnd))
                #win32gui.SetForegroundWindow(hwnd)


def get_screen(x1, y1, x2, y2):
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    box = (x1 + 8, y1 + 30, x2 - 8, y2)
    screen = ImageGrab.grab(box, all_screens=True)
    #screen.save('test_image.png')
    img = array(screen.getdata(), dtype=uint8).reshape((screen.size[1], screen.size[0], 3))
    return img

def get_screen_fast(x1, y1, x2, y2):
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)
    box = (x1 + 8, y1 + 30, x2 - 8, y2)
    with mss.mss() as sct:
        im = sct.grab(box)
        pil_img = Image.frombytes('RGB', im.size, im.bgra, 'raw', 'BGRX') #BGRX #RGBX
    #img = array(pil_img.getdata(), dtype=uint8).reshape((pil_img.size[1], pil_img.size[0], 3))
    img = array(im)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #cv2.imwrite('./screen_fast_2.png', img)
    return img

def return_hp_percent(hp_image, hp_color, no_hp_color):
    def distance(v1,v2):
        return np.sqrt((v1[0]-v2[0])**2+(v1[1]-v2[1])**2+(v1[2]-v2[2])**2)
    filled_red_pixels = 0
    missing_hp_pixels = 0
    pixels = hp_image[0].tolist()
    #print(len(pixels))
    for pixel in pixels:
        #print(pixel)
        #print(distance(pixel, no_hp_color))
        if distance(pixel, hp_color) < 2:
            filled_red_pixels += 1
        elif distance(pixel, no_hp_color) < 40:
            missing_hp_pixels += 1

    percent = 100 * filled_red_pixels / len(pixels)

    if missing_hp_pixels == 0 and filled_red_pixels == 0:
        return -1

    print(percent)
    return percent

def filter_by_template(img, filters):
    for template in filters:
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if count_nonzero(loc) == 2:
            for pt in zip(*loc[::-1]):
                cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 0), -1)
    return img


def get_target_centers(img, filters):

    # Hide buff line
    # img[0:70, 0:500] = (0, 0, 0)

    # Hide your name in first camera position (default)
    #img[154:177, 377:416] = (0, 0, 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #cv2.imwrite('1_gray_img.png', gray)
    gray = filter_by_template(gray, filters)
    #cv2.imwrite('1_gray_img_filtered.png', gray)

    # Find only white text
    ret, threshold1 = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY)
    #cv2.imwrite('2_threshold1_img.png', threshold1)

    # Morphological transformation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5)) #(50, 5)
    closed = cv2.morphologyEx(threshold1, cv2.MORPH_CLOSE, kernel)
    #cv2.imwrite('3_morphologyEx_img.png', closed)
    closed = cv2.erode(closed, kernel, iterations=1)
    #cv2.imwrite('4_erode_img.png', closed)
    closed = cv2.dilate(closed, kernel, iterations=1)
    #cv2.imwrite('5_dilate_img.png', closed)
    #print('dialated')

    (centers, hierarchy) = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return centers

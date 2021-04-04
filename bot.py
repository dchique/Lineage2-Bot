from functions import *
from lib.InterceptionWrapper import InterceptionMouseState, InterceptionMouseStroke
import cv2
import imutils
import numpy as np
import time


class Bot:

    def __init__(self, autohot_py):
        with open('./hwnd.txt') as f:
            lines = f.readlines()
            hwnd = int(lines[0])
        self.autohot_py = autohot_py
        self.step = 0
        self.window_info = get_window_info(hwnd)
        self.useless_steps = 0
        self.dead_target_counter = 0
        self.not_attacking_counter = 0
        self.no_target_counter = 0
        self.set_target_counter = 0
        self.current_center  = 0 
        self.follower_attack = time.time()
        self.target_bead = cv2.imread('img/target_template_2.png', 0)
        self.target_bar = cv2.imread('img/target_bar_3.png', 0)
        self.filter_names = []
        for filter_image in glob.glob('./img/ignore/*.png'):
            self.filter_names += [cv2.imread(filter_image, 0)]
        self.buffed = False
        self.skill_dict = {}

    def buff_check(self):
        if self.buffed:
            if (time.time() - self.last_buff) > 1180:
                self.last_buff = time.time()
                return True
            else:
                return False
        else:
            self.buffed = True
            self.last_buff = time.time()
            return True

    def set_default_camera(self):
        for i in range(0,3,1):
            self.autohot_py.PAGE_DOWN.press()
            time.sleep(0.1)
        for i in range(0,10,1):
            self.autohot_py.BACKSLASH.down()
            time.sleep(0.2)
            self.autohot_py.BACKSLASH.up()
            time.sleep(0.3)
        
    def move_to_motion(self):
        window_box = [self.window_info["x"] + self.window_info["width"]*.1,
                    self.window_info["y"] + self.window_info["height"]*.05,
                    self.window_info["x"] + self.window_info["width"]*.9,
                    self.window_info["y"] + self.window_info["height"]*.3]
        img1 = get_screen_fast(window_box[0], window_box[1], window_box[2], window_box[3])
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        #cv2.imwrite('motion_1.png', img1)
        time.sleep(0.4)
        img2 = get_screen_fast(window_box[0], window_box[1], window_box[2], window_box[3])
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        #cv2.imwrite('motion_2.png', img2)
        frameDelta = cv2.absdiff(img1, img2)
        #cv2.imwrite('motion_diff.png', frameDelta)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # loop over the contours
        for c in cnts[:5]:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 20:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            center_x = x + w/2 + window_box[0]
            center_y = y + h/2 + window_box[1]
            iterator = -20
            cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imwrite('motion_cao.png', img2)
            while iterator < 30:
                x_mouse = center_x + 10*np.sin((iterator+20)/np.pi)
                y_mouse = center_y + iterator
                smooth_move(self.autohot_py, x_mouse, y_mouse)
                if self.find_from_targeted(x_mouse,y_mouse):
                    self.click_target()
                    return True
                iterator += 6
            
        return False

    def go_somewhere(self):
        """
        click to go
        """
        #self.set_default_camera()
        smooth_move(self.autohot_py, self.window_info['x'] + self.window_info['width']*0.55, self.window_info['y'] + self.window_info['height']*.48)  # @TODO dynamic
        stroke = InterceptionMouseStroke()
        time.sleep(0.2)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
        self.autohot_py.sendToDefaultMouse(stroke)
        time.sleep(0.1)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
        self.autohot_py.sendToDefaultMouse(stroke)
        #self.set_default_camera()

    def unstuck(self):
        self.autohot_py.RIGHT_ARROW.down()
        time.sleep(1.5)
        self.autohot_py.RIGHT_ARROW.up()
        time.sleep(0.3)
        self.autohot_py.UP_ARROW.down()
        time.sleep(3)
        self.autohot_py.UP_ARROW.up()

    def long_move(self):
        self.autohot_py.RIGHT_ARROW.down()
        time.sleep(1.5)
        self.autohot_py.RIGHT_ARROW.up()
        self.autohot_py.UP_ARROW.down()
        time.sleep(15)
        self.autohot_py.UP_ARROW.up()
        self.set_default_camera()

    def turn(self, turn_y):
        """
        turn right
        """
        smooth_move(self.autohot_py, self.window_info['x'] + self.window_info['width']*0.3, self.window_info['y'] + self.window_info['height']*.45)  # @TODO dynamic
        stroke = InterceptionMouseStroke()
        time.sleep(0.1)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
        self.autohot_py.sendToDefaultMouse(stroke)
        smooth_move(self.autohot_py, self.window_info['x'] + self.window_info['width']*0.3+18, self.window_info['y'] + self.window_info['height']*.45+turn_y)  # @TODO dynamic
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
        self.autohot_py.sendToDefaultMouse(stroke)

    def get_targeted_hp(self):
        """
        return victim's hp
        or -1 if there is no target
        """
        hp_color = [200, 41, 34]
        no_hp_color = [23,18,15]
        target_widget_coordinates = {}
        bottom_trim = 190
        img = get_screen_fast(
            self.window_info["x"],
            self.window_info["y"],
            self.window_info["x"] + self.window_info["width"],
            self.window_info["y"] + self.window_info["height"] - bottom_trim
        )

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('hp_gray_img.png', img_gray)

        template = self.target_bar
        #w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if count_nonzero(loc) == 2:
            for pt in zip(*loc[::-1]):
                target_widget_coordinates = {"x": pt[0], "y": pt[1]}
                #cv2.rectangle(img_gray, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)

        #cv2.imwrite('hp_gray_img_rect.png', img_gray)
        #print(target_widget_coordinates)

        if not target_widget_coordinates:
            return -1

        # pil_image_hp = get_screen(
        #     self.window_info["x"] + target_widget_coordinates['x'] + 16,
        #     self.window_info["y"] + target_widget_coordinates['y'] + 30,
        #     self.window_info["x"] + target_widget_coordinates['x'] + 181,
        #     self.window_info["y"] + target_widget_coordinates['y'] + 61
        # )
        pil_image_hp = get_screen_fast(
            self.window_info["x"] + target_widget_coordinates['x'] + 17,
            self.window_info["y"] + target_widget_coordinates['y'] + 27, # 27
            self.window_info["x"] + target_widget_coordinates['x'] + 229,
            self.window_info["y"] + target_widget_coordinates['y'] + 58 # 58
        )
        Image.fromarray(pil_image_hp).save("hp_pil.png")

        percent = return_hp_percent(pil_image_hp, hp_color, no_hp_color)
        return percent

    def check_for_heal(self, threshold):
        """
        return own hp
        or -1 if there is no target
        """

        own_hp_color = [181, 8, 24]
        follower_hp_color = [210,11,49]

        full_image = get_screen_fast(
            self.window_info["x"],
            self.window_info["y"],
            self.window_info["x"] + self.window_info['width'],
            self.window_info["y"] + self.window_info['height']
        )
        Image.fromarray(full_image).save("full_window.png")

        own_image_hp = get_screen_fast(
            self.window_info["x"] + 16,
            self.window_info["y"] + 53,
            self.window_info["x"] + 182,
            self.window_info["y"] + 84
        )
        Image.fromarray(own_image_hp).save("own_hp.png")

        follower_image_hp = get_screen_fast(
            self.window_info["x"] + 16,
            self.window_info["y"] + 115,
            self.window_info["x"] + 182,
            self.window_info["y"] + 146
        )
        Image.fromarray(follower_image_hp).save("follower_hp.png")

        own_percent = return_hp_percent(own_image_hp, own_hp_color)
        print(own_percent)
        fol_percent = return_hp_percent(follower_image_hp, follower_hp_color)
        print(fol_percent)
        return [own_percent <= threshold, fol_percent <= threshold]

    def set_target(self,last_target_hp):
        """
        find target and click
        """
        img = get_screen_fast(
            self.window_info["x"],
            self.window_info["y"],
            self.window_info["x"] + self.window_info["width"],
            self.window_info["y"] + self.window_info["height"] - 100
        )
        if last_target_hp == 0:
            print('image size: {}'.format(img.shape))
            img[int(.353*self.window_info['height']):int(.725*self.window_info['height']), 
                int(.362*self.window_info['width']):int(.639*self.window_info['width'])] = (0, 0, 0)
        Image.fromarray(img).save("set_target.png")

        cnts = get_target_centers(img, self.filter_names)
        approxes = []
        hulls = []
        for cnt in cnts:
            if self.dead_target_counter > 2 and np.array_equal(self.current_center, cnt):
                continue
            approxes.append(cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True))
            hulls.append(cv2.convexHull(cnt))
            left = list(cnt[cnt[:, :, 0].argmin()][0])
            right = list(cnt[cnt[:, :, 0].argmax()][0])
            if right[0] - left[0] < 20:
                continue
            center = round((right[0] + left[0]) / 2)
            center = int(center)

            # smooth_move(self.autohot_py, center + self.window_info["x"], left[1] + 110 + self.window_info["y"])
            # time.sleep(0.1)
            # if self.find_from_targeted(left, right):
            #     self.click_target()
            #     return True

            # Slide mouse down to find target
            iterator = 0
            while iterator < 2*np.pi:
                x_mouse = center + self.window_info["x"]+ 30*np.sin(iterator)
                y_mouse = int(left[1] + 20*iterator/np.pi + self.window_info["y"]+30)
                smooth_move(self.autohot_py, x_mouse, y_mouse)
                if self.find_from_targeted(x_mouse, y_mouse):
                    self.click_target()
                    self.current_center = cnt
                    return True
                iterator += np.pi/32

        return False

    def find_from_targeted(self, x, y):

        # @TODO ignore red target - it is attacked and dead
        template = self.target_bead

        # print template.shape
        # roi = get_screen_fast(
        #     self.window_info["x"],
        #     self.window_info["y"],
        #     self.window_info["x"] + self.window_info["width"],
        #     self.window_info["y"] + self.window_info["height"] - 300
        # )

        roi = get_screen_fast(
            x-150,
            y-100,
            x+150,
            y
        )

        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('./find_from_targeted.png',roi)
        ret, th1 = cv2.threshold(roi, 224, 255, cv2.THRESH_TOZERO_INV)
        ret, th2 = cv2.threshold(th1, 135, 255, cv2.THRESH_BINARY)
        ret, tp1 = cv2.threshold(template, 224, 255, cv2.THRESH_TOZERO_INV)
        ret, tp2 = cv2.threshold(tp1, 135, 255, cv2.THRESH_BINARY)
        if not hasattr(th2, 'shape'):
            return False
        wth, hth = th2.shape
        wtp, htp = tp2.shape
        if wth > wtp and hth > htp:
            res = cv2.matchTemplate(th2, tp2, cv2.TM_CCORR_NORMED)
            if res.any():
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                if max_val > 0.7:
                    return True
                else:
                    return False
        return False

    def click_target(self):
        stroke = InterceptionMouseStroke()
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
        self.autohot_py.sendToDefaultMouse(stroke)
        time.sleep(0.1)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
        self.autohot_py.sendToDefaultMouse(stroke)

    def right_click_target(self):
        stroke = InterceptionMouseStroke()
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN
        self.autohot_py.sendToDefaultMouse(stroke)
        time.sleep(0.1)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
        self.autohot_py.sendToDefaultMouse(stroke)

    def find_skill_loc(self, skill_image, skill_name):
        roi = get_screen_fast(
            self.window_info["x"],
            self.window_info["y"],
            self.window_info["x"] + self.window_info["width"],
            self.window_info["y"] + self.window_info["height"]
        )

        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('skill.png', roi)

        template = cv2.imread(skill_image, 0)
        

        res = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if count_nonzero(loc) == 2:
            for pt in zip(*loc[::-1]):
                self.skill_dict[skill_name] = {"x": pt[0]+15, "y": pt[1]+30}

        return None

    def click_skill(self, skill_name):
        x_mouse = self.window_info["x"] + self.skill_dict[skill_name]['x']
        y_mouse = self.window_info["y"] + self.skill_dict[skill_name]['y']
        smooth_move(self.autohot_py, x_mouse, y_mouse)
        self.right_click_target()
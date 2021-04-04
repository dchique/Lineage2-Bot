from functions import *
from bot import Bot
import numpy as np


class Duck (Bot):

    def loop(self, stop_event):
        """
        main bot logic
        """
        #self.set_default_camera()
        self.fresh_kill = False
        self.toggle = 1
        self.roar_time = 0
        self.rage_time = 0
        while not stop_event.is_set():
            time.sleep(0.1)
            if time.time() - self.roar_time > 10*60:
                self.autohot_py.F8.press()
                self.roar_time = time.time()
                time.sleep(1)
            if time.time() - self.rage_time > 3*50:
                self.autohot_py.F10.press()
                self.rage_time = time.time()
                time.sleep(0.3)
            if np.any(self.check_for_heal(70)): #Getting low
                self.autohot_py.N6.press() # Follower heal
                #self.autohot_py.N0.press() # Follower follow
            if self.buff_check():
                self.autohot_py.N5.press() #Follower buffs
                time.sleep(9)
            # Continue attacking if victim is alive
            targeted_hp = self.get_targeted_hp()
            low_health = self.check_for_heal(40)
            if low_health[0]: #LOW HEALTH USE POTS
                self.autohot_py.F9.press()
            if low_health[1]:
                self.autohot_py.N9.press()
            if targeted_hp > 99:
                self.autohot_py.F12.press()
            if targeted_hp < 15:
                self.autohot_py.F2.press()
            if targeted_hp > 0:
                self.useless_steps = 0
                print("attack the target")
                self.autohot_py.F3.press()
                self.autohot_py.F1.press() #Auto-attack
                continue
            elif targeted_hp == 0:
                print("Pick-up")
                time.sleep(0.4)
                self.fresh_kill = True
                self.toggle = 1
                self.autohot_py.F12.press() # Select next target if being attacked
                for i in range(0,3,1):
                    self.autohot_py.F4.press()
                    time.sleep(0.3)
                print("target is dead")
                self.dead_target_counter += 1
                if self.dead_target_counter > 20:
                    self.autohot_py.ESC.press()
                    self.dead_target_counter = 0
                continue
            else:
                print("no target yet")
                # Find and click on the victim
                if self.fresh_kill:
                    self.autohot_py.F5.press()
                    time.sleep(6)
                    self.autohot_py.ESC.press()
                    self.autohot_py.ESC.press()
                    self.fresh_kill = False

                elif self.set_target(targeted_hp) and not np.any(low_health):
                    self.autohot_py.DOWN_ARROW.press()
                    self.useless_steps = 0
                    self.no_target_counter = 0
                    self.set_target_counter += 1
                    if self.set_target_counter > 10:
                        self.turn(0)
                    time.sleep(0.2)
                    print("set_target - attack")
                    self.autohot_py.F1.press()
                    continue

            if self.useless_steps > 1 and not np.any(low_health):
                # We're stuck, go somewhere
                self.useless_steps = 0
                print("move a bit")
                self.toggle = self.toggle*-1
                if self.toggle == -1:
                    self.set_default_camera()
                    self.autohot_py.DOWN_ARROW.down()
                    time.sleep(1.5)
                    self.autohot_py.DOWN_ARROW.press()
                elif self.toggle == 1:
                    self.autohot_py.UP_ARROW.down()
                    time.sleep(1.5)
                    self.autohot_py.UP_ARROW.press()
            elif not np.any(low_health):
                # Turn on 90 degrees
                turn_ys = [0,0,0,0]
                self.no_target_counter += 1
                self.turn(turn_ys[self.useless_steps])
                self.useless_steps += 1
                print("turn")

            print("next iteration")
            pass

        print("loop finished!")
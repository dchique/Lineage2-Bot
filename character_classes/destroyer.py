from functions import *
from bot import Bot
import numpy as np


class Destroyer (Bot):

    def loop(self, stop_event):
        """
        main bot logic
        """
        #self.set_default_camera()
        self.autohot_py.N0.press() # Follower follow
        while not stop_event.is_set():

            time.sleep(0.1)
            # if np.any(self.check_for_heal(70)): #Getting low
            #     self.autohot_py.N6.press() # Follower heal
            #     self.autohot_py.N0.press() # Follower follow
            # if self.buff_check():
            #     self.autohot_py.N5.press() #Follower buffs
            #     time.sleep(9)
            # Continue attacking if victim is alive
            targeted_hp = self.get_targeted_hp()
            low_health = self.check_for_heal(40)
            if low_health[0]: #LOW HEALTH USE POTS
                self.autohot_py.F9.press()
            if low_health[1]:
                self.autohot_py.N9.press()
            if targeted_hp > 99:
                self.autohot_py.F12.press() # Select next target if being attacked
                print('Not attacking counter: {}'.format(self.not_attacking_counter))
                self.not_attacking_counter += 1
                self.set_target_counter = 0
                if self.not_attacking_counter > 30:
                    self.autohot_py.N0.press() # Follower Follow
                    self.unstuck()
                    self.not_attacking_counter = 0
            if targeted_hp < 15:
                self.autohot_py.F2.press()
            if targeted_hp > 0:
                if (time.time()  - self.follower_attack) > 3:
                    self.follower_attack = time.time()
                    self.autohot_py.N3.press() #Follower assist / attack
                self.useless_steps = 0
                self.no_target_counter = 0
                self.dead_target_counter = 0
                self.set_target_counter = 0
                print("attack the target")
                self.autohot_py.F1.press() #Auto-attack
                continue
            elif targeted_hp == 0 and self.dead_target_counter <= 1:
                print("Pick-up")
                time.sleep(0.4)
                self.autohot_py.F12.press() # Select next target if being attacked
                for i in range(0,3,1):
                    self.autohot_py.F4.press()
                    time.sleep(0.3)
                self.autohot_py.N0.press() #Follow main
                self.not_attacking_counter = 0
                self.dead_target_counter += 1
                print("target is dead")
                continue
            else:
                print("no target yet")
                #print('no dead target counter: {}'.format(self.dead_target_counter))
                # Find and click on the victim
                if self.set_target(targeted_hp) and not np.any(low_health):
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

            if self.move_to_motion() and not np.any(low_health):
                self.autohot_py.DOWN_ARROW.press()
                self.useless_steps = 0
                self.no_target_counter = 0
                print("set_target - attack")
                self.autohot_py.F1.press()
                continue

            if self.no_target_counter >= 15 and not np.any(low_health):
                self.long_move()
                self.no_target_counter = 0

            if self.useless_steps > 4 and not np.any(low_health):
                # We're stuck, go somewhere
                self.useless_steps = 0
                self.not_attacking_counter += 1
                print("go_somewhere - we're stuck")
                self.go_somewhere()
                time.sleep(4)
                self.autohot_py.DOWN_ARROW.press()
            elif not np.any(low_health):
                # Turn on 90 degrees
                turn_ys = [0,0,0,-1,0]
                self.no_target_counter += 1
                self.turn(turn_ys[self.useless_steps])
                self.useless_steps += 1
                print("turn")

            print("next iteration")
            pass

        print("loop finished!")
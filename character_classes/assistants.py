from functions import *
from bot import Bot
import numpy as np


class Assistant (Bot):

    def loop(self, stop_event):
        """
        main bot logic
        """
        def spoil():
            self.click_skill('spoil')

        def sweep():
            self.click_skill('sweep')

        def assist():
            self.autohot_py.F7.press()

        def follow():
            self.autohot_py.F8.press()

        def move():
            self.autohot_py.RIGHT_ARROW.down()
            time.sleep(0.25)
            self.autohot_py.RIGHT_ARROW.up()
            self.autohot_py.UP_ARROW.down()
            time.sleep(1)
            self.autohot_py.UP_ARROW.up()

        def buff():
            self.autohot_py.F9.press()
            time.sleep(4)
        
        #self.set_default_camera()
        timeout = 0
        useless_steps = 0
        buff_time = 0
        fresh_kill = False
        self.find_skill_loc('img/spoil.png','spoil')
        self.find_skill_loc('img/sweep.png','sweep')
        print(self.skill_dict)
        while not stop_event.is_set():
            time.sleep(0.5)
            
            targeted_hp = self.get_targeted_hp()
            
            # if targeted_hp > 99:
            #     print('waiting for damage to target')
            #     time.sleep(0.3)
            #     timeout += 1
            #     if timeout == 3:
            #         print('target timed out - following')
            #         timeout = 0
            #         follow()
            #     continue
            if targeted_hp > 0: #and targeted_hp < 99:
                print('Spoiling')
                #time.sleep(np.random.randint(1,2)*0.5)
                spoil()
                fresh_kill = True
                time.sleep(1.5)
                continue
            elif targeted_hp == 0:
                if fresh_kill:
                    for i in range(0,4,1):
                        self.go_somewhere()
                    fresh_kill = False
                print("target is dead - sweeping")
                sweep()
                self.dead_target_counter += 1
                time.sleep(0.2)
                if (time.time() - buff_time) > 60*2+6:
                    buff_time = time.time()
                    buff()
                if self.dead_target_counter > 1:
                    print('target is dead - following')
                    follow()
                    self.dead_target_counter = 0
                continue
            else:
                self.dead_target_counter = 0
                if useless_steps >= 4:
                    print('no target yet - following')
                    time.sleep(0.2)
                    follow()
                    useless_steps = 0
                else:
                    print('no target yet - assisting')
                    time.sleep(0.1)
                    assist()
                    useless_steps += 1
                
                # Find and click on the victim
                continue

            print("next iteration")
            pass

        print("loop finished!")
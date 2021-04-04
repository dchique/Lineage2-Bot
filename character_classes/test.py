from functions import *
from bot import Bot



class Test (Bot):

    def loop(self, stop_event):
        """
        main bot logic
        """
        #self.set_default_camera()
        while not stop_event.is_set():
            count = 0
            if count == 0:
                self.move_to_motion()
                #self.check_for_heal(70)
            time.sleep(2)

            print("next iteration")
            pass

        print("loop finished!")
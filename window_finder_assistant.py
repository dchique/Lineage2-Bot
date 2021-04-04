import win32gui
import re

class window_finder:

    def __init__(self):
        self.WINDOW_SUBSTRING = "Lineage"
        self.COUNT = 0

    def get_window_info(self):
        # set window info
        window_info = {}
        win32gui.EnumWindows(self.set_window_coordinates, window_info)
        return window_info
    
    def edit_ahk_script(self, hwnd, char_type):
        new_lines = []
        with open('./Keys_to_Assistants.ahk') as f:
            change = False
            for line in f.readlines():
                if change:
                    new_lines += [re.sub('(ahk_id) (\d*)', '\g<1> ' + str(hwnd), line)]
                else:
                    new_lines += [line]
                if char_type in line:
                    change = True
                else:
                    change = False
        with open('./Keys_to_Assistants.ahk', 'w') as f:
            f.writelines(new_lines)

    def set_window_coordinates(self, hwnd, win):
        if win32gui.IsWindowVisible(hwnd):
            if self.WINDOW_SUBSTRING in win32gui.GetWindowText(hwnd):
                if self.COUNT == 0:
                    with open('./hwnd.txt','w') as f:
                        f.writelines([str(hwnd)])
                    print('Extra Char: ' + str(hwnd))
                    self.edit_ahk_script(hwnd, '^')
                    self.COUNT += 1
                else:
                    with open('./hwnd.txt','w') as f:
                        f.writelines([str(hwnd)])
                    win32gui.SetForegroundWindow(hwnd)
                    self.edit_ahk_script(hwnd, '!')
                    print('Spoiler: ' + str(hwnd))

if __name__ == '__main__':
    wf = window_finder()
    window_info = wf.get_window_info()
    test = 1
import time
import pyautogui
def restart(initial = False):
    if initial == False:
        print("死,restart")
        print("开始新一轮")
        time.sleep(0.01)
        # 以下用风灵月影满血以增加训练效率
        pyautogui.keyDown('f2')
        pyautogui.keyDown('f2')
        pyautogui.keyDown('f2') 
        time.sleep(1)
        pyautogui.keyUp('f2') 
        # pass
    else :
        pass
  
if __name__ == "__main__":  
    restart()
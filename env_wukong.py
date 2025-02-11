import pyautogui
import cv2
import time
import matplotlib.pyplot as plt
import utils.directkeys as directkeys
import numpy as np
from screen_key_grab.grabscreen import grab_screen
from screen_key_grab.getkeys import key_check
from utils.restart import restart

from PIL import Image

class Wukong(object):
    def __init__(self, observation_w, observation_h, action_dim):
        super().__init__()

        self.observation_dim = observation_w * observation_h
        self.width = observation_w
        self.height = observation_h
        self.death_cnt = 0
        self.action_dim = action_dim
        self.obs_window = (336,135,1395,885)
        self.boss_blood_window = (677, 908, 1028, 916)
        self.self_blood_window = (184, 972, 504, 980)
        self.boss_stamina_window = (345, 78, 690, 81)  # 如果后期有格挡条的boss可以用，刀郎没有
        self.self_stamina_window = (1473, 948, 1510, 1018)  # 棍势条
        self.boss_blood = 0
        self.self_blood = 0
        self.boss_stamina = 0
        self.self_stamina = 0
        self.power = 0
        self.stop = 0
        self.emergence_break = 0
        
    # 用canny边缘检测实现血量识别，不是特别准确，但打刀郎由于血条有特效只能用这个
    def self_blood_count(self, obs_gray): 
        blurred_img = cv2.GaussianBlur(obs_gray, (3, 3), 0) 
        canny_edges = cv2.Canny(blurred_img, 130, 180)

        # 使用 Pillow 显示
        # image = Image.fromarray(canny_edges)
        # image.show()

        value = canny_edges.argmax(axis=-1)
        return np.max(value)

    def boss_blood_count(self, boss_blood_hsv_img):
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([360, 30, 220])
        mask = cv2.inRange(boss_blood_hsv_img, lower_white, upper_white)
        white_pixel_count = cv2.countNonZero(mask)
        return white_pixel_count
        # blurred_img = cv2.GaussianBlur(boss_blood_hsv_img, (5, 5), 0) 
        # canny_edges = cv2.Canny(blurred_img, 160, 200)
        # value = canny_edges.argmax(axis=-1)
        # return np.max(value)
        

    def self_stamina_count(self, self_stamina_hsv_img):
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([360, 30, 220])
        mask = cv2.inRange(self_stamina_hsv_img, lower_white, upper_white)
        white_pixel_count = cv2.countNonZero(mask)
        return white_pixel_count

    def boss_stamina_count(self, boss_stamina_hsv_img): # 目前刀郎没有架势条（格挡条）
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([360, 30, 220])
        mask = cv2.inRange(boss_stamina_hsv_img, lower_white, upper_white)
        white_pixel_count = cv2.countNonZero(mask)
        return white_pixel_count
    
    def self_power_count(self,self_power_hsv_img): # 天命人棍势条（斜的棍势条，不包含棍势点）
        lower_white = np.array([0, 0, 220])
        upper_white = np.array([360, 45, 256])
        mask = cv2.inRange(self_power_hsv_img, lower_white, upper_white)
        white_pixel_count = cv2.countNonZero(mask)
        return white_pixel_count

    def self_endurance_count(self,obs_gray): # 天命人气力条
        blurred_img = cv2.GaussianBlur(obs_gray, (3,3), 0)
        canny_edges = cv2.Canny(blurred_img, 120, 180)

        # 使用 Pillow 显示
        # image = Image.fromarray(canny_edges)
        # image.show()

        value = canny_edges.argmax(axis=-1)
        return np.max(value)

    def take_action(self, action):
        if action == 0:  # j
            directkeys.light_attack()
        elif action == 1:  # m
            directkeys.left_dodge()
        elif action == 2:
            directkeys.sanlian()
        elif action == 3:
            directkeys.right_dodge()
        elif action == 4:
            directkeys.hard_attack()
        elif action == 5:
            directkeys.stay_still()
        elif action == 6:
            directkeys.forward_dodge()
        elif action == 7:
            directkeys.kan_po()
        elif action == 8:
            directkeys.ding_shen_gong_ji()

    def get_reward(self, boss_blood, next_boss_blood, self_blood, next_self_blood,
                   boss_stamina, next_boss_stamina, self_stamina, next_self_stamina,
                   self_power, next_self_power,
                   stop, emergence_break, action, boss_attack):
        if next_self_blood < 70:     # self dead 用hsv识别则量值大约在400，用canny大约在40
            print("dead")
            # print("快死了，当前血量：",self_blood,"马上血量：",next_self_blood)
            reward = -6
            done = 1
            stop = 0
            emergence_break += 1
            
            # 用风灵月影增加训练效率
            pyautogui.keyDown('f2')
            pyautogui.keyDown('f2')
            pyautogui.keyDown('f2') 
            time.sleep(1)
            pyautogui.keyUp('f2') 
            return reward, done, stop, emergence_break

        else:
            reward = 0
            self_blood_reward = 0
            boss_blood_reward = 0
            self_stamina_reward = 0
            resource_reward = 0
            if next_self_blood - self_blood < -10:
                self_blood_reward = (next_self_blood - self_blood) // 5
                print("掉血惩罚" + str(self_blood_reward))
                # time.sleep(0.05)
                # # 防止连续取帧时一直计算掉血
            # elif next_self_blood - self_blood > 100 and action == 6:
            #     self_blood_reward = (next_self_blood - self_blood) // 10
            #     print("回血奖励" + str(self_blood_reward))
            #     # time.sleep(0.05)
            # elif next_self_blood - self_blood >= 30 and next_self_blood - self_blood <= 100 and action == 6:
            #     self_blood_reward = (next_self_blood - self_blood) // 30 - 1
            #     print("回血奖励" + str(self_blood_reward))
            #     # time.sleep(0.05)
            # elif next_self_blood - self_blood < 30 and next_self_blood - self_blood > 5 and action == 6:
            #     self_blood_reward = (next_self_blood - self_blood) // 50 - 0.6
            #     print("回血奖励" + str(self_blood_reward))
                # time.sleep(0.05)
            
            if next_boss_blood - boss_blood <= -18:
                boss_blood_reward = (boss_blood - next_boss_blood) // 5
                boss_blood_reward = min(boss_blood_reward, 20)
                print("打掉boss血而奖励" + str(boss_blood_reward))
            
            if next_boss_blood - boss_blood > -5 and self_power - next_self_power > 30:
                resource_reward = float(next_self_power - self_power) / 50
                print("耗豆但打空的惩罚" + str(resource_reward))
            # elif next_self_blood - self_blood <= 50 and action == 6:
            #     resource_reward = max(float(next_self_blood - self_blood) / 20 - 5, -5)
            #     print("喝葫芦溢出的惩罚" + str(resource_reward))
            
            if (action == 1 or action == 3 or action == 6) and boss_attack == True and \
                    (next_self_stamina - self_stamina >= 7 or next_self_power - self_power > 30) and \
                    next_self_blood - self_blood >= -10:
                self_stamina_reward += 2    # 回复了棍势条，说明是完美闪避
                print("完美闪避奖励" + str(self_stamina_reward))
            elif (action == 1 or action == 3 or action == 6) and boss_attack == True and \
                    next_self_blood - self_blood >= -10:
                self_stamina_reward += 0.5
                print("成功闪避奖励" + str(self_stamina_reward))
            elif action == 7 and boss_attack == True and next_self_blood - self_blood >= -10:
                self_stamina_reward += 1.0
                print("成功格挡奖励" + str(self_stamina_reward))
            reward = reward + self_blood_reward * 0.8 + \
                boss_blood_reward * 1.6 + self_stamina_reward * 1.0 + resource_reward * 8.0
            done = 0
            emergence_break = 0
            return reward, done, stop, emergence_break

    def step(self, action, boss_attack, next_power):
        obs_screen = grab_screen(self.obs_window)

        obs_resize = cv2.resize(obs_screen, (self.width, self.height))
        obs = np.array(obs_resize).reshape(-1, self.height, self.width, 4)[0]
        # 血量统计
        self_blood_img1 = grab_screen(self.self_blood_window)
        self_blood_hsv_img1 = cv2.cvtColor(self_blood_img1, cv2.COLOR_BGR2HSV)
        next_self_blood1 = self.self_blood_count(self_blood_hsv_img1)
        next_self_blood = next_self_blood1
        print("自身剩余血量：" + str(next_self_blood))
        # boss血量统计
        boss_blood_img = grab_screen(self.boss_blood_window)
        boss_blood_hsv_img = cv2.cvtColor(boss_blood_img, cv2.COLOR_BGR2HSV)
        next_boss_blood = self.boss_blood_count(boss_blood_hsv_img)
        print("BOSS剩余血量：" + str(next_boss_blood))
        # 棍势统计
        self_stamina_img = grab_screen(self.self_stamina_window)
        self_stamina_hsv_img = cv2.cvtColor(self_stamina_img, cv2.COLOR_BGR2HSV)
        next_self_stamina = self.self_stamina_count(self_stamina_hsv_img)
        # boss架势条统计
        boss_stamina_img = grab_screen(self.boss_stamina_window)
        boss_stamina_hsv_img = cv2.cvtColor(
            boss_stamina_img, cv2.COLOR_BGR2HSV)
        next_boss_stamina = self.self_stamina_count(boss_stamina_hsv_img)

        if (action == 0):
            print("一连")
        elif (action == 1):
            print("左闪避")
        elif (action == 2):
            print("三连")
        elif action == 3:
            print("右闪避")
        elif action == 4:
            print("重棍")
        elif action == 5:
            print("静止")
        elif action == 6:
            print("前闪避")
        elif action == 7:
            print("轻棍+识破")
        elif action == 8:
            print("定！绝世五连！")

        if next_self_blood < 150:
            directkeys.recover()
            time.sleep(0.4)
        self.take_action(action)

        reward, done, stop, emergence_break = self.get_reward(self.boss_blood, next_boss_blood, self.self_blood, next_self_blood,
                                                              self.boss_stamina, next_boss_stamina, self.self_stamina, next_self_stamina,
                                                              self.power, next_power,
                                                              self.stop, self.emergence_break, action, boss_attack)
        self.self_blood = next_self_blood
        self.boss_blood = next_boss_blood
        self.self_stamina = next_self_stamina
        self.boss_stamina = next_boss_stamina
        self.power = next_power
        return (obs, reward, done, stop, emergence_break)

    def pause_game(self, paused): # 用于训练中暂停
        keys = key_check()
        if 'T' in keys:
            if paused:
                paused = False
                print('start game')
                time.sleep(1)
            else:
                paused = True
                print('pause game')
                time.sleep(1)
        if paused:
            print('paused')
            while True:
                keys = key_check()
                if 'T' in keys:
                    if paused:
                        paused = False
                        print('start game')
                        time.sleep(1)
                        break
                    else:
                        paused = True
                        time.sleep(1)
        return paused

    def reset(self, initial=False):
        restart(initial)
        obs_screen = grab_screen(self.obs_window)
        obs_resize = cv2.resize(obs_screen, (self.width, self.height))
        obs = np.array(obs_resize).reshape(-1, self.height, self.width, 4)[0]
        return obs

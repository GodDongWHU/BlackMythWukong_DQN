import ctypes
import time
from pykeyboard import PyKeyboard
import pyautogui
SendInput = ctypes.windll.user32.SendInput


W = 0x11
A = 0x1E
S = 0x1F
D = 0x20

M = 0x32
J = 0x24
K = 0x25
LSHIFT = 0x2A
R = 0x13#用R代替识破
V = 0x2F

Q = 0x10
I = 0x17
O = 0x18
P = 0x19
C = 0x2E
F = 0x21

up = 0xC8
down = 0xD0
left = 0xCB
right = 0xCD

esc = 0x01

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    
def light_attack():
    PressKey(J)
    time.sleep(0.1)
    ReleaseKey(J)
    time.sleep(0.3)
    
def hard_attack():
    PressKey(M)
    time.sleep(0.2)
    ReleaseKey(M)
    time.sleep(1.5)

def stay_still():
    time.sleep(0.05)


def hard_attack_long():
    PressKey(W)
    PressKey(O)
    PressKey(M)
    time.sleep(4.8)
    ReleaseKey(M)
    ReleaseKey(W)
    ReleaseKey(O)
    PressKey(C)
    ReleaseKey(C)
    time.sleep(2.5)

    
def dodge():
    PressKey(K)
    time.sleep(0.1)
    ReleaseKey(K)
    time.sleep(0.1)

def wulian():
    light_attack()
    light_attack()
    light_attack()
    light_attack()
    time.sleep(0.5)
    light_attack()
    time.sleep(0.1)

def erlian():
    light_attack()
    light_attack()

def sanlian():
    light_attack()
    light_attack()
    light_attack()

def silian():
    light_attack()
    light_attack()
    light_attack()
    light_attack()
    
def left_dodge():
    PressKey(A)
    dodge()
    ReleaseKey(A)

def right_dodge():
    PressKey(D)
    dodge()
    ReleaseKey(D)

def back_dodge():
    PressKey(S)
    dodge()
    ReleaseKey(S)

def forward_dodge():
    PressKey(W)
    dodge()
    ReleaseKey(W)

def ding_shen_gong_ji():
    pyautogui.keyDown('1')
    pyautogui.keyUp('1')
    time.sleep(0.5)
    PressKey(F)
    ReleaseKey(F)
    time.sleep(0.8)
    wulian()

def kan_po():
    PressKey(J)
    time.sleep(0.1)
    ReleaseKey(J)
    # time.sleep(0.2)
    # light_attack()
    PressKey(M)
    time.sleep(0.01)
    ReleaseKey(M)
    time.sleep(0.2)
    PressKey(M)
    time.sleep(0.01)
    ReleaseKey(M)
    time.sleep(0.5)
    light_attack()

def recover():
    back_dodge()
    PressKey(D)
    time.sleep(0.1)
    PressKey(R)
    time.sleep(0.01)
    ReleaseKey(R)
    ReleaseKey(D)

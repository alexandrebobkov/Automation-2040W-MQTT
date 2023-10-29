#import machine
#from network import WLAN
#wlan = WLAN()
#if machine.reset_cause() != machine.SOFT_RESET:
#    wlan.init(WLAN.STA)
#    wlan.ifconfig(config=('10.100.71.21', '255.255.255.0', '10.100.71.1', '10.100.71.1'))   
#if not wlan.isconnected():
#    wlan.connect('IoT_bots', auth=(WLAN.WPA2, '208208208'), timeout=5000)
#    while not wlan.isconnected():
#        machine.idle()

#import machine
#from machine import Pin
#import time
#from automation import *

#board = Automation2040W()

#for i in range (0,10):
#    board.conn_led(True)
#    time.sleep(250)
#    board.conn_led(False)
#    time.sleep(500)

import time
from machine import Pin, Timer

led = machine.Pin("LED", machine.Pin.OUT)
timer = Timer()

def blink_led(timer):
    led.toggle()

timer.init(freq=10, mode=Timer.PERIODIC, callback=blink_led)

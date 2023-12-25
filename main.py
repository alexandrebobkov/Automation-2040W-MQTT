import machine
from machine import Pin, Timer
import time
from automation import *
import network
#import secrets
#import _thread
from umqtt.simple import MQTTClient

board = Automation2040W()

toggleA = False
toggleB = False
debounce_time = 0
mqtt_host = "10.100.50.16"
mqtt_username = ""
mqtt_password = ""
mqtt_publish_topic = "esp32/sw2"
mqtt_publish_topic_msg = "OK"
mqtt_client_id = "esp32-prototype"

sw_A = Pin(12,Pin.IN, Pin.PULL_UP)
sw_B = Pin(13,Pin.IN, Pin.PULL_UP)
led = machine.Pin("LED", machine.Pin.OUT)
timer = Timer()

def blink_led(timer):
    led.toggle()

def connect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi ...')
        wlan.active(True)
        wlan.connect('IoT_bots', '208208208')
        
        while not (wlan.isconnected) or (wlan.ifconfig()[0] == '0.0.0.0'):
            time.sleep(3)
            wlan.connect('IoT_bots', '208208208')
            board.conn_led(False)
#        while not wlan.isconnected:
#            print('.')
#            board.conn_led(True)
#            time.sleep(1)
#            board.conn_led(False)
#            time.sleep(1)
#            machine.reset()
     
#    if (wlan.isconnected()) == True:
#        board.conn_led(True)
#        print(wlan.ifconfig())
#    else:
#        board.conn_led(False)
    print('IP Address: ', wlan.ifconfig()[0])
    
    if wlan.ifconfig()[0] != '0.0.0.0':
        print('Connected!')
        board.conn_led(True)
    if wlan.ifconfig()[0] == '0.0.0.0':
#        time.sleep(0.5)
        print('Not Connected :(')
        board.conn_led(False)
#        machine.reset()
    
def callback_A(sw_A):
    global debounce_time
    if (time.ticks_ms()-debounce_time)>1000:        
        debounce_time = time.ticks_ms()
        print('Button A was pressed')
        toggle = not board.relay(0)
        board.switch_led(0, toggle)
        board.relay(0, toggle)
        board.output(0, 100)	# CAREFUL! Supplies 9V !!!
        client.publish("pico2040/sw1", "sw 1 pressed")
    
def callback_B(sw_B):
    print('Button B was pressed')
    toggle = not board.relay(1)
    board.switch_led(1, toggle)
    board.relay(1, toggle)
    client.publish("pico2040/sw2", "sw 2 pressed")
    
##
## MQTT
##
# Callback function. Listens to a subscribed topic
def mqtt_callback(topic, msg):
    #global toggle
    print("New message on topic {}".format(topic.decode('utf-8')))
    msg = msg.decode('utf-8')
    print(msg)
    # turn Relay 2 and LED 2 ON
    if msg == "on":
        board.switch_led(1, True)
        board.relay(1, True)
    # turn Relay 2 and LED 2 OFF
    elif msg == "off":
        board.switch_led(1, False)
        board.relay(1, False)
    # toggle state of Relay 2 ON and OFF
    elif msg == "toggle":
        toggle = not board.relay(1)
        board.switch_led(1, toggle)
        board.relay(1, toggle)

# MQTT Connect to a brocker
def mqtt_connect():
    client = MQTTClient(mqtt_client_id, mqtt_host, keepalive=3600)
#    client.connect()
#    client = MQTTClient(mqtt_client_id, mqtt_host, mqtt_username, mqtt_password)
    client.set_callback(mqtt_callback)
    client.connect()
    print('Connected to MQTT Brocker')
    return client

def mqtt_reconnect():
    time.sleep(5)
    #machine.reset()
    
timer.init(freq=2, mode=Timer.PERIODIC, callback=blink_led)

# Try connect to a Wi-Fi
try:
    connect()
except KeyboardInterrupt:
    machine.reset()
    
# Try connect to a Mosquitto brocker
try:
    client = mqtt_connect()
except OSError as e:
    mqtt_reconnect()

#time.sleep(1)

while True:
    if (board.switch_pressed(SWITCH_A)):
        toggleA = not toggleA
        board.switch_led(0, toggleA)
        board.relay(0, toggleA)
        print('Button A was pressed')        
    sw_A.irq(trigger=Pin.IRQ_FALLING, handler=callback_A)
    sw_B.irq(trigger=Pin.IRQ_FALLING, handler=callback_B)
    client.subscribe("pico2040/sw2")
#    client.publish(mqtt_publish_topic, mqtt_publish_topic_msg)
    time.sleep(0.5)

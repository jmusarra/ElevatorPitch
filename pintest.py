
'''
Limit Switches:
    Brown/White - normally closed - connected to step+ and step-
    Black/Blue - normally open - not connected

Speeds:
    The motor moves in discrete units called 'steps'. For this motor and drivetrain, 3031 steps move the belt 1 inch.
    Acceleration and deceleration are set in revolutions per second per second. Lower numbers produce a more gradual accel/decel.
    Speed is in revolutions per second. Max for this application should be about 2.75 revolutions per second.

Dimensions:
    Sprocket pitch diameter = 2.1"
    Sprocket circumference = 6.597339" (too precise? MAYBE.)
    Steps per revolution: 20,000
    Steps per inch: 3031
    Door travel: 24" / 72,744 steps

Timing:
    Target open time: 1.5 seconds
    Target close time: 2.0 seconds
'''


import network
import socket
import websockets
from machine import UART               # UART documentation at http://docs.micropython.org/en/v1.9.3/pyboard/library/machine.UART.html
from machine import Pin                # General-Purpose Input/Out pins for button and limit switch inputs
from uosc.client import Client

limitOpen = Pin(12, Pin.IN)
limitClose = Pin(14, Pin.IN)


drive = UART(1,9600)
drive.init(9600, bits=8, parity=None, stop=1)  # 9600 baud, 8 data bits, 1 stop bit, no parity

moveDistance = 72744                           # distance in steps to close / open doors

spi = 3031                                     # steps per inch of the motor/sprocket/belt

CONSOLE_IP = "192.168.1.114"                   # Make this the same as the IP address of the lighting console

console = Client(CONSOLE_IP, 8000)             # creates an OSC client that will send to the lighting console at CONSOLE_IP





nic = network.WLAN(network.STA_IF)
if not nic.isconnected():
    nic.active(True)
    nic.config(dhcp_hostname='NetIO Gateway')
    nic.connect('Stagehouse', 'Stage75!$Pp?')
    while not nic.isconnected():
        pass
print(nic.ifconfig())


def pinTest():
    closeLast = limitClose.value()
    openLast = limitOpen.value()
    while True:
        if (closeLast == 0 && limitClose == 1):
            console.send('/eos/sub/1/fire',1.0)
            closeLast = limitClose.value()
        if (closeLast == 1 && limitClose == 0):
            console.send('/eos/sub/1/fire',0.0)
            closeLast = limitClose.value()



def fireCue(num):
    eos.send('/eos/cue/fire',num)

'''
def initializeDrive():                         # Move this to boot.py
    'PM2' # sets power-up mode to SCL
    'VE2.75' # sets speeed to 2.75 revolutions per second
    'AM' # sets maximum acceleration
    'JD' # Jog Disable
    'AC' # sets acceleration rate
    'DE' # sets deceleration rate
    'EG20000' # microstep resolution 20,000 steps per revolution
    'DL1' # set STEP and DIR inputs to be used as normally open limit inputs
'''

pinTest()























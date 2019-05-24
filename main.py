
'''
Limit Switches:
    Brown/White - normally closed - connected to step+ and step-
    Black/Blue - normally open - not connected

Speeds:
    The motor moves in discrete units called 'steps'. For this motor and drivetrain, 3031 steps move the belt 1 inch.
    Acceleration and deceleration are set in revolutions per second per second. Lower numbers produce a more gradual accel/decel.
    Speed is in revolutions per second. Max for this application should be about 4 revolutions per second.

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
import time
print('main.py loaded')
print('delaying 5 seconds...')
time.sleep(2)
print('ok lets go')
#import network
#import socket
#import sys
#import websockets
from machine import UART               # UART documentation at http://docs.micropython.org/en/v1.9.3/pyboard/library/machine.UART.html
from machine import Pin                # General-Purpose Input/Out pins for button and limit switch inputs
from machine import RTC
from machine import Timer

blinky = Timer(0)
limitOpen = Pin(35, Pin.IN)            # Labeled SW1
limitClose = Pin(34, Pin.IN)           # Labeled SW2
buttonOpen = Pin(32, Pin.IN)           # Labeled B1
buttonClose = Pin(10, Pin.IN)          # Labeled B2
indicatorLight = Pin(5, Pin.OUT)       # Labeled L1

pins = [limitOpen, limitClose, buttonOpen, buttonClose]

debounceDelay = 150                    # in milliseconds

drive = UART(2,9600,tx=17,rx=16)
drive.init(9600, bits=8, parity=None, stop=1)  # 9600 baud, 8 data bits, 1 stop bit, no parity
time.sleep_ms(100)

closedPosition = '80800'                      # distance in steps to close / open doors
openPosition = '2100'                          # defined as a string so it can be sent over serial
spi = 3031                                     # steps per inch of the motor/sprocket/belt
limitDistance = 2100                           # number of steps from contact with limit switch to switch engaging. Use to back motor off once limit has been hit. (eg, after homing)

#CONSOLE_IP = '10.0.0.100'                  # Make this the same as the IP address of the lighting console
#console = Client(CONSOLE_IP, 8000)         # creates an OSC client that will send commands to the lighting console at CONSOLE_IP

actuations = 0
homed = False
#nic = network.LAN(mdc = Pin(23), mdio = Pin(18), power = Pin(17), phy_type = network.PHY_LAN8720, phy_addr=0)

'''
def networkConnect():
    if not nic.isconnected():
        nic.active(True)
        nic.ifconfig(('10.0.0.10', '255.255.255.0','10.0.0.1', '10.0.0.1'))
    print(nic.ifconfig())
'''

def readReply():
    print('Drive says: ')
    if drive.any():
        if drive.read() == b'%\r':
            return "OK"
        else:
            return "shruggie?"


def pinTest():
    print('Testing pins')
    closeLast = limitClose.value()
    openLast = limitOpen.value()
    buttonLast = buttonOpen.value()
    while True:
        if (closeLast == 0 and limitClose.value() == 1):
            #console.send('/eos/sub/1/fire',1.0)
            closeLast = limitClose.value()
            print('switch 1 closed')
            #websocket send "S1=1"
        if (closeLast == 1 and limitClose.value() == 0):
            #console.send('/eos/sub/1/fire',0.0)
            closeLast = limitClose.value()
            print("switch 1 open")
            #websocket send "S1=0"
        if (openLast == 0 and limitOpen.value() == 1):
            #console.send('/eos/sub/2/fire',1.0)
            openLast = limitOpen.value()
            print('switch 2 closed')
            #websocket send "S2=1"
        if (openLast == 1 and limitOpen.value() == 0):
            #console.send('/eos/sub/2/fire',0.0)
            openLast = limitOpen.value()
            print("switch 2 open")
            #websocket send "S2=0"
        if (buttonLast == 0 and buttonOpen.value() == 1):
            #console.send('/eos/sub/3/fire',1.0)
            buttonLast = buttonOpen.value()
            print('button down')
            #websocket send "B=1"
        if (buttonLast == 1 and buttonOpen.value() == 0):
            #console.send('/eos/sub/3/fire',0.0)
            buttonLast = buttonOpen.value()
            print("button up")
            #websocket send "B=0"

def checkPin(pin):
    # wait for pin to change value
    # it needs to be stable for a continuous amount of time, defined as debounceDelay - tested happy at 150ms
    cur_value = pin.value()
    active = 0
    while active < debounceDelay:
        if pin.value() != cur_value:
            active += 1
        else:
            active = 0
        time.sleep_ms(1)
    return True

'''
### this stuff is all useless:

def openLimitHit(state):
    print('The OPEN limit switch has been triggered, and is in state ' + state)
    drive.write('SP0\r')  # If we hit this limit, set current position as zero

def closeLimitHit(state):
    print('The CLOSE limit switch has been triggered, and is in state ' + state)
    # this is the close limit so really we should try to NEVER EVER hit this

def openButtonHit():
    print('The OPEN DOOR button has been pressed')
    drive.write('DI74244\r')     # Tell the drive where we'd like to go
    time.sleep_ms(50)
    drive.write('FP\r')                         # Begin movement, to position defined above
    drive.read()
    time.sleep(3)

def closeButtonHit():
    print('The CLOSE DOOR button has been pressed')
    drive.write('DI-' + closedPosition + '\r')
    time.sleep_ms(50)
    drive.write('FL\r')
    '''


def sendSCL(command, value=None):          # utility function to build Serial Command Language strings and write them to the drive because omg am I tired of typing 'drive.write()'
    drive.read()
    drive.read()
    if value == None:
        drive.write(str(command.upper()) + '\r')
        print("Sent: " + str(command.upper()) + '\r')
    else:
        drive.write(str(command).upper() + str(value) + '\r')
    time.sleep_ms(150)
    reply = drive.read()
    if reply == b'%\r':
        return('OK')
    else: 
        return(str(reply))

def timestamp():
    return(str(str(time.localtime()[0]) + '-' + str(time.localtime()[1]) + '-' + str(time.localtime()[2]) + '  ' + str(time.localtime()[3]) + ':' + str(time.localtime()[4]) + ':' + str(time.localtime()[5])))


def initializeDrive():
    '''
    Send desired parameters to the drive as soon as we start up. Set things like speed, microstep resolution, accel/decel, etc.

    # 'PM2'     sets power-up mode to SCL
    # 'VE4'     sets speeed to 4 revolutions per second
    # 'AM3'     sets maximum acceleration
    # 'JD'      Jog Disable
    # 'AC2'     sets acceleration rate
    # 'DE2'     sets deceleration rate
    # 'EG25000' microstep resolution 25,000 steps per revolution
    # 'IFD'     tells drive to send status information in decimal (default is hexadecimal)

    '''
    print('Initializing Drive...')
    initCmds = ['PM2', 'EG25000', 'VE1.2', 'AM1', 'JD', 'AC0.8', 'DE0.8', 'IFD']
    for cmd in initCmds:
        sendSCL(cmd)
        time.sleep_ms(20)
    initQueries = ['PM', 'EG', 'VE', 'AM', 'JD', 'AC', 'DE']
    for q in initQueries:
        sendSCL(q)
    time.sleep_ms(200)
    status = drive.read()
    # if 
    print(status)
    print('Done.')
    if sendSCL('RS') == "b'RS=R\\r'":
        print('Drive is ready.')

    # TODO add code that reads responses and sorts out ACKs from NACKS. Return good if all ACKS.

def xxx():
    sendSCL('SK')

def getValue(s):
    if s == None:
        print('Invalid data return. Drive not powered?')
        pass
    t = s.split('=')
    u = t[1]
    return(int(u[:-3]))

def blink(blinky):         # worst function signature ever? maybe.
    indicatorLight.value(not indicatorLight.value())

def home():
    blinky.init(freq=3, mode=Timer.PERIODIC, callback=blink)
    global homed
    print("homing....")
    sendSCL('di', -5)      # Set movement to counterclockwise / door opening
    sendSCL('js',0.4)      # Set speed and accel/decel for homing - slower than show speed
    sendSCL('ja',0.25)     # slow accel
    sendSCL('jl',500)      # REALLY FAST decel, so we can get a good position for the limit switch
    sendSCL('JE')          # Enable Jog
    drive.read()
    time.sleep_ms(30)
    drive.read()
    p = getValue(sendSCL('SP'))
    print(p)
    if p < 2000 or limitOpen.value() == 0:
        sendSCL('FL',10000)
        time.sleep(3)
    sendSCL('CJ')          # COMMENCE JOGGING
    if checkPin(limitOpen):
        print("WE HIT IT!")
        sendSCL('SJ')
        time.sleep_ms(30)
        p = getValue(sendSCL('SP'))
        print(p)
        print("SETTING ZERO")
        sendSCL('sp',-1950)
        blinky.deinit()
        homed = True
        print("done.")
        indicatorLight.value(0)

    '''
    while checkPin(limitOpen) == 1:

    Drive motor counter-clockwise until limitOpen is hit
    When limitOpen is hit, immediately stop motion - drive.write('SK')
    sendSCL('FL2100')     #Back off clockwise 2100 steps
    Set this position as zero
    '''



def bff(delay):
    global actuations
    global homed
    if homed == True:
        indicatorLight.value(1)
        #sendSCL('FP', 0)
        #time.sleep(delay1)
        sendSCL('FP', 2100)
        time.sleep(delay)
        sendSCL('FP', 80500)          # changed from 80800 to help alleviate gaposis
        time.sleep(0.5)               # TODO - increase this so the light goes out when the doors close
        indicatorLight.value(0)
        actuations += 1
        print("Last actuation (#" + str(actuations) + ") at " + timestamp())
        indicatorLight.value(0)
    else:
        print("Drive not homed. No movey!")

def openOrClose():
    global actuations
    global homed
    if homed:
        here = getValue(sendSCL('sp'))
        print("Here = " + str(here))
        if here >= 40000:
            sendSCL('fp',2100)
            indicatorLight.value(1)
            time.sleep(4)
            indicatorLight.value(0)
        if here <= 39999:
            sendSCL('fp',80800)
            indicatorLight.value(1)
            time.sleep(4)
            indicatorLight.value(0)
        actuations += 1
        print("Last actuation (#" + str(actuations) + ") at " + timestamp())

def gsx():
    global homed
    while True:
        if homed:
            if checkPin(buttonOpen):
                bff(6)


initializeDrive()
buttonCount = 0
print('Current location: ' + sendSCL('SP'))
home()

while True:
    #if !nic.isconnected():            # commenting out network code, because nothing uses the network :(
    #    networkConnect()
    if checkPin(buttonOpen):
        if homed == True:
            openOrClose()





















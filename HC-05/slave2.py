import uos
from machine import UART,Pin
import utime
from neopixel import NeoPixel
import _thread
import random

"""
Raspberry Pi Pico/MicroPython
Pair two HC-05s as Slave & Master
Slave HC-05 connected to UART0
Master HC-05 connected to UART1
CMODE=1 - connect any address

default UART
UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=0, rx=1)
UART(1, baudrate=115200, bits=8, parity=None, stop=1, tx=4, rx=5)

Connection:
RPi Pico UART0  Slave HC-05
GP0(pin 1)      RX
GP1(pin 2)      TX

RPi Pico UART1  Master HC-05
GP4(pin 6)      RX
GP5(pin 7)      TX

To enter AT-Command mode-
HC05:
Press & Hold the onboard button while power on.

ROLE  0 = Slave
      1 = Master
      2 = Slave-loop
CMODE 0 = connect fixed address
      1 = connect any address
      2 = Slave-loop
"""

print(uos.uname())
uart1 = UART(0,baudrate=38400)  #at-command
#uart1.init(baudrate=38400,bits=8, parity=None, stop=1)
#uart1 = machine.UART(1,baudrate=38400)  #at-comand

#2 sec timeout is arbitrarily chosen
def sendCMD_waitResp(cmd, uart=uart1, timeout=2000):
    print("CMD: " + cmd)
    uart.write(cmd)
    waitResp(uart, timeout)
    print()
    
def waitResp(uart=uart1, timeout=2000):
    prvMills = utime.ticks_ms()
    resp = b""
    while (utime.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.read(1)])
    print(resp)



#indicate program started visually
led_onboard = Pin(25, machine.Pin.OUT)
led_onboard.value(0)     # onboard LED OFF/ON for 0.5/1.0 sec
utime.sleep(0.5)
led_onboard.value(1)
utime.sleep(1.0)
led_onboard.value(0)


"""
print("- uart0 -")
waitResp()
sendCMD_waitResp("AT\r\n")
sendCMD_waitResp("AT+ORGL\r\n")           #Restore default setting
sendCMD_waitResp("AT+VERSION\r\n")
sendCMD_waitResp("AT+UART?\r\n")
#sendCMD_waitResp("AT+UART=38400,0,0\r\n")  #9600 baud, 1 stop, parity=none
#sendCMD_waitResp("AT+UART?\r\n")
sendCMD_waitResp("AT+PSWD?\r\n")
sendCMD_waitResp("AT+PSWD=1234\r\n")      #Set PIN = "1234"
sendCMD_waitResp("AT+PSWD?\r\n")
sendCMD_waitResp("AT+ROLE?\r\n")
sendCMD_waitResp("AT+ROLE=0\r\n")         #Slave
sendCMD_waitResp("AT+ROLE?\r\n")
sendCMD_waitResp("AT+CMODE?\r\n")
sendCMD_waitResp("AT+CMODE=1\r\n")        #connect any address
sendCMD_waitResp("AT+CMODE?\r\n")
sendCMD_waitResp("AT+NAME?\r\n")
sendCMD_waitResp("AT+NAME=HC-05S\r\n")
sendCMD_waitResp("AT+NAME?\r\n")
sendCMD_waitResp("AT+ADDR?\r\n")
"""

def toBLT(chnl,rgb=0, timeout=3000):
    rxData = bytes()
    # ".$DM" & ch1 & ":" & vl1 & Chr(13)
    txData = ".$DM{}:{}\r".format(chnl,rgb)
    #print (txData)#shell output
    uart1.write(txData)
    start_time = utime.ticks_ms()
    while True:
        utime.sleep_ms(3)
        
        end_time = utime.ticks_ms()
        if end_time-start_time>timeout:
            break
        
        if uart1.any() > 0:
            # #OK<CR>
            # #NOK,CR>
            rxData = uart1.read()
            #print(rxData," ,last:",rxData[-1]," )
            last = rxData[-1]
            if last==13:
                return 1
    return 0

NUMBER_PIXELS = 16
LED_PIN = 28

ring = strip = NeoPixel(Pin(LED_PIN), NUMBER_PIXELS)

ch = 0
rgb = 255
spd = 0.1
pot = True
# main program

def showpoint():
    global ch,rgb
       
    for i in range(0, NUMBER_PIXELS):
        if ch==0:                 
            ring[i] = (rgb,0,0)
        elif ch==1: 
            ring[i] = (0,rgb,0)
        else: 
            ring[i] = (0,0,rgb)           
           
        ring.write() # send the data from RAM down the wire
        utime.sleep(0.2) # keep on 1/10 of a second
        ring[i] = (0,0,0) # change the RAM back but don't resend the data 
    
def showcircle():
    global ch,rgb

    if ch==0:                 
        ring.fill((rgb,0,0))
    elif ch==1: 
         ring.fill((0,rgb,0))
    else: 
        ring.fill((0,0,rgb))
    ring.write()
    utime.sleep(0.5)
    ring.fill((0,0,0))
    ring.write()
    utime.sleep(0.2)

def blink():
    global pot

    while True:
        if pot==True:
            showpoint() 
        else:
            showcircle()

def change_rgb():   
    global rgb, spd, bt1, ch, pot
   
    rs = "NOK"
    i = uart1.any()
    if i>0:
        et1 = utime.ticks_ms() 
        if et1-bt1>50:
            rxData = uart1.read()            
            if rxData.find(b"RED")>=0:
                ch = 0                
                rs="OK"
            elif rxData.find(b"GRE")>=0:
                ch = 1
                rs="OK"
            elif rxData.find(b"BLU")>=0:
                ch = 2
                rs="OK"      
            elif rxData.find(b"Th+")>=0:
                rgb = rgb+10 if rgb<=240 else 0
                rs="OK#{}".format(rgb)  
            elif rxData.find(b"Th-")>=0:
                rgb = rgb-10 if rgb>=10 else 250
                rs="OK#{}".format(rgb) 
            elif rxData.find(b"PO")>=0:
                pot = True
                rs="OK#{}".format(pot)  
            elif rxData.find(b"CL")>=0:
                pot = False
                rs="OK#{}".format(pot)   

            print("{}.{} > {}".format(rxData,rgb,rs))
            uart1.write("{}\n".format(rs)) 
        else:
            bt1 = utime.ticks_ms()              
       
_thread.start_new_thread(blink,())
#_thread.start_new_thread(change_rgb,())
     
bt1 = utime.ticks_ms()
bt2 = utime.ticks_ms()
while True:
    et2 = utime.ticks_ms()
    if et2-bt2>500:
        led_onboard.toggle()
        bt2 = utime.ticks_ms()
        
    change_rgb()
    










import uos
from machine import UART,Pin
import utime
from neopixel import NeoPixel

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

patern = (255,0,0)
spd = 0.1
# main program

while True:
    for i in range(0, NUMBER_PIXELS):
        ring[i] = pattern # red=255, green and blue are 0
        ring.write() # send the data from RAM down the wire
        utime.sleep(spd) # keep on 1/10 of a second
        ring[i] = (0,0,0) # change the RAM back but don't resend the data 
    
        i = uart1.any()
        if i > 0:   
            bt1 = utime.ticks_ms()      
            while True:
                et1 = utime.ticks_ms()
                if et1-bt1 > 100:
                    rs = "NOK"
                    i = uart1.any()
                    rxData = uart1.read()            
                    if rxData.find(b"RED")>=0:
                        pattern = (255,0,0)
                        rs="OK"
                    elif rxData.find(b"GRE")>=0:
                        pattern = (0,255,0)
                        rs="OK"
                    elif rxData.find(b"BLU")>=0:
                        pattern=(0,0,255)
                        rs="OK"      
                    
                    uart1.write("{}\n".format(rs))                   
                    break    










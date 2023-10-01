import uasyncio
from machine import UART,Pin
import utime
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


uart1 = UART(0,baudrate=38400,timeout=25)  #at-command
uart1.init(baudrate=38400,bits=8, parity=None, stop=1)
#uart1 = machine.UART(1,baudrate=38400)  #at-comand


#indicate program started visually
led_onboard = Pin(25, Pin.OUT)
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



bt1 = utime.ticks_ms()
def uart_rw():   
    ndx = 0   
    rxBuf = bytearray(30)

    sreader = uasyncio.StreamReader(uart1)
    swriter = uasyncio.StreamWriter(uart1, {})
    rs = "OK"
    while True:       
        res = await sreader.readline()      
        print("{}".format(res))                

        swriter.write('OK\n')
        await swriter.drain()  # Transmission starts now.
        await uasyncio.sleep_ms(3)
                                   
       
def blink():
    while True:
        led_onboard.toggle()
        await uasyncio.sleep_ms(500)
        


async def main():
    rx = uasyncio.create_task(uart_rw())
    tx = uasyncio.create_task(blink())
    while True:
        await uasyncio.sleep_ms(5)    

def test():
    try:
        uasyncio.run(main())

    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        uasyncio.new_event_loop()
        print('as_demos.auart.test() to run again.')

test()
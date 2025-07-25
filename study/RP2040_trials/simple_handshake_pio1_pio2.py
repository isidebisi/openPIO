  
# Example of writing a parallel byte from data; with data ready and simulated data taken flow control
# for a more wrapped-up examples, see https://github.com/raspberrypi/pico-micropython-examples/blob/master/pio/pio_pwm.py


from machine import Pin
from rp2 import PIO, StateMachine, asm_pio, PIOASMEmit
from time import sleep

#outputs a byte through 8 GPIO pins and set the data ready high
@asm_pio(sideset_init=PIO.OUT_LOW, out_init=(rp2.PIO.OUT_HIGH,) * 8, out_shiftdir=PIO.SHIFT_RIGHT, 
         autopull=True, pull_thresh=16 )
def paral_prog():
    pull()                  #pull data from the transmit SR      
    out(pins, 8)  .side(1)  #output data to 8 pins and set "data ready" line high
    nop() [7]
    nop() [7]
    wait(1, pin, 0)         #wait for the "data taken" line to go high
    nop()         .side(0)  #set the "data ready" line low
    nop() [7]
    nop() [7]

print(paral_prog)  # Output: List of 16-bit binary instructions

#this sets the other PIO to act as a surrogate TIM computer to
#generate a "data taken" signal when a "data ready" signal is received
@rp2.asm_pio(sideset_init=PIO.OUT_LOW)
def wait_pin_high():
    wrap_target()

    wait(1, pin, 0)         #wait for the "data ready" line to go high
    nop()      .side(1)     #set the "data taken" line high
    wait(0, pin, 0)         #wait for the "data ready" line to go low
    nop()      .side(0)     #set the "data taken" line low   

    wrap()

print(wait_pin_high)  # Output: List of 16-bit binary instructions
    
pin17 = Pin(17, Pin.IN, Pin.PULL_DOWN)   #define "data taken" in for first PIO
pin18 = Pin(18, Pin.IN, Pin.PULL_DOWN)   #define "data ready" in for second PIO

paral_sm = StateMachine(0, paral_prog, freq=2000, sideset_base=Pin(16), out_base=Pin(0), in_base=Pin(17))
#parallel data out pins 0-7, "data ready" out-pin 16, "data taken" in-pin 17
paral_sm.active(1)          #Activates paral_sm program in first PIO 

sm4 = StateMachine(4, wait_pin_high, sideset_base=Pin(19), in_base=Pin(18))
#"data ready" in-pin 18; "data taken" out-pin 19 
sm4.active(1)               #Activates wait_pin_high on second PIO


#routine to generate data to output
while True:
    for i in range(500):
        while paral_sm.tx_fifo() > 0:
            sleep(0.01)
        paral_sm.put(i)
        print(i , "sent = ", bin(i))
        sleep(0.5 )


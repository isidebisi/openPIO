from rp2 import *

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink_1hz():
    # fmt: off
    # Cycles: 1 + 1 + 6 + 32 * (30 + 1) = 1000
    irq(rel(0))
    set(pins, 1)
    set(x, 31)                  [5]
    label("delay_high")
    nop()                       [29]
    jmp(x_dec, "delay_high")

    # Cycles: 1 + 1 + 6 + 32 * (30 + 1) = 1000
    nop()
    set(pins, 0)
    set(x, 31)                  [5]
    label("delay_low")
    nop()                       [29]
    jmp(x_dec, "delay_low")
    # fmt: on

print(blink_1hz)  # Output: List of 16-bit binary instructions
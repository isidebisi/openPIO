'''
clockDivider_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.log import SimLog

CLOCK_PERIOD = 1 # in ns


def convert_float_to_Q16_8(value):
    """Convert a float to a 32-bit fixed point value of {16 int, 8 frac, 8 reserved}."""
    if value < 0:
        raise ValueError("Value must be non-negative")
    integer_part = int(value)
    fractional_part = int((value - integer_part) * 2**8)  # Assuming 8 bits for fractional part
    return int((integer_part << 16) | (fractional_part << 8))



class ClockDividerWrapper():
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("ClockDivider")

        self.dut.in_clkDiv.setimmediatevalue(0)
        self.dut.clk.setimmediatevalue(0)
        self.dut.reset.setimmediatevalue(1)

        self.rising_edge = RisingEdge(self.dut.clk)
        self.falling_edge = FallingEdge(self.dut.clk)

    async def start_clk(self):
        self.log.info("Starting clock")
        cocotb.start_soon(Clock(self.dut.clk, CLOCK_PERIOD, units="ns").start())

    async def reset(self):
        self.log.info("Resetting DUT")
        await self.falling_edge
        self.dut.reset.value = 1
        await self.falling_edge
        self.dut.reset.value = 0
        await self.falling_edge
        self.dut.reset.value = 1
        self.log.info("DUT reset complete")

    async def init_state(self):
        await self.start_clk()
        await self.reset()

    async def test_with_given_clkDiv(self, divider):
        # only test with rather small dividers, else the test will take too long
        self.dut.in_clkDiv.value = convert_float_to_Q16_8(divider)
        await self.reset()

        fractional_part = int(divider * 2**8) % 256

        exp_fractional_carry = 0
        skip_iteration = 0

        j=0

        for i in range(256):
            while j < int(divider):

                if j == int(divider) - 1:
                    assert self.dut.out_clkEnable.value == 1, f"Test failed at i = {i} and j= {j}: out_clkEnable should be 1"
                    exp_fractional_carry += fractional_part
                    if exp_fractional_carry >= 256:
                        exp_fractional_carry -= 256
                        j += 1
                     
                else:
                    assert self.dut.out_clkEnable.value == 0, f"Test failed at i = {i} and j= {j}: out_clkEnable should be 0"
                
                await self.falling_edge
                j += 1

            j = j - int(divider)
                

        
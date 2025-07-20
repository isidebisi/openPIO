'''
clockDivider_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
import math
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.utils import get_sim_time
from clockDivider_wrapper import *




@cocotb.test()
async def test_clock_divider(dut):
    # Initialize the clock divider wrapper
    clkDiv = ClockDividerWrapper(dut)
    await clkDiv.init_state()

    testvalues = [1, 3, 7, 11, 12, 1.5, 2.1, 7.6, 11.11, 13.13, 17.28]

    for divider in testvalues:
        cocotb.log.info(f"Testing with clkDiv = {divider}")
        await clkDiv.test_with_given_clkDiv(divider)

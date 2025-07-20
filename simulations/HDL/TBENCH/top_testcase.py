'''
ipbus_pio_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
import math
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.utils import get_sim_time
from top_wrapper import *

@cocotb.test()
async def test_top_all_addresses(dut):
    cocotb.log.info("Starting test_top")
    print("Starting test_top")
    
    tb = TopWrapper(dut)
    cocotb.log.info("Starting test")

    await tb.init_state()

    cocotb.log.info("state inited")

    for reg in REGISTERS:
        cocotb.log.info("Write Register: %s", str(reg))
        addr_formatted = [0xFF & reg.address, 0xFF & (reg.address >> 8), 0xFF & (reg.address >> 16), 0xFF & (reg.address >> 24)]
        data_formatted = [0xFF & reg.value, 0xFF & (reg.value >> 8), 0xFF & (reg.value >> 16), 0xFF & (reg.value >> 24)]
        await tb.writeToAddress(addr_formatted, data_formatted)
    
    for reg in REGISTERS:
        addr_formatted = [0xFF & reg.address, 0xFF & (reg.address >> 8), 0xFF & (reg.address >> 16), 0xFF & (reg.address >> 24)]
        data_formatted = [0xFF & reg.value, 0xFF & (reg.value >> 8), 0xFF & (reg.value >> 16), 0xFF & (reg.value >> 24)]
        await tb.readFromAddress(addr_formatted, verificationValue=data_formatted)
        cocotb.log.info("Read successfully Register: %s", str(reg))

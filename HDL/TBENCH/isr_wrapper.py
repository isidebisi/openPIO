'''
isr_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.clock import Clock
from cocotb.log import SimLog

CLOCK_PERIOD = 1  # in ns

class ISRWrapper:
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("isr_wrapper")
        # Set default signal values (use immediatevalue for simulation startup)
        self.dut.in_shiftDirection.setimmediatevalue(1)  # default right shift (new bits enter at MSB)
        self.dut.in_data.setimmediatevalue(0)
        self.dut.in_inEnable.setimmediatevalue(0)
        self.dut.in_pushNow.setimmediatevalue(0)
        self.dut.in_autoPushEnable.setimmediatevalue(0)
        self.dut.in_pushThreshold.setimmediatevalue(0)
        self.dut.in_bitReqLength.setimmediatevalue(0)
        # Internal registers
        self.dut.reg_data.setimmediatevalue(0)
        self.dut.reg_shiftCount.setimmediatevalue(0)
        self.dut.next_data.setimmediatevalue(0)
        self.dut.next_shiftCount.setimmediatevalue(0)
        
        self.rising_edge = RisingEdge(self.dut.clk)
        self.falling_edge = FallingEdge(self.dut.clk)

    async def start_clk(self):
        self.log.info("Starting clock")
        cocotb.start_soon(Clock(self.dut.clk, CLOCK_PERIOD, units="ns").start())

    async def reset(self):
        self.log.info("Resetting DUT")
        self.dut.reset.value = 0
        await self.rising_edge
        self.dut.reset.value = 1
        await self.rising_edge
        self.log.info("Reset complete")

    async def init_state(self):
        await self.start_clk()
        await self.reset()

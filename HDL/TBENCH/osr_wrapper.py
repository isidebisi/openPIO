'''
osr_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.clock import Clock
from cocotb.log import SimLog

CLOCK_PERIOD = 1

class OSRWrapper():
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("osr_wrapper")
        self.clk = 0
        self.dut.in_shiftDirection.setimmediatevalue(1)
        self.dut.in_data.setimmediatevalue(0)
        self.dut.in_outEnable.setimmediatevalue(0)
        self.dut.reset.setimmediatevalue(1)
        self.dut.in_refillNow.setimmediatevalue(0)
        self.dut.in_autoPullEnable.setimmediatevalue(0)
        self.dut.in_pullThreshold.setimmediatevalue(0)
        self.dut.in_bitReqLength.setimmediatevalue(0)
        self.dut.reg_data.setimmediatevalue(0)
        self.dut.reg_shiftCount.setimmediatevalue(3)
        self.dut.next_data.setimmediatevalue(0)
        self.dut.temp_data.setimmediatevalue(0)
        self.dut.shifted_data.setimmediatevalue(0)
        self.rising_edge = RisingEdge(self.dut.clk)
        self.falling_edge = FallingEdge(self.dut.clk)



    async def init_state(self):
        await self.start_clk()
        await self.reset()
    
    async def reset(self):
        """Reset the dut"""
        self.log.info("Resetting the DUT")
        await self.rising_edge
        await self.rising_edge
        self.dut.reset.value = 1
        await self.rising_edge
        self.dut.reset.value = 0
        await self.rising_edge
        self.dut.reset.value = 1
        await self.rising_edge
        self.log.info("Reset done")

    async def start_clk(self):
        """Start the clock"""
        self.log.info("Starting the clock")
        self.clk = Clock(self.dut.clk, CLOCK_PERIOD, "ns")
        await cocotb.start(self.clk.start())
       

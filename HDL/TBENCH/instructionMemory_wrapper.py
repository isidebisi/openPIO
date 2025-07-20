'''
instructionMemory_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.log import SimLog

CLOCK_PERIOD = 1  # in ns

class InstructionMemoryWrapper:
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("instruction_memory_wrapper")
        # Set default signal values (use immediatevalue for simulation startup)
        self.dut.clk.setimmediatevalue(0)
        self.dut.reset.setimmediatevalue(1)
        self.dut.writeData.setimmediatevalue(0)
        self.dut.writeEnable.setimmediatevalue(0)
        self.dut.writeAddress.setimmediatevalue(0)
        self.dut.sm0Address.setimmediatevalue(0)
        self.dut.sm1Address.setimmediatevalue(0)
        self.dut.sm2Address.setimmediatevalue(0)
        self.dut.sm3Address.setimmediatevalue(0)

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
        await self.falling_edge
        self.log.info("DUT initialized")
    
    async def write_memory(self, address, data):
        await self.falling_edge
        self.log.info(f"Writing data {data} to address {address}")
        self.dut.writeAddress.value = address
        self.dut.writeData.value = data & 0xFFFF
        self.dut.writeEnable.value = 1
        await self.falling_edge
        self.dut.writeEnable.value = 0
        await self.falling_edge
        assert self.dut.regMemory[address].value == data & 0xFFFF, f"Memory write failed at address {address}: expected {data & 0xFFFF}, got {self.dut.regMemory[address].value}"
    
    async def read_memory(self, address, sm=0):
        await self.falling_edge
        self.log.info(f"Reading data with sm{sm} from address {address}")
        if sm == 0:
            self.dut.sm0Address.value = address
        elif sm == 1:
            self.dut.sm1Address.value = address
        elif sm == 2:
            self.dut.sm2Address.value = address
        elif sm == 3:
            self.dut.sm3Address.value = address
        else:
            raise ValueError("Invalid SM value. Must be between 0 and 3.")
        
        await Timer(0.2, units="ns")
        data = self.dut.regMemory[address].value
        
        if sm == 0:
            assert self.dut.sm0Data.value == data, f"Memory read failed at address {address}: expected {data}, got {self.dut.sm0Data.value}"
        elif sm == 1:
            assert self.dut.sm1Data.value == data, f"Memory read failed at address {address}: expected {data}, got {self.dut.sm1Data.value}"
        elif sm == 2:
            assert self.dut.sm2Data.value == data, f"Memory read failed at address {address}: expected {data}, got {self.dut.sm2Data.value}"
        elif sm == 3:
            assert self.dut.sm3Data.value == data, f"Memory read failed at address {address}: expected {data}, got {self.dut.sm3Data.value}"
        await self.falling_edge

    
    async def read_and_write_memory(self, writeAddress, writeData, sm0Addr = 0, sm1Addr = 1, sm2Addr = 2, sm3Addr = 3):
        self.dut.writeAddress.value = writeAddress
        self.dut.writeData.value = writeData
        self.dut.writeEnable.value = 1
        self.dut.sm0Address.value = sm0Addr
        self.dut.sm1Address.value = sm1Addr
        self.dut.sm2Address.value = sm2Addr
        self.dut.sm3Address.value = sm3Addr

        await Timer(0.2, units="ns")
        assert self.dut.sm0Data.value == self.dut.regMemory[sm0Addr].value, f"Memory read failed at address {sm0Addr}: expected {self.dut.regMemory[sm0Addr].value}, got {self.dut.sm0Data.value}"
        assert self.dut.sm1Data.value == self.dut.regMemory[sm1Addr].value, f"Memory read failed at address {sm1Addr}: expected {self.dut.regMemory[sm1Addr].value}, got {self.dut.sm1Data.value}"
        assert self.dut.sm2Data.value == self.dut.regMemory[sm2Addr].value, f"Memory read failed at address {sm2Addr}: expected {self.dut.regMemory[sm2Addr].value}, got {self.dut.sm2Data.value}"
        assert self.dut.sm3Data.value == self.dut.regMemory[sm3Addr].value, f"Memory read failed at address {sm3Addr}: expected {self.dut.regMemory[sm3Addr].value}, got {self.dut.sm3Data.value}"

        await self.falling_edge
        self.dut.writeEnable.value = 0
        assert self.dut.regMemory[writeAddress].value == writeData, f"Memory write failed at address {writeAddress}: expected {writeData}, got {self.dut.regMemory[writeAddress].value}"
        assert self.dut.sm0Data.value == self.dut.regMemory[sm0Addr].value, f"Memory read failed at address {sm0Addr}: expected {self.dut.regMemory[sm0Addr].value}, got {self.dut.sm0Data.value}"
        assert self.dut.sm1Data.value == self.dut.regMemory[sm1Addr].value, f"Memory read failed at address {sm1Addr}: expected {self.dut.regMemory[sm1Addr].value}, got {self.dut.sm1Data.value}"
        assert self.dut.sm2Data.value == self.dut.regMemory[sm2Addr].value, f"Memory read failed at address {sm2Addr}: expected {self.dut.regMemory[sm2Addr].value}, got {self.dut.sm2Data.value}"
        assert self.dut.sm3Data.value == self.dut.regMemory[sm3Addr].value, f"Memory read failed at address {sm3Addr}: expected {self.dut.regMemory[sm3Addr].value}, got {self.dut.sm3Data.value}"
        
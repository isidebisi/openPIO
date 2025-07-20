'''
instructionMemory_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.utils import get_sim_time
from instructionMemory_wrapper import InstructionMemoryWrapper

@cocotb.test()
async def test_instruction_memory(dut):
    """Test instruction memory read and write operations."""
    imem = InstructionMemoryWrapper(dut)
    await imem.init_state()

    # Test writing to memory
    for address in range(0, 32):
        data = address << 10 | address << 5 | address
        await imem.write_memory(address, data)

    for address in range(0, 32):
        await imem.read_memory(address, sm=0)
        await imem.read_memory(address, sm=1)
        await imem.read_memory(address, sm=2)
        await imem.read_memory(address, sm=3)
    
    for writeAddr in range(0, 32):
        sm0Addr = (writeAddr + 1) % 32
        sm1Addr = (writeAddr + 2) % 32
        sm2Addr = (writeAddr + 3) % 32
        sm3Addr = (writeAddr + 4) % 32
        data = writeAddr << 10 | writeAddr << 5 | writeAddr
        await imem.read_and_write_memory(writeAddr,data, sm0Addr, sm1Addr, sm2Addr, sm3Addr)
        
    

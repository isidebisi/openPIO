'''
stateMachine_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
import math
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.utils import get_sim_time
from stateMachine_wrapper import *


@cocotb.test()
async def test_fillRegisters(dut):
    #fill_registers functions initializes the registers with wanted values
    #default: scratchX = "X", scratchY = "Y", ISR/OSR = TEST_VALUE
    sm = StateMachineWrapper(dut)
    await sm.fill_registers()

@cocotb.test()
async def test_JMP(dut):
    sm = StateMachineWrapper(dut)

    #test all different jump instructions
    await sm.JMPAlways()
    cocotb.log.info("JMP always test passed")
    await sm.JMPnotX()
    cocotb.log.info("JMP not X test passed")
    await sm.JMPXDec()
    cocotb.log.info("JMP X decrement test passed")
    await sm.JMPnotY()
    cocotb.log.info("JMP not Y test passed")
    await sm.JMPYDec()
    cocotb.log.info("JMP Y decrement test passed")
    await sm.JMPXnotY()
    cocotb.log.info("JMP X not Y test passed")
    await sm.JMPBranchPIN()
    cocotb.log.info("JMP Branch PIN test passed")

    cocotb.log.info("All JMP tests passed.")


@cocotb.test()
async def test_WAIT(dut):
    sm = StateMachineWrapper(dut)
    #test all different wait instructions
    await sm.WAITforGPIO()
    cocotb.log.info("WAIT for GPIO test passed")
    await sm.WAITforPIN()
    cocotb.log.info("WAIT for PIN test passed")

@cocotb.test()
async def test_IN(dut):
    sm = StateMachineWrapper(dut)

    #test all different IN instructions
    await sm.INfromPINS()
    cocotb.log.info("IN from PINS test passed")
    await sm.INfromX()
    cocotb.log.info("IN from X test passed")
    await sm.INfromY()
    cocotb.log.info("IN from Y test passed")
    await sm.INfromNULL()
    cocotb.log.info("IN from NULL test passed")
    await sm.INfromISR()
    cocotb.log.info("IN from ISR test passed")
    await sm.INfromOSR()
    cocotb.log.info("IN from OSR test passed")

    cocotb.log.info("All IN tests passed.")


@cocotb.test()
async def test_OUT(dut):
    sm = StateMachineWrapper(dut)

    #test all different OUT instructions
    await sm.OUTtoPINS()
    cocotb.log.info("OUT to PINS test passed")
    await sm.OUTtoX()
    cocotb.log.info("OUT to X test passed")
    await sm.OUTtoY()
    cocotb.log.info("OUT to Y test passed")
    await sm.OUTtoNULL()
    cocotb.log.info("OUT to NULL test passed")
    await sm.OUTtoPINDIRS()
    cocotb.log.info("OUT to PINDIRS test passed")
    await sm.OUTtoPC()
    cocotb.log.info("OUT to PC test passed")
    await sm.OUTtoISR()
    cocotb.log.info("OUT to ISR test passed")
    await sm.OUTtoEXEC()
    cocotb.log.info("OUT to EXEC test passed")

    cocotb.log.info("All OUT tests passed.")

@cocotb.test()
async def test_PUSH(dut):
    sm = StateMachineWrapper(dut)
    await sm.PUSH()
    cocotb.log.info("PUSH test passed")
    

@cocotb.test()
async def test_PULL(dut):
    sm = StateMachineWrapper(dut)
    await sm.PULL()
    cocotb.log.info("PULL test passed")


@cocotb.test()
async def test_MOV(dut):
    sm = StateMachineWrapper(dut)
    
    for src_name, src_code in sm.SRC.items():
        cocotb.log.info(f"MOV testing for source: {src_name}")
        for dest_name, dest_code in sm.DEST.items():
            #cocotb.log.info(f"MOV testing for destination: {dest_name}")
            for op_name, op_code in sm.BINARY_OP.items():
                #cocotb.log.info(f"MOV testing for operation: {op_name}")
                await sm.MOV(source=src_name, dest=dest_name, operation=op_name)

    cocotb.log.info("MOV TEST PASSED")


@cocotb.test()
async def test_some_instr_with_delay(dut):
    sm = StateMachineWrapper(dut)
    await sm.SOME_INSTR_WITH_DELAY()
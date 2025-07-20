'''
instructionDecoder_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer
from instructionDecoder_wrapper import InstructionDecoderWrapper

initial_instruction =       0b0000000000000000
instruction_interval =      0b0010000000000000
delay_sideSet_interval =    0b0000000100000000

sideSetCountBitShift = 29


@cocotb.test()
async def test_instruction_decoding(dut):
    instruction = initial_instruction
    expected_instruction = 0b000
    instructionDecoder = InstructionDecoderWrapper(dut)

    for i in range(0b1000):
        instructionDecoder.set_instruction(instruction)
        await Timer(1, units='ns')
        assert dut.out_instruction.value == expected_instruction, f"Error: instruction {expected_instruction} not decoded correctly"
        instruction = instruction + instruction_interval
        expected_instruction += 1


@cocotb.test()
async def test_side_set_count_sideSetEnableOff(dut):
    instructionDecoder = InstructionDecoderWrapper(dut)

    for i in range(6):
        #sideSet MSB as Enable off
        dut.in_smExecCtrl.value = 0
        instructionDecoder.set_sm_pin_ctrl(i<<sideSetCountBitShift)
        #print("pin_ctrl=", dut.in_smPinCtrl.value, " sideSetCount=", int(dut.sideSetCount.value), " delayCount=", int(dut.delayCount.value))
        for j in range(2**5):
            instruction = (j<<8)
            instructionDecoder.set_instruction(instruction)
            instr_sideSet_delay = (instruction >> 8) & 0b11111
            expected_delay = ((instr_sideSet_delay << i) & 0b11111) >> i
            expected_sideSet = instr_sideSet_delay >> (5-i)
            expected_sideSetEnable = 0 if i==0 else 1
            await Timer(1, units='ns')
            #print("pin_ctrl_sideSetCnt=", i, " instr_sideSet_delay=", instr_sideSet_delay, " expect_delay=", expected_delay, " actual_delay=", int(dut.out_delay.value), " expect_sideSet = ", expected_sideSet, " actual_sideSet=", int(dut.out_sideSet.value))
            assert dut.out_delay.value == expected_delay, f"Error: delay count {expected_delay} not decoded correctly"
            assert dut.out_sideSet.value == expected_sideSet, f"Error: sideSet count {expected_sideSet} not decoded correctly"
            assert dut.out_sideEnable.value == expected_sideSetEnable, f"Error: sideSetEnable {1} not decoded correctly"

@cocotb.test()
async def test_side_set_count_sideSetEnableOn(dut):
    instructionDecoder = InstructionDecoderWrapper(dut)

    for i in range(6):
        #sideSet MSB as Enable on
        dut.in_smExecCtrl.value = 1 << 30
        instructionDecoder.set_sm_pin_ctrl(i<<sideSetCountBitShift)
        for j in range(2**5):
            instruction = (j<<8)
            instructionDecoder.set_instruction(instruction)
            instr_sideSet_delay = (instruction >> 8) & 0b11111
            expected_delay = ((instr_sideSet_delay << i) & 0b11111) >> i
            expected_sideSet = instr_sideSet_delay >> (5-i) & 0b01111
            expected_sideSetEnable = (instr_sideSet_delay >> 4) if i != 0 else 0
            await Timer(1, units='ns')
            #print("pin_ctrl_sideSetCnt=", i, " instr_sideSet_delay=", instr_sideSet_delay, " expect_delay=", expected_delay, " actual_delay=", int(dut.out_delay.value), " expect_sideSet = ", expected_sideSet, " actual_sideSet=", int(dut.out_sideSet.value))
            assert dut.out_delay.value == expected_delay, f"Error: delay count {expected_delay} not decoded correctly"
            assert dut.out_sideSet.value == expected_sideSet, f"Error: sideSet count {expected_sideSet} not decoded correctly"
            assert dut.out_sideEnable.value == expected_sideSetEnable, f"Error: sideSetEnable {expected_sideSetEnable} not decoded correctly, i = {i}, j = {bin(j)}"   
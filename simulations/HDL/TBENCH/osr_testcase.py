'''
osr_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.clock import Clock
from osr_wrapper import OSRWrapper

TESTVALUE = 0b01001100011100001111000001111100



async def initial_load(osr, text=""):
    print(text)
    #load word TESTVALUE 
    await osr.falling_edge
    osr.dut.in_bitReqLength.value = 0
    osr.dut.in_data.value = TESTVALUE
    osr.dut.in_refillNow.value = 1
    await osr.rising_edge
    osr.dut.in_refillNow.value = 0
    osr.dut.in_data.value = 0
    await osr.falling_edge
    assert osr.dut.reg_data.value == TESTVALUE, f"initial_load Error: data {osr.dut.reg_data.value} not pulled into OSR correctly (should be {TESTVALUE})"
    assert osr.dut.out_data.value ==  TESTVALUE, f"initial_load Error: out_data {osr.dut.out_data.value} not output correctly (should be {TESTVALUE})"
    assert osr.dut.reg_shiftCount.value == 0, f"initial_load Error: shift count not reset correctly"
    await osr.rising_edge
    await osr.rising_edge
    assert osr.dut.reg_data.value == TESTVALUE, f"initial_load Error: data {osr.dut.reg_data.value} not hold in OSR correctly (should be {TESTVALUE})"
    assert osr.dut.reg_shiftCount.value == 0, f"initial_load Error: shift count not hold correctly"
    assert osr.dut.out_data.value ==  TESTVALUE, f"initial_load Error: out_data {osr.dut.out_data.value} not output correctly (should be {TESTVALUE})"


@cocotb.test()
async def pull_data(dut):
    print("running test: pull_data")
    osr = OSRWrapper(dut)
    await osr.init_state()

    await initial_load(osr)

@cocotb.test()
async def output_shift_with_output_disabled(dut):
    print("running test: output_shift_with_output_disabled")
    osr = OSRWrapper(dut)
    await osr.init_state()
    await initial_load(osr)
    osr.dut.in_outEnable.value = 0
    osr.dut.in_pullThreshold.value = 21

    # try different output lengths WITHOUT enabelling output (right shift)
    osr.dut.in_shiftDirection.value = 1
    for i in range(1,31):
        await osr.falling_edge
        osr.dut.in_bitReqLength.value = i
        await osr.rising_edge
        assert osr.dut.out_data.value ==  ((TESTVALUE) & (2**i-1)), f"Error: out_data {osr.dut.temp_data.value} not output correctly (should be {TESTVALUE & 2**i-1})"
        await osr.rising_edge
    
    # same but a full word
    await osr.falling_edge
    osr.dut.in_bitReqLength.value = 0
    await osr.rising_edge
    assert osr.dut.out_data.value ==  TESTVALUE, f"Error: out_data {osr.dut.temp_data.value} not output correctly"
    await osr.rising_edge

    #now with inversed shift direction (left shift)
    osr.dut.in_shiftDirection.value = 0
    for i in range(1,31):
        await osr.falling_edge
        osr.dut.in_bitReqLength.value = i
        await osr.rising_edge
        #print(f'mask_gen = {osr.dut.mask_gen.value}, temp_data = {osr.dut.temp_data.value}, out_data = {osr.dut.out_data.value}')
        assert osr.dut.out_data.value ==  (TESTVALUE >> (32-i)) , f"Error Left Shift by {i} bits: out_data {osr.dut.out_data.value} not output correctly (should be {TESTVALUE >> (32-i)})"
        assert osr.dut.reg_shiftCount.value == 0, f"Error right shift output: shift count not adjusted correctly"
        expected_refill = 1 if (int(osr.dut.reg_shiftCount.value) >= int(osr.dut.in_pullThreshold.value)) else 0
        assert int(osr.dut.out_requestRefill.value or 0) == expected_refill, f"Error: out_requestRefill not set correctly (got {osr.dut.out_empty.value}, expected {expected_empty})"
        assert osr.dut.out_requestRefill.value == 0, f"Error: out_requestRefill not set correctly"

        await osr.rising_edge

    # same but a full word
    await osr.falling_edge
    osr.dut.in_bitReqLength.value = 0
    await osr.rising_edge
    assert osr.dut.out_data.value ==  TESTVALUE, f"Error Left Shift 32 bits: out_data {osr.dut.temp_data.value} not output correctly (should be {TESTVALUE})"
    await osr.rising_edge

@cocotb.test()
async def output_shift_with_output_enabled(dut):
    print("running test: output_shift_with_output_enabled")
    osr = OSRWrapper(dut)
    await osr.init_state()
    await initial_load(osr, "output shift output enabled init")
    osr.dut.in_pullThreshold.value = 21
    osr.dut.in_autoPullEnable.value = 1

    # try different output lengths WITHOUT enabelling output (right shift)
    osr.dut.in_shiftDirection.value = 1
    for i in range(1,31):
        await initial_load(osr)#, f"initial_load nr. {i} right with output enabled")
        await osr.rising_edge
        #enable output of length i
        osr.dut.in_outEnable.value = 1
        osr.dut.in_bitReqLength.value = i
        await osr.falling_edge
        #check if output is correct
        #print(f" right shift output: out_data is {osr.dut.out_data.value} should be {TESTVALUE & 2**i-1})")
        assert osr.dut.out_data.value ==  ((TESTVALUE) & (2**i-1)), f"Error right shift output: out_data {osr.dut.out_data.value} not output correctly (should be {TESTVALUE & 2**i-1})"
        await osr.falling_edge
        expected_refill = 1 if (int(osr.dut.reg_shiftCount.value) + int(osr.dut.in_bitReqLength.value) >= int(osr.dut.in_pullThreshold.value)) else 0
        assert int(osr.dut.out_requestRefill.value or 0) == expected_refill, f"Error: out_requestRefill not set correctly (got {osr.dut.out_empty.value}, expected {expected_refill})"
        osr.dut.in_outEnable.value = 0
        #check if output adjusted correctly
        await osr.falling_edge
        #print(f"right shift output: after shift reg_data is: {osr.dut.reg_data.value}, should be {TESTVALUE >> i})")
        assert osr.dut.reg_data.value ==  ((TESTVALUE) >> i), f"Error right shift output: reg_data {osr.dut.reg_data.value} not hold correctly after output (should be {TESTVALUE >> i})"
        assert osr.dut.reg_shiftCount.value == i, f"Error right shift output: shift count not adjusted correctly"
        #assert int(osr.dut.out_empty.value) == int(osr.dut.reg_shiftCount.value + osr.dut.in_bitReqLength.value >= osr.dut.in_pullThreshold.value), f"Error: at n={i} out_empty not set correctly"
        assert osr.dut.out_requestRefill.value == (i >= 21), f"Error: out_requestRefill not set correctly"
        await osr.rising_edge
    
    # same but a full word (right shift)
    await initial_load(osr)#, f"initial_load full word right with output enabled")
    await osr.rising_edge
    osr.dut.in_outEnable.value = 1
    osr.dut.in_bitReqLength.value = 0
    await osr.falling_edge
    assert osr.dut.out_data.value ==  TESTVALUE, f"Error right shift output: out_data {osr.dut.out_data.value} not output correctly (should be {TESTVALUE})"
    await osr.falling_edge
    osr.dut.in_outEnable.value = 0
    await osr.falling_edge
    assert osr.dut.reg_data.value ==  0, f"Error right shift full word output: reg_data {osr.dut.reg_data.value} not hold correctly after output (should be 0)"
    assert osr.dut.out_empty.value == 1, f"Error: out_empty not set correctly"
    await osr.rising_edge
    
    #now with inversed shift direction (left shift)
    osr.dut.in_shiftDirection.value = 0
    for i in range(1,31):
        await initial_load(osr)
        await osr.rising_edge
        #enable output of length i 
        osr.dut.in_outEnable.value = 1
        osr.dut.in_bitReqLength.value = i
        await osr.falling_edge
        #check if output is correct

        assert osr.dut.out_data.value ==  (TESTVALUE >> (32-i)) , f"Error Left Shift by {i} bits: out_data {osr.dut.out_data.value} not output correctly (should be {bin(TESTVALUE >> (32-i))})"
        await osr.falling_edge
        osr.dut.in_outEnable.value = 0
        #check if output adjusted correctly
        await osr.falling_edge
        assert osr.dut.reg_data.value ==  (((TESTVALUE) << i) & ((1 << 32)-1)), f"Error Left Shift by {i} bits: reg_data {osr.dut.reg_data.value} not hold correctly after output (should be {bin((((TESTVALUE) << i) & ((1 << 32)-1)))})"
        await osr.rising_edge

    # same but a full word (left shift)
    await initial_load(osr)
    await osr.rising_edge
    osr.dut.in_outEnable.value = 1
    osr.dut.in_bitReqLength.value = 0
    await osr.falling_edge
    assert osr.dut.out_data.value ==  TESTVALUE, f"Error Left Shift 32 bits: out_data {osr.dut.out_data.value} not output correctly (should be {TESTVALUE})"
    await osr.falling_edge
    osr.dut.in_outEnable.value = 0
    await osr.falling_edge
    assert osr.dut.reg_data.value ==  0, f"Error Left Shift 32 bits: reg_data {osr.dut.reg_data.value} not hold correctly after output (should be 0)"
    assert osr.dut.out_empty.value == 1, f"Error: out_empty not set correctly"
    await osr.rising_edge
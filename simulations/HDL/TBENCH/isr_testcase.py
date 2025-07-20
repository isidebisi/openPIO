'''
isr_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.utils import get_sim_time
from isr_wrapper import ISRWrapper

# Define the test value exactly as specified
TESTVALUE = 0b01001100011100001111000001111100

'''
ISR Testcases
IMPORTANT: 
File doesn't test correct Autopush functionality.
Actually doesn't test ISR loading a full word. This was, however validated in the stateMachine MOV operation test
(this happens when autopush is enabled, the autopush threshold is reached and an IN/MOV operation is executed at the same time)
'''

@cocotb.test()
async def test_isr_partial_shift_right(dut):
    """Test ISR partial shift in right-shift mode.
       For each n from 1 to 31, starting with an empty ISR, shift in n bits,
       then verify reg_data equals: (TESTVALUE & ((1<<n)-1)) << (32-n).
       Finally, clear the ISR using in_pushNow.
    """
    isr = ISRWrapper(dut)
    await isr.init_state()

    for n in range(1, 32):
        # Clear the ISR by asserting in_pushNow
        await isr.falling_edge
        dut.in_pushNow.value = 1
        await isr.falling_edge
        dut.in_pushNow.value = 0
        await isr.falling_edge
        
        # Set the shift parameters for a partial shift
        dut.in_shiftDirection.value = 1  # right shift mode: new bits enter at MSB
        dut.in_bitReqLength.value = n
        dut.in_inEnable.value = 1
        # Provide TESTVALUE on in_data (the module uses only the lower n bits)
        dut.in_data.value = TESTVALUE
        await isr.falling_edge
        dut.in_inEnable.value = 0
        await Timer(0.3, units="ns")

        # For right shift: expected = (TESTVALUE & ((1<<n)-1)) << (32 - n)
        expected = ((TESTVALUE & ((1 << n) - 1)) << (32 - n)) & 0xFFFFFFFF
        #cocotb.log.info(f"Right shift n={n}: expected {bin(expected)}, got {dut.reg_data.value}")
        current_time = get_sim_time("ns")
        assert dut.reg_data.value == expected, f"Right shift failed at timestamp={current_time} ns for n={n}: expected {expected}, got {dut.reg_data.value}"
        
        # Check valid count equals n
        assert dut.reg_shiftCount.value == n, f"Right shift valid count incorrect for n={n}: got {dut.reg_shiftCount.value}, expected {n}"
        
        # Clear the ISR before the next iteration
        dut.in_pushNow.value = 1
        await isr.rising_edge
        dut.in_pushNow.value = 0
        await isr.rising_edge
        assert int(dut.reg_data.value) == 0, "ISR not cleared after pushNow (right shift)"
        assert int(dut.reg_shiftCount.value) == 0, "Valid count not cleared after pushNow (right shift)"
        
@cocotb.test()
async def test_isr_partial_shift_left(dut):
    """Test ISR partial shift in left-shift mode.
       For each n from 1 to 31, starting with an empty ISR, shift in n bits,
       then verify reg_data equals: (TESTVALUE & ((1<<n)-1))
       Finally, clear the ISR using in_pushNow.
    """
    isr = ISRWrapper(dut)
    await isr.init_state()

    for n in range(1, 32):
        # Clear the ISR first
        dut.in_pushNow.value = 1
        await isr.rising_edge
        dut.in_pushNow.value = 0
        await isr.rising_edge
        await isr.falling_edge
        
        # Set for left shift: in_shiftDirection = 0 means new bits enter at LSB
        dut.in_shiftDirection.value = 0
        dut.in_bitReqLength.value = n
        dut.in_inEnable.value = 1
        dut.in_data.value = TESTVALUE  # Only lower n bits are used.
        await isr.falling_edge
        dut.in_inEnable.value = 0
        await Timer(0.3, units="ns")
        
        # For left shift: expected = TESTVALUE & ((1 << n) - 1)
        expected = TESTVALUE & ((1 << n) - 1)
        actual = int(dut.reg_data.value)
        #cocotb.log.info(f"Left shift n={n}: expected {expected}, got {actual}")
        assert actual == expected, f"Left shift failed for n={n}: expected {expected}, got {actual}"
        
        # Check valid count equals n
        vc = int(dut.reg_shiftCount.value)
        assert vc == n, f"Left shift valid count incorrect for n={n}: got {vc}, expected {n}"
        
        # Clear the ISR before the next iteration
        dut.in_pushNow.value = 1
        await isr.rising_edge
        dut.in_pushNow.value = 0
        await isr.rising_edge
        assert int(dut.reg_data.value) == 0, "ISR not cleared after pushNow (left shift)"
        assert int(dut.reg_shiftCount.value) == 0, "Valid count not cleared after pushNow (left shift)"

@cocotb.test()
async def test_isr_partial_shift_right_while_pushing(dut):

    isr = ISRWrapper(dut)
    await isr.init_state()

    for n in range(1, 32):
        # Clear the ISR by asserting in_pushNow
        await isr.falling_edge
        dut.in_pushNow.value = 1
        await isr.falling_edge
        dut.in_pushNow.value = 0
        await isr.falling_edge
        # Push TESTVALUE in ISR completely
        dut.in_shiftDirection.value = 1  # right shift mode: new bits enter at MSB
        dut.in_bitReqLength.value = 0
        dut.in_inEnable.value = 1
        dut.in_data.value = TESTVALUE
        await isr.falling_edge

        
        # Set the shift parameters for a partial shift
        dut.in_shiftDirection.value = 1  # right shift mode: new bits enter at MSB
        dut.in_bitReqLength.value = n
        dut.in_inEnable.value = 1
        # Provide TESTVALUE on in_data (the module uses only the lower n bits)
        dut.in_data.value = TESTVALUE
        dut.in_pushNow.value = 1
        await Timer(0.3, units="ns")
        assert dut.out_data.value == TESTVALUE, f"PushNow failed for n={n}: expected {TESTVALUE}, got {dut.out_data.value}"
        
        await isr.falling_edge
        dut.in_inEnable.value = 0

        # For right shift: expected = (TESTVALUE & ((1<<n)-1)) << (32 - n)
        expected = ((TESTVALUE & ((1 << n) - 1)) << (32 - n)) & 0xFFFFFFFF
        #cocotb.log.info(f"Right shift n={n}: expected {bin(expected)}, got {dut.reg_data.value}")
        current_time = get_sim_time("ns")
        assert dut.reg_data.value == expected, f"Right shift failed at timestamp={current_time} ns for n={n}: expected {expected}, got {dut.reg_data.value}"
        
        # Check valid count equals n
        assert dut.reg_shiftCount.value == n, f"Right shift valid count incorrect for n={n}: got {dut.reg_shiftCount.value}, expected {n}"
        
        # Clear the ISR before the next iteration
        dut.in_pushNow.value = 1
        await isr.rising_edge
        dut.in_pushNow.value = 0
        await isr.rising_edge
        assert int(dut.reg_data.value) == 0, "ISR not cleared after pushNow (right shift)"
        assert int(dut.reg_shiftCount.value) == 0, "Valid count not cleared after pushNow (right shift)"
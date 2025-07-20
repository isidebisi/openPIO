'''
binaryOperations_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer
from binaryOperations_wrapper import BinaryOperationWrapper


test_data =     0b01001100011100001111000001111100
invert_data =   0b10110011100011110000111110000011
reverse_data =  0b00111110000011110000111000110010

NONE = 0b00
INVERT = 0b01
REVERSE = 0b10

@cocotb.test()
async def test_binary_operation(dut):
    binary_operation = BinaryOperationWrapper(dut)

    # Test NONE operation
    binary_operation.set_op(NONE)
    binary_operation.set_data(test_data)
    await Timer(1, units='ns')
    assert dut.out_data.value == test_data, f"Error: NONE operation failed, expected {test_data}, got {dut.out_data.value}"
    
    # Test INVERT operation
    binary_operation.set_op(INVERT)
    binary_operation.set_data(test_data)
    await Timer(1, units='ns')
    assert dut.out_data.value == invert_data, f"Error: INVERT operation failed, expected {invert_data}, got {dut.out_data.value}"

    # Test REVERSE operation
    binary_operation.set_op(REVERSE)
    binary_operation.set_data(test_data)
    await Timer(1, units='ns')
    assert dut.out_data.value == reverse_data, f"Error: REVERSE operation failed, expected {reverse_data}, got {dut.out_data.value}"
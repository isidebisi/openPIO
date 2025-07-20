'''
binaryOperations_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer
from cocotb.log import SimLog

class BinaryOperationWrapper():
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("binary_operation_wrapper")
        # Set default signal values (use immediatevalue for simulation startup)
        self.dut.in_data.setimmediatevalue(0)
        self.dut.in_op.setimmediatevalue(0)
    
    def set_data(self, data):
        self.dut.in_data.value = data
    
    def set_op(self, op):
        self.dut.in_op.value = op
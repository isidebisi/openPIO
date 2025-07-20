'''
instructionDecoder_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.log import SimLog

class InstructionDecoderWrapper():
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("instructionDecoder_wrapper")
    
    def set_instruction(self, opCode): #pep8, camelcase for class names
        self.dut.in_opCode.value = opCode
    
    def set_sm_pin_ctrl(self, sm_pin_ctrl):
        self.dut.in_smPinCtrl.value = sm_pin_ctrl
    
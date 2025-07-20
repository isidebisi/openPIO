'''
smGPIOMapper_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.log import SimLog

CLOCK_PERIOD = 1  # in ns

class SMGPIOMapperWrapper:
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("sm_gpio_mapper_wrapper")
        # Set default signal values (use immediatevalue for simulation startup)
        self.dut.in_outSetEnable.setimmediatevalue(0)
        self.dut.in_outNotSet.setimmediatevalue(0)
        self.dut.in_outSetPinsNotPindirs.setimmediatevalue(0)
        self.dut.in_sideSetEnable.setimmediatevalue(0)
        self.dut.in_outSetData.setimmediatevalue(0)
        self.dut.in_sideSetData.setimmediatevalue(0)
        self.dut.in_smPinCtrl.setimmediatevalue(0)
        self.dut.in_smExecCtrl.setimmediatevalue(0)
        self.dut.in_GPIO.setimmediatevalue(0)

        self.someTime = Timer(0.2 * CLOCK_PERIOD, units="ns")


    async def set_smPinCtrl(self, sideSetCount = 0, setCount = 0, outCount = 0,
                         inBase = 0, sideSetBase = 0, setBase = 0, outBase = 0):
        """
        Constructs the in_smPinCtrl register value from individual fields.
        """
        value = 0
        value |= (sideSetCount & 0b111) << 29
        value |= (setCount     & 0b111) << 26
        value |= (outCount     & 0b111111) << 20
        value |= (inBase       & 0b11111) << 15
        value |= (sideSetBase  & 0b11111) << 10
        value |= (setBase      & 0b11111) << 5
        value |= (outBase      & 0b11111) << 0
        self.dut.in_smPinCtrl.value = value
        #self.log.debug(f"Setting in_smPinCtrl to {value:08X}")


    async def set_smExecCtrl(self, sidePindir = 0, sideEnable = 0):
        """
        Constructs the in_smExecCtrl register value from specified fields.
        Assumes other bits are 0 or managed elsewhere.
        """
        value = 0
        value |= (sideEnable & 0b1) << 30
        value |= (sidePindir & 0b1) << 29
        self.dut.in_smExecCtrl.value = value
        #print(f"smExecCtrl value: {value:32b}")
        #self.log.debug(f"Setting in_smExecCtrl to {value:08X}")

    async def set_outSet(self, outSetEnable=0, outNotSet=0, outSetPinsNotPindirs=0, outSetData=0):
        self.dut.in_outSetEnable.value = outSetEnable & 0b1
        self.dut.in_outNotSet.value = outNotSet & 0b1
        self.dut.in_outSetPinsNotPindirs.value = outSetPinsNotPindirs & 0b1
        self.dut.in_outSetData.value = outSetData & 0XFFFFFFFF

    async def set_sideSet(self, sideSetEnable=0, sideSetData=0):
        self.dut.in_sideSetEnable.value = sideSetEnable & 0b1
        self.dut.in_sideSetData.value = sideSetData & 0X1F

    async def check_outSignals(self, exp_pinsWriteData=0, exp_pinsWriteMask=0,
                               exp_pinDirsWriteData=0, exp_pinDirsWriteMask=0, iter=0):
        await self.someTime
        assert self.dut.out_pinsWriteData.value == exp_pinsWriteData, f"Error iter={iter}: pinsWriteData {self.dut.out_pinsWriteData.value} not decoded correctly"
        assert self.dut.out_pinsWriteMask.value == exp_pinsWriteMask, f"Error iter={iter}: pinsWriteMask {self.dut.out_pinsWriteMask.value} not decoded correctly"
        assert self.dut.out_pinDirsWriteData.value == exp_pinDirsWriteData, f"Error iter={iter}: pinDirsWriteData {self.dut.out_pinDirsWriteData.value} not decoded correctly"
        assert self.dut.out_pinDirsWriteMask.value == exp_pinDirsWriteMask, f"Error iter={iter}: pinDirsWriteMask {self.dut.out_pinDirsWriteMask.value} not decoded correctly"


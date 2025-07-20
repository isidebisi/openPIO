'''
stateMachine_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.log import SimLog

CLOCK_PERIOD = 1 # in ns

TEST_VALUE = 0b01001100011100001111000001111100
N_TEST_VALUE = (~TEST_VALUE) & 0xFFFFFFFF

NOP_OPERATION = 0b1010000001000010

X = ord("X") & 0xFFFFFFFF
Y = ord("Y") & 0xFFFFFFFF
OSR = ord("OSR"[0]) & 0xFFFFFFFF
ISR = ord("ISR"[0]) & 0xFFFFFFFF

JMP =   0b000
WAIT =  0b001
IN =    0b010
OUT =   0b011
PUSH =  0b100
PULL =  0b100
MOV =   0b101
IRQ =   0b110
SET =   0b111



class StateMachineWrapper():
    def __init__(self, dut):
        self.dut = dut
        self.log = SimLog("state_machine_wrapper")

        self.dut.in_SMEnable.setimmediatevalue(1)
        self.dut.in_CLKDIVRestart.setimmediatevalue(0)
        self.dut.in_SMRestart.setimmediatevalue(0)
        self.dut.in_opCode.setimmediatevalue(0)
        self.dut.in_dataTXFifo.setimmediatevalue(TEST_VALUE)
        self.dut.in_GPIO.setimmediatevalue(0)
        self.dut.in_SM_EXECCTRL.setimmediatevalue(0)
        self.dut.in_SM_SHIFTCTRL.setimmediatevalue(0)
        self.dut.in_SM_PINCTRL.setimmediatevalue(0)
        self.dut.in_SM_CLKDIV.setimmediatevalue(1<<16)
        self.dut.in_TXFifoEmpty.setimmediatevalue(0)
        self.dut.in_RXFifoFull.setimmediatevalue(0)
        self.rising_edge = RisingEdge(self.dut.clk)
        self.falling_edge = FallingEdge(self.dut.clk)

    async def start_clk(self):
        self.log.info("Starting clock")
        cocotb.start_soon(Clock(self.dut.clk, CLOCK_PERIOD, units="ns").start())

    async def reset(self):
        self.log.info("Resetting DUT")
        self.dut.reset.value = 1
        await self.falling_edge
        self.dut.reset.value = 0
        await self.falling_edge
        self.dut.reset.value = 1
        await self.falling_edge
        self.log.info("Reset complete")
        await self.falling_edge
    
    async def init_state(self):
        await self.start_clk()
        await self.reset()

    async def init_EXECCTRL_PINCTRL(self, sideSetBits=5, sideEnableBit=0, jmpPin=0):
        self.dut.in_SM_EXECCTRL.value = sideEnableBit << 30 | (31 & 0x1F) << 12 | jmpPin << 24  # define wrap top as address 31
        self.dut.in_SM_PINCTRL.value = sideSetBits << 29

    async def test_GPIO_interaction(self, data=0, enable=0, length=0, outNotSet=0, pinsNotPindirs=0):
        assert self.dut.out_outSetEnable.value == enable, f"GPIO interaction detected: outSetEnable {self.dut.out_outSetEnable.value} != {enable}"
        assert self.dut.out_outNotSet.value == outNotSet, f"GPIO interaction detected: outNotSet {self.dut.out_outNotSet.value} != {outNotSet}"
        assert self.dut.out_outSetPinsNotPindirs.value == pinsNotPindirs, f"GPIO interaction detected: outSetPinsNotPindirs {self.dut.out_outSetPinsNotPindirs.value} != {pinsNotPindirs}"
        assert self.dut.out_outSetData.value == data, f"GPIO interaction detected: outSetData {self.dut.out_outSetData.value} != {data}"

    async def fill_registers(self, x=X, y=Y, isrValue=TEST_VALUE, osrValue=TEST_VALUE, sideSetBits=5, sideEnableBit=0, jmpPin=0 ):
        await self.init_state()
        self.dut.in_SM_SHIFTCTRL.value = 1 << 18 | 1 << 19 # right shift ISR and OSR

        await self.init_EXECCTRL_PINCTRL(sideSetBits=sideSetBits, sideEnableBit=sideEnableBit, jmpPin=jmpPin)

        await self.falling_edge
        # Set X value in tx fifo and opCode to pull
        self.dut.in_dataTXFifo.value = x
        self.dut.in_opCode.value = PULL << 13 | 1 << 7
        self.dut.in_TXFifoEmpty.value = 0
        await self.falling_edge
        assert self.dut.osrReadData.value == x, f"X value in osr is not correct: {self.dut.osrReadData.value} != {bin(x)}"
        # MOV X value from osr to X scratch
        self.dut.in_opCode.value = MOV << 13 | 1 << 5 | 0b111
        await self.falling_edge
        assert self.dut.reg_scratchX.value == x, f"X value in scratchX is not correct: {self.dut.reg_scratchX.value} != {x}"
        await self.test_GPIO_interaction()

        # Set Y value in tx fifo and opCode to pull
        self.dut.in_dataTXFifo.value = y
        self.dut.in_opCode.value = PULL << 13 | 1 << 7
        await self.falling_edge
        assert self.dut.osrReadData.value == y, f"Y value in osr is not correct: {self.dut.osrReadData.value} != {y}"
        # MOV Y value from osr to Y scratch
        self.dut.in_opCode.value = MOV << 13 | 0b10 << 5 | 0b111
        await self.falling_edge
        assert self.dut.reg_scratchY.value == y, f"Y value in scratchY is not correct: {self.dut.reg_scratchY.value} != {y}"

        # Set TEST_VALUE in tx fifo and opCode to pull into osr, then into isr
        self.dut.in_dataTXFifo.value = isrValue
        self.dut.in_opCode.value = PULL << 13 | 1 << 7
        await self.falling_edge
        assert self.dut.osrReadData.value == isrValue, f"TEST_VALUE in osr is not correct: {self.dut.osrReadData.value} != {isrValue}"
        #MOV TEST_VALUE value from osr to isr
        self.dut.in_opCode.value = MOV << 13 | 0b110 << 5 | 0b111
        await self.falling_edge
        assert self.dut.isrReadData.value == isrValue, f"TEST_VALUE value in isr is not correct: {self.dut.isrReadData.value} != {isrValue}"
        await self.test_GPIO_interaction()

        #Set TEST_VALUE in tx fifo and opCode to pull into osr
        self.dut.in_dataTXFifo.value = osrValue
        self.dut.in_opCode.value = PULL << 13 | 1 << 7
        await self.falling_edge
        assert self.dut.osrReadData.value == osrValue, f"TEST_VALUE in osr is not correct: {self.dut.osrReadData.value} != {osrValue}"

        await self.testRegisters(x=x, y=y, isrValue=isrValue, osrValue=osrValue)

    async def testRegisters(self, x=X, y=Y, isrValue=TEST_VALUE, osrValue=TEST_VALUE, EXECEnable=0, EXECValue=0):
        assert self.dut.reg_scratchX.value == x, f"testRegisters failed: scratchX {self.dut.reg_scratchX.value} != {x}"
        assert self.dut.reg_scratchY.value == y, f"testRegisters failed: scratchY {self.dut.reg_scratchY.value} != {y}"
        assert self.dut.isrReadData.value == isrValue, f"testRegisters failed: isrReadData {self.dut.isrReadData.value} != {isrValue}"
        assert self.dut.OSR.reg_data.value == osrValue, f"testRegisters failed: osrReadData {self.dut.OSR.reg_data.value} != {osrValue}" 
        if EXECEnable:
            assert self.dut.reg_EXECEnable.value == 1, f"testRegisters failed: EXECEnable {self.dut.reg_EXECEnable.value} != 1"
            assert self.dut.reg_EXECRegister.value == EXECValue & 0xFFFF, f"testRegisters failed: EXEC {self.dut.reg_EXECRegister.value & 0xFFFF} != {EXECValue}"


    async def JMPAlways(self):
        for i in range(0,32):
            # always
            await self.fill_registers()
            self.dut.in_opCode.value = JMP << 13 | i
            await self.falling_edge
            assert self.dut.out_regPC.value == i, f"JMP instruction failed: {self.dut.out_regPC.value} != {i}"
            

    async def JMPnotX(self):
        await self.fill_registers()
        # not scratchX with X != 0
        self.dut.in_opCode.value = JMP << 13 | 0b001 << 5 | 0b111
        outPC = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == outPC + 1, f"JMP instruction failed: {self.dut.out_regPC.value} != {outPC + 1}"

        #not scratchX with X == 0
        await self.fill_registers(x=0)
        self.dut.in_opCode.value = JMP << 13 | 0b001 << 5 | 0b111
        await self.falling_edge
        assert self.dut.out_regPC.value == 0b111, f"JMP instruction failed: {self.dut.out_regPC.value} != 0b111"

    async def JMPXDec(self):
        # scratchX 0 prior to decrement
        xIter = X
        await self.fill_registers()
        while(xIter > 0):
            xIter -= 1
            self.dut.in_opCode.value = JMP << 13 | 0b010 << 5 | 0b111
            await self.falling_edge
            assert self.dut.out_regPC.value == 0b111, f"JMP instruction failed at xIter = {xIter}: PC: {self.dut.out_regPC.value} != {7}"
            assert self.dut.reg_scratchX.value == xIter, f"JMP instruction failedat xIter = {xIter}: scratchX:{self.dut.reg_scratchX.value} != {xIter}"
        
        outPC = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == outPC+1, f"JMP instruction failed: PC: {self.dut.out_regPC.value} != 0b111"
        assert self.dut.reg_scratchX.value == 2**32-1, f"JMP instruction failed: scratchX: {self.dut.reg_scratchX.value} != overflow value"

    async def JMPnotY(self):
        # not scratchY with Y != 0
        self.dut.in_opCode.value = JMP << 13 | 0b011 << 5 | 0b111
        outPC = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == outPC + 1, f"JMP instruction for scratchY failed: {self.dut.out_regPC.value} != {outPC + 1}"

        # not scratchY with Y == 0
        await self.fill_registers(y=0)
        self.dut.in_opCode.value = JMP << 13 | 0b011 << 5 | 0b111
        await self.falling_edge
        assert self.dut.out_regPC.value == 0b111, f"JMP instruction for scratchY failed: {self.dut.out_regPC.value} != 0b111"

    async def JMPYDec(self):
        # scratchY non-zero prior to decrement
        yIter = Y
        await self.fill_registers()
        while yIter > 0:
            yIter -= 1
            self.dut.in_opCode.value = JMP << 13 | 0b100 << 5 | 0b111
            await self.falling_edge
            assert self.dut.out_regPC.value == 0b111, f"JMP instruction for scratchY failed at yIter = {yIter}: PC: {self.dut.out_regPC.value} != 7"
            assert self.dut.reg_scratchY.value == yIter, f"JMP instruction for scratchY failed at yIter = {yIter}: scratchY: {self.dut.reg_scratchY.value} != {yIter}"

        outPC = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == outPC+1, f"JMP instruction for scratchY failed: PC: {self.dut.out_regPC.value} != 0b111"
        assert self.dut.reg_scratchY.value == 2**32-1, f"JMP instruction for scratchY failed: scratchY: {self.dut.reg_scratchY.value} != overflow value"


    async def JMPXnotY(self):
        #X not equal to Y
        await self.fill_registers()
        self.dut.in_opCode.value = JMP << 13 | 0b101 << 5 | 0b111
        outPC = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == 0b111, f"JMP instruction for scratchY failed: {self.dut.out_regPC.value} != 0b111"
        assert self.dut.reg_scratchX.value == X, f"JMP instruction for scratchY failed: scratchX: {self.dut.reg_scratchX.value} != {X}"
        assert self.dut.reg_scratchY.value == Y, f"JMP instruction for scratchY failed: scratchY: {self.dut.reg_scratchY.value} != {Y}"

        #X equal to Y
        await self.fill_registers(x=Y)
        self.dut.in_opCode.value = JMP << 13 | 0b101 << 5 | 0b111
        outPC = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == outPC + 1, f"JMP instruction for scratchY failed: {self.dut.out_regPC.value} != {outPC + 1}"
        assert self.dut.reg_scratchX.value == Y, f"JMP instruction for scratchY failed: scratchX: {self.dut.reg_scratchX.value} != {Y}"
        assert self.dut.reg_scratchY.value == Y, f"JMP instruction for scratchY failed: scratchY: {self.dut.reg_scratchY.value} != {Y}"

    async def JMPBranchPIN(self):
        # Branch PIN = 0
        await self.fill_registers(jmpPin=21)
        self.dut.in_GPIO.value = 0
        currentPC = self.dut.out_regPC.value
        self.dut.in_opCode.value = JMP << 13 | 0b110 << 5 | currentPC+7
        await self.falling_edge
        assert self.dut.out_regPC.value == currentPC + 1, f"JMP instruction for Branch PIN = 0 failed: {self.dut.out_regPC.value} != {currentPC + 1}"

        # Branch PIN = 1
        await self.fill_registers(jmpPin=21)
        self.dut.in_GPIO.value = 1 << 21
        currentPC = self.dut.out_regPC.value
        self.dut.in_opCode.value = JMP << 13 | 0b110 << 5 | currentPC+7
        await self.falling_edge
        assert self.dut.out_regPC.value == currentPC + 7, f"JMP instruction for Branch PIN = 1 failed: {self.dut.out_regPC.value} != {currentPC + 7}"

    async def WAITforGPIO(self):  
        # WAIT for GPIO
        polPos = 7

        for polarity in range(0,2):
            for i in range(0, 32):
                for j in range(0, 2):
                    await self.fill_registers()
                    self.dut.in_opCode.value = WAIT << 13 | 0b00 << 5 | polarity << polPos | i
                    self.dut.in_GPIO.value = j << i
                    pc = self.dut.out_regPC.value
                    await self.falling_edge
                    if j == polarity:
                        assert self.dut.out_regPC.value == pc + 1, f"WAIT instruction failed: {self.dut.out_regPC.value} != {pc + 1}"
                    else:
                        assert self.dut.out_regPC.value == pc, f"WAIT instruction failed: {self.dut.out_regPC.value} != {pc}"
                    

    async def WAITforPIN(self):
        polPos = 7

        for polarity in range(0,2):
            for i in range(0, 32):
                for j in range(0, 2):
                    await self.fill_registers()
                    self.dut.in_opCode.value = WAIT << 13 | 0b01 << 5 | polarity << polPos | i
                    self.dut.in_inData.value = j << i
                    pc = self.dut.out_regPC.value
                    await self.falling_edge
                    if j == polarity:
                        assert self.dut.out_regPC.value == pc + 1, f"WAIT instruction failed: {self.dut.out_regPC.value} != {pc + 1}"
                    else:
                        assert self.dut.out_regPC.value == pc, f"WAIT instruction failed: {self.dut.out_regPC.value} != {pc}"
                    

    async def INfromPINS(self):
        await self.fill_registers()
        self.dut.in_inData.value = N_TEST_VALUE
        self.dut.in_opCode.value = IN << 13 | 0b000 << 5 | 0b0
        await self.falling_edge
        assert self.dut.isrReadData.value == N_TEST_VALUE, f"IN instruction failed: isrReadData {self.dut.isrReadData.value} != {N_TEST_VALUE}"

        # Partial loads: lower i bits from GPIO pins and upper bits from TX FIFO (TEST_VALUE)
        for i in range(1, 32):
            await self.fill_registers()
            self.dut.in_inData.value = N_TEST_VALUE
            self.dut.in_opCode.value = IN << 13 | 0b000 << 5 | i
            await self.falling_edge
            expected = ((N_TEST_VALUE & ((1 << i) - 1)) << 32-i) | (TEST_VALUE >> i)
            assert self.dut.isrReadData.value == expected, f"IN instruction failed at i = {i}: isrReadData {self.dut.isrReadData.value} != {expected}"


    async def INfromX(self):
        # IN Full register from scratchX
        await self.fill_registers()
        self.dut.in_opCode.value = IN << 13 | 0b001 << 5 | 0b0
        await self.falling_edge
        assert self.dut.reg_scratchX.value == X, f"IN instruction failed: scratchX {self.dut.reg_scratchX.value} != {X}"
        assert self.dut.isrReadData.value == X, f"IN instruction failed at i = 0: isrReadData {self.dut.isrReadData.value} != {X}"

        for i in range(1,32):
            await self.fill_registers()
            # IN from scratchX
            self.dut.in_opCode.value = IN << 13 | 0b001 << 5 | i
            await self.falling_edge
            assert self.dut.reg_scratchX.value == X, f"IN instruction failed: scratchX  {self.dut.reg_scratchX.value} != {X}"
            assert self.dut.isrReadData.value == ((X & ((1 << i)-1)) << 32-i) | (TEST_VALUE >> i), f"IN instruction failed at i= {i}: isrReadData {self.dut.isrReadData.value} != {((X & ((1 << i)-1)) << 32-i) | (TEST_VALUE >> i)}"


    async def INfromY(self):
        # IN Full register from scratchY
        await self.fill_registers()
        self.dut.in_opCode.value = IN << 13 | 0b010 << 5 | 0b0
        await self.falling_edge
        assert self.dut.reg_scratchY.value == Y, f"IN instruction failed: scratchY {self.dut.reg_scratchY.value} != {Y}"
        assert self.dut.isrReadData.value == Y, f"IN instruction failed at i = 0: isrReadData {self.dut.isrReadData.value} != {Y}"

        for i in range(1,32):
            await self.fill_registers()
            # IN from scratchY
            self.dut.in_opCode.value = IN << 13 | 0b010 << 5 | i
            await self.falling_edge
            assert self.dut.reg_scratchY.value == Y, f"IN instruction failed: scratchY {self.dut.reg_scratchY.value} != {Y}"
            expected = ((Y & ((1 << i) - 1)) << (32 - i)) | (TEST_VALUE >> i)
            assert self.dut.isrReadData.value == expected, f"IN instruction failed at i = {i}: isrReadData {self.dut.isrReadData.value} != {expected}"

    async def INfromNULL(self):
        # IN Full register from NULL (always zero)
        await self.fill_registers()
        self.dut.in_opCode.value = IN << 13 | 0b011 << 5 | 0b0
        await self.falling_edge
        # When i = 0, the full 32-bit load from NULL should result in 0.
        assert self.dut.isrReadData.value == 0, f"IN from NULL failed at i = 0: isrReadData {self.dut.isrReadData.value} != 0"
    
        # For partial loads (i > 0), the low i bits are taken from 0 and the rest comes from the TX FIFO (TEST_VALUE)
        for i in range(1, 32):
            await self.fill_registers()
            self.dut.in_opCode.value = IN << 13 | 0b011 << 5 | i
            await self.falling_edge
            expected = (TEST_VALUE >> i)  # since (0 & mask) is 0
            assert self.dut.isrReadData.value == expected, f"IN from NULL failed at i = {i}: isrReadData {self.dut.isrReadData.value} != {expected}"

    async def INfromISR(self):
        # IN Full register from ISR (TEST_VALUE source)
        await self.fill_registers()
        self.dut.in_opCode.value = IN << 13 | 0b110 << 5 | 0b0
        await self.falling_edge
        assert self.dut.isrReadData.value == TEST_VALUE, f"IN from ISR failed at i = 0: isrReadData {self.dut.isrReadData.value} != {TEST_VALUE}"
    
        # Partial loads: lower i bits from ISR and upper bits from TX FIFO (TEST_VALUE)
        for i in range(1, 32):
            await self.fill_registers()
            self.dut.in_opCode.value = IN << 13 | 0b110 << 5 | i
            await self.falling_edge
            expected = ((TEST_VALUE & ((1 << i) - 1)) << (32 - i)) | (TEST_VALUE >> i)
            assert self.dut.isrReadData.value == expected, f"IN from ISR failed at i = {i}: isrReadData {self.dut.isrReadData.value} != {expected}"

    async def INfromOSR(self):
        # IN Full register from OSR (TEST_VALUE source)
        await self.fill_registers()
        self.dut.in_opCode.value = IN << 13 | 0b111 << 5 | 0b0
        await self.falling_edge
        assert self.dut.OSR.reg_data.value == 0, f"IN from OSR failed at i = 0: osrReadData {self.dut.osrReadData.value} != {0}"
        assert self.dut.isrReadData.value == TEST_VALUE, f"IN from OSR failed at i = 0: isrReadData {self.dut.isrReadData.value} != {TEST_VALUE}"
        # Partial loads: lower i bits from OSR and upper bits from TX FIFO (TEST_VALUE)
        for i in range(1, 32):
            await self.fill_registers()
            self.dut.in_opCode.value = IN << 13 | 0b111 << 5 | i
            await self.falling_edge
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"IN from OSR failed at i = {i}: osrReadData {self.dut.osrReadData.value} != {TEST_VALUE >> i}"

            expected = ((TEST_VALUE & ((1 << i) - 1)) << (32 - i)) | (TEST_VALUE >> i)
            assert self.dut.isrReadData.value == expected, f"IN from OSR failed at i = {i}: isrReadData {self.dut.isrReadData.value} != {expected}"

    async def OUTtoPINS(self):
        # OUT Full register to GPIO pins
        await self.fill_registers()
        await self.test_GPIO_interaction()

        self.dut.in_opCode.value = OUT << 13 | 0b000 << 5 | 0b0

        await Timer(0.2 * CLOCK_PERIOD, units="ns")
        assert self.dut.out_outSetData == TEST_VALUE, f"OUT instruction failed: outSetData {self.dut.out_outSetData} != {TEST_VALUE}"
        assert self.dut.out_outSetEnable.value == 0b1, f"OUT instruction failed: outSetEnable {self.dut.out_outSetEnable.value} != 0b1"
        assert self.dut.out_outNotSet.value == 1, f"OUT instruction failed: outNotSet {self.dut.out_outNotSet.value} != 1"
        assert self.dut.out_outSetPinsNotPindirs.value == 1, f"OUT instruction failed: outSetPinsNotPindirs {self.dut.out_outSetPinsNotPindirs.value} != 1"
        await self.falling_edge
        assert self.dut.reg_outSetData.value == TEST_VALUE, f"OUT instruction failed: reg_outSetData {self.dut.reg_outSetData.value} != {TEST_VALUE}"
        
        # Partial loads: lower i bits from OSR (TEST_VALUE) into GPIO pins
        for i in range(1, 32):
            #print(f"Iteration {i} for OUT to GPIO pins")
            await self.fill_registers()
            await self.test_GPIO_interaction()
            self.dut.in_opCode.value = OUT << 13 | 0b000 << 5 | i
            await Timer(0.2 * CLOCK_PERIOD, units="ns")
            expected_data = TEST_VALUE & ((1 << i) - 1)
            await self.test_GPIO_interaction(data=expected_data, enable=1, length=i, outNotSet=1, pinsNotPindirs=1)

            await self.falling_edge
            assert self.dut.reg_outSetData.value == expected_data, f"OUT instruction failed at i = {i}: reg_outSetData {self.dut.reg_outSetData.value} != {expected_data}"


    async def OUTtoX(self):
        # OUT Full register to scratchX
        await self.fill_registers()
        self.dut.in_opCode.value = OUT << 13 | 0b001 << 5 | 0b0
        await self.falling_edge
        assert self.dut.reg_scratchX.value == TEST_VALUE, f"OUT instruction failed: scratchX {self.dut.reg_scratchX.value} != {TEST_VALUE}"
        assert self.dut.OSR.reg_data.value == 0, f"OUT instruction failed at i = 0: osrReadData {self.dut.OSR.reg_data.value} != {0}"
        # Partial loads: lower i bits from OSR (TEST_VALUE) into scratchX 
        for i in range(1,32):
            await self.fill_registers()
            self.dut.in_opCode.value = OUT << 13 | 0b001 << 5 | i
            await self.falling_edge
            expected = TEST_VALUE & ((1 << i) - 1)
            assert self.dut.reg_scratchX.value == expected, f"OUT instruction failed at i = {i}: scratchX {self.dut.reg_scratchX.value} != {expected}"
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"OUT instruction failed at i = {i}: osrReadData {self.dut.OSR.reg_data.value} != {TEST_VALUE >> i}"

    async def OUTtoY(self):
        # OUT Full register to scratchY
        await self.fill_registers()
        self.dut.in_opCode.value = OUT << 13 | 0b010 << 5 | 0b0
        await self.falling_edge
        assert self.dut.reg_scratchY.value == TEST_VALUE, f"OUT instruction failed: scratchY {self.dut.reg_scratchY.value} != {TEST_VALUE}"
        assert self.dut.OSR.reg_data.value == 0, f"OUT instruction failed at i = 0: osrReadData {self.dut.OSR.reg_data.value} != {0}"
        # Partial loads: lower i bits from OSR (TEST_VALUE) into scratchY
        for i in range(1,32):
            await self.fill_registers()
            self.dut.in_opCode.value = OUT << 13 | 0b010 << 5 | i
            await self.falling_edge
            expected = TEST_VALUE & ((1 << i) - 1)
            assert self.dut.reg_scratchY.value == expected, f"OUT instruction failed at i = {i}: scratchY {self.dut.reg_scratchY.value} != {expected}"
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"OUT instruction failed at i = {i}: osrReadData {self.dut.OSR.reg_data.value} != {TEST_VALUE >> i}"

    async def OUTtoNULL(self):
        # Partial loads: lower i bits from OSR (TEST_VALUE) into NULL
        for i in range(1,32):
            await self.fill_registers()
            self.dut.in_opCode.value = OUT << 13 | 0b011 << 5 | i
            await self.falling_edge
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"OUT instruction failed at i = {i}: osrReadData {self.dut.OSR.reg_data.value} != {TEST_VALUE >> i}"
        # OUT Full register to NULL (always zero)
        await self.fill_registers()
        self.dut.in_opCode.value = OUT << 13 | 0b011 << 5 | 0b0
        await self.falling_edge
        assert self.dut.OSR.reg_data.value == 0, f"OUT instruction failed: osrReadData {self.dut.OSR.reg_data.value} != {0}"


    async def OUTtoPINDIRS(self):
        # OUT Full register to GPIO pindirs
        await self.fill_registers()
        await self.test_GPIO_interaction()
        self.dut.in_opCode.value = OUT << 13 | 0b100 << 5 | 0b0
        await Timer(0.2 * CLOCK_PERIOD, units="ns")
        await self.test_GPIO_interaction(data=TEST_VALUE, enable=1, length=0, outNotSet=1, pinsNotPindirs=0)

        await self.falling_edge
        assert self.dut.reg_outSetData.value == TEST_VALUE, f"OUT instruction failed: reg_outSetData {self.dut.reg_outSetData.value} != {TEST_VALUE}"

        # OUT to GPIO pindirs with partial loads
        for i in range(1, 32):
            await self.fill_registers()
            await self.test_GPIO_interaction()
            self.dut.in_opCode.value = OUT << 13 | 0b100 << 5 | i
            await Timer(0.2 * CLOCK_PERIOD, units="ns")
            expected_data = TEST_VALUE & ((1 << i) - 1)
            await self.test_GPIO_interaction(data=expected_data, enable=1, length=i, outNotSet=1, pinsNotPindirs=0)

            await self.falling_edge
            assert self.dut.reg_outSetData.value == expected_data, f"OUT instruction failed at i = {i}: reg_outSetData {self.dut.reg_outSetData.value} != {expected_data}" 

    async def OUTtoPC(self):
        # OUT Full register to PC, note that PC register is 5 bits
        await self.fill_registers()
        self.dut.in_opCode.value = OUT << 13 | 0b101 << 5 | 0b0
        await self.falling_edge
        assert self.dut.out_regPC.value == TEST_VALUE & 0b11111, f"OUT instruction failed at i=0: PC {self.dut.out_regPC.value} != {TEST_VALUE & 0b11111}"
        assert self.dut.OSR.reg_data.value == 0, f"OUT instruction failed at i = 0: osrReadData {self.dut.OSR.reg_data.value} != {0}"
        # Partial loads: lower i bits from OSR (TEST_VALUE) into PC
        for i in range(1,32):
            await self.fill_registers()
            self.dut.in_opCode.value = OUT << 13 | 0b101 << 5 | i
            await self.falling_edge
            if i < 6:
                expected = TEST_VALUE & ((1 << i) - 1)
            else:
                expected = TEST_VALUE & 0b11111
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"OUT instruction failed at i = {i}: osrReadData {self.dut.OSR.reg_data.value} != {TEST_VALUE >> i}"
            assert self.dut.out_regPC.value == expected, f"OUT instruction failed at i = {i}: PC {self.dut.out_regPC.value} != {expected}"

    async def OUTtoISR(self):
        # OUT Full register to ISR
        await self.fill_registers()
        self.dut.in_opCode.value = OUT << 13 | 0b110 << 5 | 0b0
        await self.falling_edge
        assert self.dut.isrReadData.value == TEST_VALUE, f"OUT instruction failed: ISR {self.dut.isrReadData.value} != {TEST_VALUE}"
        assert self.dut.OSR.reg_data.value == 0, f"OUT instruction failed at i = 0: osrReadData {self.dut.OSR.reg_data.value} != {0}"
        # Partial loads: lower i bits from OSR (TEST_VALUE) into ISR
        for i in range(1,32):
            await self.fill_registers()
            self.dut.in_opCode.value = OUT << 13 | 0b110 << 5 | i
            await self.falling_edge
            expected = ((TEST_VALUE << (32-i)) | (TEST_VALUE >> i)) & 0xFFFFFFFF
            assert self.dut.isrReadData.value == expected, f"OUT instruction failed at i = {i}: ISR {self.dut.isrReadData.value} != {bin(expected)}"
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"OUT instruction failed at i = {i}: osrReadData {self.dut.OSR.reg_data.value} != {TEST_VALUE >> i}"

    async def OUTtoEXEC(self):
        # OUT Full register to EXEC, Note that EXEC register is 16 bits
        await self.fill_registers()
        self.dut.in_opCode.value = OUT << 13 | 0b111 << 5 | 0b0
        pc = self.dut.out_regPC.value
        await self.falling_edge
        self.dut.in_opCode.value = 0
        assert self.dut.reg_EXECRegister.value == TEST_VALUE & 0xFFFF, f"OUT instruction failed: EXEC {self.dut.reg_EXECRegister.value} != {TEST_VALUE & 0xFFFF}"
        assert self.dut.OSR.reg_data.value == 0, f"OUT instruction failed at i = 0: osrReadData {self.dut.OSR.reg_data.value} != {0}"
        assert self.dut.out_regPC.value == pc+1, f"OUT instruction failed: PC {self.dut.out_regPC.value} != {pc}"
        await Timer(0.2 * CLOCK_PERIOD, units="ns")
        assert self.dut.instruction.value == (TEST_VALUE >> 12)& 0b111, f"OUT instruction failed: instruction {self.dut.instruction.value} != {(TEST_VALUE >> 12)& 0b111}"
        await self.falling_edge #wait because EXEC instruction is executed
        assert self.dut.out_regPC.value == pc+1, f"OUT instruction failed: PC {self.dut.out_regPC.value} != {pc}"

        # Partial loads: lower i bits from OSR (TEST_VALUE) into EXEC
        for i in range(1,32):
            await self.fill_registers()
            self.dut.in_opCode.value = OUT << 13 | 0b111 << 5 | i
            await self.falling_edge
            self.dut.in_opCode.value = 0
            if i < 17:
                expected = TEST_VALUE & ((1 << i) - 1)
            else:
                expected = TEST_VALUE & 0xFFFF
            assert self.dut.OSR.reg_data.value == TEST_VALUE >> i, f"OUT instruction failed at i = {i}: osrReadData {self.dut.OSR.reg_data.value} != {TEST_VALUE >> i}"
            assert self.dut.reg_EXECRegister.value == expected, f"OUT instruction failed at i = {i}: EXEC {self.dut.reg_EXECRegister.value} != {expected}"
            
            await self.falling_edge #wait because EXEC instruction is executed

    async def PUSH(self):
        for ifFull in [0, 1]:
            for block in [0, 1]:
                for rxFull in [0, 1]:
                    await self.fill_registers()  # ISR is filled with TEST_VALUE
                    pc = self.dut.out_regPC.value
                    self.dut.in_RXFifoFull.setimmediatevalue(rxFull)
                    # Construct the opcode using the two control bits:
                    opCode = PUSH << 13 | (ifFull << 6) | (block << 5)
                    self.dut.in_opCode.value = opCode

                    await Timer(0.2 * CLOCK_PERIOD, units="ns")  # advance time a bit to evaluate asserts

                    push_occurs = (block == 1 and rxFull == 0) or (block == 0 and (ifFull == 0 or (ifFull == 1 and self.dut.isrFull.value == 1)))
                    if push_occurs:
                        expected_rxfifo = TEST_VALUE
                        expected_isr    = 0
                        expected_pc     = pc + 1
                        expected_valid  = 1 if rxFull == 0 else 0
                    else:
                        expected_rxfifo = 0
                        expected_isr    = TEST_VALUE
                        expected_pc     = pc
                        expected_valid  = 0

                    assert self.dut.out_dataRXFifo.value == expected_rxfifo, \
                        f"PUSH FAIL: ifFull={ifFull}, block={block}, rxFull={rxFull}: out_dataRXFifo {self.dut.out_dataRXFifo.value} != {expected_rxfifo}"
                    assert self.dut.out_RXFifoDataValid.value == expected_valid, \
                        f"PUSH FAIL: ifFull={ifFull}, block={block}, rxFull={rxFull}: out_RXFifoDataValid {self.dut.out_RXFifoDataValid.value} != {expected_valid}"
                    
                    await self.falling_edge    # next clock cycle
                    
                    assert self.dut.isrReadData.value == expected_isr, \
                        f"PUSH FAIL: ifFull={ifFull}, block={block}, rxFull={rxFull}: isrReadData {self.dut.isrReadData.value} != {expected_isr}"
                    assert self.dut.out_regPC.value == expected_pc, \
                        f"PUSH FAIL: ifFull={ifFull}, block={block}, rxFull={rxFull}: out_regPC {self.dut.out_regPC.value} != {expected_pc}"

    async def PULL(self):
        for osr_force_empty in [False, True]:                
            for ifEmpty in [0, 1]:
                for block in [0, 1]:
                    for txEmpty in [0, 1]:

                        # Before each test iteration, restore the desired OSR state.
                        if osr_force_empty:
                            # With Out operation first, the OSR will be empty.
                            await self.OUTtoNULL()
                            osr_state = "empty"
                        else:
                            await self.fill_registers()
                            osr_state = "full"
                        local_pc = self.dut.out_regPC.value
                        
                        # Set TX FIFO state and data.
                        self.dut.in_TXFifoEmpty.setimmediatevalue(txEmpty)
                        self.dut.in_dataTXFifo.value = TEST_VALUE-1
                        
                        # Construct the PULL opcode:
                        # Bit 7 is fixed at 1 for PULL; bit 6 = ifEmpty; bit 5 = block.
                        opCode = (PULL << 13) | 1<<7 | (ifEmpty << 6) | (block << 5)
                        self.dut.in_opCode.value = opCode
                                                
                        # Determine whether a pull should occur.
                        #  • If ifEmpty==1, pull happens only when OSR is empty.
                        #  • Regardless, if TX FIFO is empty:
                        #       – When block==1, the pull stalls.
                        #       – When block==0, the pull executes nonblocking and OSR is taken from scratchX.
                        osr_is_empty = self.dut.osrEmpty.value
                        tx_ok = (txEmpty == 0) or (txEmpty == 1 and (block == 0))
                        if (ifEmpty == 1 and not osr_is_empty):
                            pull_occurs = False
                        else:
                            pull_occurs = tx_ok

                        if pull_occurs:
                            # Determine expected OSR:
                            if txEmpty == 1 and block == 0:
                                expected_osr = X  # fallback: OSR gets scratchX.
                            else:
                                expected_osr = TEST_VALUE-1
                            expected_pc = local_pc + 1
                        else:
                            # No pull occurs, OSR remains unchanged.
                            expected_osr = 0 if osr_is_empty else TEST_VALUE

                            if block == 1 and txEmpty == 1:
                                expected_pc = local_pc
                            else:
                                expected_pc = local_pc+1
                            
                        await self.falling_edge

                        assert self.dut.reg_scratchX == X, \
                            f"PULL FAIL (OSR {osr_state}): ifEmpty={ifEmpty}, block={block}, txEmpty={txEmpty}: scratchX {self.dut.reg_scratchX.value} != {X}"
                        
                        assert self.dut.osrReadData.value == expected_osr, \
                            f"PULL FAIL (OSR {osr_state}): ifEmpty={ifEmpty}, block={block}, txEmpty={txEmpty}: osrReadData {self.dut.osrReadData.value} != {bin(expected_osr)}"
                        assert self.dut.out_regPC.value == expected_pc, \
                            f"PULL FAIL (OSR {osr_state}): ifEmpty={ifEmpty}, block={block}, txEmpty={txEmpty}: PC {self.dut.out_regPC.value} != {expected_pc}"


    # Destination codes for the MOV instruction.
    SRC = {
        "PINS":      0b000,
        "X":         0b001,
        "Y":         0b010,
        "NULL":      0b011,
        #"STATUS":    0b101,
        "ISR":       0b110,
        "OSR":       0b111 
    }

    DEST = {
        "PINS":      0b000,
        "X":         0b001,
        "Y":         0b010,
        "EXEC":      0b100,
        "PC":        0b101,
        "ISR":       0b110,
        "OSR":       0b111 
    }

    # Operation codes for binary operations to be applied during MOV.
    BINARY_OP = {
        "NONE":      0b00,
        "INVERT":    0b01,
        "BIT_REV":   0b10
    }

    def bit_reverse(self, i, n):
        return int(format(i, '0%db' % n)[::-1], 2)

    async def MOV(self, source="Y", dest="Y",operation="NONE"):
        
        await self.fill_registers(x=X, y=Y, isrValue=ISR, osrValue=OSR)
        self.dut.in_inData.value = TEST_VALUE

        oldPC = self.dut.out_regPC.value
        self.dut.in_opCode.value = MOV << 13 | self.DEST[dest] << 5 | self.BINARY_OP[operation] << 3 | self.SRC[source]

        await self.falling_edge
        self.dut.in_opCode.value = 0

        isrValue=ISR
        osrValue=OSR

        # calculate Values after operation
        destinationValue = 0
        match source:
            case "PINS":
                destinationValue = TEST_VALUE
            case "X":
                destinationValue = X
            case "Y":
                destinationValue = Y
            case "ISR":
                #if ISR is source, it will get wiped
                destinationValue = ISR
                isrValue = 0
            case "OSR":
                #if OSR is source, it will get wiped
                destinationValue = OSR
                osrValue = 0
            case "NULL":
                destinationValue = 0
            case _:
                raise ValueError(f"Invalid source: {source}. Valid options are: {', '.join(self.SRC.keys())}")
            
        match operation:
            case "NONE":
                pass
            case "INVERT":
                destinationValue = (~destinationValue) & 0xFFFFFFFF
            case "BIT_REV":
                destinationValue = self.bit_reverse(destinationValue, 32)
            case _:
                raise ValueError(f"Invalid operation: {operation}. Valid options are: {', '.join(self.BINARY_OP.keys())}")

        # check destination value
        match dest:
            case "PINS":
                assert self.dut.out_regPC.value == oldPC + 1, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {oldPC + 1}"
                await self.testRegisters(x=X, y=Y, isrValue=isrValue, osrValue=osrValue)
                assert self.dut.reg_outSetData.value == destinationValue, f"MOV instruction failed: outSetData {self.dut.reg_outSetData.value} != {destinationValue}"
            case "X":
                assert self.dut.out_regPC.value == oldPC + 1, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {oldPC + 1}"
                await self.testRegisters(x=destinationValue, y=Y, isrValue=isrValue, osrValue=osrValue)
            case "Y":
                assert self.dut.out_regPC.value == oldPC + 1, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {oldPC + 1}"
                await self.testRegisters(x=X, y=destinationValue, isrValue=isrValue, osrValue=osrValue)
            case "EXEC":
                assert self.dut.out_regPC.value == oldPC + 1, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {oldPC + 1}"
                await self.testRegisters(x=X, y=Y, isrValue=isrValue, osrValue=osrValue, EXECEnable=1, EXECValue=destinationValue)
                #cocotb.log.info(f"EXEC opCode: {self.dut.opCode.value} == {self.dut.reg_EXECRegister.value}")
                await self.falling_edge #wait because EXEC instruction is executed
            case "PC":
                assert self.dut.out_regPC.value == destinationValue & 0b11111, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {destinationValue & 0b11111}"
                await self.testRegisters(x=X, y=Y, isrValue=isrValue, osrValue=osrValue)
            case "ISR":
                assert self.dut.out_regPC.value == oldPC + 1, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {oldPC + 1}"
                await self.testRegisters(x=X, y=Y, isrValue=destinationValue, osrValue=osrValue)
            case "OSR":
                assert self.dut.out_regPC.value == oldPC + 1, f"MOV instruction failed: PC {self.dut.out_regPC.value} != {oldPC + 1}"
                await self.testRegisters(x=X, y=Y, isrValue=isrValue, osrValue=destinationValue)
            case _:
                raise ValueError(f"Invalid destination: {dest}. Valid options are: {', '.join(self.DEST.keys())}, EXCEPT FOR PINS: NOT YET IMPLEMENTED")
            
    async def SOME_INSTR_WITH_DELAY(self):
        await self.fill_registers()

        # no delay
        self.dut.in_opCode.value = IN << 13 
        pc = self.dut.out_regPC.value
        await self.falling_edge
        assert self.dut.out_regPC.value == pc + 1, f"TEST instruction failed: {self.dut.out_regPC.value} != {pc + 1}"

        # delay
        for i in range(0,6):
            for j in range(0,32):
                await self.fill_registers(sideSetBits=i)
                self.dut.in_opCode.value = IN << 13 | j << 8
                pc = self.dut.out_regPC.value
                await self.falling_edge
                self.dut.in_opCode.value = 0

                waitTime = j & ((1 <<(5-i))-1)
                waitCounter = waitTime
                assert self.dut.out_regPC.value == pc+1 if waitTime == 0 else pc, f"TEST instruction failed: {self.dut.out_regPC.value} != {pc + 1 if waitTime == 0 else pc}"
                assert self.dut.reg_delayCounter.value == waitTime, f"TEST at i={i}, j={j} instruction failed: {self.dut.reg_delayCounter.value} != {waitTime}"
                for k in range(0,waitTime):
                    waitCounter -= 1
                    await self.falling_edge
                    assert self.dut.reg_delayCounter.value == waitCounter, f"TEST instruction failed: {self.dut.reg_delayCounter.value} != {waitCounter}"
                    assert self.dut.out_regPC.value == pc+1 if waitCounter == 0 else pc, f"TEST instruction failed: {self.dut.out_regPC.value} != {pc + 1 if waitCounter == 0 else pc}"
                    
            
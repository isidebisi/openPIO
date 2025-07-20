"""Simple test for shift registers"""

# pylint: disable=protected-access,no-value-for-parameter, invalid-name
# import random
import cocotb
import mash_1_bit_tb
from cocotb.clock import Clock
from cocotb.triggers import Timer, FallingEdge


@cocotb.test()
async def mash_1_bit_AC(dut):
    """Simple test for shift registers"""

    dut._log.info("Start")
    tb = mash_1_bit_tb.ModulatorSigmaDeltaTestBench(dut)
    dut.rst.value = int(0)
    dut.data_i.value = int(0)
    clk = Clock(dut.clk, 25, "ns")

    await cocotb.start(clk.start())
    dut.rst.value = int(1)

    await Timer(1, "us")
    dut.rst.value = int(0)

    await FallingEdge(dut.clk)
    await tb.sinus_test()
    # dut.data_i.value = int(30000)
    # await Timer(100, "us")
    # dut.data_i.value = int(5432)
    # await Timer(100, "us")
    dut._log.info("Done")

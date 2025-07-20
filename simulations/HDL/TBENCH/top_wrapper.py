'''
ipbus_pio_wrapper.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
from cocotb.log import SimLog
from utils import *
from rmii_ipbus import RmiiPhy
from ipbus_pkt import *

TEST_VALUE = 0b01001100011100001111000001111100

ADDR = 0x058

INSTR_MEM_ADDR = []

class Register:
    """A hardware register with name, address, bit length, and value."""
    def __init__(self, name, address, length=32, value=0):
        self.name = name
        self.address = address
        self.length = length
        self.value = value
    
    def __str__(self):
        """String representation of the register."""
        return f"{self.name} (0x{self.address:03x}): {self.length} bits = 0x{self.value:x}"
    
    def get_bytes(self):
        """Get the value as a list of bytes (little-endian)."""
        return [(self.value >> (i*8)) & 0xFF for i in range(4)]

# Define registers as constants
REGISTERS = [
    # Instruction memory
    Register("INSTR_MEM0", 0x048, length=16, value=0x0048),
    Register("INSTR_MEM1", 0x04C, length=16, value=0x004C),
    Register("INSTR_MEM2", 0x050, length=16, value=0x0050),
    Register("INSTR_MEM3", 0x054, length=16, value=0x0054),
    Register("INSTR_MEM4", 0x058, length=16, value=0x0058),
    Register("INSTR_MEM5", 0x05C, length=16, value=0x005C),
    Register("INSTR_MEM6", 0x060, length=16, value=0x0060),
    Register("INSTR_MEM7", 0x064, length=16, value=0x0064),
    Register("INSTR_MEM8", 0x068, length=16, value=0x0068),
    Register("INSTR_MEM9", 0x06C, length=16, value=0x006C),
    Register("INSTR_MEM10", 0x070, length=16, value=0x0070),
    Register("INSTR_MEM11", 0x074, length=16, value=0x0074),
    Register("INSTR_MEM12", 0x078, length=16, value=0x0078),
    Register("INSTR_MEM13", 0x07C, length=16, value=0x007C),
    Register("INSTR_MEM14", 0x080, length=16, value=0x0080),
    Register("INSTR_MEM15", 0x084, length=16, value=0x0084),
    Register("INSTR_MEM16", 0x088, length=16, value=0x0088),
    Register("INSTR_MEM17", 0x08C, length=16, value=0x008C),
    Register("INSTR_MEM18", 0x090, length=16, value=0x0090),
    Register("INSTR_MEM19", 0x094, length=16, value=0x0094),
    Register("INSTR_MEM20", 0x098, length=16, value=0x0098),
    Register("INSTR_MEM21", 0x09C, length=16, value=0x009C),
    Register("INSTR_MEM22", 0x0A0, length=16, value=0x00A0),
    Register("INSTR_MEM23", 0x0A4, length=16, value=0x00A4),
    Register("INSTR_MEM24", 0x0A8, length=16, value=0x00A8),
    Register("INSTR_MEM25", 0x0AC, length=16, value=0x00AC),
    Register("INSTR_MEM26", 0x0B0, length=16, value=0x00B0),
    Register("INSTR_MEM27", 0x0B4, length=16, value=0x00B4),
    Register("INSTR_MEM28", 0x0B8, length=16, value=0x00B8),
    Register("INSTR_MEM29", 0x0BC, length=16, value=0x00BC),
    Register("INSTR_MEM30", 0x0C0, length=16, value=0x00C0),
    Register("INSTR_MEM31", 0x0C4, length=16, value=0x00C4),

    Register("CTRL",         0x000, length=32, value=(0x01 << 16) | 0x01),

    Register("SM0_CLKDIV",   0x0c8, length=32, value=(0x0c8 << 16) | 0x0c8),
    Register("SM0_EXECCTRL", 0x0cc, length=32, value=(0x0cc << 16) | 0x0cc),
    Register("SM0_SHIFTCTRL",0x0d0, length=32, value=(0x0d0 << 16) | 0x0d0),
    Register("SM0_PINCTRL",  0x0dc, length=32, value=(0x0dc << 16) | 0x0dc),
    
    Register("SM1_CLKDIV",   0x0e0, length=32, value=(0x0e0 << 16) | 0x0e0),
    Register("SM1_EXECCTRL", 0x0e4, length=32, value=(0x0e4 << 16) | 0x0e4),
    Register("SM1_SHIFTCTRL",0x0e8, length=32, value=(0x0e8 << 16) | 0x0e8),
    Register("SM1_PINCTRL",  0x0f4, length=32, value=(0x0f4 << 16) | 0x0f4),
    
    Register("SM2_CLKDIV",   0x0f8, length=32, value=(0x0f8 << 16) | 0x0f8),
    Register("SM2_EXECCTRL", 0x0fc, length=32, value=(0x0fc << 16) | 0x0fc),
    Register("SM2_SHIFTCTRL",0x100, length=32, value=(0x100 << 16) | 0x100),
    Register("SM2_PINCTRL",  0x10c, length=32, value=(0x10c << 16) | 0x10c),
    
    Register("SM3_CLKDIV",   0x110, length=32, value=(0x110 << 16) | 0x110),
    Register("SM3_EXECCTRL", 0x114, length=32, value=(0x114 << 16) | 0x114),
    Register("SM3_SHIFTCTRL",0x118, length=32, value=(0x118 << 16) | 0x118),
    Register("SM3_PINCTRL",  0x124, length=32, value=(0x124 << 16) | 0x124),
]

# Create a dictionary for quick lookup by name or address
REGISTER_BY_NAME = {reg.name: reg for reg in REGISTERS}
REGISTER_BY_ADDR = {reg.address: reg for reg in REGISTERS}


class TopWrapper():
    def __init__(self, dut, speed=100e6):
        self.dut = dut
        self.log = SimLog("Top_wrapper")

        self.dut.clk_32_i.setimmediatevalue(0)
        self.dut.clk_125_i.setimmediatevalue(0)
        self.dut.clk_200_i.setimmediatevalue(0)
        self.dut.rst_i.setimmediatevalue(1)

        self.rmii_phy = RmiiPhy(dut.rmii_txd, dut.rmii_tx_en, dut.rmii_rxd, dut.rmii_rx_er, 
            dut.rmii_crs_dv, dut.rmii_ref_clk, speed=speed)

        dut.rmii_txd.setimmediatevalue(0)
        dut.rmii_tx_en.setimmediatevalue(0)
        dut.rgmii_mdio_a.setimmediatevalue(0)
        dut.dip_sw.setimmediatevalue(0)

        self.rising_edge_ipbus = RisingEdge(self.dut.clk_32_i)
        self.falling_edge_ipbus = FallingEdge(self.dut.clk_32_i)
        self.rising_edge_125 = RisingEdge(self.dut.clk_125_i)
        self.falling_edge_125 = FallingEdge(self.dut.clk_125_i)

    async def start_clk(self):
        cocotb.start_soon(Clock(self.dut.clk_125_i, 8, units="ns").start())
        cocotb.start_soon(Clock(self.dut.clk_200_i, 5, units="ns").start())
        cocotb.start_soon(Clock(self.dut.clk_32_i, 32, units="ns").start())

    async def reset(self):
        self.log.info("Resetting DUT")
        await self.falling_edge_ipbus
        self.dut.rst_i.value = 0
        await self.falling_edge_ipbus
        self.dut.rst_i.value = 1
        await self.falling_edge_ipbus
        self.dut.rst_i.value = 0
        self.log.info("DUT reset complete")
    
    async def init_state(self):
        cocotb.log.info("A")
        await self.start_clk()
        cocotb.log.info("B")
        await self.reset()
        cocotb.log.info("C")

        
    async def writeToAddress(self, addr, data, id=124):
        write_pkt = build_write_transaction(cocotb, id, 1, addr, data)
        frame_to_send, eth_frame, ipbus_pkt = send_ipbus_frame(cocotb, [write_pkt])
        # ipbus_pkt.print_pkt()
        await self.rmii_phy.rx.send(frame_to_send)
        res_frame_raw = await self.rmii_phy.tx.recv()
        res_frame = Ether(bytes(res_frame_raw.get_payload()))
        check_response(eth_frame, res_frame)
        res_ipbus_pkt = IpbusPkt(cocotb)
        res_ipbus_pkt.construct_pkt(res_frame[UDP].load)
        # res_ipbus_pkt.print_pkt()

    async def readFromAddress(self, addr, id=123, verificationValue=0):
        read_pkt = build_read_transaction(cocotb, id, 1, addr)
        frame_to_send, eth_frame, ipbus_pkt = send_ipbus_frame(cocotb, [read_pkt])
        # ipbus_pkt.print_pkt()
        await self.rmii_phy.rx.send(frame_to_send)
        res_frame_raw = await self.rmii_phy.tx.recv()
        res_frame = Ether(bytes(res_frame_raw.get_payload()))
        check_response(eth_frame, res_frame)
        res_ipbus_pkt = IpbusPkt(cocotb)
        res_ipbus_pkt.construct_pkt(res_frame[UDP].load)
        # res_ipbus_pkt.print_pkt()
        assert res_ipbus_pkt.transactions[0].data == verificationValue, f"Read value {res_ipbus_pkt.transactions[0].data} does not match expected value {verificationValue}"

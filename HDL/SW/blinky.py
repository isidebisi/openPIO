import uhal
import argparse
import time # Added for potential small delay

'''
The program should be
00: SET 1 at LED PINDIRS GPIO with 31 cycle delay
01: SET 1 at LED GPIO with 31 cycle delay
02: NOP with 31 cycle delay
03: NOP with 31 cycle delay
04: NOP with 31 cycle delay
05: NOP with 31 cycle delay
06: NOP with 31 cycle delay
07: SET 0 at LED GPIO with 30 cycle delay
08: NOP with 31 cycle delay
09: NOP with 31 cycle delay
10: NOP with 31 cycle delay
11: NOP with 31 cycle delay
12: NOP with 31 cycle delay
13: JMP to program start with 31 cycle delay

All should run on SM0
The registers should be set as follows:
CTRL = 1 (<<0) at SM0_ENABLE
CLKDIV = 65535.00 (<<16)
EXECCTRL =  WRAP TOP = 31 (<<12) or something big (optionally STICKY_OUT = 1 << 17)
SHIFTCTRL = 0
PINCTRL = SideSetCount=0, SetCount=1 (<<26), Set_Base=0
'''
OUT_STICKY = 0x1 << 17

TEST_WRITE_VALUE = 0b01001100011100001111000001111100
LED_GPIO = 0b0


NOP_31Delay = 0b1011111101000010 & 0xFFFFFFFF
SET_PINDIRS = 0b1110000010000001 & 0xFFFFFFFF
SET_1_31Delay = 0b1111111100000001 & 0xFFFFFFFF
SET_0_30Delay = 0b1111111000000000 & 0xFFFFFFFF # Corrected: was 0xFFFFFFFF, now 0xFFFFFFFE for delay 30
JMP_TO_0_31Delay = 0b0001111100000000 & 0xFFFFFFFF


CTRL = 1 & 0xFFFFFFFF

SM0_CLKDIV = ((65535 & 0xFFFF) << 16) & 0xFFFFFFFF
SM0_EXECCTRL = (((31 & 0xFFF) << 12) |  OUT_STICKY) & 0xFFFFFFFF # WRAP_TOP = 31. Program is 14 instructions (0-13). JMP at 13.
SM0_PINCTRL = ((5 << 26)) & 0xFFFFFFFF # SET_COUNT = 1

# Reorder REGISTERS and REGVALS to write CTRL last
# Original order: CTRL, SM0_CLKDIV, SM0_EXECCTRL, SM0_PINCTRL, INSTR_MEM...
# New order: SM0_CLKDIV, SM0_EXECCTRL, SM0_PINCTRL, INSTR_MEM..., CTRL

# Define individual instruction memory values for clarity in REGVALS_NEW
INSTR_MEM_VALS = [
    SET_PINDIRS ,SET_1_31Delay, NOP_31Delay, NOP_31Delay, NOP_31Delay,
    NOP_31Delay, NOP_31Delay, SET_0_30Delay, NOP_31Delay, NOP_31Delay,
    NOP_31Delay, NOP_31Delay, NOP_31Delay, JMP_TO_0_31Delay
]

# Create names for instruction memory registers
INSTR_MEM_NAMES = [f'INSTR_MEM{i}' for i in range(len(INSTR_MEM_VALS))]

REGISTERS_ORDERED = ['SM0_CLKDIV', 'SM0_EXECCTRL', 'SM0_PINCTRL'] + INSTR_MEM_NAMES + ['CTRL']
REGVALS_ORDERED = [SM0_CLKDIV, SM0_EXECCTRL, SM0_PINCTRL] + INSTR_MEM_VALS + [CTRL]


def main():
    parser = argparse.ArgumentParser(description='PIO Blinky Test')
    parser.add_argument('--ip', type=str, default='192.168.0.3', help='IP address of the board', required=False)
    parser.add_argument('--xml', type=str, default='addr_table/ipbus_pio.xml', help='Path to the xml file', required=False)
    args = parser.parse_args()

    uhal.setLogLevelTo(uhal.LogLevel.WARNING)
    hw = uhal.getDevice('board', f'ipbusudp-2.0://{args.ip}:50001', f'file://{args.xml}')

    try:
        pio0_node = hw.getNode('pio0')
        print(f"Successfully accessed base node: pio0")
    except Exception as e:
        print(f"Error accessing base node pio0: {e}")
        print("Please ensure 'pio0' is defined in your XML address table and the XML path is correct.")
        return

    for idx, reg_name in enumerate(REGISTERS_ORDERED):
        val_to_write = REGVALS_ORDERED[idx]
        print(f"\nProcessing register: {reg_name}")
        
        try:
            reg_node = pio0_node.getNode(reg_name)
            
            print(f"Writing value 0x{val_to_write:08X} to {reg_name} ...")
            reg_node.write(val_to_write)
            hw.dispatch()
            # time.sleep(0.01) # Optional: small delay after write dispatch

            print(f"Reading from {reg_name} ...")
            read_value_uhal = reg_node.read()
            hw.dispatch()
            # time.sleep(0.01) # Optional: small delay after read dispatch
            read_value = int(read_value_uhal)
            
            # Special handling for CTRL register if its enable bit might not read back as 1
            # For now, we'll keep the direct comparison.
            if read_value != val_to_write:
                print(f"ERROR: For {reg_name}, read value (0x{read_value:08X}) does not match expected value (0x{val_to_write:08X}).")
            else:
                print(f"SUCCESS: For {reg_name}, read value (0x{read_value:08X}) matches expected value (0x{val_to_write:08X}).")

        except uhal._core.UdpTimeout as e:
            print(f"UDP TIMEOUT occurred while processing register {reg_name}: {e}")
            print("This might indicate a problem with the hardware responding or network connectivity.")
            print("Stopping further operations.")
            break # Stop if a timeout occurs
        except Exception as e:
            print(f"An unexpected error occurred while processing register {reg_name}: {e}")
            print("Stopping further operations.")
            break # Stop on other errors too

if __name__ == '__main__':
    main()





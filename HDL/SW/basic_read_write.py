import uhal
import argparse


'''
instr_mem0
instr_mem1
instr_mem5
instr_mem7
instr_mem12
instr_mem013

'''


TEST_WRITE_VALUE = ((5 << 26)) & 0xFFFFFFFF #0b1111111100000001 & 0xFFFFFFFF

SHORT_TESTVALUE = 0b1101 #0b1111111100000001 & 0xFFFFFFFF

REGS = ['INSTR_MEM0', 'INSTR_MEM1', 'INSTR_MEM2', 'INSTR_MEM3', 'INSTR_MEM4', 
        'INSTR_MEM5', 'INSTR_MEM6', 'INSTR_MEM7', 'INSTR_MEM8', 'INSTR_MEM9',
        'INSTR_MEM10', 'INSTR_MEM11', 'INSTR_MEM12', 'INSTR_MEM13']



def main():
    parser = argparse.ArgumentParser(description='Test uHAL single write/read to SM1_SHIFTCTRL')
    parser.add_argument('--ip', type=str, default='192.168.0.3', help='IP address of the board', required=False)
    parser.add_argument('--xml', type=str, default='addr_table/ipbus_pio.xml', help='Path to the xml file', required=False) # Assuming ipbus_pio.xml contains SM1_SHIFTCTRL
    # parser.add_argument('--nb_times', type=int, default=1, help='Number of times to write and read', required=False) # Not needed for single operation
    args = parser.parse_args()

    uhal.setLogLevelTo(uhal.LogLevel.WARNING)    
    hw = uhal.getDevice('board', f'ipbusudp-2.0://{args.ip}:50001', f'file://{args.xml}')
    
    for i in range(0,2):
        #print(f"i = {i}")

        if i == 0:
            ctrl_node = hw.getNode('pio0').getNode('SM0_PINCTRL')
            print(f"Writing value 0x{TEST_WRITE_VALUE:04X} to CTRL...")
            ctrl_node.write(TEST_WRITE_VALUE)
            hw.dispatch()
            print("Write dispatched.")
            print(f"Reading from CTRL...")
            read_value_uhal2 = ctrl_node.read()
            hw.dispatch()
            read_value2 = int(read_value_uhal2) # Convert uHAL IntVector/ValWord to Python int
            print("Read dispatched.")
            if read_value2 == TEST_WRITE_VALUE:
                print("SUCCESS: Read value 2 matches written value.")
            else:
                print(f"MISMATCH: Read value (0x{read_value2:08X}) does not match written value (0x{TEST_WRITE_VALUE:08X}).")

        # else:
        #     instr_mem0_node = hw.getNode('pio0').getNode('INSTR_MEM0')
        #     print(f"Writing value 0x{SHORT_TESTVALUE:04X} to INSTR_MEM0...")
        #     instr_mem0_node.write(SHORT_TESTVALUE)
        #     hw.dispatch()
        #     print("Write dispatched.")
        #     print(f"Reading from INSTR_MEM0...")
        #     read_value_uhal = instr_mem0_node.read()
        #     hw.dispatch()
        #     read_value = int(read_value_uhal) # Convert uHAL IntVector/ValWord to Python int
        #     print("Read dispatched.")
        #     if read_value == SHORT_TESTVALUE:#TEST_WRITE_VALUE & 0xFFFF:
        #         print("SUCCESS: Read value matches written value.")
        #     else:
        #         print(f"MISMATCH: Read value (0x{read_value:08X}) does not match written value (0x{SHORT_TESTVALUE:08X}).")

            

        # Perform a single 32-bit write
        
        # for idx, reg in enumerate(REGS):
            # print(f"Writing value 0x{TEST_WRITE_VALUE:08X} to %s ...", reg)
            # reg_node = hw.getNode('pio0').getNode(reg)
            # reg_node.write(idx << 2)

        regsReceived = []
        # Perform a single 32-bit read
        # for idx, reg in enumerate(REGS):
            # print(f"Reading from %s...",reg)
            # reg_node = hw.getNode('pio0').getNode(reg)
            # regsReceived.append(reg_node.read())

        
        # Verify if the read value matches the written value
        

        # for idx, reg in enumerate(REGS):
            # read_value = int(regsReceived[idx])
            # if  read_value != idx << 2:
                # print(f"Read value (0x{read_value:08X}) does not match expected value (0x{TEST_WRITE_VALUE:08X}).")
            # else:
                # print(f"Read value (0x{read_value:08X}) matches expected value (0x{TEST_WRITE_VALUE:08X}).")


if __name__ == '__main__':
    main()





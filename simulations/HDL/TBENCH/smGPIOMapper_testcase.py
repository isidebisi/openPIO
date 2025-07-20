'''
smGPIOMapper_testcase.py
openPIO Project
Author: Ismael Frei
EPFL - TCL 2025
'''

import cocotb
from cocotb.triggers import Timer
from smGPIOMapper_wrapper import SMGPIOMapperWrapper


TEST_VALUE = 0b01001100011100001111000001111100

@cocotb.test()
async def test_sideSet(dut):
    smGPIOM = SMGPIOMapperWrapper(dut)
    
    for i in range(0,32):
        await smGPIOM.someTime
        await smGPIOM.set_smPinCtrl(sideSetCount=4, sideSetBase=i)
        await smGPIOM.set_smExecCtrl(sidePindir=0, sideEnable=0)
        await smGPIOM.set_sideSet(sideSetEnable=1, sideSetData=(i&0X1F))
        await smGPIOM.someTime

        expected_out_pinsWriteData = (((i & 0b1111) << i) | ((i & 0b1111) >> 32-i)) & 0xFFFFFFFF
        expected_out_pinsWriteMask = (((0b1111) << i) | ((0b1111) >> 32-i)) & 0xFFFFFFFF

        # TEST PINS 
        await smGPIOM.check_outSignals(exp_pinsWriteData=expected_out_pinsWriteData, 
                                       exp_pinsWriteMask=expected_out_pinsWriteMask, 
                                       iter=i)
        pinsWriteData = dut.out_pinsWriteData.value
        pinsWriteMask = dut.out_pinsWriteMask.value
        if i < 28:
            assert pinsWriteMask >> i == 0b1111, f"Error: pinsWriteMask at i={i} not decoded correctly"
            assert pinsWriteData >> i == i%16, f"Error: pinsWriteData at i={i} not decoded correctly"
        else:
            assert ((pinsWriteMask >> i) | (pinsWriteMask << 32-i)) & 0XFFFFFFFF == 0b1111 , f"Error: pinsWriteMask at i={i} not decoded correctly"
            assert ((pinsWriteData >> i) | (pinsWriteData << 32-i)) & 0XFFFFFFFF == i%16, f"Error: pinsWriteData at i={i} not decoded correctly"
        
        # TEST PINDIRS
        await smGPIOM.set_smExecCtrl(sidePindir=1, sideEnable=0)
        await smGPIOM.someTime
        await smGPIOM.check_outSignals(exp_pinDirsWriteData=expected_out_pinsWriteData, 
                                       exp_pinDirsWriteMask=expected_out_pinsWriteMask, 
                                       iter=i)
        pinDirsWriteData = dut.out_pinDirsWriteData.value
        pinDirsWriteMask = dut.out_pinDirsWriteMask.value
        if i < 28:
            assert pinDirsWriteMask >> i == 0b1111, f"Error: pinDirsWriteMask at i={i} not decoded correctly"
            assert pinDirsWriteData >> i == i%16, f"Error: pinDirsWriteData at i={i} not decoded correctly"
        else:
            assert ((pinDirsWriteMask >> i) | (pinDirsWriteMask << 32-i)) & 0XFFFFFFFF == 0b1111 , f"Error: pinDirsWriteMask at i={i} not decoded correctly"
            assert ((pinDirsWriteData >> i) | (pinDirsWriteData << 32-i)) & 0XFFFFFFFF == i%16, f"Error: pinDirsWriteData at i={i} not decoded correctly"
        



@cocotb.test()
async def test_setOut(dut):
    smGPIOM = SMGPIOMapperWrapper(dut)
    
    for i in range(0,32):
        await smGPIOM.someTime
        await smGPIOM.set_smPinCtrl(setCount=4, setBase=i, outBase=(i+5)%32, outCount=i)
        await smGPIOM.set_smExecCtrl()

        '''
        TEST SET
        '''
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=0, outSetPinsNotPindirs=1, outSetData=(i&0X1F))
        await smGPIOM.someTime
        expected_out_pinsWriteData = (((i & 0b1111) << i) | ((i & 0b1111) >> 32-i)) & 0xFFFFFFFF
        expected_out_pinsWriteMask = (((0b1111) << i) | ((0b1111) >> 32-i)) & 0xFFFFFFFF
        #print(f"SET at i={i}")
        
        # TEST PINS
        await smGPIOM.check_outSignals(exp_pinsWriteData=expected_out_pinsWriteData, 
                                       exp_pinsWriteMask=expected_out_pinsWriteMask, 
                                       iter=i)
        
        pinsWriteData = dut.out_pinsWriteData.value
        pinsWriteMask = dut.out_pinsWriteMask.value
        assert ((pinsWriteMask >> i) | (pinsWriteMask << 32-i)) & 0XFFFFFFFF == 0b1111 , f"Error: pinsWriteMask at i={i} not decoded correctly"
        assert ((pinsWriteData >> i) | (pinsWriteData << 32-i)) & 0XFFFFFFFF == i%16, f"Error: pinsWriteData at i={i} not decoded correctly"

        # TEST PINDIRS
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=0, outSetPinsNotPindirs=0, outSetData=(i&0X1F))
        await smGPIOM.check_outSignals(exp_pinDirsWriteData=expected_out_pinsWriteData, 
                                       exp_pinDirsWriteMask=expected_out_pinsWriteMask, 
                                       iter=i)
        
        pinDirsWriteData = dut.out_pinDirsWriteData.value
        pinDirsWriteMask = dut.out_pinDirsWriteMask.value
        assert ((pinDirsWriteMask >> i) | (pinDirsWriteMask << 32-i)) & 0XFFFFFFFF == 0b1111 , f"Error: pinDirsWriteMask at i={i} not decoded correctly"
        assert ((pinDirsWriteData >> i) | (pinDirsWriteData << 32-i)) & 0XFFFFFFFF == i%16, f"Error: pinDirsWriteData at i={i} not decoded correctly"
        '''
        TEST OUT
        '''
        await smGPIOM.someTime
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=1, outSetPinsNotPindirs=1, outSetData=i)
        await smGPIOM.someTime
        k=((i+5)%32)
        expected_out_pinsWriteData = ((i & 2**i-1) << k | ((i & 2**i-1) >> 32-k)) & 0xFFFFFFFF
        expected_out_pinsWriteMask = ((2**i-1) << k | ((2**i-1) >> 32-k)) & 0xFFFFFFFF
        
        # TEST PINS
        await smGPIOM.check_outSignals(exp_pinsWriteData=expected_out_pinsWriteData,
                                       exp_pinsWriteMask=expected_out_pinsWriteMask, 
                                       iter=i)
        pinsWriteData = dut.out_pinsWriteData.value
        pinsWriteMask = dut.out_pinsWriteMask.value
        assert (pinsWriteMask >> k | (pinsWriteMask << 32-k)) & 0XFFFFFFFF == (2**i-1) , f"Error Out: pinsWriteMask at i={i} not decoded correctly"
        assert (pinsWriteData >> k | (pinsWriteData << 32-k)) & 0XFFFFFFFF == i, f"Error Out: pinsWriteData at i={i} not decoded correctly"

        # TEST PINDIRS
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=1, outSetPinsNotPindirs=0, outSetData=i)
        await smGPIOM.check_outSignals(exp_pinDirsWriteData=expected_out_pinsWriteData,
                                       exp_pinDirsWriteMask=expected_out_pinsWriteMask, 
                                       iter=i)
        
        pinDirsWriteData = dut.out_pinDirsWriteData.value
        pinDirsWriteMask = dut.out_pinDirsWriteMask.value
        assert (pinDirsWriteMask >> k | (pinDirsWriteMask << 32-k)) & 0XFFFFFFFF == (2**i-1) , f"Error Out: pinDirsWriteMask at i={i} not decoded correctly"
        assert (pinDirsWriteData >> k | (pinDirsWriteData << 32-k)) & 0XFFFFFFFF == i, f"Error Out: pinDirsWriteData at i={i} not decoded correctly"

@cocotb.test()
async def AI_test_combined_setSideSetOut(dut):
    smGPIOM = SMGPIOMapperWrapper(dut)
    
    for i in range(0,32): # Main loop iterator
        await smGPIOM.someTime

        # --- Parameters and Expected Values Calculation ---

        # SideSet (ss) parameters - based on test_sideSet
        ss_base = i
        ss_count_val = 4 # SIDESET_COUNT is 4
        ss_data_input = (i & 0x1F) # 5-bit input data
        
        # Effective unrotated mask and data for SideSet (4 bits)
        ss_mask_unrotated = (1 << ss_count_val) - 1 
        ss_data_unrotated = ss_data_input & ss_mask_unrotated
        
        exp_d_ss = ((ss_data_unrotated << ss_base) | (ss_data_unrotated >> (32 - ss_base))) & 0xFFFFFFFF
        exp_m_ss = ((ss_mask_unrotated << ss_base) | (ss_mask_unrotated >> (32 - ss_base))) & 0xFFFFFFFF

        # SET (s) parameters - based on test_setOut (SET part)
        s_base = i # setBase is i
        s_count_val = 4 # SET_COUNT is 4
        s_data_input = (i & 0x1F) # 5-bit input data
        
        # Effective unrotated mask and data for SET (4 bits)
        s_mask_unrotated = (1 << s_count_val) - 1
        s_data_unrotated = s_data_input & s_mask_unrotated
        
        exp_d_s = ((s_data_unrotated << s_base) | (s_data_unrotated >> (32 - s_base))) & 0xFFFFFFFF
        exp_m_s = ((s_mask_unrotated << s_base) | (s_mask_unrotated >> (32 - s_base))) & 0xFFFFFFFF

        # OUT (o) parameters - based on test_setOut (OUT part)
        o_base = (i + 5) % 32 # outBase
        o_count_val = i # outCount is i
        o_data_input = i # data for OUT is i
        
        # Effective unrotated mask and data for OUT
        o_mask_unrotated = (1 << o_count_val) - 1 if o_count_val > 0 else 0
        o_data_unrotated = o_data_input & o_mask_unrotated
        
        exp_d_o = ((o_data_unrotated << o_base) | (o_data_unrotated >> (32 - o_base))) & 0xFFFFFFFF
        exp_m_o = ((o_mask_unrotated << o_base) | (o_mask_unrotated >> (32 - o_base))) & 0xFFFFFFFF

        # Configure smPinCtrl for all operations
        await smGPIOM.set_smPinCtrl(sideSetCount=ss_count_val, sideSetBase=ss_base, 
                                    setCount=s_count_val, setBase=s_base, 
                                    outCount=o_count_val, outBase=o_base)

        # --- Test Part 1: SideSet + SET ---
        #cocotb.log.info(f"Combined Test (i={i}): SideSet + SET")
        
        final_exp_d_ss_s = exp_d_ss | exp_d_s
        final_exp_m_ss_s = exp_m_ss | exp_m_s

        # Target PINS for (SideSet + SET)
        await smGPIOM.set_smExecCtrl(sidePindir=0, sideEnable=0) # sideEnable=0 as in test_sideSet
        await smGPIOM.set_sideSet(sideSetEnable=1, sideSetData=ss_data_input)
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=0, outSetPinsNotPindirs=1, outSetData=s_data_input)
        await smGPIOM.someTime
        await smGPIOM.check_outSignals(exp_pinsWriteData=final_exp_d_ss_s, 
                                       exp_pinsWriteMask=final_exp_m_ss_s,
                                       exp_pinDirsWriteData=0, 
                                       exp_pinDirsWriteMask=0, 
                                       iter=f"{i}_ss_s_pins")

        # Target PINDIRS for (SideSet + SET)
        await smGPIOM.set_smExecCtrl(sidePindir=1, sideEnable=0) # sideEnable=0 as in test_sideSet
        await smGPIOM.set_sideSet(sideSetEnable=1, sideSetData=ss_data_input) # sideSet inputs remain
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=0, outSetPinsNotPindirs=0, outSetData=s_data_input)
        await smGPIOM.someTime
        await smGPIOM.check_outSignals(exp_pinsWriteData=0, 
                                       exp_pinsWriteMask=0,
                                       exp_pinDirsWriteData=final_exp_d_ss_s, 
                                       exp_pinDirsWriteMask=final_exp_m_ss_s, 
                                       iter=f"{i}_ss_s_pindirs")

        # --- Test Part 2: SideSet + OUT ---
        #cocotb.log.info(f"Combined Test (i={i}): SideSet + OUT")
        
        final_exp_d_ss_o = exp_d_ss | exp_d_o
        final_exp_m_ss_o = exp_m_ss | exp_m_o

        # Target PINS for (SideSet + OUT)
        await smGPIOM.set_smExecCtrl(sidePindir=0, sideEnable=0) # sideEnable=0 as in test_sideSet
        await smGPIOM.set_sideSet(sideSetEnable=1, sideSetData=ss_data_input)
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=1, outSetPinsNotPindirs=1, outSetData=o_data_input)
        await smGPIOM.someTime
        await smGPIOM.check_outSignals(exp_pinsWriteData=final_exp_d_ss_o, 
                                       exp_pinsWriteMask=final_exp_m_ss_o,
                                       exp_pinDirsWriteData=0, 
                                       exp_pinDirsWriteMask=0, 
                                       iter=f"{i}_ss_o_pins")

        # Target PINDIRS for (SideSet + OUT)
        await smGPIOM.set_smExecCtrl(sidePindir=1, sideEnable=0) # sideEnable=0 as in test_sideSet
        await smGPIOM.set_sideSet(sideSetEnable=1, sideSetData=ss_data_input) # sideSet inputs remain
        await smGPIOM.set_outSet(outSetEnable=1, outNotSet=1, outSetPinsNotPindirs=0, outSetData=o_data_input)
        await smGPIOM.someTime
        await smGPIOM.check_outSignals(exp_pinsWriteData=0, 
                                       exp_pinsWriteMask=0,
                                       exp_pinDirsWriteData=final_exp_d_ss_o, 
                                       exp_pinDirsWriteMask=final_exp_m_ss_o, 
                                       iter=f"{i}_ss_o_pindirs")

@cocotb.test()
async def test_GPIOInputMapping(dut):
    smGPIOM = SMGPIOMapperWrapper(dut)
    
    for i in range(0,32):
        dut.in_GPIO.value = TEST_VALUE
        await smGPIOM.set_smPinCtrl(inBase=i)
        await smGPIOM.set_smExecCtrl()
        await smGPIOM.someTime

        k = 2**i-1
        l = 2**(32-i)-1

        expected_inGPIOmappedData = (((TEST_VALUE & l) << i) | ((TEST_VALUE) >> 32-i) & k) & 0xFFFFFFFF
        
        assert dut.out_inGPIOmappedData.value == expected_inGPIOmappedData, f"Error: GPIO mapped data at i={i} not decoded correctly"
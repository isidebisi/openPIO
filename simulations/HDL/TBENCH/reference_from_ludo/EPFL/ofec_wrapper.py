from ofec.memory_manager import MemoryManagerGeneric
from ofec.memory_manager import FIFO_WIDTH, FIFO_SOFT_DEPTH_DEFAULT, FIFO_HARD_DEPTH_DEFAULT, HDD_BIT_PER_WORD, SDD_BIT_PER_SYMBOL, SDD_BIT_PER_WORD, FIFO_SDD_LINEAR_OFFSET, FIFO_SDD_DIAGONAL_OFFSET_DEFAULT, FIFO_HDD_LINEAR_OFFSET_DEFAULT, FIFO_HDD_DIAGONAL_OFFSET
import random
import coloredlogs
import cocotb
from cocotb.log import SimLog
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.clock import Clock
from cocotb.binary import BinaryValue, BinaryRepresentation
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import math
import matplotlib.pyplot as plt

#from ofec.memory_manager import SOFT_FOR_HARD_DECISION
import ofec.memory_manager as memory_manager

DEBUG = True

CLOCK_PERIOD = 1
from ofec import  NB_CLOCK_C_PER_WORD_SDD as NB_CLOCK_CYCLE_SOFT
from ofec import  NB_CLOCK_C_PER_WORD_HDD as NB_CLOCK_CYCLE_HARD

NB_CLOCK_CYCLE_DECODE_SOFT = 15
NB_CLOCK_CYCLE_DECODE_HARD = 8






BCH_IN_PARALLEL = 32
BCH_N = 256
BCH_N_o_2 = BCH_N // 2
MATRIX_SIZE = (BCH_IN_PARALLEL, BCH_N)


class ofecUnscheduleWrapper(MemoryManagerGeneric):
    def __init__(self, *args):
        self.log = SimLog("cocotb")
        self.dut = args[0]
        self.clk = None
        self.dut.RSTxSI.setimmediatevalue(0)
        self.dut.hard_push_back.setimmediatevalue(0)
        self.dut.hard_clock_index.setimmediatevalue(0)
        self.dut.hard_write_enable.setimmediatevalue(0)
        self.dut.hard_read_enable.setimmediatevalue(0)
        self.dut.soft_push_back.setimmediatevalue(0)
        self.dut.soft_clock_index.setimmediatevalue(0)
        self.dut.soft_write_enable.setimmediatevalue(0)
        self.dut.soft_read_enable.setimmediatevalue(0)
        self.dut.push_back_mode.setimmediatevalue(0)
        self.dut.soft_push_zeros_updated_soft_memory.setimmediatevalue(0)
        self.dut.soft_push_to_memory_in.setimmediatevalue(0)
        self.dut.soft_start_decoder.setimmediatevalue(0)
        self.dut.hard_start_decoder.setimmediatevalue(0)
        self.rising_edge = RisingEdge(self.dut.CLKxCI)

    async def init_state(self):
        await self.start_clk()
        await self.reset()

    async def reset(self):
        """Reset the dut"""
        self.log.info("Resetting the DUT")
        await self.rising_edge
        await self.rising_edge
        self.dut.RSTxSI.value = 0
        await self.rising_edge
        self.dut.RSTxSI.value = 1
        await self.rising_edge
        self.dut.RSTxSI.value = 0
        await self.rising_edge
        self.log.info("Reset done")
        

    async def start_clk(self):
        """Start the clock"""
        if self.clk is None:
            self.log.info("Starting the clock")
            self.clk = Clock(self.dut.CLKxCI, CLOCK_PERIOD, "ns")
            await cocotb.start(self.clk.start())
        else:
            self.log.warning("Clock already started")

    @staticmethod
    def twos_complement_to_signed_magnitude(data):
        """
        """
        # Precompute constant values
        SIGN_BIT = 1 << (SDD_BIT_PER_SYMBOL - 1)
        abs_data = np.abs(data)  # Precompute absolute values
        # Handle conversion
        data_new = np.where(data < 0, SIGN_BIT | abs_data, abs_data)
        return data_new
    @staticmethod
    def integer_twos_complement(data):
        """
        When we write to HDL we need to have the value represented as twos complement.
        """
        # Precompute constant values
        SIGN_BIT = (1 << (SDD_BIT_PER_SYMBOL - 1))
        MASK = (~np.uint8(SIGN_BIT)) & 0xFF
        #local_data = data.copy()
        local_data = data
        # Handle conversion 
        return np.where(local_data & SIGN_BIT, -np.int8(MASK & local_data), local_data)

    @staticmethod
    def random_for_unresolved():
        return np.random.randint(0, 2**(SDD_BIT_PER_SYMBOL))

    async def push_back(self, data, push_zeros_updated_soft=False):
        """Method to push back new data and return the data that is pushed out
        :param data: data to write
        :param psuh_zeros_updated_soft: status of the decoding True if need to push 0 is updated soft else False
        """
        
        reshaped_data = np.empty((BCH_IN_PARALLEL, BCH_N), dtype=np.int8)
        for R in range(data.shape[0]):
            for C in range(data.shape[1]):
                for r in range(data.shape[2]):
                    for c in range(data.shape[3]):
                        reshaped_data[r+R*data.shape[2]][c+C*data.shape[3]] = data[R][C][r][c]
        
        reshaped_data = self.twos_complement_to_signed_magnitude(reshaped_data)
        if push_zeros_updated_soft:
            self.dut.soft_push_zeros_updated_soft_memory.value = 1
        else:
            self.dut.soft_push_zeros_updated_soft_memory.value = 0

        # increment address pointer:
        self.dut.push_back_mode.value = 1
        self.dut.soft_push_back.value = 1
        self.dut.hard_push_back.value = 1
        # set stage index to 0 to read the oldes data of memories
        self.dut.soft_read_stage_index.value = 0
        self.dut.hard_read_stage_index.value = 0
        # perform the read operation
        self.dut.soft_clock_index.value = 0
        self.dut.hard_clock_index.value = 0
        # finish the push back operation 
        await self.rising_edge
        self.dut.soft_push_back.value = 0
        self.dut.hard_push_back.value = 0
        # read soft and hard data that is pushed out
        # we can read both in parallel
        self.dut.soft_read_enable.value = 1
        self.dut.hard_read_enable.value = 1
        self.set_hard_read_mode_linear(True)
        self.set_soft_read_mode_linear(True)
        for _ in range(NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.soft_clock_index.value = (self.dut.soft_clock_index.value + 1) % NB_CLOCK_CYCLE_SOFT
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.dut.soft_read_enable.value = 0
        await self.rising_edge # need one more clock cycle to get data out of the memory
        data_for_hard_decision = np.empty((BCH_IN_PARALLEL, BCH_N_o_2), dtype=np.int8)
        #data_for_hard_decision_test = np.empty((BCH_IN_PARALLEL, BCH_N_o_2), dtype=np.int8)
        for x in range(BCH_IN_PARALLEL):
            for y in range(BCH_N_o_2):
                temp_value = self.dut.soft_read_bch_codeword[x][y+BCH_N_o_2].value
                data_for_hard_decision[x][y] = temp_value.integer if temp_value.is_resolvable else  self.random_for_unresolved()
                # temp_value = self.dut.soft_read_bybass_mapping[x][y].value
                # data_for_hard_decision_test [x][y] = temp_value.integer if temp_value.is_resolvable else  self.random_for_unresolved()

        # finish reading the rest
        self.dut.soft_clock_index.value = 0
        
        self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        for _ in range(NB_CLOCK_CYCLE_HARD-NB_CLOCK_CYCLE_SOFT - 1):
            await self.rising_edge
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD

        self.dut.hard_read_enable.value = 0
        await self.rising_edge # need one more clock cycle to get data out of the memory
        data_out = np.empty((BCH_IN_PARALLEL, BCH_N_o_2), dtype=np.int8)

        for x in range(BCH_IN_PARALLEL):
            for y in range(BCH_N_o_2):
                # read only back data
                temp_value =  self.dut.decoder_out[x][y].value
                data_out[x][y] = temp_value.integer if temp_value.is_resolvable else self.random_for_unresolved()
        # hard decision
        #print(data_for_hard_decision[0])
        data_for_hard_decision = self.integer_twos_complement(data_for_hard_decision)
        #print(data_for_hard_decision[0])
        np.savetxt("data_for_hard_decision.csv", data_for_hard_decision, delimiter=",", fmt='%i')
        hard_decision = data_for_hard_decision < 0 # convert to bool
        #print(hard_decision[0])
        hard_decision = hard_decision.astype(np.int8) # convert to int8
        hard_decision_tmp = np.empty((BCH_IN_PARALLEL, BCH_N_o_2), dtype=np.int8)
        hard_decision_tmp = hard_decision
        # debug start
        # if push_zeros_updated_soft == False:
        #     sample_original = memory_manager.SOFT_FOR_HARD_DECISION
        #     sample_measured = self.integer_twos_complement(data_for_hard_decision_test[:,:16].ravel('C'))

        #     if np.any(sample_original != sample_measured):
        #         print("sample_original")
        #         print(sample_original)
        #         print("sample_measured")
        #         print(sample_measured)
        #         print("What you should look for in the simulation")

        #         print(self.twos_complement_to_signed_magnitude(sample_original))
        #         print(self.twos_complement_to_signed_magnitude(sample_measured))
        # debug end
        
        # write new data
        self.dut.soft_push_to_memory_in.value = True
        # set stage index to 0 to write the oldes data of memories
        self.dut.soft_write_stage_index.value = 0
        self.dut.hard_write_stage_index.value = 0
        # perform the write operation
        self.dut.soft_clock_index.value = 0
        self.dut.hard_clock_index.value = 0
        # write soft and hard data that is pushed out
        # we can write both in parallel
        self.dut.soft_write_enable.value = 1
        self.dut.hard_write_enable.value = 1
        self.set_hard_write_mode_linear(True)
        self.set_soft_write_mode_linear(True)
        for x in range(BCH_IN_PARALLEL):
            for y in range(BCH_N_o_2):
                self.dut.decoder_in[x][y].value = int(reshaped_data[x,y])
                self.dut.hard_write_bch_codeword[x][y+BCH_N_o_2].value = bool(hard_decision_tmp[x , y])

        for _ in range(NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.soft_clock_index.value = (self.dut.soft_clock_index.value + 1) % NB_CLOCK_CYCLE_SOFT
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.dut.soft_clock_index.value = 0
        self.dut.soft_write_enable.value = 0
        for _ in range(NB_CLOCK_CYCLE_HARD-NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.dut.hard_write_enable.value = 0
        self.dut.push_back_mode.value = 0
        self.dut.soft_push_to_memory_in.value = False
        self.dut.soft_push_zeros_updated_soft_memory.value = 0
        return data_out

    def set_hard_read_mode_linear(self, value):
        self.dut.hard_read_linear_b_diagonal.value = int(not value)

    def set_hard_write_mode_linear(self, value):
        self.dut.hard_write_linear_b_diagonal.value = int(not value)

    def set_soft_read_mode_linear(self, value):
        self.dut.soft_read_linear_b_diagonal.value = int(not value)

    def set_soft_write_mode_linear(self, value):
        self.dut.soft_write_linear_b_diagonal.value = int(not value)


    async def read_soft_stage(self, stage_idx):
        """Method to read from the soft decision stage
        :param stage_idx: index of the stage to read from
        :return: data from the stage"""
        self.set_soft_read_mode_linear(True)
        self.dut.soft_clock_index.value = 0
        self.dut.soft_read_enable.value = 1
        self.dut.soft_read_stage_index.value = stage_idx
        for _ in range(NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.soft_clock_index.value = (self.dut.soft_clock_index.value + 1) % NB_CLOCK_CYCLE_SOFT
        self.set_soft_read_mode_linear(False)
        self.dut.soft_clock_index.value = 0
        for _ in range(NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.soft_clock_index.value = (self.dut.soft_clock_index.value + 1) % NB_CLOCK_CYCLE_SOFT
        self.dut.soft_read_enable.value = 0
        await self.rising_edge # need one more clock cycle to get data out of the memory
        bch_codeword = np.empty(MATRIX_SIZE, dtype=np.int8)
        for x in range(BCH_IN_PARALLEL):
            for y in range(BCH_N):
                temp_value = self.dut.soft_read_bch_codeword[x][y].value
                bch_codeword[x][y] = temp_value.integer if temp_value.is_resolvable else  self.random_for_unresolved()
        
        await self.soft_decode() # TODO: make sure of this position
        return self.integer_twos_complement(bch_codeword)
    

    async def read_hard_stage(self, stage_idx, debug= False):
        """Method to read from the hard decision stage
        :param stage_idx: index of the stage to read from
        :return: data from the stage"""

        self.set_hard_read_mode_linear(True)
        self.dut.hard_clock_index.value = 0
        self.dut.hard_read_enable.value = 1
        self.dut.hard_read_stage_index.value = stage_idx
        for _ in range(NB_CLOCK_CYCLE_HARD):
            await self.rising_edge
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.set_hard_read_mode_linear(False)
        self.dut.hard_clock_index.value = 0
        for _ in range(NB_CLOCK_CYCLE_HARD):
            await self.rising_edge
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.dut.hard_read_enable.value = 0
        await self.rising_edge # need one more clock cycle to get data out of the memory
        bch_codeword = np.empty(MATRIX_SIZE, dtype=np.int8)
        for x in range(BCH_IN_PARALLEL):
            for y in range(BCH_N):
                temp_value = self.dut.hard_read_bch_codeword[x][y].value
                bch_codeword[x][y] = temp_value.integer if temp_value.is_resolvable else  self.random_for_unresolved()
        if not debug:
            await self.hard_decode() # TODO: make sure of this position
        return bch_codeword
    

    async def update_soft_stage(self, stage_idx, updated_data):
        global DEBUG
        """Method to update the memory
        :param stage_idx: index of the stage to update
        :param updated_data: new data to write"""
        self.set_soft_write_mode_linear(False)
        self.dut.soft_push_to_memory_in.value = False
        local_updated_data = self.twos_complement_to_signed_magnitude(updated_data)
        # for x in range(BCH_IN_PARALLEL):
        #     for y in range(BCH_N):
        #         self.dut.soft_write_bch_codeword[x][y].value = int(local_updated_data[x][y])
        #self.dut.soft_write_bch_codeword.value = updated_data
        self.dut.soft_write_enable.value = 1
        self.dut.soft_write_stage_index.value = stage_idx
        self.dut.soft_clock_index.value = 0
        for _ in range(NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.soft_clock_index.value = (self.dut.soft_clock_index.value + 1) % NB_CLOCK_CYCLE_SOFT
        self.dut.soft_clock_index.value = 0
        self.set_soft_write_mode_linear(True)
        for _ in range(NB_CLOCK_CYCLE_SOFT):
            await self.rising_edge
            self.dut.soft_clock_index.value = (self.dut.soft_clock_index.value + 1) % NB_CLOCK_CYCLE_SOFT
        self.dut.soft_write_enable.value = 0
        if DEBUG:
            expected_data = np.array(updated_data)
            # read_data = await self.read_soft_stage(stage_idx)
            decoder_data = np.empty(expected_data.shape, dtype=np.int8)
            for x in range(BCH_IN_PARALLEL):
                for y in range(BCH_N):
                    decoder_data[x][y] = self.dut.soft_write_bch_codeword[x][y].value.integer
                    if decoder_data[x][y] == (1 << (SDD_BIT_PER_SYMBOL - 1)):
                        decoder_data[x][y] = 0

            decoder_data = self.integer_twos_complement(decoder_data)
            # write both into a debug csv
            with open("expected_data.csv", "w") as f:
                np.savetxt(f, expected_data, delimiter=",", fmt='%i')
            with open("decoder_data.csv", "w") as f:
                np.savetxt(f, decoder_data, delimiter=",", fmt='%i')
            assert np.all(expected_data == decoder_data), f"soft stage {stage_idx} Data read is not the same as the data written"

    async def update_hard_stage(self, stage_idx, updated_data):
        global DEBUG
        """Method to update the memory
        :param stage_idx: index of the stage to update
        :param updated_data: new data to write"""
        self.set_hard_write_mode_linear(False)
        # for x in range(BCH_IN_PARALLEL):
        #     for y in range(BCH_N):
        #         self.dut.hard_write_bch_codeword[x][y].value = bool(updated_data[x][y])
        self.dut.hard_write_enable.value = 1
        self.dut.hard_write_stage_index.value = stage_idx
        self.dut.hard_clock_index.value = 0
        for _ in range(NB_CLOCK_CYCLE_HARD):
            await self.rising_edge
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.dut.hard_clock_index.value = 0
        self.set_hard_write_mode_linear(True)
        for _ in range(NB_CLOCK_CYCLE_HARD):
            await self.rising_edge
            self.dut.hard_clock_index.value = (self.dut.hard_clock_index.value + 1) % NB_CLOCK_CYCLE_HARD
        self.dut.hard_write_enable.value = 0
        if DEBUG:
            expected_data = np.array(updated_data)
            # read_data = await self.read_hard_stage(stage_idx, debug=True)
            decoder_data = np.empty(expected_data.shape, dtype=np.int8)
            for x in range(BCH_IN_PARALLEL):
                for y in range(BCH_N):
                    decoder_data[x][y] = self.dut.hard_write_bch_codeword[x][y].value.integer
            # write both into a debug csv
            assert np.all(expected_data == decoder_data), f"hard stage {stage_idx} Data read is not the same as the data written"
        #await self.rising_edge

    async def soft_decode(self):
        """Method to soft decode the data"""
        self.dut.soft_start_decoder.value = 1
        for _ in range(NB_CLOCK_CYCLE_DECODE_SOFT):
            await self.rising_edge
            self.dut.soft_start_decoder.value = 0
        return
    
    async def hard_decode(self):
        """Method to hard decode the data"""
        self.dut.hard_start_decoder.value = 1
        for _ in range(NB_CLOCK_CYCLE_DECODE_HARD):
            await self.rising_edge
            self.dut.hard_start_decoder.value = 0
        return
    @staticmethod
    def supported_type(type_name):
        """
        Check if the Memory support those type of memory behavior.

        Args:
            type_name (str): Type name to check.

        Returns:
            bool: True if supported, False otherwise.
        """
        return type_name == "cocotb_unscheduled"
    


from ofec_wrapper import (ofecUnscheduleWrapper,BCH_IN_PARALLEL, BCH_N, BCH_N_o_2, MATRIX_SIZE, NB_CLOCK_CYCLE_HARD, NB_CLOCK_CYCLE_SOFT)
from ofec import (
    OFECDecoder,
    OFECEncoder,
    MemoryManager,
    OFECMemoryConfig,
    bpsk_transmit,
    configure_logger,
)
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
import pandas as pd
import logging


#@cocotb.test()
async def hard_read_write_test(dut):
    dut._log.info("Start Simulation hard_read_write_test")
    hdl_wrapper = ofecUnscheduleWrapper(dut)

    # run simulation
    await hdl_wrapper.init_state()
    for j in range(50):
        for stage in range(len(FIFO_HDD_DIAGONAL_OFFSET)):
            data = np.random.randint(0,2,MATRIX_SIZE).astype(np.bool)
            await hdl_wrapper.update_hard_stage(stage, data)
            read_data = await hdl_wrapper.read_hard_stage(stage)
            assert data.tolist() == read_data.tolist(), f"hard stage {stage} Data read is not the same as the data written"
        await hdl_wrapper.rising_edge
        if j % 10 == 0:
            dut._log.info(f"Test {j} passed")
        dut.hard_push_back.value = 1
        await hdl_wrapper.rising_edge
        dut.hard_push_back.value = 0


#@cocotb.test()
async def soft_read_write(dut):
    dut._log.info("Start Simulation soft_read_write_first_address_and_push_zeros_to_updated_soft")
    hdl_wrapper = ofecUnscheduleWrapper(dut)
    
    data_to_push = np.zeros((2,8,16,16), dtype=np.int8)
    
    error = 0
    data_write = np.ones((32,256), dtype=np.int8)
    #run simulation
    await hdl_wrapper.init_state()
    for _ in range(FIFO_SOFT_DEPTH_DEFAULT):
        await hdl_wrapper.push_back(data_to_push, push_zeros_updated_soft=True)

    # special case, stage 0:
    dut.soft_push_to_memory_in.value = 0
    dut.soft_push_zeros_updated_soft_memory.value = 0
    await hdl_wrapper.update_soft_stage(0, data_write)
    dut.soft_push_to_memory_in.value = 1
    dut.soft_push_zeros_updated_soft_memory.value = 1
    await hdl_wrapper.update_soft_stage(0, data_write)
    dut.soft_push_to_memory_in.value = 0
    dut.soft_push_zeros_updated_soft_memory.value = 0

    read_data = await hdl_wrapper.read_soft_stage(0)
    

    # And now the rest
    if np.any(read_data != data_write):
        error += 1
        front_read_data = read_data[:, :128]
        front_data = data_write[:, :128]
        back_read_data = read_data[:, 128:]
        back_data = data_write[:, 128:]
        if np.any(front_read_data != front_data):
            error += 1
            dut._log.error("front data read is not the same as the data written at stage 0")
            print(front_read_data)
            print(front_data)
        if np.any(back_read_data != back_data):
            error += 1
            dut._log.error("back data read is not the same as the data written at stage 0")
            print(back_read_data)
            print(back_data)

    # clear

    # special case, stage 0:
    dut.soft_push_to_memory_in.value = 0
    dut.soft_push_zeros_updated_soft_memory.value = 0
    await hdl_wrapper.update_soft_stage(0, np.zeros_like(data_write))
    dut.soft_push_to_memory_in.value = 1
    dut.soft_push_zeros_updated_soft_memory.value = 1
    await hdl_wrapper.update_soft_stage(0, np.zeros_like(data_write))
    dut.soft_push_to_memory_in.value = 0
    dut.soft_push_zeros_updated_soft_memory.value = 0

    for stage in range (1,len(FIFO_SDD_DIAGONAL_OFFSET_DEFAULT)):
        data_write = np.random.randint(-31,32,(32,256)).astype(np.int8)
        await hdl_wrapper.update_soft_stage(stage, data_write)
        read_data = await hdl_wrapper.read_soft_stage(stage)
        back_read_data = read_data[:, 128:]
        back_data = data_write[:, 128:]
        front_read_data = read_data[:, :128]
        front_data = data_write[:, :128]
        if np.any(back_read_data != back_data):
            error += 1
            dut._log.error(f"back data read is not the same as the data written at stage {stage}")
            print(back_read_data)
            print(back_data)
        if np.any(front_read_data != front_data):
            error += 1
            dut._log.error(f"front data read is not the same as the data written at stage {stage}")
            print(front_read_data)
            print(front_data)
        

    assert error == 0, "Data read is not the same as the data written"
    






MIN_ERROR = 200
MIN_VALID = 200
MAX_VALID = 10000
LOGGING_FREQ = 10

async def equivalent_memory_test(hdl_wrapper, snr, only_ones=True, disable_modulation=True):
    """
    disable modulation is used to disable the AWGN and only send -1 for 1 and 1 for 0 no matter the snr
    """

    hdl_wrapper.dut._log.info("Start Simulation soft_read_write_first_address_and_push_zeros_to_updated_soft")
    # memory managers

    memory_manager_reference = MemoryManager("ARM_8Fifo", NB_CLOCK_CYCLE_HARD, NB_CLOCK_CYCLE_SOFT)
    #memory_manager_reference = MemoryManager("Monolithic_4D")
    # decoders and encoder
    decoder_reference = OFECDecoder(memory_manager_reference)
    decoder_under_test = OFECDecoder(hdl_wrapper)
    encoder = OFECEncoder()
    hdl_wrapper.dut._log.info("Start oFEC test at snr = %.2f", snr)

    delta_rx_tx = (
        encoder.encoded_window_height + OFECMemoryConfig.decoded_window_height + 2
    )  # 2 because sdd and hdd now pipelined
    info_buff = np.zeros(
        [delta_rx_tx * OFECMemoryConfig.block_size, 111], dtype=np.int8
    )  # TODO magic number
    pointer = 0
    error_num = 0
    valid_frame = 0
    error_frame = 0
    idx = 0
    while (error_num < MIN_ERROR or valid_frame < MIN_VALID) and (
        valid_frame < MAX_VALID):
        if (idx + 1) % LOGGING_FREQ == 0:
            hdl_wrapper.dut._log.info(
                "| SNR %1.3f | Iteration %6d | error_frame %4d | error_num %7d | valid_frame %6d |",
                snr,
                idx + 1,
                error_frame,
                error_num,
                valid_frame,
            )
        tx_data, truth_data = encoder.encode(
            only_ones=only_ones
        )  # set to true to test only ones and speed up the process

        #tx_data = np.zeros_like(tx_data)
        info_buff[pointer * 16 : (pointer + 2) * 16, :] = truth_data

        pointer = (pointer + 2) % delta_rx_tx
        rx_data = bpsk_transmit(
            tx_data, SNR=snr, disable=disable_modulation
        )  # set to true to disable the transmission and only send -1 for 1 and 1 for 0
        #dut._log.info("start decoding ref")

        #rx_data = np.zeros_like(rx_data) + 31
        decoded_vector_ref = decoder_reference.decode(rx_data)
        #dut._log.info("start decoding hdl")
        decoder_vector_under_test = await decoder_under_test.async_decode(rx_data)
        if idx > delta_rx_tx // 2:
            assert np.all(decoded_vector_ref == decoder_vector_under_test), f"Decoded vectors are not equal at iteration {idx}"
            if np.any(decoded_vector_ref != decoder_vector_under_test):
                print('Output different')
                print('Expected', decoded_vector_ref)
                print('Got', decoder_vector_under_test)
                assert False
            valid_frame += 1
            original = info_buff[pointer * 16 : (pointer + 2) * 16, :]
            local_error = np.sum(original != decoder_vector_under_test[:, :111])
            # find which line of info_buff is equal to decoded_vector the first vector
            index = np.where(np.all(info_buff == decoder_vector_under_test[0, :111], axis=1))
            error_num += local_error
            error_frame += 1 if local_error > 0 else 0
        idx += 1
    final_ber = error_num / (valid_frame * 32 * 111)
    final_fer = error_frame / valid_frame
    hdl_wrapper.dut._log.info("SNR: %.2f\tBER: %.6f\tFER: %.6f", snr, final_ber, final_fer)
    hdl_wrapper.dut._log.info("finish SNR: %.2f", snr)
    return snr, final_ber, final_fer

@cocotb.test()
async def compare_python_model_in_operation(dut):
    logging.basicConfig(level=logging.INFO)
    #snr_range = np.arange(1, 6, 1)
    #snr_range=[3.2, 3.4]
    snr_range = np.arange(3.2, 3.9, 0.05)
    SNR_stored = []
    BER_stored = []
    FER_stored = []
    hdl_wrapper = ofecUnscheduleWrapper(dut)
    await hdl_wrapper.init_state()
    # Set up plot with log scale and grid (no interactive mode)
    # fig, (ax_ber, ax_fer) = plt.subplots(2, 1, figsize=(8, 6))
    # ax_ber.set_title("BER vs $E_b/N_0$")
    # ax_fer.set_title("FER vs $E_b/N_0$")
    # line_ber, = ax_ber.plot([], [], 'bo-', label="BER")
    # line_fer, = ax_fer.plot([], [], 'ro-', label="FER")
    # #add space between subplots to avoid overlap 
    # plt.subplots_adjust(hspace=0.5)
    # # Configure axes with log scale for BER and FER
    # ax_ber.set_yscale("log")
    # ax_fer.set_yscale("log")
    # ax_ber.set_xlabel("$E_b/N_0$ (dB)")
    # ax_fer.set_xlabel("$E_b/N_0$ (dB)")
    # ax_ber.set_ylabel("BER (log scale)")
    # ax_fer.set_ylabel("FER (log scale)")

    # # Enable grid with minor ticks
    # for ax in (ax_ber, ax_fer):
    #     ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    #     ax.minorticks_on()
    #     ax.grid(True, which='minor', linestyle=':', linewidth=0.5)
    # ax_ber.legend()
    # ax_fer.legend()

    # # Define file path for saving plot
    plot_file_path = os.path.join(os.getcwd(), "live_plot")

    for snr in snr_range:
        snr_loc, ber_loc, fer_loc = await equivalent_memory_test(hdl_wrapper, snr, only_ones=False, disable_modulation=False)
        SNR_stored.append(snr_loc)
        BER_stored.append(ber_loc)
        FER_stored.append(fer_loc)

        # # Update the plot with the new data
        snr_sorted = np.array(SNR_stored)
        ber_sorted = np.array(BER_stored)
        fer_sorted = np.array(FER_stored)

        # # Update plot data
        # line_ber.set_xdata(snr_sorted)
        # line_ber.set_ydata(ber_sorted)
        # line_fer.set_xdata(snr_sorted)
        # line_fer.set_ydata(fer_sorted)
        # ax_ber.relim()
        # ax_ber.autoscale_view()
        # ax_fer.relim()
        # ax_fer.autoscale_view()

        # # Save the updated plot to an image file
        # plt.savefig(plot_file_path+".pdf", format="pdf")
        # dut._log.info(f"Updated plot saved to {plot_file_path}")

    # Final DataFrame creation for all results
    data_frame = pd.DataFrame({
        "SNR": SNR_stored,
        "BER": BER_stored,
        "FER": FER_stored,
    })

    # save as csv
    data_frame.to_csv(plot_file_path+".csv", index=False)
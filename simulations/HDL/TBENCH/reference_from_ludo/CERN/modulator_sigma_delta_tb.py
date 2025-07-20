"""Test bench file"""
import random
from cocotb.log import SimLog
from cocotb.triggers import Timer, FallingEdge, RisingEdge
import matplotlib.pyplot as plt
import numpy as np
from definitions import (
    fourier_analysis_1signal,
    # fourier_analysis_no_centering,
    save,
    save_2,
    s_d_plot,
)

plt.rc("font", family="serif", serif="cm10")
plt.rc("text", usetex=True)
plt.rcParams.update(plt.rcParamsDefault)


class ModulatorSigmaDeltaTestBench:
    """Test bench class"""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=invalid-unary-operand-type
    def __init__(self, dut):
        self.log = SimLog("cocotb")
        self.dut = dut
        self.n_in = 16
        self.n_out = 5
        self.time_constant_filter = 10e-6  # [s]
        self.max_amp = 2 ** 16 - 1  # max value
        self.sampling_freq = 40e6  # [Hz]
        self.sampling_time = 1 / self.sampling_freq  # [s]
        self.window_size = int(
            self.sampling_freq * 12 * np.pi * self.time_constant_filter
        )
        self.ratio_out_in = (2 ** self.n_in) / (2 ** self.n_out)
        # self.ratio_out_in = 1

    def reset(self, value):
        """Assert/deassert reset of PLL"""
        self.dut.rst.value = int(value)

    async def generate_reset_pulse(self):
        """Generate a reset pulse for the PLL"""
        self.reset(True)
        await Timer(1, "us")
        self.reset(False)
        await Timer(100, "ns")

    async def sinus_test(self):
        """initial testbench for sigma-delta modulator
        nbsample -> simulation time -> from fsample/nbsamples = minimum freq"""
        nb_sample = 2 ** 20
        base_freq = self.sampling_freq / nb_sample  # [Hz]
        signal_freq = base_freq * 25  # [s]
        # time = np.linspace(0, sampling_time * nb_sample * 1e-9, nb_sample)  # time axis
        time = np.arange(0, nb_sample) / self.sampling_freq
        # input_1 = np.uint16(
        #     15/16 * self.max_amp / 2.0 * np.sin(2 * np.pi * signal_freq * time)
        #     + 15/16* self.max_amp / 2.0
        # )
        input_1 = np.uint16(
            # (2 ** 16 - 1) * (0.5 + 0.5 * np.sin(2 * np.pi * signal_freq * time))
            (2 ** 16 - 1)
            * (0.5 + 0.25 * np.sin(2 * np.pi * signal_freq * time))
        )
        # input_1 = np.uint16(np.linspace(0,1000,nb_sample))
        output = np.empty(input_1.size + 2 * self.window_size)
        filtered = np.empty(output.size)
        await RisingEdge(self.dut.clk)
        for i in range(input_1.size + 2 * self.window_size):
            output[i] = self.dut.data_o.value.integer * self.ratio_out_in
            filtered[i] = self.dut.v.value
            # print(filtered[i])
            if (i % 2 ** 16) == 0:
                print(i // 2 ** 16 + 1)
            # await FallingEdge(self.dut.clk)
            self.dut.data_i.value = int(
                input_1[i % input_1.size]  # pylint: disable=unsubscriptable-object
            )
            await RisingEdge(self.dut.clk)

        # filtered = moving_average(output, self.window_size)
        # filtered = moving_average(output, self.window_size)
        save(input_1, output, time, filtered, "sin")
        s_d_plot(
            time=time,
            input_s=input_1,
            output=output[: input_1.size],
            filter_s=filtered[: input_1.size],
            title="Second order (MOD2)",
        )
        fourier_analysis_1signal(
            output[self.window_size : self.window_size + input_1.size],
            self.sampling_time,
            "output signal",
        )
        fourier_analysis_1signal(
            filtered[self.window_size : self.window_size + input_1.size],
            self.sampling_time,
            "filtered signal",
        )

        plt.show()
        # input("Press [enter] to continue.")

    async def dc_test(self, plot=True, input_val=None):

        "analyse DC test and return max abs value of quantisation error"
        nb_sample = 2 ** 18
        if input is not None:
            input_1 = np.ones(nb_sample) * input_val
        else:
            input_1 = np.ones(nb_sample) * random.randint(0, 2 ** self.n_in - 1)
        print("Test at input =", int(input_1[0]))

        # print('Window size:', self.window_size)
        output = np.empty(input_1.size)
        filtered = np.empty(output.size)
        await RisingEdge(self.dut.clk)
        for i in range(input_1.size):
            output[i] = self.dut.data_o.value.integer * self.ratio_out_in
            filtered[i] = self.dut.v.value
            await FallingEdge(self.dut.clk)
            self.dut.data_i.value = int(
                input_1[i]  # pylint: disable=unsubscriptable-object
            )
            await RisingEdge(self.dut.clk)

        # filtered = moving_average(output, self.window_size)
        if plot:
            # time = np.arange(0, nb_sample) / self.sampling_freq
            # save(input_1, output, time, filtered, "dc")
            # s_d_plot(
            #     time=time,
            #     input_s=input_1,
            #     output=output,
            #     filter_s=filtered,
            #     title="DC analysis",
            # )

            fourier_analysis_1signal(
                output[input_1.size // 2 :],
                self.sampling_time,
                "output signal",
            )
            # fourier_analysis_no_centering(
            #     input_1[input_1.size // 2 :],
            #     filtered[input_1.size // 2 :],
            #     self.sampling_time,
            #     "filtered signal",
            # )
        diff = input_1[input_1.size // 2 :] - filtered[input_1.size // 2 :]
        print("Diff:", diff)
        delta_q = np.abs(diff).max()
        # print('Delta Q+:', diff.max(),'\nDelta Q-', diff.min(), '\nDelta Q:', delta_q)
        delta_i = 35 / (2 ** self.n_in - 1) * delta_q  # [mA]
        delta_p = delta_i ** 2 * 120  # [mW]
        delta_wl = 1e3 * 0.272 * delta_p  # [pm]
        print(
            "{:0.0f}: dq {:0.3f} Considering 35mA full range, delta {:0.3f} µA".format(
                input_1[0], delta_q, delta_i * 1e3
            )
            + "-> precision delta ~{:0.5f} pm".format(
                delta_wl
            )  # deltaI = Fullscale/nb_values * delta_quantisation
            # deltaP = R deltaI**2
            # deltaWL [pm] = 1e3 * resolution[nm/mW]*deltaP
            # WL : wavelength
        )
        print(
            "{:0.0f}: Considering wavelength linear : {:0.5f} pm".format(
                input_1[0], 10e3 / (2 ** self.n_in - 1) * delta_q
            )
        )
        # if plot:
        #     plt.figure()
        #     plt.plot(
        #         time[: -input_1.size // 2],
        #         diff,
        #     )
        #     plt.show()

        if input_val is None:
            return delta_q, input_1[0]
        return delta_q

    async def dc_tests(self):
        "perform multiple dc_test"
        nb_tests = 100
        input_vals = np.linspace(0, 2 ** self.n_in - 1, nb_tests, dtype=np.uint16)
        deltas = np.empty_like(input_vals)
        for i in range(nb_tests):
            deltas[i] = await self.dc_test(plot=False, input_val=input_vals[i])

        save_2(input_vals, deltas, "dc_deltas")
        plt.figure()
        plt.plot(input_vals, deltas)
        plt.grid()
        plt.show()

    async def create_vectors(self):
        "generate waveform that will be used with the arbritrary function generator"
        nb_sample = 65536  # maximum number of possible stored samples
        command = 32128  # 0b0111|1101|1000|0000
        ratio = 2047 / 15  # Max_amplitude / 15 = 2**4 -1
        self.dut.data_i.value = command
        output = np.empty(nb_sample, dtype=np.int)
        for i in range(nb_sample):
            await RisingEdge(self.dut.clk)
            output[i] = int(self.dut.data_o.value.integer * ratio)
        fourier_analysis_1signal(output, 25e-9, "Fourier")
        plt.show()
        np.savetxt(
            "vector_for_arbritrary_function_generator.csv", output, delimiter=",\n"
        )

    async def static_ramp_test(self, nb_test):
        """Test DC performances"""
        nb_points = 5000
        input_i = np.empty(nb_test)
        output = np.empty(nb_test)
        fig = plt.figure()
        axis_1 = fig.add_subplot(111)
        j = 0
        for test in range(nb_test):
            input_i[j] = test
            self.dut.data_i.value = test
            await Timer(round(nb_points / self.sampling_freq * 1e6), "us")
            output[j] = self.dut.v.value
            print(test, ":", output[j])
            j += 1
        axis_1.plot(input_i, "-r", label="input")
        axis_1.plot(output, "-g", label="output")
        axis_1.legend()
        axis_1.grid()
        axis_1.set_title("Ramp Mash")
        axis_1.set_xlabel("Sample")
        axis_1.set_ylabel("Amplitude [No unit]")
        plt.show()

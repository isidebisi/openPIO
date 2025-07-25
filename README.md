# openPIO
open-source HDL implementation of Raspberry Pi's PIO blocks

The project is still ongoing and not yet completely published. The original project is on the [private repository of the Telecomunnication and Circuits Lab at EPFL](https://tclgit.epfl.ch/semester-projects/25s-frei-open_source_pio)

See the report for more information

## PIO Module Topology


The core of the PIO design is organized as follows:


[pio.v](HDL/RTL/pio.v) \
├── [stateMachine.v](HDL/RTL/stateMachine.v) \
│   ├── [isr.v](HDL/RTL/isr.v) \
│   ├── [osr.v](HDL/RTL/osr.v) \
│   ├── [clockDivider.v](HDL/RTL/clockDivider.v) \
│   ├── [binaryOperations.v](HDL/RTL/binaryOperations.v) \
│   └── [instructionDecoder.v](HDL/RTL/instructionDecoder.v) \
├── [smGPIOMapper.v](HDL/RTL/smGPIOMapper.v) \
├── [prioritySorter.v](HDL/RTL/GPIOPrioritySorter.v) \
└── [instructionMemory.v](HDL/RTL/instructionMemory.v)


This hierarchy reflects the modular structure of the PIO, with clear separation between the main state machine, GPIO mapping, priority sorting, and instruction memory, as well as the internal components of the state machine. This is only for the PIO block itself without any integration in the IP-BUS project of the FPGA prototype.

---

#### HDL/RTL Folder Structure


[HDL/RTL/](HDL/RTL/) \
├── [binaryOperations.v](HDL/RTL/binaryOperations.v) \
├── [clockDivider.v](HDL/RTL/clockDivider.v) \
├── [gpio_interface.vhd](HDL/RTL/gpio_interface.vhd) \
├── [GPIOPrioritySorter.v](HDL/RTL/GPIOPrioritySorter.v) \
├── [instructionDecoder.v](HDL/RTL/instructionDecoder.v) \
├── [instructionMemory.v](HDL/RTL/instructionMemory.v) \
├── [isr.v](HDL/RTL/isr.v) \
├── [osr.v](HDL/RTL/osr.v) \
├── [pio.v](HDL/RTL/pio.v) \
├── [pioWrapper.vhd](HDL/RTL/pioWrapper.vhd) \
├── [smGPIOMapper.v](HDL/RTL/smGPIOMapper.v) \
├── [stateMachine.v](HDL/RTL/stateMachine.v) \
├── [top.vhd](HDL/RTL/top.vhd) \
├── [ipbus_clk_bridge.vhd](HDL/RTL/ipbus_clk_bridge.vhd) * \
├── [ipbus_decode_ipbus_pio.vhd](HDL/RTL/ipbus_decode_ipbus_pio.vhd) * \
├── [ipbus_pio.vhd](HDL/RTL/ipbus_pio.vhd) * \
└── [top_fpga_rmii_pio.vhd](HDL/RTL/top_fpga_rmii_pio.vhd) *


\* These four files are not personally authored. They are modified and used for the IP-BUS integration of the FPGA prototype.

---

## Simulation

Simulation was performed with Cocotb and Modelsim. The makefile was written for the internal infrastructure at EPFL.


The results can be shown with the following scripts:
- Windows: [`SHOW_SIM_RESULTS_WINDOWS.bat`](SHOW_SIM_RESULTS_WINDOWS.bat)
- Linux: [`SHOW_SIM_RESULTS_LINUX.sh`](SHOW_SIM_RESULTS_LINUX.sh)

All of the Cocotb Testbenches are in the folder [`HDL/TBENCH`](HDL/TBENCH/).

## FPGA Prototype

The FPGA Prototype was written with the PIO integrated into the IP-BUS project, adapted by Delphine Alliman (TCL at EPFL).

Delphine's IP-BUS project was created with Tape Out in mind. Therefore their repository (integrated here as a submodule) contains intellectual property under NDA.

This means, that at this point in time the vivado project is broken and not accessible for external people.


The implementation and synthesis reports of the 62.5 MHz PIO Prototype can be accessed under:

[`study/openPIO_IPbus_integrated/openPIO_IPbus_integrated.runs`](study/openPIO_IPbus_integrated/openPIO_IPbus_integrated.runs)

Note, that simulation (also with PIO integrated in IP-BUS) has exclusively been performed with Cocotb / Modelsim and not Vivado.


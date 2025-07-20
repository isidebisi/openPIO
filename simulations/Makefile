#==============================================================================
#
# AUTHOR: Andreas Toftegaard Kristensen, 
# adapted for cocotb, by ludo
# adapted for reading filelist by wenqing
#
# BRIEF: Makefile for Modelsim
#
# EXAMPLES:
# Compile the files in the directory
# > make cmp
#
#
# Simulate the design (with and without GUI)
# > make simulate
# > make simulate -GUI=1
#
#==============================================================================

vcom    =eda mgc vcom
vlib    =eda mgc vlib
vlog    =eda mgc vlog
vopt    =eda mgc vopt
vsim 	=eda mgc vsim 
sdfcom  =eda mgc sdfcom
vacom   =eda mgc vacom
valib   =eda mgc valib
vaspi   =eda mgc vaspi
vasim   =eda mgc vasim
vmap    =eda mgc vmap
wlf2vcd	=eda mgc wlf2vcd

#------------------------------------------------------------------------------
# DIRECTORIES
#------------------------------------------------------------------------------

# Main directories
RTL_DIR=HDL/RTL
TB_DIR =HDL/TBENCH
IP_DIR=./ip
GATE_DIR = ../gate
GEN_SCRIPTS = ../dut/gen_script
GENERATED_DIR = $(RTL_DIR)/res

IPBUS_SIM_DIR = ../24w-allimann-ethernet_ipbus/study/simulation/simulation_ipbus/
IP_RTL_DIR = $(IPBUS_SIM_DIR)../../../rtl/hdl/rmii/rtl
IP_TB_DIR = $(IPBUS_SIM_DIR)../tb/ipbus
LIBRTL = $(IPBUS_SIM_DIR)../../../rtl/ip/verilog-ethernet
IP_DIR = $(IPBUS_SIM_DIR)../../../rtl/ip
LIBCOMP = $(IPBUS_SIM_DIR)../../../rtl/ip/ipbus-firmware/components


# physical_umc_library = ./DLIB/umc_65nm_ll_uk65lscllmvbbr_sdf21_vlog

# Misc
DO_DIR     =./sim/do
SCRIPT_DIR =./sim/scripts
SCRATCH_DIR_LN=./scratch

# Output directories
export OUTPUT_DIR=$(SCRATCH_DIR_LN)/output



#------------------------------------------------------------------------------
# MODULES/LIBRARIES
#------------------------------------------------------------------------------

LIB =$(SCRATCH_DIR_LN)/work
#LIB = work

#------------------------------------------------------------------------------
# CLEAN
#------------------------------------------------------------------------------

# We use echo_sep as a global pre-requisite to always run it
# https://stackoverflow.com/questions/52718536/global-prerequisite-in-gnu-make-is-it-possible
-include echo_sep

#SIM_MODULE = instructionDecoder

#.PHONY: clean echo_sep
.PHONY: clean echo_sep
# Clean up the directory

clean:
	$(if $(filter $(SIM_MODULE),$(ALL_SIM_MODULES)),, $(error "Command $(SIM_MODULE) doesn't exist"))
	mkdir -p /scratch/$(USER)/modelsim/output/$(SIM_MODULE)
	rm -f $(SCRATCH_DIR_LN)/$(SIM_MODULE)/*
	ln -sf /scratch/$(USER)/modelsim $(SCRATCH_DIR_LN)
	rm -rf $(OUTPUT_DIR)/$(SIM_MODULE)
	mkdir -p $(OUTPUT_DIR)/$(SIM_MODULE)
	rm -f *.wlf *.vcd transcript *.mpf *.mti *.out *.in *.ini *.dbg
	rm -rf $(LIB)
	$(vlib) $(LIB)

#------------------------------------------------------------------------------
# BASE COMPILATION
#------------------------------------------------------------------------------

# Logfiles
VCOM_LOG=$(OUTPUT_DIR)/$(SIM_MODULE)/vcom_compile.log
VLOG_LOG=$(OUTPUT_DIR)/$(SIM_MODULE)/vlog_compile.log
VOPT_LOG=$(OUTPUT_DIR)/$(SIM_MODULE)/vopt.log
STAT_LOG=$(OUTPUT_DIR)/$(SIM_MODULE)/static_checks.txt

# COMMON_FLAGS: Common flags to simulation and compilation
# -64           Uses 64-bit executable (default is 32)
# -fsmdebug     Allows access to FSMs for debugging
# -hazards      Detects event order hazards (must also be used for vsim)
COMMON_FLAGS=-64 -fsmdebug 

# +acc enables design object visibility as optimization otherwise removes access (may make simulation slower)
# If <spec> is omitted, access is enabled for all objects.
# -novopt is deprecated, so +acc is needed for design visibility
VOPTARGS=+acc
# VOPTARGS=

# COMP_FLAGS: Compilation flags
# -fsmverbose   Displays information on detected FSMs
# -incr         Performs incremental compilation (REVISIT: Not supported in 2020.4 for VHDL)
# -lint         Issues warnings on lint-style static checks
# -nodebug      compiles and hides the internal data, plus the ports, of the lower-level design unit
# -nologo       Removes startupbanner
# -source       Displays line of source code before each error message
#
# -O0 | -O1 | -O4 | -O5   Controls the optimization level (increasing, -O4 is default)
#
COMP_FLAGS_VERILOG=$(COMMON_FLAGS) -incr -nologo -source $(VOPTARGS)

# COMP_FLAGS_VHDL=$(COMMON_FLAGS) -nologo -source $(VOPTARGS)
COMP_FLAGS_VHDL=$(COMMON_FLAGS) -nologo -source


# VLOG_FLAGS: Flags for compiling Verilog and SystemVerilog
# -sv         Enables SystemVerilog features and keywords (if .sv extension, MSIM uses SV)
# -sv12compat Ensure compatibility with keyword set of IEEE Std 1800-2012 (REVISIT: SystemVerilog 2017?)
# -logfile    Logfile name
# +incdir+    Specifies directories to search for files included with `include compiler directives
VLOG_FLAGS=$(COMP_FLAGS_VERILOG) -sv -sv12compat -lint=full -logfile $(VLOG_LOG) +incdir+$(RTL_DIR)

# VLOG_TB_FLAGS: Flags for compiling Verilog and SystemVerilog testbenches
# -assertdebug  Allows you to debug SVA/PSL objects when used with vsim -assertdebug
# +incdir       Searches directory for files (such as .svh)
VLOG_TB_FLAGS=$(VLOG_FLAGS) -assertdebug +incdir+$(TB_DIR)/utils

# VCOM_FLAGS: Flags for compiling VHDL code
# -2008               Enables VHDL 2008
# -check_synthesis    Performs some synthesis checks
# -logfile            Logfile name
# -explicit           Directs the compiler to resolve ambiguous function overloading by favoring the explicit function definition over the implicit function definition.
# VCOM_FLAGS=$(COMP_FLAGS_VHDL) -2008 -logfile $(VCOM_LOG)
VCOM_FLAGS=$(COMP_FLAGS_VHDL) -logfile $(VCOM_LOG)

# VCOM_TB_FLAGS: Flags for compiling VHDL testbenches
VCOM_TB_FLAGS=$(VCOM_FLAGS)

# b: Branch statistics
# c: Condition statistics
# e: Expression statistics
# s: Statement statistics
# t: Toggle statistics
# x: Extended toggle statistics (precendence over t)
# f: FSM statistics
COV_FLAGS=+cover=bcesxf

#------------------------------------------------------------------------------
# BASE SIMULATION
#------------------------------------------------------------------------------

# If no GUI, then set flags accordingly (-c for console -gui for GUI)
GUI=0
ifeq ($(GUI),0)
	GUI_FLAG=-c
else
	GUI_FLAG=-gui
endif

ifeq ($(GUI),0)
	DO_FLAG="$(TCL_FILE)"
else
	DO_FLAG="$(DO_FILE)"
endif

DO_FILE=$(DO_DIR)/default.do
TCL_FILE=$(SCRIPT_DIR)/default.tcl

SIM_LOG=$(OUTPUT_DIR)/$(SIM_MODULE)/simulation.log
WLF_FILE=$(OUTPUT_DIR)/$(SIM_MODULE)/vsim.wlf
VCD_FILE=$(OUTPUT_DIR)/$(SIM_MODULE)/vsim.vcd
SAIF_FILE=$(OUTPUT_DIR)/$(SIM_MODULE)/vsim.saif

# Arguments passed from the command line with GEN_ARGS=
GEN_ARGS =
# REVISIT: Check if these are actually doing anything
PLUSARGS=\
	+LOG_INFO_FILE=$(SIM_LOG) \
	+LOG_WARN_FILE=$(SIM_LOG) \
	+LOG_ERROR_FILE=$(SIM_LOG)

# SIM_FLAGS: Common flags for simulation
# -displaymsgmode Outputs messages to both the transcript and the WLF file
# -msgmode        Location(s) for the simulator to output elaboration and runtime
# -debugdb        (optional) Instructs Questa SIM to generate a database of connectivity information to use for post-sim debug in the Dataflow and Schematic windows.
# -donotcollapsepartiallydriven (optional) Prevents the collapse of partially driven and undriven output ports during optimization.
SIM_FLAGS=$(COMMON_FLAGS) -displaymsgmode both -msgmode both -t ns -logfile $(SIM_LOG) -wlf $(WLF_FILE) -debugdb
#SIM_FLAGS=$(COMMON_FLAGS) -displaymsgmode both -msgmode both -t ns -logfile $(SIM_LOG)

# VSIM_FLAGS: Flags for vsim
# VSIM_FLAGS=$(GUI_FLAG) $(SIM_FLAGS) -vopt -voptargs="$(VOPTARGS)" $(PLUSARGS) $(GEN_ARGS)
VSIM_FLAGS=$(GUI_FLAG) $(SIM_FLAGS) -vopt $(PLUSARGS) $(GEN_ARGS)

# VSIM_FLAGS_VHDL
# -nocollapse	 (optional) Disables the optimization of internal port map connections.
#------------------------------------------------------------------------------
# COCOTB COMMANDS
#------------------------------------------------------------------------------
#include $(shell cocotb-config --makefiles)/Makefile.inc
export LIBPYTHON_LOC := $(shell cocotb-config --libpython)
FLI_LIB := $(shell cocotb-config --lib-name-path fli questa)
export GPI_EXTRA := $(shell cocotb-config --lib-name-path vpi questa):cocotbvpi_entry_point

COCOTBTESTBENCH_DIR = $(TB_DIR)
export PYTHONPATH := $(COCOTBTESTBENCH_DIR):$(PYTHONPATH)

# orbgrand_test_dir = $(TB_DIR)/../../../../study_python/orbgrand
# export PYTHONPATH:= $(orbgrand_test_dir):$(PYTHONPATH)
#------------------------------------------------------------------------------
# MISC COMMANDS
#------------------------------------------------------------------------------

# Generates a .vcd file from the modelsim .wlf file to view in other editors
gen_vcd:
	$(wlf2vcd) $(WLF_FILE) -o $(VCD_FILE)

# Prints a seperator in red (-e option enables SYNTHsing escape sequences)
echo_sep:
	@echo -e "\n\e[1;33m======================================================================\e[0m\n"
echo_start_sim:
	@echo -e "\n\e[1;33m======================================================================\e[0m\n"
	@echo -e "\e[1;33mStarting Simulation          \e[0m\n"
	@echo -e "\e[1;33m======================================================================\e[0m\n"

# #------------------------------------------------------------------------------
# # file generation
# #------------------------------------------------------------------------------
# PARALLELISM_LOCAL_DETECTORS = 65

# $(GENERATED_DIR)/syndrome_lut.vhd: $(PYTHON_SCRIPTS)/syndrome_lut_generator.py
# 	python3 $< $(PYTHON_SCRIPTS)/matrixes/H_BCH_256_239.txt $@

# $(GENERATED_DIR)/syndrome_cam.vhd: $(PYTHON_SCRIPTS)/syndrome_cam_generator.py
# 	python3 $< $(PYTHON_SCRIPTS)/matrixes/H_BCH_256_239.txt $@

# # &: means one command generates mutliple files https://www.gnu.org/software/make/manual/html_node/Multiple-Targets.html

# $(GENERATED_DIR)/error_pattern_lut.vhd $(GENERATED_DIR)/error_detector_muxes.vhd $(GENERATED_DIR)/local_error_detectors.vhd $(GENERATED_DIR)/error_detector_and_mux.vhd &: $(PYTHON_SCRIPTS)/error_pattern_lut_generator.py $(PYTHON_SCRIPTS)/matrixes/error_pattern.txt
# 	python3 $(PYTHON_SCRIPTS)/error_pattern_lut_generator.py $(PYTHON_SCRIPTS)/matrixes/error_pattern.txt $(PARALLE) $(GENERATED_DIR)/error_pattern_lut.vhd $(GENERATED_DIR)/error_detector_muxes.vhd $(GENERATED_DIR)/local_error_detectors.vhd $(GENERATED_DIR)/error_detector_and_mux.vhd

# # $(GENERATED_DIR)/error_detectors_and_mux.vhd: $(PYTHON_SCRIPTS)/error_detectors_and_mux_generator.py
# # 	python3 $< $@


# generate_hdl: $(GENERATED_DIR)/syndrome_lut.vhd $(GENERATED_DIR)/error_pattern_lut.vhd $(GENERATED_DIR)/syndrome_cam.vhd $(GENERATED_DIR)/error_pattern_lut.vhd $(GENERATED_DIR)/error_detector_muxes.vhd $(GENERATED_DIR)/local_error_detectors.vhd $(GENERATED_DIR)/error_detector_and_mux.vhd

#------------------------------------------------------------------------------
# COMPILE
#------------------------------------------------------------------------------
## The VHDL source files of the design under verification (DUV).
VHDLSRCS = \
	$(RTL_DIR)/gpio_interface.vhd \
	$(RTL_DIR)/pioWrapper.vhd \
	$(RTL_DIR)/ipbus_decode_ipbus_pio.vhd\
	$(RTL_DIR)/ipbus_pio.vhd\
	$(RTL_DIR)/top.vhd

## The Verilog source files of the design under verification (DUV).
VLOGSRCS = \
	$(RTL_DIR)/instructionDecoder.v \
	$(RTL_DIR)/osr.v \
	$(RTL_DIR)/isr.v \
	$(RTL_DIR)/binaryOperations.v \
	$(RTL_DIR)/stateMachine.v \
	$(RTL_DIR)/instructionMemory.v \
	$(RTL_DIR)/smGPIOMapper.v \
	$(RTL_DIR)/GPIOPrioritySorter.v \
	$(RTL_DIR)/clockDivider.v \
	$(RTL_DIR)/pio.v

IP_VLOGSRCS = \
		$(IP_RTL_DIR)/rmii_mii_converter.sv\
		$(LIBRTL)/rtl/eth_mac_mii_fifo.v\
		$(LIBRTL)/rtl/eth_mac_mii.v\
		$(LIBRTL)/rtl/ssio_sdr_in.v\
		$(LIBRTL)/rtl/mii_phy_if.v\
		$(LIBRTL)/rtl/eth_mac_1g.v\
		$(LIBRTL)/rtl/axis_gmii_rx.v\
		$(LIBRTL)/rtl/axis_gmii_tx.v\
		$(LIBRTL)/rtl/lfsr.v\
		$(LIBRTL)/rtl/eth_axis_rx.v\
		$(LIBRTL)/rtl/eth_axis_tx.v\
		$(LIBRTL)/rtl/eth_arb_mux.v\
		$(LIBRTL)/lib/axis/rtl/arbiter.v\
		$(LIBRTL)/lib/axis/rtl/priority_encoder.v\
		$(LIBRTL)/lib/axis/rtl/axis_fifo.v\
		$(LIBRTL)/lib/axis/rtl/axis_async_fifo.v\
		$(LIBRTL)/lib/axis/rtl/axis_async_fifo_adapter.v

IP_VHDLSRCS = \
	$(LIBCOMP)/ipbus_core/firmware/hdl/ipbus_package.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/ipbus_trans_decl.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/transactor_if.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/transactor_sm.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/transactor_cfg.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/transactor.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/trans_arb.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_ipam_block.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_build_arp.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_build_ping.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_ipaddr_ipam.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_build_payload.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_build_resend.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_build_status.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_status_buffer.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_byte_sum.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_do_rx_reset.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_packet_parser.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_rxram_mux.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_dualportram.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_buffer_selector.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_rxram_shim.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_dualportram_rx.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_buffer_selector.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_rxtransactor_if_simple.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_dualportram_tx.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_buffer_selector.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_byte_sum.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_tx_mux.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_txtransactor_if_simple.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_clock_crossing_if.vhd\
	$(LIBCOMP)/ipbus_transport_udp/firmware/hdl/udp_if_flat.vhd\
	$(LIBCOMP)/ipbus_util/firmware/hdl/masters/ipbus_ctrl.vhd\
	$(LIBCOMP)/ipbus_slaves/firmware/hdl/ipbus_ram.vhd\
	$(LIBCOMP)/ipbus_slaves/firmware/hdl/ipbus_peephole_ram.vhd\
	$(LIBCOMP)/ipbus_core/firmware/hdl/ipbus_fabric_sel.vhd\
	$(LIBCOMP)/ipbus_slaves/firmware/hdl/ipbus_reg_types.vhd\
	$(LIBCOMP)/ipbus_slaves/firmware/hdl/ipbus_ctrlreg_v.vhd\
	$(LIBCOMP)/ipbus_slaves/firmware/hdl/ipbus_reg_v.vhd\
	$(LIBCOMP)/ipbus_util/firmware/hdl/ipbus_decode_ipbus_example.vhd\
	$(LIBCOMP)/ipbus_util/firmware/hdl/ipbus_example.vhd\
	$(LIBCOMP)/ipbus_util/firmware/hdl/payload_example.vhd\
	$(LIBCOMP)/ipbus_util/firmware/hdl/cdc_reset.vhd\
	$(LIBCOMP)/ipbus_util/firmware/hdl/ipbus_clk_bridge.vhd \
	$(IP_RTL_DIR)/converter_wrapper.vhd\
	$(IP_RTL_DIR)/eth_mac_mii_merge.vhd\
	$(IPBUS_SIM_DIR)../rtl/ipbus_clock_manager_custom.vhd\
	$(IPBUS_SIM_DIR)../rtl/infrastructure_top.vhd




cmp: 
	@echo "Compiling RTL sources."
	$(vlog) -work $(LIB) $(VLOG_FLAGS) $(VLOGSRCS)
	$(vlog) -work $(LIB) $(VLOG_FLAGS) $(IP_VLOGSRCS)
	$(vcom) -work $(LIB) $(VCOM_FLAGS) $(IP_VHDLSRCS)
	$(vcom) -work $(LIB) $(VCOM_FLAGS) $(VHDLSRCS)

#------------------------------------------------------------------------------
# COMPILE: TESTBENCHES
#------------------------------------------------------------------------------

# tb_macro: macro
# 	$(vcom) -work $(LIB) $(VCOM_TB_FLAGS) $(TB_GRAND_DIR)/macro_tb.vhd

##############################################################################################
# Netlist simulations
##############################################################################################

#eda mgc vsim $(CMD) $(RUN_ARGS) -do $(SIM_BUILD)/runsim.do $(PLUSARGS) $(SIM_OUTPUT_REDIRECT)
# set -o pipefail; MODULE=$(MODULE) TESTCASE=$(TESTCASE) COCOTB_TEST_FILTER=$(COCOTB_TEST_FILTER) TOPLEVEL=$(TOPLEVEL) \
# GPI_EXTRA=$(GPI_EXTRA) TOPLEVEL_LANG=$(TOPLEVEL_LANG) \


#------------------------------------------------------------------------------
# SIMULATE: TESTBENCHES
#------------------------------------------------------------------------------sim:

# ***ADD DOWN BELOW THE MODULES TO TEST***

ALL_SIM_MODULES = \
	instructionDecoder \
	osr \
	isr \
	binaryOperations \
	stateMachine \
	instructionMemory \
	smGPIOMapper \
	clockDivider \
	top

ALL_SIM_TARGETS = \
	$(foreach module,$(ALL_SIM_MODULES),run_$(module)) \
	

ALL_MAKE_TARGETS = \
	cmp \
	$(ALL_SIM_TARGETS) \
	show_results \

# Pattern rule to set SIM_MODULE dynamically
%: 
	$(eval SIM_MODULE=$@)
	@echo "Compiling $(SIM_MODULE)"
	$(MAKE) clean SIM_MODULE=$(SIM_MODULE) 
	$(MAKE) run_$@ SIM_MODULE=$(SIM_MODULE)


run_%: cmp
	set -o pipefail; \
	MODULE=$*_testcase \
	TOPLEVEL=$* \
	TOPLEVEL_LANG=verilog \
	GPI_EXTRA=$(GPI_EXTRA) \
	COCOTB_RESULTS_FILE=$(OUTPUT_DIR)/$*/cocotb_results.xml \
	$(vsim) $(VSIM_FLAGS) $(LIB).$* -do $(DO_FLAG) -do wave.do -foreign \"cocotb_init $(FLI_LIB)\" -t 1ps | tee $(SIM_LOG)


.PHONY: simulate_all
simulate_all: $(ALL_MAKE_TARGETS)


show_results:
	@python3 HDL/TBENCH/extract_results.py $(OUTPUT_DIR)
	
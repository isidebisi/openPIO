#------------------------------------------------------------------------------
#
# AUTHOR: Andreas Toftegaard Kristensen
#
# PURPOSE: Generic TCL script for Modelsim simulations
#
#------------------------------------------------------------------------------

# The wildcard command of Modelsim does not match unpacked arrays (memories), so  add this
# See: https://www.reddit.com/r/FPGA/comments/c3hork/why_do_unpacked_arrays_not_show_up_in_modelsim/
set WildcardFilter [lsearch -not -all -inline $WildcardFilter Memory];


# Adds the waveforms in the testbench (otherwise .wlf is empty, but slower) recursively for 2 levels
add wave -recursive -depth 3 /*;
# Adds all waveforms in the testbench recursively for all levels
# add wave -recursive /*;


set DefaultRadix hex;
# Ignore integer warnings from IEEE 'numeric_std' at time 0.
set NumericStdNoWarnings 1;
#run 0;
#set NumericStdNoWarnings 0;

run -all;

exit;

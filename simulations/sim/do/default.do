#------------------------------------------------------------------------------
#
# AUTHOR: Andreas Toftegaard Kristensen
#
# PURPOSE: Generic do file for simulations
#
#------------------------------------------------------------------------------


# Restart simulation and remove waves
#restart -f -nowave

# Configure waveforms to remove long names
# config wave -signalnamewidth 1
radix -hex

set NumericStdNoWarnings 1
set StdArithNoWarnings 1
# Adds the waveforms in the testbench (otherwise .wlf is empty, but slower) recursively for 2 levels
# add wave -recursive -depth 1 /*;

# Adds all waveforms in the testbench recursively for all levels
# add wave -recursive /*;


# Run until the end
# run -all


# Clock Configuration for Ethernet PHY

create_clock -period 20.000 -name ref_clk [get_ports rmii_ref_clk]
create_generated_clock -name mii_clk -source [get_ports rmii_ref_clk] -divide_by 2 [get_pins infra/converter/rmii_mii_converter_inst/mii_clk_reg*/Q]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets rmii_ref_clk_IBUF]


# Timing constraints for Ethernet PHY

# TODO add documentation 

## Output Delay Constraints
set_output_delay -clock ref_clk -max 7.000 [get_ports {rmii_tx_en {rmii_txd[*]}}]
set_output_delay -clock ref_clk -min -2.500 [get_ports {rmii_tx_en {rmii_txd[*]}}]

# Input Delay Constraint
set_input_delay -clock ref_clk -max 6.000 [get_ports {rmii_crs_dv {rmii_rxd[*]}}]
set_input_delay -clock ref_clk -min 1.500 [get_ports {rmii_crs_dv {rmii_rxd[*]}}]
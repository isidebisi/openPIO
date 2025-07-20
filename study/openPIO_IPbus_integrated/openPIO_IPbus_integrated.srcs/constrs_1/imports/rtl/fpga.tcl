# General configuration
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.COMPRESS true [current_design]

# System clocks
# 125 MHz Clock Setup
set_property -dict { PACKAGE_PIN H16 IOSTANDARD LVCMOS33 } [get_ports { sysclk }]; #IO_L13P_T2_MRCC_35 Sch=sysclk
create_clock -name sysclk -period 8.00 -waveform {0 4} [get_ports { sysclk }];

set_false_path -through [get_pins infra/clocks/rst_reg/Q]
#set_false_path -through [get_nets infra/clocks/nuke_i]
set_false_path -through [get_pins infra/clocks/rst_125_reg/Q]

# LED Configuration
set_property -dict {PACKAGE_PIN R14   IOSTANDARD LVCMOS33} [get_ports {leds[0]}]
set_property -dict {PACKAGE_PIN P14   IOSTANDARD LVCMOS33} [get_ports {leds[1]}]
set_property -dict {PACKAGE_PIN N16   IOSTANDARD LVCMOS33} [get_ports {leds[2]}]
set_property -dict {PACKAGE_PIN M14   IOSTANDARD LVCMOS33} [get_ports {leds[3]}]

set_false_path -to [get_ports {leds[*]}]

# Toggle switches
set_property -dict {PACKAGE_PIN M20 IOSTANDARD LVCMOS33} [get_ports {dip_sw[0]}]
set_property -dict {PACKAGE_PIN M19 IOSTANDARD LVCMOS33} [get_ports {dip_sw[1]}]

set_false_path -from [get_ports {dip_sw[*]}]

# 125MHz clock
create_generated_clock -name clk_125 -source [get_pins infra/clocks/mmcm/CLKIN1] [get_pins infra/clocks/mmcm/CLKOUT1]

# IPbus clock
create_generated_clock -name ipbus_clk -source [get_pins infra/clocks/mmcm/CLKIN1] [get_pins infra/clocks/mmcm/CLKOUT3]

# Other derived clocks
create_generated_clock -name clk_aux -source [get_pins infra/clocks/mmcm/CLKIN1] [get_pins infra/clocks/mmcm/CLKOUT4]

# Declare the oscillator clock, ipbus clock and aux clock as unrelated
set_clock_groups -asynchronous -group [get_clocks sysclk] -group [get_clocks clk_125] -group [get_clocks ipbus_clk] -group [get_clocks -include_generated_clocks [get_clocks clk_aux]]

# RMII signals
set_property -dict {PACKAGE_PIN U19 IOSTANDARD LVCMOS33} [get_ports {rmii_rxd[0]}]
set_property -dict {PACKAGE_PIN Y19 IOSTANDARD LVCMOS33} [get_ports {rmii_rxd[1]}]

set_property -dict {PACKAGE_PIN Y16 IOSTANDARD LVCMOS33} [get_ports {rmii_crs_dv}]

set_property -dict {PACKAGE_PIN Y18 IOSTANDARD LVCMOS33} [get_ports {rmii_txd[0]}]
set_property -dict {PACKAGE_PIN W19 IOSTANDARD LVCMOS33} [get_ports {rmii_txd[1]}]
set_property -dict {PACKAGE_PIN U18 IOSTANDARD LVCMOS33} [get_ports {rmii_tx_en}]

set_property -dict {PACKAGE_PIN W18 IOSTANDARD LVCMOS33} [get_ports {rmii_ref_clk}]

# GPIO Interface - Total of 32 GPIO inout pins

# AR8
set_property -dict {PACKAGE_PIN V17 IOSTANDARD LVCMOS33} [get_ports {gpio_io[0]}]   
# AR9
set_property -dict {PACKAGE_PIN V18 IOSTANDARD LVCMOS33} [get_ports {gpio_io[1]}]   
# RP7
set_property -dict {PACKAGE_PIN V6  IOSTANDARD LVCMOS33} [get_ports {gpio_io[2]}]   
# RP11
set_property -dict {PACKAGE_PIN U7  IOSTANDARD LVCMOS33} [get_ports {gpio_io[3]}]   
# RP13
set_property -dict {PACKAGE_PIN V7  IOSTANDARD LVCMOS33} [get_ports {gpio_io[4]}]   
# RP15
set_property -dict {PACKAGE_PIN U8  IOSTANDARD LVCMOS33} [get_ports {gpio_io[5]}]   
# RP19
set_property -dict {PACKAGE_PIN V8  IOSTANDARD LVCMOS33} [get_ports {gpio_io[6]}]   
# RP21
set_property -dict {PACKAGE_PIN V10 IOSTANDARD LVCMOS33} [get_ports {gpio_io[7]}]   
# RP23
set_property -dict {PACKAGE_PIN W10 IOSTANDARD LVCMOS33} [get_ports {gpio_io[8]}]   
# AR10
set_property -dict {PACKAGE_PIN T16 IOSTANDARD LVCMOS33} [get_ports {gpio_io[9]}]   
# RP29
set_property -dict {PACKAGE_PIN Y6  IOSTANDARD LVCMOS33} [get_ports {gpio_io[10]}]  
# RP31
set_property -dict {PACKAGE_PIN Y7  IOSTANDARD LVCMOS33} [get_ports {gpio_io[11]}]  
# RP33
set_property -dict {PACKAGE_PIN W8  IOSTANDARD LVCMOS33} [get_ports {gpio_io[12]}]  
# RP35
set_property -dict {PACKAGE_PIN Y8  IOSTANDARD LVCMOS33} [get_ports {gpio_io[13]}]  
# RP37
set_property -dict {PACKAGE_PIN W9  IOSTANDARD LVCMOS33} [get_ports {gpio_io[14]}]  
# AR11
set_property -dict {PACKAGE_PIN R17 IOSTANDARD LVCMOS33} [get_ports {gpio_io[15]}]  
# AR12
set_property -dict {PACKAGE_PIN P18 IOSTANDARD LVCMOS33} [get_ports {gpio_io[16]}]  
# RP12
set_property -dict {PACKAGE_PIN C20 IOSTANDARD LVCMOS33} [get_ports {gpio_io[17]}]  
# RP16
set_property -dict {PACKAGE_PIN W6  IOSTANDARD LVCMOS33} [get_ports {gpio_io[18]}]  
# AR13
set_property -dict {PACKAGE_PIN N17 IOSTANDARD LVCMOS33} [get_ports {gpio_io[19]}]  
# AR4
set_property -dict {PACKAGE_PIN V15 IOSTANDARD LVCMOS33} [get_ports {gpio_io[20]}]  
# RP24
set_property -dict {PACKAGE_PIN F19 IOSTANDARD LVCMOS33} [get_ports {gpio_io[21]}]  
# RP26
set_property -dict {PACKAGE_PIN F20 IOSTANDARD LVCMOS33} [get_ports {gpio_io[22]}]  
# RP28
set_property -dict {PACKAGE_PIN Y17 IOSTANDARD LVCMOS33} [get_ports {gpio_io[23]}]  
# RP32
set_property -dict {PACKAGE_PIN B20 IOSTANDARD LVCMOS33} [get_ports {gpio_io[24]}]  
# RP36
set_property -dict {PACKAGE_PIN B19 IOSTANDARD LVCMOS33} [get_ports {gpio_io[25]}]  
# RP38
set_property -dict {PACKAGE_PIN A20 IOSTANDARD LVCMOS33} [get_ports {gpio_io[26]}]  
# RP40
set_property -dict {PACKAGE_PIN Y9  IOSTANDARD LVCMOS33} [get_ports {gpio_io[27]}]  
# AR0
set_property -dict {PACKAGE_PIN T14 IOSTANDARD LVCMOS33} [get_ports {gpio_io[28]}]  
# AR1
set_property -dict {PACKAGE_PIN U12 IOSTANDARD LVCMOS33} [get_ports {gpio_io[29]}]  
# AR2
set_property -dict {PACKAGE_PIN U13 IOSTANDARD LVCMOS33} [get_ports {gpio_io[30]}]  
# AR3
set_property -dict {PACKAGE_PIN V13 IOSTANDARD LVCMOS33} [get_ports {gpio_io[31]}]  

# test out pin at AR5 --> T15
set_property -dict {PACKAGE_PIN T15 IOSTANDARD LVCMOS33} [get_ports {test_out}]  


# Set false path for GPIO pins to prevent timing issues
# This is common for GPIO pins that don't need to meet timing requirements
set_false_path -from [get_ports {gpio_io[*]}]
set_false_path -to [get_ports {gpio_io[*]}]
onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate -expand -group top /top/clk_125_i
add wave -noupdate -expand -group top /top/clk_200_i
add wave -noupdate -expand -group top /top/clk_32_i
add wave -noupdate -expand -group top /top/rst_i
add wave -noupdate -expand -group top /top/leds
add wave -noupdate -expand -group top /top/dip_sw
add wave -noupdate -expand -group top /top/rmii_rxd
add wave -noupdate -expand -group top /top/rmii_rx_er
add wave -noupdate -expand -group top /top/rmii_crs_dv
add wave -noupdate -expand -group top /top/rmii_txd
add wave -noupdate -expand -group top /top/rmii_tx_en
add wave -noupdate -expand -group top /top/rmii_ref_clk
add wave -noupdate -expand -group top /top/phy_rst
add wave -noupdate -expand -group top /top/rgmii_mdio_a
add wave -noupdate -expand -group top /top/clk_ipb
add wave -noupdate -expand -group top /top/rst_ipb
add wave -noupdate -expand -group top /top/clk_aux
add wave -noupdate -expand -group top /top/rst_aux
add wave -noupdate -expand -group top /top/nuke
add wave -noupdate -expand -group top /top/soft_rst
add wave -noupdate -expand -group top /top/phy_rst_e
add wave -noupdate -expand -group top /top/userled
add wave -noupdate -expand -group top /top/mac_addr
add wave -noupdate -expand -group top /top/ip_addr
add wave -noupdate -expand -group top -expand /top/ipb_out
add wave -noupdate -expand -group top /top/ipb_in
add wave -noupdate -expand -group pio0 /top/payload/pio0/clk
add wave -noupdate -expand -group pio0 /top/payload/pio0/reset
add wave -noupdate -expand -group pio0 -childformat {{/top/payload/pio0/ipbus_in.ipb_wdata -radix binary}} -expand -subitemconfig {/top/payload/pio0/ipbus_in.ipb_wdata {-height 17 -radix binary}} /top/payload/pio0/ipbus_in
add wave -noupdate -expand -group pio0 /top/payload/pio0/ipbus_out
add wave -noupdate -expand -group pio0 /top/payload/pio0/in_strobe
add wave -noupdate -expand -group pio0 /top/payload/pio0/in_writeNotRead
add wave -noupdate -expand -group pio0 /top/payload/pio0/in_address
add wave -noupdate -expand -group pio0 /top/payload/pio0/in_data
add wave -noupdate -expand -group pio0 /top/payload/pio0/out_data
add wave -noupdate -expand -group pio0 /top/payload/pio0/out_ack
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/clk
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/reset
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/in_strobe
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/in_writeNotRead
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/in_address
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/in_data
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/out_data
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/out_ack
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/reg_writeData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/next_writeData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/reg_CTRL
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/next_CTRL
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm0_iMemReadAddress
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm1_iMemReadAddress
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm2_iMemReadAddress
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm3_iMemReadAddress
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/pio_iMemReadAddress
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm0_iMemData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm1_iMemData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm2_iMemData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm3_iMemData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/pio_iMemData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/iMemWriteAddress
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/iMemWriteData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/iMemWriteEnable
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_out_dataRXFifo
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_out_outSetData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_out_regPC
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_out_outReg_sideSetData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_outSetEnable
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_outNotSet
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_outSetPinsNotPindirs
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_out_TXFifoDataAck
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_out_RXFifoDataValid
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_outReg_sideSetEnable
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/sm_inData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/smGPIOMapper_out_pinsWriteData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/smGPIOMapper_out_pinsWriteMask
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/smGPIOMapper_out_pinDirsWriteData
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/smGPIOMapper_out_pinDirsWriteMask
add wave -noupdate -expand -group pioVerilog /top/payload/pio0/verilog_pio_inst/k
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/clk
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/reset
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/writeAddress
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm0Address
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm1Address
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm2Address
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm3Address
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/pioAddress
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/writeData
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/writeEnable
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm0Data
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm1Data
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm2Data
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/sm3Data
add wave -noupdate -expand -group instructionMemory /top/payload/pio0/verilog_pio_inst/iMem/pioData
add wave -noupdate {/top/payload/pio0/verilog_pio_inst/iMem/regMemory[0]}
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {13387936 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 341
configure wave -valuecolwidth 201
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns
update
WaveRestoreZoom {13308170 ps} {13507831 ps}

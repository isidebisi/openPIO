--- verilog ethernet wrapper
-- Author: Delphine Allimann
-- EPFL - TCL Jan 2025

library ieee;
use ieee.std_logic_1164.all;

entity eth_mac_mii_merge is
	port(
		clk125: in std_logic;
		clk200: in std_logic;
		rst:    in std_logic;

        mii_rx_clk : in  std_logic;
        mii_rxd    : in  std_logic_vector(3 downto 0);
        mii_rx_dv  : in  std_logic;
        mii_rx_er  : in  std_logic;
        mii_tx_clk : in  std_logic;
        mii_txd    : out std_logic_vector(3 downto 0);
        mii_tx_en  : out std_logic;

		tx_data:  in  std_logic_vector(7 downto 0);
		tx_valid: in  std_logic;
		tx_last:  in  std_logic;
		tx_error: in  std_logic;
		tx_ready: out std_logic;
		rx_data:  out std_logic_vector(7 downto 0);
		rx_valid: out std_logic;
		rx_last:  out std_logic;
		rx_error: out std_logic;
		status:   out std_logic_vector(3 downto 0)
	);

end eth_mac_mii_merge;

architecture rtl of eth_mac_mii_merge is 

    component eth_mac_mii_fifo
        generic (
            TARGET : string;
            CLOCK_INPUT_STYLE : string;
            AXIS_DATA_WIDTH : natural;
            AXIS_KEEP_ENABLE : std_logic;
            AXIS_KEEP_WIDTH : natural;
            ENABLE_PADDING : std_logic;
            MIN_FRAME_LENGTH : natural;
            TX_FIFO_DEPTH : natural;
            TX_FIFO_RAM_PIPELINE : natural;
            TX_FRAME_FIFO : std_logic;
            TX_DROP_OVERSIZE_FRAME :std_logic;
            TX_DROP_BAD_FRAME : std_logic;
            TX_DROP_WHEN_FULL : std_logic;
            RX_FIFO_DEPTH : natural;
            RX_FIFO_RAM_PIPELINE : natural;
            RX_FRAME_FIFO : std_logic;
            RX_DROP_OVERSIZE_FRAME :std_logic;
            RX_DROP_BAD_FRAME : std_logic;
            RX_DROP_WHEN_FULL : std_logic
        );
        port (
            rst         : in std_logic;
            logic_clk   : in std_logic;  
            logic_rst   : in std_logic; 

            -- AXI input 
            tx_axis_tdata   : in  std_logic_vector(AXIS_DATA_WIDTH-1 downto 0);
            tx_axis_tkeep   : in  std_logic_vector(AXIS_KEEP_WIDTH-1 downto 0);
            tx_axis_tvalid  : in  std_logic;
            tx_axis_tready  : out std_logic;
            tx_axis_tlast   : in  std_logic;
            tx_axis_tuser   : in  std_logic;

            -- AXI output
            rx_axis_tdata   : out std_logic_vector(AXIS_DATA_WIDTH-1 downto 0);
            rx_axis_tkeep   : out std_logic_vector(AXIS_KEEP_WIDTH-1 downto 0);
            rx_axis_tvalid  : out std_logic;
            rx_axis_tready  : in  std_logic;
            rx_axis_tlast   : out std_logic;
            rx_axis_tuser   : out std_logic;

            --MII interface
            mii_rx_clk : in  std_logic;
            mii_rxd    : in  std_logic_vector(3 downto 0);
            mii_rx_dv  : in  std_logic;
            mii_rx_er  : in  std_logic;
            mii_tx_clk : in  std_logic;
            mii_txd    : out std_logic_vector(3 downto 0);
            mii_tx_en  : out std_logic;

            --Status 
            tx_error_underflow  : out std_logic;
            tx_fifo_overflow    : out std_logic;
            tx_fifo_bad_frame   : out std_logic;
            tx_fifo_good_frame  : out std_logic;
            rx_error_bad_frame  : out std_logic;
            rx_error_bad_fcs    : out std_logic;
            rx_fifo_overflow    : out std_logic;
            rx_fifo_bad_frame   : out std_logic;
            rx_fifo_good_frame  : out std_logic;

            --Configuration
            cfg_ifg         : in std_logic_vector(7 downto 0);
            cfg_tx_enable   : in std_logic;
            cfg_rx_enable   : in std_logic
        );
    end component;
    
begin

    rx_error <= '0';
    
    eth_mac_inst : eth_mac_mii_fifo
    generic map(
            TARGET => "GENERIC",
            CLOCK_INPUT_STYLE => "BUFR", 
            AXIS_DATA_WIDTH => 8, 
            AXIS_KEEP_ENABLE => '0', 
            AXIS_KEEP_WIDTH => 1, 
            ENABLE_PADDING => '1',
            MIN_FRAME_LENGTH => 64,
            TX_FIFO_DEPTH => 4096,
            TX_FIFO_RAM_PIPELINE => 1,
            TX_FRAME_FIFO => '1',
            TX_DROP_OVERSIZE_FRAME => '1',
            TX_DROP_BAD_FRAME => '1',
            TX_DROP_WHEN_FULL => '0',
            RX_FIFO_DEPTH => 4096,
            RX_FIFO_RAM_PIPELINE => 1,
            RX_FRAME_FIFO => '1',
            RX_DROP_OVERSIZE_FRAME =>'1',
            RX_DROP_BAD_FRAME => '1',
            RX_DROP_WHEN_FULL => '0'
        )
        port map( 
            rst         => rst,
            logic_clk   => clk125,
            logic_rst   => rst,

            tx_axis_tdata   => tx_data,
            tx_axis_tkeep   => "0",
            tx_axis_tvalid  => tx_valid,
            tx_axis_tready  => tx_ready,
            tx_axis_tlast   => tx_last,
            tx_axis_tuser   => '0',

            rx_axis_tdata   => rx_data,
            rx_axis_tvalid  => rx_valid,
            rx_axis_tready  => '1',
            rx_axis_tlast   => rx_last,

            mii_rx_clk      => mii_rx_clk,
            mii_rxd         => mii_rxd,
            mii_rx_dv       => mii_rx_dv,
            mii_rx_er       => mii_rx_er,
            mii_tx_clk      => mii_tx_clk,
            mii_txd         => mii_txd,
            mii_tx_en       => mii_tx_en,
            
            cfg_ifg         => X"0C",
            cfg_tx_enable   => '1',
            cfg_rx_enable   => '1'
        );
end rtl;
library IEEE;
use IEEE.STD_LOGIC_1164.all;

use work.ipbus.all;

entity pynq_rmii_infra is
    generic (
        CLK_AUX_FREQ : real := 40.0;     -- Default: 40 MHz clock - LHC
        DHCP_not_RARP : std_logic := '0' -- Default use RARP not DHCP for now...
        );
    port(
        sysclk       : in  std_logic;   -- 125MHz board crystal clock
        clk_ipb_o    : out std_logic;   -- IPbus clock
        rst_ipb_o    : out std_logic;
        clk_125_o    : out std_logic;
        clk_50_o     : out std_logic;
        rst_125_o    : out std_logic;
        clk_aux_o    : out std_logic;   -- 40MHz generated clock
        rst_aux_o    : out std_logic;
        nuke         : in  std_logic;   -- The signal of doom
        soft_rst     : in  std_logic;   -- The signal of lesser doom
        leds         : out std_logic_vector(1 downto 0);   -- status LEDs
        rmii_rxd     : in  std_logic_vector(1 downto 0);   -- RMII interface to ethernet PHY
        rmii_rx_er   : in  std_logic;
        rmii_crs_dv  : in  std_logic;
        rmii_txd     : out std_logic_vector(1 downto 0);
        rmii_tx_en   : out std_logic;
        rmii_ref_clk : in  std_logic;
        mac_addr     : in  std_logic_vector(47 downto 0);  -- MAC address
        ip_addr      : in  std_logic_vector(31 downto 0);  -- IP address
        ipam_select  : in  std_logic;      -- enable RARP or DHCP
        ipb_in       : in  ipb_rbus;    -- ipbus
        ipb_out      : out ipb_wbus
        );

end pynq_rmii_infra;

architecture rtl of pynq_rmii_infra is

    signal clk125_fr, clk125, clk200, clk_50, clk_ipb, clk_ipb_i, locked, rst125, rst_ipb, rst_ipb_ctrl, rst_eth, onehz, pkt : std_logic;
    signal mac_tx_data, mac_rx_data                                                                                  : std_logic_vector(7 downto 0);
    signal mac_tx_valid, mac_tx_last, mac_tx_error, mac_tx_ready, mac_rx_valid, mac_rx_last, mac_rx_error            : std_logic;
    signal led_p                                                                                                     : std_logic_vector(0 downto 0);
    signal mii_rx_clk, mii_rx_dv, mii_rx_er, mii_tx_clk, mii_tx_en, mii_tx_er                                        : std_logic;
    signal mii_rxd, mii_txd                                                                                          : std_logic_vector(3 downto 0);



begin

--      DCM clock generation for internal bus, ethernet

    clocks : entity work.clocks_7s_extphy
        generic map(
            CLK_AUX_FREQ => CLK_AUX_FREQ,
            CLK_FR_FREQ => 125.00
            )
        port map(
            sysclk        => sysclk,
            clko_125      => clk125,
            clko_200      => clk200,
            clko_50       => clk_50,
            clko_ipb      => clk_ipb_i,
            locked        => locked,
            nuke          => nuke,
            soft_rst      => soft_rst,
            rsto_125      => rst125,
            rsto_ipb      => rst_ipb,
            rsto_ipb_ctrl => rst_ipb_ctrl,
            onehz         => onehz
            );

    clk_ipb   <= clk_ipb_i;  -- Best to align delta delays on all clocks for simulation
    clk_ipb_o <= clk_ipb_i;
    rst_ipb_o <= rst_ipb;
    clk_125_o <= clk125;
    clk_50_o  <= clk_50;
    rst_125_o <= rst125;

    stretch : entity work.led_stretcher
        generic map(
            WIDTH => 1
            )
        port map(
            clk  => clk125,
            d(0) => pkt,
            q    => led_p
            );

    leds <= (led_p(0), locked and onehz);

-- Ethernet MAC core and PHY interface

    converter : entity work.converter_wrapper
        port map(
            rst => rst125,

            mii_rx_clk => mii_rx_clk,
            mii_rxd    => mii_rxd,
            mii_rx_dv  => mii_rx_dv,
            mii_rx_er  => mii_rx_er, 
            mii_tx_clk => mii_tx_clk, 
            mii_txd    => mii_txd, 
            mii_tx_en  => mii_tx_en,
            mii_tx_er  => mii_tx_er, 
    
            rmii_rxd    => rmii_rxd, 
            rmii_rx_er  => rmii_rx_er, 
            rmii_crs_dv => rmii_crs_dv,
            rmii_txd    => rmii_txd,
            rmii_tx_en  => rmii_tx_en,
    
            rmii_ref_clk => rmii_ref_clk
        );


    eth : entity work.eth_mac_mii_merge
        port map(
            clk125       => clk125,
            clk200       => clk200,
            rst          => rst125,
            mii_rx_clk   => mii_rx_clk,
            mii_rxd      => mii_rxd,
            mii_rx_dv    => mii_rx_dv,
            mii_rx_er    => mii_rx_er,
            mii_tx_clk   => mii_tx_clk,
            mii_txd      => mii_txd,
            mii_tx_en    => mii_tx_en,
            tx_data      => mac_tx_data,
            tx_valid     => mac_tx_valid,
            tx_last      => mac_tx_last,
            tx_error     => mac_tx_error,
            tx_ready     => mac_tx_ready,
            rx_data      => mac_rx_data,
            rx_valid     => mac_rx_valid,
            rx_last      => mac_rx_last,
            rx_error     => mac_rx_error
            );

-- ipbus control logic

    ipbus : entity work.ipbus_ctrl
        generic map(
            DHCP_RARP => DHCP_not_RARP
        )
        port map(
            mac_clk      => clk125,
            rst_macclk   => rst125,
            ipb_clk      => clk_ipb,
            rst_ipb      => rst_ipb_ctrl,
            mac_rx_data  => mac_rx_data,
            mac_rx_valid => mac_rx_valid,
            mac_rx_last  => mac_rx_last,
            mac_rx_error => mac_rx_error,
            mac_tx_data  => mac_tx_data,
            mac_tx_valid => mac_tx_valid,
            mac_tx_last  => mac_tx_last,
            mac_tx_error => mac_tx_error,
            mac_tx_ready => mac_tx_ready,
            ipb_out      => ipb_out,
            ipb_in       => ipb_in,
            mac_addr     => mac_addr,
            ip_addr      => ip_addr,
            ipam_select  => ipam_select,
            pkt          => pkt
            );

end rtl;

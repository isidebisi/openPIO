-- Modified by Ismael Frei, TCL, 2025
-- Modified by Delphine Alliman, TCL, 2025

---------------------------------------------------------------------------------
--
--   Copyright 2017 - Rutherford Appleton Laboratory and University of Bristol
--
--   Licensed under the Apache License, Version 2.0 (the "License");
--   you may not use this file except in compliance with the License.
--   You may obtain a copy of the License at
--
--       http://www.apache.org/licenses/LICENSE-2.0
--
--   Unless required by applicable law or agreed to in writing, software
--   distributed under the License is distributed on an "AS IS" BASIS,
--   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--   See the License for the specific language governing permissions and
--   limitations under the License.
--
--                                     - - -
--
--   Additional information about ipbus-firmare and the list of ipbus-firmware
--   contacts are available at
--
--       https://ipbus.web.cern.ch/ipbus
--
---------------------------------------------------------------------------------


-- Top-level design for ipbus demo
--
-- This version is for simulation
--
-- You must edit this file to set the IP and MAC addresses
--


library IEEE;
use IEEE.STD_LOGIC_1164.all;
-- Library UNISIM;
-- use UNISIM.vcomponents.bufg;

use work.ipbus.all;

entity top is generic (
	ENABLE_DHCP  : std_logic := '0'; -- Default is build with support for RARP rather than DHCP
	USE_IPAM     : std_logic := '0'; -- Default is no, use static IP address as specified by ip_addr below
	MAC_ADDRESS  : std_logic_vector(47 downto 0) := X"0060d7c0ffee"-- Careful here, arbitrary addresses do not always work
	);
	port (
    -- sysclk       : in  std_logic;
    clk_125_i    : in  std_logic;   -- 125MHz clock 
    clk_200_i    : in  std_logic;   -- 200MHz clock
    clk_32_i     : in  std_logic;   -- 32MHz clock
    rst_i        : in  std_logic;   -- Asynchronous reset
    leds         : out std_logic_vector(3 downto 0);  -- status LEDs
    dip_sw       : in  std_logic_vector(3 downto 0);  -- switches
    rmii_rxd     : in  std_logic_vector(1 downto 0);
    rmii_rx_er   : in  std_logic;
    rmii_crs_dv  : in  std_logic;
    rmii_txd     : out std_logic_vector(1 downto 0);
    rmii_tx_en   : out std_logic;
    rmii_ref_clk : in  std_logic;
    phy_rst      : out std_logic;
    rgmii_mdio_a : inout std_logic;
    
    -- GPIO signals
    gpio_io   : inout std_logic_vector(31 downto 0)
    );

end top;

architecture rtl of top is

    signal clk_ipb, rst_ipb, clk_aux, rst_aux, nuke, soft_rst, phy_rst_e, userled : std_logic;
    signal mac_addr                                                               : std_logic_vector(47 downto 0);
    signal ip_addr                                                                : std_logic_vector(31 downto 0);
    signal ipb_out                                                                : ipb_wbus;
    signal ipb_in                                                                 : ipb_rbus;
    signal in_gpio, out_gpio, dir_gpio                                            : std_logic_vector(31 downto 0);
begin

-- Infrastructure

    infra : entity work.infrastructure
		generic map(
			DHCP_not_RARP => ENABLE_DHCP
		)
        port map(
            -- sysclk       => sysclk,
            clk_125_i    => clk_125_i,
            clk_200_i    => clk_200_i,
            clk_32_i     => clk_32_i,
            rst_i        => rst_i,
            clk_ipb_o    => clk_ipb,
            rst_ipb_o    => rst_ipb,
            rst_125_o    => phy_rst_e,
            clk_aux_o    => clk_aux,
            rst_aux_o    => rst_aux,
            nuke         => nuke,
            soft_rst     => soft_rst,
            -- leds         => leds(1 downto 0),
            rmii_rxd     => rmii_rxd,
            rmii_rx_er   => rmii_rx_er,
            rmii_crs_dv  => rmii_crs_dv,
            rmii_txd     => rmii_txd,
            rmii_tx_en   => rmii_tx_en,
            rmii_ref_clk => rmii_ref_clk,
            mac_addr     => mac_addr,
            ip_addr      => ip_addr,
            ipam_select  => USE_IPAM,
            ipb_in       => ipb_in,
            ipb_out      => ipb_out
            );

    leds(3 downto 2) <= '0' & userled;
    --phy_rst          <= not phy_rst_e;
    phy_rst          <= phy_rst_e;

    mac_addr <= MAC_ADDRESS;
	ip_addr <= X"c0a80203"; -- 192.168.2.3

-- ipbus slaves live in the entity below, and can expose top-level ports
-- The ipbus fabric is instantiated within.

    payload : entity work.ipbus_pio
        port map(
            ipb_clk  => clk_ipb,
            clk_125  => clk_125_i,
            ipb_rst  => rst_i,
            ipb_in   => ipb_out,
            ipb_out  => ipb_in,
            nuke     => nuke,
            soft_rst => soft_rst,
            userled  => userled,
            in_gpio => in_gpio,
            out_gpio => out_gpio,
            dir_gpio => dir_gpio
            );


    -- GPIO interface
    gpio_interface : entity work.gpio_interface
        port map(
            clk       => clk_125_i,
            gpio_io   => gpio_io,
            gpio_out  => out_gpio,
            gpio_dir  => dir_gpio,
            gpio_in   => in_gpio
        );
end rtl;

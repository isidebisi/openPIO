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


-- ipbus_pio
--
-- selection of different IPBus slaves without actual function,
-- just for performance evaluation of the IPbus/uhal system
--
-- Modified by Ismael Frei, Mai 2025
-- based on Kristian Harder, March 2014
-- based on code by Dave Newbold, February 2011

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use work.ipbus.all;
use work.ipbus_reg_types.all;
use work.ipbus_decode_ipbus_pio.all;

entity ipbus_pio is
	port(
		ipb_clk: in std_logic;
		clk_125: in std_logic;
		ipb_rst: in std_logic;
		ipb_in: in ipb_wbus;
		status: in std_logic_vector(31 downto 0) := X"abcdfedc";
		ipb_out: out ipb_rbus;
		nuke: out std_logic;
		soft_rst: out std_logic;
		userled: out std_logic;
		userled2: out std_logic;
		-- GPIO signals
        in_gpio: in std_logic_vector(31 downto 0);
        out_gpio: out std_logic_vector(31 downto 0);
        dir_gpio: out std_logic_vector(31 downto 0)
	);

end ipbus_pio;

architecture rtl of ipbus_pio is

	signal ipbw: ipb_wbus_array(N_SLAVES - 1 downto 0);
	signal ipbr: ipb_rbus_array(N_SLAVES - 1 downto 0);
	signal ctrl, stat: ipb_reg_v(0 downto 0);
    signal sig_out_gpio, sig_dir_gpio: std_logic_vector(31 downto 0);
	signal not_rst: std_logic;
	signal s_clk : std_logic;
	signal s_rst : std_logic;
	signal s_ipbw : ipb_wbus;
	signal s_ipbr : ipb_rbus;
begin

-- ipbus address decode
		
	fabric: entity work.ipbus_fabric_sel
    generic map(
    	NSLV => N_SLAVES,
    	SEL_WIDTH => IPBUS_SEL_WIDTH)
    port map(
      ipb_in => ipb_in,
      ipb_out => ipb_out,
      sel => ipbus_sel_ipbus_pio(ipb_in.ipb_addr),
      ipb_to_slaves => ipbw,
      ipb_from_slaves => ipbr
    );

-- pio0 slave 0: id / rst reg
	not_rst <= not ipb_rst;

	pio0: entity work.pioWrapper
		port map(
			clk => clk_125,
			reset => not_rst,
			ipbus_in => s_ipbw,
			ipbus_out => s_ipbr,
			in_gpio => in_gpio,
			out_gpio => sig_out_gpio,
			dir_gpio => sig_dir_gpio
		);
		
		stat(0) <= status;
		soft_rst <= ctrl(0)(0);
		nuke <= ctrl(0)(1);
		userled <= sig_out_gpio(0);
		userled2 <= sig_dir_gpio(0);
		out_gpio <= sig_out_gpio;
		dir_gpio <= sig_dir_gpio;

	clk_bridge : entity work.ipbus_clk_bridge
		port map (
			m_clk     => ipb_clk,
			m_rst     => ipb_rst,
			m_ipb_in  => ipbw(N_SLV_PIO0),
			m_ipb_out => ipbr(N_SLV_PIO0),

			s_clk     => clk_125,
			s_rst     => ipb_rst,
			s_ipb_out => s_ipbw,
			s_ipb_in  => s_ipbr
		);	

end rtl;
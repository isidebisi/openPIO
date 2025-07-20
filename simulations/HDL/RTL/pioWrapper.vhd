-- pioWrapper.vhd
-- Author: Ismael Frei
-- EPFL TCL 2025


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use work.ipbus.all;

entity pioWrapper is
    port(
        clk: in std_logic;
        reset: in std_logic;
        ipbus_in: in ipb_wbus;
        ipbus_out: out ipb_rbus;
        -- GPIO signals
        in_gpio: in std_logic_vector(31 downto 0);
        out_gpio: out std_logic_vector(31 downto 0);
        dir_gpio: out std_logic_vector(31 downto 0)
    );
end pioWrapper;

architecture rtl of pioWrapper is

    -- Internal signals to map ipbus to native signals
    signal in_strobe: std_logic;
    signal in_writeNotRead: std_logic;
    signal in_address: std_logic_vector(31 downto 0);
    signal in_data: std_logic_vector(31 downto 0);
    signal out_data: std_logic_vector(31 downto 0);
    signal out_ack: std_logic;

begin

    -- Map ipbus signals to native signals
    in_strobe <= ipbus_in.ipb_strobe;
    in_writeNotRead <= ipbus_in.ipb_write;
    in_address <= std_logic_vector(resize(unsigned(ipbus_in.ipb_addr), 32));
    in_data <= ipbus_in.ipb_wdata;

    -- Map native signals to ipbus signals
    ipbus_out.ipb_rdata <= out_data;
    ipbus_out.ipb_ack <= out_ack;
    ipbus_out.ipb_err <= '0';

    -- Instantiate the Verilog module
    verilog_pio_inst: entity work.pio
        port map (
            clk => clk,
            reset => reset,
            in_strobe => in_strobe,
            in_writeNotRead => in_writeNotRead,
            in_address => in_address(11 downto 0),
            in_data => in_data,
            out_data => out_data,
            out_ack => out_ack,
            in_GPIO => in_gpio,
            out_GPIOWriteData => out_gpio,
            out_GPIODirWriteData => dir_gpio
        );

end rtl;
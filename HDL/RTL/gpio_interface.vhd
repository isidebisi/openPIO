library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity gpio_interface is
  port (
    clk       : in  std_logic;
    -- external pads
    gpio_io   : inout std_logic_vector(31 downto 0);
    -- from your core
    gpio_out  : in  std_logic_vector(31 downto 0);
    gpio_dir  : in  std_logic_vector(31 downto 0);
    -- synchronized inputs
    gpio_in   : out std_logic_vector(31 downto 0)
  );
end entity;

architecture rtl of gpio_interface is
  -- raw pad input (combinational readback)
  signal gpio_pad : std_logic_vector(31 downto 0);
  -- 2‐stage synchronizer
  signal sync_ff1 : std_logic_vector(31 downto 0);
  signal sync_ff2 : std_logic_vector(31 downto 0);
begin

  ----------------------------------------------------------------
  -- 1) Tri‐state driver: if dir='1' drive out, else high-Z
  ----------------------------------------------------------------
  gen_tri: for i in 0 to 31 generate
    gpio_io(i) <= gpio_out(i) when gpio_dir(i) = '1' else 'Z';
    -- read whatever is actually on the pad
    gpio_pad(i) <= gpio_io(i);
  end generate;

  ----------------------------------------------------------------
  -- 2) Two‐stage synchronizer on the pad readback
  ----------------------------------------------------------------
  sync_process: process(clk)
  begin
    if rising_edge(clk) then
      sync_ff1 <= gpio_pad;
      sync_ff2 <= sync_ff1;
    end if;
  end process;

  -- export the clean input vector
  gpio_in <= sync_ff2;

end architecture;

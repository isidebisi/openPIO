---------------------------------------------------------------------------------
-- Address decode logic for IPbus fabric.
--
-- This file has been AUTOGENERATED from the address table - do not
-- hand edit.
--
-- We assume the synthesis tool is clever enough to recognise
-- exclusive conditions in the if statement.
---------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package ipbus_decode_ipbus_pio is

-- START automatically generated VHDL (Mon May 19 12:03:12 2025)
  constant IPBUS_SEL_WIDTH: positive := 1;
-- END automatically generated VHDL

  subtype ipbus_sel_t is std_logic_vector(IPBUS_SEL_WIDTH - 1 downto 0);
  function ipbus_sel_ipbus_pio(addr : in std_logic_vector(31 downto 0)) return ipbus_sel_t;

-- START automatically generated VHDL (Mon May 19 12:03:12 2025)
  constant N_SLV_PIO0: integer := 0;
  constant N_SLAVES: integer := 1;
-- END automatically generated VHDL

end ipbus_decode_ipbus_pio;

package body ipbus_decode_ipbus_pio is

  function ipbus_sel_ipbus_pio(addr : in std_logic_vector(31 downto 0)) return ipbus_sel_t is
    variable sel: ipbus_sel_t;
  begin

-- START automatically generated VHDL (Mon May 19 12:03:12 2025)
    sel := ipbus_sel_t(to_unsigned(N_SLV_PIO0, IPBUS_SEL_WIDTH));
-- END automatically generated VHDL

    return sel;

  end function ipbus_sel_ipbus_pio;

end ipbus_decode_ipbus_pio;

---------------------------------------------------------------------------------

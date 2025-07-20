/*
 * clockDivider.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module clockDivider (
    input clk, reset,
    input [31:0] in_clkDiv,
    output wire out_clkEnable  
);

wire [7:0] in_clkDiv_frac = in_clkDiv[15:8];
wire [16:0] in_clkDiv_int = (in_clkDiv[31:16] == 0) ? 17'h10000 : in_clkDiv[31:16]; // 0 means 65536

reg [15:0] reg_intCounter;
reg [7:0] reg_fracCounter;

wire [15:0] next_intCounter;
wire [7:0] next_fracCounter;


always @(posedge clk or negedge reset)
begin
    if (!reset) begin
        reg_intCounter <= 0;
        reg_fracCounter <= 0;
    end else begin
        reg_intCounter <= next_intCounter;
        reg_fracCounter <= next_fracCounter;
    end
end

wire enableCondition = (reg_intCounter >= in_clkDiv_int - 1) ? 1 : 0;

wire [8:0] addedFracCounter = (enableCondition) ? reg_fracCounter + in_clkDiv_frac : reg_fracCounter;

wire [16:0] addedIntCounter = addedFracCounter[8] ? reg_intCounter + 2 : reg_intCounter + 1;

assign next_fracCounter = (!reset) ? 0 : addedFracCounter[7:0];

assign next_intCounter = (!reset) ? 0 :
                          enableCondition ? 
                          addedIntCounter - in_clkDiv_int : 
                          addedIntCounter;

assign out_clkEnable = enableCondition;


endmodule
/*
 * instructionMemory.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module instructionMemory(
    input clk,
    input reset,
    input [4:0] writeAddress, sm0Address, sm1Address, sm2Address, sm3Address, pioAddress,
    input [15:0] writeData,
    input writeEnable,

    output [15:0] sm0Data, sm1Data, sm2Data, sm3Data, pioData
);

reg [15:0] regMemory [31:0];

// Asynchronous Read Ports - Read directly from the register array
assign sm0Data = regMemory[sm0Address];
assign sm1Data = regMemory[sm1Address];
assign sm2Data = regMemory[sm2Address];
assign sm3Data = regMemory[sm3Address];
assign pioData = regMemory[pioAddress];

integer i;
// Synchronous Write Port Logic
always @(posedge clk, negedge reset) begin
    if (!reset) begin
        for (i = 0; i < 32; i = i + 1) begin
            regMemory[i] <= 16'b0;
        end
    end else if (writeEnable) begin
        regMemory[writeAddress] <= writeData;
        // All other memory locations implicitly hold their previous value
    end
end
endmodule
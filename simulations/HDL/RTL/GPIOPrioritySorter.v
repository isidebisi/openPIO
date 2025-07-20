/*
 * GPIOPrioritySorter.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module GPIOPrioritySorter(
    input clk, reset,
    input [31:0] in_sm0PinData, in_sm0PinMask, in_sm0PindirsData, in_sm0PindirsMask,
    input [31:0] in_sm1PinData, in_sm1PinMask, in_sm1PindirsData, in_sm1PindirsMask,
    input [31:0] in_sm2PinData, in_sm2PinMask, in_sm2PindirsData, in_sm2PindirsMask,
    input [31:0] in_sm3PinData, in_sm3PinMask, in_sm3PindirsData, in_sm3PindirsMask,

    output [31:0] out_pinsWriteData, out_pinsWriteMask, out_pinDirsWriteData, out_pinDirsWriteMask
);

    //make pinDir sticky
    reg [31:0] reg_pinDirWriteData;
    wire [31:0] next_pinDirWriteData, maskedNewPinDirData;


    always @(posedge clk, negedge reset) begin
        if (!reset) begin
            reg_pinDirWriteData <= 32'h0;
        end else begin
            reg_pinDirWriteData <= next_pinDirWriteData;
        end
    end


        

    // Priority: sm3 (highest) > sm2 > sm1 > sm0 (lowest)

    assign out_pinsWriteMask = in_sm3PinMask | in_sm2PinMask | in_sm1PinMask | in_sm0PinMask;

    assign out_pinsWriteData =
        (in_sm3PinData & in_sm3PinMask) |
        (in_sm2PinData & in_sm2PinMask & ~in_sm3PinMask) |
        (in_sm1PinData & in_sm1PinMask & ~in_sm2PinMask & ~in_sm3PinMask) |
        (in_sm0PinData & in_sm0PinMask & ~in_sm1PinMask & ~in_sm2PinMask & ~in_sm3PinMask);

    assign out_pinDirsWriteMask = in_sm3PindirsMask | in_sm2PindirsMask | in_sm1PindirsMask | in_sm0PindirsMask;

    assign maskedNewPinDirData =
        (in_sm3PindirsData & in_sm3PindirsMask) |
        (in_sm2PindirsData & in_sm2PindirsMask & ~in_sm3PindirsMask) |
        (in_sm1PindirsData & in_sm1PindirsMask & ~in_sm2PindirsMask & ~in_sm3PindirsMask) |
        (in_sm0PindirsData & in_sm0PindirsMask & ~in_sm1PindirsMask & ~in_sm2PindirsMask & ~in_sm3PindirsMask);
    
    //The following is to make the WriteData Sticky
    assign next_pinDirWriteData = reg_pinDirWriteData & ~out_pinDirsWriteMask | maskedNewPinDirData;
    assign out_pinDirsWriteData = next_pinDirWriteData;


endmodule
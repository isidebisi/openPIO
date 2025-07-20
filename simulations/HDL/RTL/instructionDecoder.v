/*
 * instructionDecoder.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module instructionDecoder (
    input [31:0] in_smPinCtrl,in_smExecCtrl,
    input [15:0] in_opCode,
    output [2:0] out_instruction,
    output [4:0] out_delay,
    output       out_sideEnable,
    output [4:0] out_sideSet,
    output [7:0] out_instructionParams
);

    wire [4:0] sideDelay = in_opCode[12:8];
    wire [2:0] sideSetCount = in_smPinCtrl[31:29];
    wire sideEnable = in_smExecCtrl[30];

    wire [2:0] delayCount = 5 - sideSetCount;
    
    wire [4:0] sideSet = sideDelay >> delayCount;

    // sideSet is 5 bits, but only 4 if sideEnable is 1 (MSB becomes enable)
    assign out_sideSet = sideEnable ? sideSet & 5'b01111 : sideSet;
    assign out_delay = sideDelay & ((1 << delayCount) - 1);

    assign out_instruction = in_opCode[15:13];

    assign out_instructionParams = in_opCode[7:0];

    // when sideSetEnable is 1, sideDelay[4] is the actual sideSet enable for each instruction
    // else the sideSet is always enabled
    assign out_sideEnable = (sideEnable == 0) ? ((sideSetCount == 0) ? 1'b0 :1'b1) :
                            (sideSetCount == 0) ? 1'b0 : sideDelay[4];

endmodule
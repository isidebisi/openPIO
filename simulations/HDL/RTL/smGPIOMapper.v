/*
 * smGPIOMapper.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module smGPIOMapper(
    input           in_outSetEnable, in_outNotSet,
                    in_outSetPinsNotPindirs, in_sideSetEnable,
    input [31:0]    in_outSetData,
    input [4:0]     in_sideSetData,
    input [31:0]    in_smPinCtrl, in_smExecCtrl,
    input [31:0]    in_GPIO,

    output [31:0]   out_pinsWriteData, out_pinsWriteMask, 
                    out_pinDirsWriteData, out_pinDirsWriteMask,
                    out_inGPIOmappedData
);


wire SIDE_ENABLE = in_smExecCtrl[30];
wire SIDE_PINDIR = in_smExecCtrl[29];
wire sidePinsNotPindirs = ! SIDE_PINDIR;

wire [2:0] SIDESET_COUNT = in_smPinCtrl[31:29]; //including sideSetEnable
wire [2:0] SET_COUNT = in_smPinCtrl[28:26]; 
wire [5:0] OUT_COUNT = in_smPinCtrl[25:20];
wire [4:0] IN_BASE = in_smPinCtrl[19:15];
wire [4:0] SIDESET_BASE = in_smPinCtrl[14:10];
wire [4:0] SET_BASE = in_smPinCtrl[9:5];
wire [4:0] OUT_BASE = in_smPinCtrl[4:0];

wire [4:0] sideSetLength = SIDESET_COUNT - SIDE_ENABLE;

wire [31:0] sideSetLengthMask = (1 << sideSetLength) - 1;
wire [31:0] maskedSideSet = in_sideSetEnable ?  in_sideSetData & sideSetLengthMask : 0;
wire [31:0] mappedSideSet = maskedSideSet << SIDESET_BASE | maskedSideSet >> 32-SIDESET_BASE;
wire [31:0] mappedSideSetMask = in_sideSetEnable ? sideSetLengthMask << SIDESET_BASE | sideSetLengthMask >> 32-SIDESET_BASE : 0;

wire [31:0] setLengthMask = (1 << SET_COUNT) - 1;
wire [31:0] maskedSet = (in_outSetEnable & in_outNotSet == 0) ? in_outSetData & setLengthMask : 0;
wire [31:0] mappedSet = maskedSet << SET_BASE | maskedSet >> 32-SET_BASE;
wire [31:0] mappedSetMask = (in_outSetEnable & in_outNotSet == 0) ? setLengthMask << SET_BASE | setLengthMask >> 32-SET_BASE : 0;

wire [31:0] outLengthMask = (1 << OUT_COUNT) - 1;
wire [31:0] maskedOut = (in_outSetEnable & in_outNotSet) ? in_outSetData & outLengthMask : 0;
wire [31:0] mappedOut = maskedOut << OUT_BASE | maskedOut >> 32-OUT_BASE;
wire [31:0] mappedOutMask = (in_outSetEnable & in_outNotSet) ? outLengthMask << OUT_BASE | outLengthMask >> 32-OUT_BASE : 0;

assign out_pinsWriteData = (in_outSetPinsNotPindirs == 1 & sidePinsNotPindirs == 1) ? mappedOut | mappedSet | mappedSideSet : 
                            (in_outSetPinsNotPindirs == 1 & sidePinsNotPindirs == 0) ? mappedOut | mappedSet : 
                            (in_outSetPinsNotPindirs == 0 & sidePinsNotPindirs == 1) ? mappedSideSet :
                            0;

assign out_pinsWriteMask = (in_outSetPinsNotPindirs == 1 & sidePinsNotPindirs == 1) ? mappedOutMask | mappedSetMask | mappedSideSetMask :
                            (in_outSetPinsNotPindirs == 1 & sidePinsNotPindirs == 0) ? mappedOutMask | mappedSetMask : 
                            (in_outSetPinsNotPindirs == 0 & sidePinsNotPindirs == 1) ? mappedSideSetMask :
                            0;

assign out_pinDirsWriteData = (in_outSetPinsNotPindirs == 0 & sidePinsNotPindirs == 0) ? mappedOut | mappedSet | mappedSideSet :
                               (in_outSetPinsNotPindirs == 0 & sidePinsNotPindirs == 1) ? mappedOut | mappedSet :
                               (in_outSetPinsNotPindirs == 1 & sidePinsNotPindirs == 0) ? mappedSideSet :
                               0;

assign out_pinDirsWriteMask = (in_outSetPinsNotPindirs == 0 & sidePinsNotPindirs == 0) ? mappedOutMask | mappedSetMask | mappedSideSetMask : 
                                 (in_outSetPinsNotPindirs == 0 & sidePinsNotPindirs == 1) ? mappedOutMask | mappedSetMask :
                                 (in_outSetPinsNotPindirs == 1 & sidePinsNotPindirs == 0) ? mappedSideSetMask :
                                 0;


assign out_inGPIOmappedData = in_GPIO << IN_BASE | in_GPIO >> 32-IN_BASE;

endmodule

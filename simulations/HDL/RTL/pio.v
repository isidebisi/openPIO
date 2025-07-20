/*
 * pio.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module pio(
    input clk, reset,
    input in_strobe, in_writeNotRead,
    input [11:0] in_address,
    input [31:0] in_data,
    input [31:0] in_GPIO,
    output reg [31:0] out_data,
    output reg out_ack,

    output wire [31:0] out_GPIODirWriteData, out_GPIOWriteData
);

parameter FIFO_TX_TEST_VALUE = 32'b01001100011100001111000001111100;



reg [31:0] reg_writeData;
reg [31:0] next_writeData;

reg [31:0] reg_CTRL; //pio control register
reg [31:0] reg_EXECCTRL [3:0];
reg [31:0] reg_SHIFTCTRL [3:0];
reg [31:0] reg_PINCTRL [3:0];
reg [31:0] reg_CLKDIV [3:0];

reg [31:0] next_CTRL;
reg [31:0] next_EXECCTRL [3:0];
reg [31:0] next_SHIFTCTRL [3:0];
reg [31:0] next_PINCTRL [3:0];
reg [31:0] next_CLKDIV [3:0];

integer i;
integer j;

always @(posedge clk or negedge reset) begin
    if (!reset) begin
        for (i = 0; i < 4; i = i + 1) begin
            reg_EXECCTRL[i] <= (5'h1F << 12); // WRAP_TOP = 0x1F
            reg_SHIFTCTRL[i] <= (2'b11 << 18); //IN-/OUT_SHIFTDIR = 1
            reg_PINCTRL[i] <= (3'b101 <<26); // SET_COUNT = 5
            reg_CLKDIV[i] <= (1'b1 << 16); // CLKDIV_INT = 1
        end
        reg_writeData <= 32'b0;
        reg_CTRL <= 32'b0;

    end else begin
        for (j = 0; j < 4; j = j + 1) begin
            reg_EXECCTRL[j] <= next_EXECCTRL[j];
            reg_SHIFTCTRL[j] <= next_SHIFTCTRL[j];
            reg_PINCTRL[j] <= next_PINCTRL[j];
            reg_CLKDIV[j] <= next_CLKDIV[j];
        end
        reg_writeData <= next_writeData;
        reg_CTRL <= next_CTRL;
    end
end

reg [4:0] pio_iMemReadAddress;

wire [15:0] sm0_iMemData, sm1_iMemData, sm2_iMemData;
wire [15:0] sm3_iMemData, pio_iMemData;


reg [4:0] iMemWriteAddress;
reg [15:0] iMemWriteData;
reg iMemWriteEnable;
wire [4:0] sm_out_regPC [3:0];
instructionMemory iMem(
    .clk(clk),
    .reset(reset),
    .writeAddress(iMemWriteAddress),
    .sm0Address(sm_out_regPC[0]),
    .sm1Address(sm_out_regPC[1]),
    .sm2Address(sm_out_regPC[2]),
    .sm3Address(sm_out_regPC[3]),
    .pioAddress(pio_iMemReadAddress),
    .writeData(iMemWriteData),
    .writeEnable(iMemWriteEnable),
    .sm0Data(sm0_iMemData),
    .sm1Data(sm1_iMemData),
    .sm2Data(sm2_iMemData),
    .sm3Data(sm3_iMemData),
    .pioData(pio_iMemData)  
    );


wire [31:0] sm_out_dataRXFifo [3:0], sm_out_outSetData [3:0];
wire [4:0] sm_out_out_sideSetData [3:0];
wire sm_outSetEnable [3:0], sm_outNotSet [3:0], sm_outSetPinsNotPindirs [3:0];
wire sm_out_TXFifoDataAck [3:0], sm_out_RXFifoDataValid [3:0], sm_out_sideSetEnable [3:0];
wire [31:0] sm_inData [3:0];

wire [31:0] smGPIOMapper_out_pinsWriteData [3:0], smGPIOMapper_out_pinsWriteMask [3:0];
wire [31:0] smGPIOMapper_out_pinDirsWriteData [3:0], smGPIOMapper_out_pinDirsWriteMask [3:0];

/*
 * State Machines with GPIOMappers
 */

stateMachine sm0(
    .clk(clk),
    .reset(reset),
    .in_SMEnable(reg_CTRL[0]),
    .in_SMRestart(reg_CTRL[4]),
    .in_CLKDIVRestart(reg_CTRL[8]),
    .in_opCode(sm0_iMemData),
    .in_dataTXFifo(FIFO_TX_TEST_VALUE), // TODO: Replace with actual data
    .in_GPIO(in_GPIO),
    .in_inData(sm_inData[0]),
    .in_SM_EXECCTRL(reg_EXECCTRL[0]),
    .in_SM_SHIFTCTRL(reg_SHIFTCTRL[0]),
    .in_SM_PINCTRL(reg_PINCTRL[0]),
    .in_SM_CLKDIV(reg_CLKDIV[0]),
    .in_TXFifoEmpty(1'b0), // TODO: Replace with actual TX FIFO empty signal
    .in_RXFifoFull(1'b0), // TODO: Replace with actual RX FIFO full signal
    .out_dataRXFifo(sm_out_dataRXFifo[0]),
    .out_outSetEnable(sm_outSetEnable[0]),
    .out_outNotSet(sm_outNotSet[0]),
    .out_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[0]),
    .out_outSetData(sm_out_outSetData[0]),
    .out_sideSetData(sm_out_out_sideSetData[0]),
    .out_TXFifoDataAck(sm_out_TXFifoDataAck[0]),
    .out_RXFifoDataValid(sm_out_RXFifoDataValid[0]),
    .out_sideSetEnable(sm_out_sideSetEnable[0]),
    .out_regPC(sm_out_regPC[0])
);

stateMachine sm1(
    .clk(clk),
    .reset(reset),
    .in_SMEnable(reg_CTRL[1]),
    .in_SMRestart(reg_CTRL[5]),
    .in_CLKDIVRestart(reg_CTRL[9]),
    .in_opCode(sm1_iMemData),
    .in_dataTXFifo(FIFO_TX_TEST_VALUE), // TODO: Replace with actual data
    .in_GPIO(in_GPIO),
    .in_inData(sm_inData[1]),
    .in_SM_EXECCTRL(reg_EXECCTRL[1]),
    .in_SM_SHIFTCTRL(reg_SHIFTCTRL[1]),
    .in_SM_PINCTRL(reg_PINCTRL[1]),
    .in_SM_CLKDIV(reg_CLKDIV[1]),
    .in_TXFifoEmpty(1'b0), // TODO: Replace with actual TX FIFO empty signal
    .in_RXFifoFull(1'b0), // TODO: Replace with actual RX FIFO full signal
    .out_dataRXFifo(sm_out_dataRXFifo[1]),
    .out_outSetEnable(sm_outSetEnable[1]),
    .out_outNotSet(sm_outNotSet[1]),
    .out_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[1]),
    .out_outSetData(sm_out_outSetData[1]),
    .out_sideSetData(sm_out_out_sideSetData[1]),
    .out_TXFifoDataAck(sm_out_TXFifoDataAck[1]),
    .out_RXFifoDataValid(sm_out_RXFifoDataValid[1]),
    .out_sideSetEnable(sm_out_sideSetEnable[1]),
    .out_regPC(sm_out_regPC[1])
);

stateMachine sm2(
    .clk(clk),
    .reset(reset),
    .in_SMEnable(reg_CTRL[2]),
    .in_SMRestart(reg_CTRL[6]),
    .in_CLKDIVRestart(reg_CTRL[10]),
    .in_opCode(sm2_iMemData),
    .in_dataTXFifo(FIFO_TX_TEST_VALUE), // TODO: Replace with actual data
    .in_GPIO(in_GPIO),
    .in_inData(sm_inData[2]),
    .in_SM_EXECCTRL(reg_EXECCTRL[2]),
    .in_SM_SHIFTCTRL(reg_SHIFTCTRL[2]),
    .in_SM_PINCTRL(reg_PINCTRL[2]),
    .in_SM_CLKDIV(reg_CLKDIV[2]),
    .in_TXFifoEmpty(1'b0), // TODO: Replace with actual TX FIFO empty signal
    .in_RXFifoFull(1'b0), // TODO: Replace with actual RX FIFO full signal
    .out_dataRXFifo(sm_out_dataRXFifo[2]),
    .out_outSetEnable(sm_outSetEnable[2]),
    .out_outNotSet(sm_outNotSet[2]),
    .out_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[2]),
    .out_outSetData(sm_out_outSetData[2]),
    .out_sideSetData(sm_out_out_sideSetData[2]),
    .out_TXFifoDataAck(sm_out_TXFifoDataAck[2]),
    .out_RXFifoDataValid(sm_out_RXFifoDataValid[2]),
    .out_sideSetEnable(sm_out_sideSetEnable[2]),
    .out_regPC(sm_out_regPC[2])
);

stateMachine sm3(
    .clk(clk),
    .reset(reset),
    .in_SMEnable(reg_CTRL[3]),
    .in_SMRestart(reg_CTRL[7]),
    .in_CLKDIVRestart(reg_CTRL[11]),
    .in_opCode(sm3_iMemData),
    .in_dataTXFifo(FIFO_TX_TEST_VALUE), // TODO: Replace with actual data
    .in_GPIO(in_GPIO),
    .in_inData(sm_inData[3]),
    .in_SM_EXECCTRL(reg_EXECCTRL[3]),
    .in_SM_SHIFTCTRL(reg_SHIFTCTRL[3]),
    .in_SM_PINCTRL(reg_PINCTRL[3]),
    .in_SM_CLKDIV(reg_CLKDIV[3]),
    .in_TXFifoEmpty(1'b0), // TODO: Replace with actual TX FIFO empty signal
    .in_RXFifoFull(1'b0), // TODO: Replace with actual RX FIFO full signal
    .out_dataRXFifo(sm_out_dataRXFifo[3]),
    .out_outSetEnable(sm_outSetEnable[3]),
    .out_outNotSet(sm_outNotSet[3]),
    .out_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[3]),
    .out_outSetData(sm_out_outSetData[3]),
    .out_sideSetData(sm_out_out_sideSetData[3]),
    .out_TXFifoDataAck(sm_out_TXFifoDataAck[3]),
    .out_RXFifoDataValid(sm_out_RXFifoDataValid[3]),
    .out_sideSetEnable(sm_out_sideSetEnable[3]),
    .out_regPC(sm_out_regPC[3])
);






/*
 * GPIO Mappers and Sorter
 */

smGPIOMapper sm0GPIOMapper(
    .in_outSetEnable(sm_outSetEnable[0]),
    .in_outNotSet(sm_outNotSet[0]),
    .in_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[0]),
    .in_sideSetEnable(sm_out_sideSetEnable[0]),
    .in_outSetData(sm_out_outSetData[0]),
    .in_sideSetData(sm_out_out_sideSetData[0]),
    .in_smPinCtrl(reg_PINCTRL[0]),
    .in_smExecCtrl(reg_EXECCTRL[0]),
    .in_GPIO(in_GPIO),
    .out_pinsWriteData(smGPIOMapper_out_pinsWriteData[0]),
    .out_pinsWriteMask(smGPIOMapper_out_pinsWriteMask[0]),
    .out_pinDirsWriteData(smGPIOMapper_out_pinDirsWriteData[0]),
    .out_pinDirsWriteMask(smGPIOMapper_out_pinDirsWriteMask[0]),
    .out_inGPIOmappedData(sm_inData[0])
);

smGPIOMapper sm1GPIOMapper(
    .in_outSetEnable(sm_outSetEnable[1]),
    .in_outNotSet(sm_outNotSet[1]),
    .in_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[1]),
    .in_sideSetEnable(sm_out_sideSetEnable[1]),
    .in_outSetData(sm_out_outSetData[1]),
    .in_sideSetData(sm_out_out_sideSetData[1]),
    .in_smPinCtrl(reg_PINCTRL[1]),
    .in_smExecCtrl(reg_EXECCTRL[1]),
    .in_GPIO(in_GPIO),
    .out_pinsWriteData(smGPIOMapper_out_pinsWriteData[1]),
    .out_pinsWriteMask(smGPIOMapper_out_pinsWriteMask[1]),
    .out_pinDirsWriteData(smGPIOMapper_out_pinDirsWriteData[1]),
    .out_pinDirsWriteMask(smGPIOMapper_out_pinDirsWriteMask[1]),
    .out_inGPIOmappedData(sm_inData[1])
);

smGPIOMapper sm2GPIOMapper(
    .in_outSetEnable(sm_outSetEnable[2]),
    .in_outNotSet(sm_outNotSet[2]),
    .in_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[2]),
    .in_sideSetEnable(sm_out_sideSetEnable[2]),
    .in_outSetData(sm_out_outSetData[2]),
    .in_sideSetData(sm_out_out_sideSetData[2]),
    .in_smPinCtrl(reg_PINCTRL[2]),
    .in_smExecCtrl(reg_EXECCTRL[2]),
    .in_GPIO(in_GPIO),
    .out_pinsWriteData(smGPIOMapper_out_pinsWriteData[2]),
    .out_pinsWriteMask(smGPIOMapper_out_pinsWriteMask[2]),
    .out_pinDirsWriteData(smGPIOMapper_out_pinDirsWriteData[2]),
    .out_pinDirsWriteMask(smGPIOMapper_out_pinDirsWriteMask[2]),
    .out_inGPIOmappedData(sm_inData[2])
);

smGPIOMapper sm3GPIOMapper(
    .in_outSetEnable(sm_outSetEnable[3]),
    .in_outNotSet(sm_outNotSet[3]),
    .in_outSetPinsNotPindirs(sm_outSetPinsNotPindirs[3]),
    .in_sideSetEnable(sm_out_sideSetEnable[3]),
    .in_outSetData(sm_out_outSetData[3]),
    .in_sideSetData(sm_out_out_sideSetData[3]),
    .in_smPinCtrl(reg_PINCTRL[3]),
    .in_smExecCtrl(reg_EXECCTRL[3]),
    .in_GPIO(in_GPIO),
    .out_pinsWriteData(smGPIOMapper_out_pinsWriteData[3]),
    .out_pinsWriteMask(smGPIOMapper_out_pinsWriteMask[3]),
    .out_pinDirsWriteData(smGPIOMapper_out_pinDirsWriteData[3]),
    .out_pinDirsWriteMask(smGPIOMapper_out_pinDirsWriteMask[3]),
    .out_inGPIOmappedData(sm_inData[3])
);

GPIOPrioritySorter GPIOSorter(
    .clk(clk),
    .reset(reset),
    .in_sm0PinData(smGPIOMapper_out_pinsWriteData[0]),
    .in_sm0PinMask(smGPIOMapper_out_pinsWriteMask[0]),
    .in_sm0PindirsData(smGPIOMapper_out_pinDirsWriteData[0]),
    .in_sm0PindirsMask(smGPIOMapper_out_pinDirsWriteMask[0]),
    .in_sm1PinData(smGPIOMapper_out_pinsWriteData[1]),
    .in_sm1PinMask(smGPIOMapper_out_pinsWriteMask[1]),
    .in_sm1PindirsData(smGPIOMapper_out_pinDirsWriteData[1]),
    .in_sm1PindirsMask(smGPIOMapper_out_pinDirsWriteMask[1]),
    .in_sm2PinData(smGPIOMapper_out_pinsWriteData[2]),
    .in_sm2PinMask(smGPIOMapper_out_pinsWriteMask[2]),
    .in_sm2PindirsData(smGPIOMapper_out_pinDirsWriteData[2]),
    .in_sm2PindirsMask(smGPIOMapper_out_pinDirsWriteMask[2]),
    .in_sm3PinData(smGPIOMapper_out_pinsWriteData[3]),
    .in_sm3PinMask(smGPIOMapper_out_pinsWriteMask[3]),
    .in_sm3PindirsData(smGPIOMapper_out_pinDirsWriteData[3]),
    .in_sm3PindirsMask(smGPIOMapper_out_pinDirsWriteMask[3]),
    .out_pinsWriteData(out_GPIOWriteData),
    .out_pinsWriteMask(),
    .out_pinDirsWriteData(out_GPIODirWriteData),
    .out_pinDirsWriteMask()
);

/*
 * BUS Interface 
 */
integer k;

always @(*) begin 
    
    out_ack = 1'b0;
    out_data = 32'b0;
    
    for (k = 0; k < 4; k = k + 1) begin
        next_EXECCTRL[k] = reg_EXECCTRL[k];
        next_SHIFTCTRL[k] = reg_SHIFTCTRL[k];
        next_PINCTRL[k] = reg_PINCTRL[k];
        next_CLKDIV[k] = reg_CLKDIV[k];
    end

    next_CTRL = reg_CTRL;
    next_writeData = reg_writeData;
    pio_iMemReadAddress = 5'b0;
    iMemWriteAddress = 5'b0;
    iMemWriteEnable = 1'b0;
    iMemWriteData = 16'b0;

    if (in_strobe) begin
        out_ack = 1'b1; // for ipbus we can directly set ack as ipBus runs slower than pio
        if (in_writeNotRead) begin
            // Write operation
            if (in_address == 12'h000) begin
                next_CTRL = in_data;
            end else if ((in_address >= 12'h048) && (in_address <= 12'h0C4)) begin
                iMemWriteAddress = (in_address[6:2] - 5'h12); // 0x48 = 0b0100 1000 >> 2 = 0b0001 0010
                iMemWriteEnable = 1'b1;
                iMemWriteData = in_data[15:0];
            end else begin
                case (in_address[11:0])
                //12'h000: next_CTRL = in_data;

                12'h0C8: next_CLKDIV[0] = in_data;
                12'h0CC: next_EXECCTRL[0] = in_data;
                12'h0D0: next_SHIFTCTRL[0] = in_data;
                12'h0DC: next_PINCTRL[0] = in_data;

                12'h0E0: next_CLKDIV[1] = in_data;
                12'h0E4: next_EXECCTRL[1] = in_data;
                12'h0E8: next_SHIFTCTRL[1] = in_data;
                12'h0F4: next_PINCTRL[1] = in_data;

                12'h0F8: next_CLKDIV[2] = in_data;
                12'h0FC: next_EXECCTRL[2] = in_data;
                12'h100: next_SHIFTCTRL[2] = in_data;
                12'h10C: next_PINCTRL[2] = in_data;

                12'h110: next_CLKDIV[3] = in_data;
                12'h114: next_EXECCTRL[3] = in_data;
                12'h118: next_SHIFTCTRL[3] = in_data;
                12'h124: next_PINCTRL[3] = in_data;
                
                default: begin
                    // Do nothing
                end
                endcase
            end
        end else begin
            // Read operation
            if (in_address == 12'h000) begin
                out_data = reg_CTRL;
            end else if ((in_address >= 12'h048) && (in_address <= 12'h0C4)) begin
                pio_iMemReadAddress = (in_address[6:2] - 5'h12); // 0x48 = 0b0100 1000 >> 2 = 0b0001 0010
                out_data = {16'b0, pio_iMemData};
            end else begin
                case (in_address[11:0])
                //12'h000: out_data = reg_CTRL;

                12'h0C8: out_data = reg_CLKDIV[0];
                12'h0CC: out_data = reg_EXECCTRL[0];
                12'h0D0: out_data = reg_SHIFTCTRL[0];
                12'h0DC: out_data = reg_PINCTRL[0];

                12'h0E0: out_data = reg_CLKDIV[1];
                12'h0E4: out_data = reg_EXECCTRL[1];
                12'h0E8: out_data = reg_SHIFTCTRL[1];
                12'h0F4: out_data = reg_PINCTRL[1];

                12'h0F8: out_data = reg_CLKDIV[2];
                12'h0FC: out_data = reg_EXECCTRL[2];
                12'h100: out_data = reg_SHIFTCTRL[2];
                12'h10C: out_data = reg_PINCTRL[2];

                12'h110: out_data = reg_CLKDIV[3];
                12'h114: out_data = reg_EXECCTRL[3];
                12'h118: out_data = reg_SHIFTCTRL[3];
                12'h124: out_data = reg_PINCTRL[3];

                default: begin
                    // Do nothing
                end
                endcase

            end
        end

    end
end


endmodule
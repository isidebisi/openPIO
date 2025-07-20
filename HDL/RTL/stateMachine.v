/*
 * isr.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

module stateMachine(
    input clk, reset,
    input in_SMEnable, in_CLKDIVRestart, in_SMRestart,
    input [15:0] in_opCode,
    input [31:0] in_dataTXFifo, in_GPIO, in_inData, // in data is already mapped wheras in_GPIO is not
    input [31:0] in_SM_EXECCTRL, in_SM_SHIFTCTRL, in_SM_PINCTRL, in_SM_CLKDIV,
    input in_TXFifoEmpty, in_RXFifoFull,

    output reg [31:0] out_dataRXFifo,
    output            out_outSetEnable, out_outNotSet, out_outSetPinsNotPindirs,
    output [31:0]     out_outSetData, // output data for GPIOs from OUT and SET instructions
    output [4:0]      out_sideSetData,
    output            out_TXFifoDataAck, out_sideSetEnable,
    output reg        out_RXFifoDataValid,
    output reg [4:0]  out_regPC
);

// Control REGISTERS

wire EXEC_STALLED   = in_SM_EXECCTRL[31];    // RO, reset: 0x0

// SIDE_EN, SIDE_PINDIR, and JMP_PIN already defined:
wire SIDE_PINDIR    = in_SM_EXECCTRL[29];    
wire [4:0] JMP_PIN  = in_SM_EXECCTRL[28:24]; 

wire [4:0] OUT_EN_SEL   = in_SM_EXECCTRL[23:19]; 
wire INLINE_OUT_EN    = in_SM_EXECCTRL[18];      
wire OUT_STICKY       = in_SM_EXECCTRL[17];      
wire [4:0] WRAP_TOP   = in_SM_EXECCTRL[16:12]; 
wire [4:0] WRAP_BOTTOM = in_SM_EXECCTRL[11:7]; 

wire STATUS_SEL       = in_SM_EXECCTRL[4];       
wire [3:0] STATUS_N   = in_SM_EXECCTRL[3:0];     

wire [4:0] PULL_THRESH = in_SM_SHIFTCTRL[29:25];
wire [4:0] PUSH_THRESH = in_SM_SHIFTCTRL[24:20];
wire OUT_SHIFTDIR = in_SM_SHIFTCTRL[19];        
wire IN_SHIFTDIR  = in_SM_SHIFTCTRL[18];        
wire AUTOPULL    = in_SM_SHIFTCTRL[17];         
wire AUTOPUSH    = in_SM_SHIFTCTRL[16];         





//TODO: implement TX and RX Fifo. Question: are they synchronized to the clock ? Are they in statemachine our outside ?
//TODO: implement Sticky outputs, etc.
//TODO: SM_INSTR and SM_ADDR Register implementation

wire clkDiv_enable;
wire clkDiv_reset = reset | ~in_CLKDIVRestart;

clockDivider clkDiv (
    .clk(clk),
    .reset(reset),
    .in_clkDiv(in_SM_CLKDIV),
    .out_clkEnable(clkDiv_enable)
);

/*
 * Initialize registers
 */
reg [31:0] reg_scratchX, reg_scratchY, reg_outSetData;
reg [4:0] reg_delayCounter;
reg [15:0] reg_EXECRegister;
reg reg_EXECEnable;

reg reg_outSetEnable, reg_outNotSet, reg_outSetPinsNotPindirs, reg_sideSetEnable;
reg [4:0] reg_sideSetData;
reg next_outSetEnable, next_outNotSet, next_outSetPinsNotPindirs; // Added for holding state

reg [31:0] next_scratchX, next_scratchY;
reg [31:0] next_outSetData;
reg [4:0] next_PC, next_delayCounter, next_sideSetData;
reg [15:0] next_EXECRegister;
reg next_EXECEnable, next_sideSetEnable;
    
always @(posedge clk, negedge reset) begin
    if (!reset) begin
        reg_scratchX <= 32'b0;
        reg_scratchY <= 32'b0;

        out_regPC <= 5'b0;
        reg_delayCounter <= 5'b0;

        reg_EXECRegister <= 16'b0;
        reg_EXECEnable <= 1'b0;
        reg_sideSetData <= 5'b0;
        reg_sideSetEnable <= 1'b0;
        reg_outSetData <= 32'b0;

        reg_outSetEnable <= 1'b0;
        reg_outNotSet <= 1'b0;
        reg_outSetPinsNotPindirs <= 1'b0;

    end else begin
        reg_scratchX <= next_scratchX;
        reg_scratchY <= next_scratchY;
        out_regPC <= next_PC;
        reg_delayCounter <= next_delayCounter;

        reg_EXECRegister <= next_EXECRegister;
        reg_EXECEnable <= next_EXECEnable;

        reg_sideSetData <= next_sideSetData;
        reg_sideSetEnable <= next_sideSetEnable;
        
        reg_outSetData <= next_outSetData;
        reg_outSetEnable <= next_outSetEnable;
        reg_outNotSet <= next_outNotSet;
        reg_outSetPinsNotPindirs <= next_outSetPinsNotPindirs;
    end
end

assign out_outSetEnable = next_outSetEnable;
assign out_outNotSet = next_outNotSet;
assign out_outSetPinsNotPindirs = next_outSetPinsNotPindirs;
assign out_outSetData = next_outSetData;

assign out_sideSetData = next_sideSetData;
assign out_sideSetEnable = next_sideSetEnable;


/*
 * Instantiate instruction decoder
 */


wire [2:0] instruction;
wire [4:0] delay, sideSet;
wire [7:0] instructionParams;

wire [2:0] instruction_condition = instructionParams[7:5];
wire [4:0] instruction_data = instructionParams[4:0];

wire sideSetEnable;
wire wait_polarity = instructionParams[7];

//if EXEC is enabled, the instruction is taken from the EXEC register
wire [15:0] opCode = reg_EXECEnable ? reg_EXECRegister : in_opCode;

instructionDecoder ID(
    .in_opCode(opCode),
    .in_smPinCtrl(in_SM_PINCTRL),
    .in_smExecCtrl(in_SM_EXECCTRL),
    .out_instruction(instruction),
    .out_delay(delay),
    .out_sideSet(sideSet),
    .out_sideEnable(sideSetEnable),
    .out_instructionParams(instructionParams)
);

/*
 * Instantiate ISR
 */

wire [31:0] isrReadData;
reg [31:0] isrWriteData;
reg [4:0] isrBitReqLength;

wire isrFull, isrRequestPush, isrPushNow;

reg reg_isrPushNow;

assign isrPushNow = reg_isrPushNow;
reg isrEnable;

isr ISR(
    .clk(clk),
    .reset(reset),
    .in_shiftDirection(IN_SHIFTDIR),
    .in_data(isrWriteData),
    .in_inEnable(isrEnable),
    .in_pushNow(isrPushNow),
    .in_autoPushEnable(AUTOPUSH),
    .in_pushThreshold(PUSH_THRESH),
    .in_bitReqLength(isrBitReqLength),
    .out_data(isrReadData),
    .out_full(isrFull),
    .out_requestPush(isrRequestPush)
);

/*
 * Instantiate OSR
 */

wire [31:0] osrReadData;
reg [31:0] osrWriteData;
reg [4:0] osrBitReqLength;

wire osrEmpty, osrRequestRefill;
reg osrEnable, reg_osrPullNow;

osr OSR(
    .clk(clk),
    .reset(reset),
    .in_shiftDirection(OUT_SHIFTDIR),
    .in_data(osrWriteData),
    .in_outEnable(osrEnable),
    .in_refillNow(reg_osrPullNow),
    .in_autoPullEnable(AUTOPULL),
    .in_pullThreshold(PULL_THRESH),
    .in_bitReqLength(osrBitReqLength),
    .out_data(osrReadData),
    .out_empty(osrEmpty),
    .out_requestRefill(osrRequestRefill)
);





/*
 * Initialize binaryOperations for MOV operator
 */

wire [31:0] binaryOpReadData;
reg [31:0] binaryOpWriteData;

binaryOperations binOp(
    .in_data(binaryOpWriteData),
    .in_op(instruction_data[4:3]),
    .out_data(binaryOpReadData)
);


/*
 * ALU
 */

localparam JMP = 0;
localparam WAIT = 1;
localparam IN = 2;
localparam OUT = 3;
localparam PUSHPULL = 4;
localparam MOV = 5;
localparam IRQ = 6;
localparam SET = 7; 

localparam MOV_PINS = 3'b000;
localparam MOV_SCRATCHX = 3'b001;
localparam MOV_SCRATCHY = 3'b010;
localparam MOV_NULL = 3'b011;
localparam MOV_EXEC = 3'b100;
localparam MOV_PC_STATUS = 3'b101;
localparam MOV_ISR = 3'b110;
localparam MOV_OSR = 3'b111;


// calculate the next PC position taking into account the wrap around
// if EXEC is enabled, the next PC is still the same as the current PC
wire [4:0] next_calculatedPC =  reg_EXECEnable ? out_regPC :
                                ((out_regPC == WRAP_TOP) ? WRAP_BOTTOM : out_regPC + 1); 



reg ignoreDelay; 

always @* begin
    next_scratchX = reg_scratchX;
    next_scratchY = reg_scratchY;
    next_PC = out_regPC;
    next_delayCounter = reg_delayCounter;

    next_EXECRegister = reg_EXECRegister;
    next_EXECEnable = reg_EXECEnable;

    next_sideSetData = reg_sideSetData;
    next_sideSetEnable = reg_sideSetEnable;
    
    next_outSetData = reg_outSetData;
    next_outSetEnable = reg_outSetEnable;
    next_outNotSet = reg_outNotSet;
    next_outSetPinsNotPindirs = reg_outSetPinsNotPindirs;



    isrWriteData = 32'b0;
    osrWriteData = 32'b0;
    isrEnable = 0;
    osrEnable = 0;
    isrBitReqLength = 0;
    osrBitReqLength = 0;

    reg_isrPushNow = 0;
    reg_osrPullNow = 0;

    out_dataRXFifo = 32'b0;
    out_RXFifoDataValid = 0;

    binaryOpWriteData = 32'b0;


    ignoreDelay = 0;

    //TODO: implement how PC is actually read and written to and from SM_ADDR register, not reg_PC
    if (in_SMEnable & clkDiv_enable) begin

        if (OUT_STICKY == 0) begin
            next_outSetData = 0;
            next_outSetEnable = 0;
            next_outNotSet = 0;
            next_outSetPinsNotPindirs = 0;
        end

        if (reg_delayCounter != 0) begin //ONLY EXECUTE INSTRUCTION IF DELAY COUNTER == 0
            next_delayCounter = reg_delayCounter - 1;
            next_PC = out_regPC; // stall PC
        end else begin

            //SIDE SET
            if (sideSetEnable) begin
                next_sideSetData = sideSet;
                next_sideSetEnable = 1;
            end
            
            //DELAY SET
            next_delayCounter = ignoreDelay ? 1'b0 : delay;

            // INSTRUCTION
            case (instruction)
                JMP: begin
                    case (instruction_condition)
                        3'b000: begin //always
                            next_PC = instruction_data;
                        end
                        3'b001: begin // !X: scratch X zero
                            if (reg_scratchX == 32'b0) begin
                                next_PC = instruction_data;
                            end else begin
                                next_PC = next_calculatedPC;
                            end
                        end
                        3'b010: begin // X--: scratch X non-zero, prior to decrement
                            if (reg_scratchX != 32'b0) begin
                                next_PC = instruction_data;
                            end else begin
                                next_PC = next_calculatedPC;
                            end
                            next_scratchX = reg_scratchX - 1; //decrement scratch X independent of branch
                        end
                        3'b011: begin // !Y: scratch Y zero
                            if (reg_scratchY == 32'b0) begin
                                next_PC = instruction_data;
                            end else begin
                                next_PC = next_calculatedPC;
                            end
                        end
                        3'b100: begin // Y--: scratch Y non-zero, prior to decrement
                            if (reg_scratchY != 32'b0) begin
                                next_PC = instruction_data;
                            end else begin
                                next_PC = next_calculatedPC;
                            end
                            next_scratchY = reg_scratchY - 1; //decrement scratch Y independent of branch
                        end
                        3'b101: begin // X!=Y: scratch X not equal scratch Y
                            if (reg_scratchX != reg_scratchY) begin
                                next_PC = instruction_data;
                            end else begin
                                next_PC = next_calculatedPC;
                            end
                        end
                        3'b110: begin // PIN: branch on input pin
                            if (in_GPIO[JMP_PIN] == 1'b1) begin
                                next_PC = instruction_data;
                            end else begin
                                next_PC = next_calculatedPC;
                            end
                        end
                        3'b111: begin // !OSRE: output shift register not empty
                            next_PC = next_calculatedPC; //TODO: implement
                        end
                    endcase
                end

                WAIT: begin
                    case (instruction_condition[1:0])
                        2'b00: begin // wait for GPIO
                            if (in_GPIO[instruction_data] == wait_polarity) begin
                                next_PC = next_calculatedPC;
                            end else begin
                                ignoreDelay = 1;
                            end
                        end

                        2'b01: begin // wait for Input PIN selected by index (= (PINCTRL_IN_BASE + index) modulo 32)
                            if (in_inData[instruction_data] == wait_polarity) begin
                                next_PC = next_calculatedPC;
                            end else begin
                                ignoreDelay = 1;
                            end
                        end

                        2'b10: begin // wait for IRQ (PIO IRQ Flag selected by index)
                            next_PC = next_calculatedPC; // TODO: implement
                        end

                        default: 
                            next_PC = next_calculatedPC;
                    endcase
                end

                IN: begin
                    isrEnable = 1;
                    isrBitReqLength = instruction_data;
                    next_PC = next_calculatedPC;

                    case (instruction_condition)
                        3'b000: begin // source: PINS
                        isrWriteData = in_inData;
                        end
                        3'b001: begin // source: scratch X
                        isrWriteData = reg_scratchX;
                        end
                        3'b010: begin // source: scratch Y
                        isrWriteData = reg_scratchY;
                        end
                        3'b011: begin // source: null (all zeros)
                        isrWriteData = 32'b0;
                        end
                        3'b110: begin // source: ISR
                        isrWriteData = isrReadData;
                        end
                        3'b111: begin // source: OSR
                        osrEnable = 1;
                        osrBitReqLength = instruction_data;
                        isrWriteData = osrReadData;
                        end
                        default: begin // source not defined: fill with ones I guess ?
                        isrWriteData = 32'hFFFFFFFF;
                        end
                    endcase
                end

                OUT: begin
                    osrEnable = 1;
                    osrBitReqLength = instruction_data;
                    next_PC = next_calculatedPC;

                    case (instruction_condition)
                        3'b000: begin // destination: PINS
                            next_outNotSet = 1;
                            next_outSetEnable = 1;
                            next_outSetPinsNotPindirs = 1;
                            next_outSetData = osrReadData;
                        end
                        3'b001: begin // destination: scratch X
                            next_scratchX = osrReadData;
                        end
                        3'b010: begin // destination: scratch Y
                            next_scratchY = osrReadData;
                        end
                        3'b011: begin // destination: null (discard data)
                        end
                        3'b100: begin // destination: PINDIRS
                            next_outNotSet = 1;
                            next_outSetEnable = 1;
                            next_outSetPinsNotPindirs = 0;
                            next_outSetData = osrReadData;
                        end
                        3'b101: begin // destination: PC
                            next_PC = osrReadData[4:0];
                        end
                        3'b110: begin // destination: ISR
                            isrWriteData = osrReadData;
                            isrBitReqLength = instruction_data;
                            isrEnable = 1;
                        end
                        3'b111: begin // destination: EXEC
                        // ATTENTION: DELAY CYCLES ARE NOT TAKEN INTO ACCOUNT IF OUT EXEC !!!
                            next_EXECRegister = osrReadData[15:0];
                            next_EXECEnable = 1;
                            ignoreDelay = 1;
                        end
                    endcase
                end

                PUSHPULL: begin
                    if (instruction_condition[2] == 0) begin //PUSH or PULL
                        //PUSH
                        if ((instruction_condition[0] & in_RXFifoFull == 0) | instruction_condition[0] == 0) begin
                            // RX Fifo Stalling condition
                            next_PC = next_calculatedPC;

                            if((instruction_condition[1] & isrFull) | (instruction_condition[1] == 0 )) begin
                                //ISR Full check
                                
                                //TODO: FDEBUG_RXSTALL FLAG ON IF RX FIFO Full and DATA lost
                                out_dataRXFifo = isrReadData;
                                out_RXFifoDataValid = in_RXFifoFull ? 1'b0 : 1'b1;
                                isrBitReqLength = 5'b0;
                                isrEnable = 1;
                            end
                        end else begin
                            // stall
                            next_PC = out_regPC;
                        end

                    end else begin
                        //PULL
                        //TODO: With autopull the PULL instuction becomes a NOP when the OSR is full (see datasheet note at PULL Op)
                        if ((instruction_condition[0] & in_TXFifoEmpty == 0) | instruction_condition[0] == 0) begin
                            // TX Fifo Stalling condition
                            next_PC = next_calculatedPC;

                            if((instruction_condition[1] & osrEmpty) | (instruction_condition[1] == 0 )) begin
                                //OSR Empty check
                                osrBitReqLength = 5'b0;
                                reg_osrPullNow = 1;
                                
                                if (instruction_condition[0] == 0 & in_TXFifoEmpty == 1) begin
                                    //According to datasheet: A nonblocking PULL on an empty FIFO has the same effect as MOV OSR, X.
                                    osrWriteData = reg_scratchX;
                                end else begin
                                    osrWriteData = in_dataTXFifo;
                                end
                            end
                        end else begin
                            // stall
                            next_PC = out_regPC;
                        end

                    end
                end

                MOV: begin
                    next_PC = next_calculatedPC;
                    // MOVING SOURCE
                    case (instruction_data[2:0])
                        MOV_PINS: begin
                            binaryOpWriteData = in_inData;
                        end

                        MOV_SCRATCHX: begin
                            binaryOpWriteData = reg_scratchX;
                        end

                        MOV_SCRATCHY: begin
                            binaryOpWriteData = reg_scratchY;
                        end

                        MOV_NULL: begin
                            binaryOpWriteData = 32'b0;
                        end

                        MOV_PC_STATUS: begin
                        end //TODO: implement

                        MOV_ISR: begin
                            reg_isrPushNow = 1;
                            isrBitReqLength = 0;
                            isrEnable = 1;
                            binaryOpWriteData = isrReadData;
                        end

                        MOV_OSR: begin
                            osrBitReqLength = 0;
                            osrEnable = 1;
                            binaryOpWriteData = osrReadData;
                        end

                        default: begin
                            binaryOpWriteData = 32'b0;
                        end
                    endcase

                    // MOVING DESTINATION
                    case (instruction_condition)
                        MOV_PINS: begin
                            next_outSetEnable = 1;
                            next_outNotSet = 1;
                            next_outSetPinsNotPindirs = 1;
                            next_outSetData = binaryOpReadData;
                        end

                        MOV_SCRATCHX: begin
                            next_scratchX = binaryOpReadData;
                        end

                        MOV_SCRATCHY: begin
                            next_scratchY = binaryOpReadData;
                        end

                        MOV_EXEC: begin
                            next_EXECRegister = binaryOpReadData[15:0];
                            next_EXECEnable = 1;
                            ignoreDelay = 1;
                        end

                        MOV_PC_STATUS: begin
                            next_PC = binaryOpReadData;
                        end

                        MOV_ISR: begin
                            isrEnable = 1;
                            isrBitReqLength = 0;
                            isrWriteData = binaryOpReadData;
                        end

                        MOV_OSR: begin
                            osrEnable = 1;
                            osrBitReqLength = 0;
                            reg_osrPullNow = 1;
                            osrWriteData = binaryOpReadData;
                        end
                    endcase    
                end

                IRQ: begin
                        //TODO: implement IRQ
                    next_PC = next_calculatedPC;
                end

                SET: begin
                    next_PC = next_calculatedPC;
                    // SETTING DESTINATION
                    case (instruction_condition)
                        3'b000: begin // PINS
                            next_outSetEnable = 1;
                            next_outNotSet = 0;
                            next_outSetPinsNotPindirs = 1;
                            next_outSetData = {{27{1'b0}}, instruction_data};
                        end

                        3'b001: begin // scratch X
                            next_scratchX = {{27{1'b0}}, instruction_data};
                        end

                        3'b010: begin // scratch Y
                            next_scratchY = {{27{1'b0}}, instruction_data};
                        end

                        3'b100: begin //PINDIRS
                            next_outSetEnable = 1;
                            next_outNotSet = 0;
                            next_outSetPinsNotPindirs = 0;
                            next_outSetData = {{27{1'b0}}, instruction_data};
                        end

                        default: begin //not defined
                        end
                    endcase

                end
            endcase
        end
    end
end

endmodule

/*
 * isr.v
 * openPIO Project
 * Author: Ismael Frei
 * EPFL - TCL 2025
 */

 
// ISR (Input Shift Register) module for Open PIO
// This module models the behavior of the ISR:
// - It accumulates incoming bits into a 32-bit register.
// - It supports two modes: full-word load (when in_bitReqLength==0) and partial shifting.
// - The shift direction is controlled at runtime (in_shiftDirection).
// - When in_pushNow is asserted, the register and valid counter are cleared (simulate a push).
// - out_requestPush is asserted if (current valid count + incoming bits) >= in_pushThreshold and auto-push is enabled.

module isr(
    input         clk,
    input         reset,             // active low reset
    input         in_shiftDirection, // 1 = right shift (new bits enter at MSB), 0 = left shift (new bits enter at LSB)
    input  [31:0] in_data,           // input data for shifting; if in_bitReqLength==0, full word load
    input         in_inEnable,       // enable shifting (for partial loads)
    input         in_pushNow,        // when high, perform a push (clear the ISR and valid count)
    input         in_autoPushEnable, // auto-push enable signal
    input  [4:0]  in_pushThreshold,  // threshold (0-32) for requesting an auto-push
    input  [4:0]  in_bitReqLength,   // number of bits to shift in this cycle; if 0, treat as full 32-bit load
    
    output [31:0] out_data,          // current ISR contents
    output        out_full,          // asserted when 32 valid bits have been shifted in
    output        out_requestPush    // asserted when (valid count + in_bitReqLength) >= in_pushThreshold (and auto-push is enabled)
);

    // Internal registers:
    reg [31:0] reg_data;
    reg [5:0]  reg_shiftCount; // counts valid bits (0 to 32)

    // Next-state signals:
    reg [31:0] next_data;
    reg [5:0]  next_shiftCount;

    // Temporary signal for the result of shifting in new bits.
    wire [31:0] shift_mask = (in_bitReqLength == 5'd0) ? 32'hFFFFFFFF : (1 << in_bitReqLength) - 1;

    wire [31:0] shiftedRegData = in_shiftDirection ? (reg_data >> in_bitReqLength) : (reg_data << in_bitReqLength);
    wire [31:0] shiftedNewData =    in_bitReqLength == 0 ? in_data :
                                    in_shiftDirection ? ((in_data & shift_mask) << (32 - in_bitReqLength)) : (in_data & shift_mask);


    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            reg_data <= 32'b0;
            reg_shiftCount <= 6'd0;
        end else begin
            reg_data <= next_data;
            reg_shiftCount <= next_shiftCount;
        end
    end

    
    // Combinational logic for next state.
    always @(*) begin
        // Default values
        next_data = reg_data;
        next_shiftCount = reg_shiftCount;
        

        if (in_inEnable) begin
            if (in_pushNow) begin
                // Push now at same time as new data is inserted.
                next_data = shiftedNewData; // Push, then insert new data.
                next_shiftCount = in_bitReqLength == 5'd0 ? 6'd32 : in_bitReqLength;
            end else if (in_bitReqLength == 5'd0) begin
                // Full word load: in_data is loaded as-is.
                next_data = in_data;
                next_shiftCount = 6'd32;
            end else begin
                // Normal shift operation without Push Now
                next_data = shiftedRegData | shiftedNewData;
                next_shiftCount = reg_shiftCount + in_bitReqLength;
            end
        end else if (in_pushNow) begin 
            // Push now without new data arriving
            next_data = 32'b0;
            next_shiftCount = 6'd0;
        end
    end

    assign out_data = reg_data;

    // The ISR is "full" when 32 valid bits are present.
    assign out_full = ((reg_shiftCount >= in_pushThreshold) & (in_pushThreshold != 5'b0)) | reg_shiftCount >= 6'd32;
    // out_requestPush is asserted if adding the next in_bitReqLength would meet or exceed the threshold and auto-push is enabled.
    assign out_requestPush =  out_full   & in_autoPushEnable 
                                | (((reg_shiftCount + in_bitReqLength) >= in_pushThreshold) & in_pushThreshold != 0 & in_autoPushEnable & in_inEnable)
                                | ((reg_shiftCount + in_bitReqLength) >= 6'd32 & in_autoPushEnable & in_inEnable);
    
endmodule

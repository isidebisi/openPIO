/*
 * osr.v
 * Author: Ismael Frei
 * EPFL - TCL 2025
 *
 */

module osr(
    input clk, reset, //active low reset
    input in_shiftDirection, // 1=right, 0=left
    input [31:0] in_data,   // data directly from FIFO
    input in_outEnable, in_refillNow, in_autoPullEnable,
    input [4:0] in_pullThreshold, in_bitReqLength,
    
    output [31:0] out_data,
    output out_empty, out_requestRefill
);

    reg [31:0] reg_data;
    reg [5:0] reg_shiftCount;

    reg [31:0]  shifted_data, temp_data, next_data;
    reg [5:0] next_shiftCount;
    wire [31:0] mask_gen;

    always @(posedge clk, negedge reset) begin
        if (!reset) begin
            reg_data <= 32'b0;
            reg_shiftCount <= 5'b0;
        end else begin
            reg_data <= next_data;
            reg_shiftCount <= next_shiftCount;
        end
    end

    always @(*) begin
        // default values
        next_data = reg_data;
        next_shiftCount = reg_shiftCount;


        if (in_shiftDirection) begin
            temp_data = reg_data;
            shifted_data = (in_bitReqLength == 0) ? 32'b0 : reg_data >> in_bitReqLength;
        end else begin
            // special case: 0 input length means full word with no shift
            temp_data = (in_bitReqLength == 0) ? reg_data : reg_data >> (32 - in_bitReqLength);
            shifted_data = (in_bitReqLength == 0) ? 32'b0 : reg_data << in_bitReqLength;
        end

        if (in_outEnable) begin
            next_data = shifted_data;
            next_shiftCount = (in_bitReqLength == 0) ? reg_shiftCount + 32 : reg_shiftCount + in_bitReqLength;
        end else begin
            next_data = reg_data;
            next_shiftCount = reg_shiftCount;
        end

        if (in_refillNow) begin
            next_data = in_data;
            next_shiftCount = 0;
        end
    end


assign mask_gen = (in_bitReqLength == 0) ? 32'hFFFFFFFF : (1 << in_bitReqLength) - 1;
assign out_data = temp_data & mask_gen;
assign out_empty = ((reg_shiftCount >= in_pullThreshold) & in_pullThreshold != 5'b0) | (reg_shiftCount >= 6'd32);
assign out_requestRefill =  (out_empty & in_autoPullEnable)
                            | (((reg_shiftCount + in_bitReqLength) >= in_pullThreshold) & in_pullThreshold != 0 & in_autoPullEnable & in_outEnable)
                            | ((reg_shiftCount + in_bitReqLength) >= 6'd32 & in_autoPullEnable & in_outEnable);

endmodule
/*
 * binaryOperations.v
 * Author: Ismael Frei
 * EPFL - TCL 2025
 *
 */

module binaryOperations(
    input[31:0] in_data,
    input[1:0] in_op,

    output[31:0] out_data
);

localparam NONE = 2'b00;
localparam INVERT = 2'b01;
localparam BIT_REVERSE = 2'b10;

wire [31:0] inversed_data, reversed_data;
assign inversed_data = ~in_data;
assign reversed_data = {in_data[0], in_data[1], in_data[2], in_data[3], in_data[4], in_data[5], in_data[6], in_data[7],
                        in_data[8], in_data[9], in_data[10], in_data[11], in_data[12], in_data[13], in_data[14], in_data[15],
                        in_data[16], in_data[17], in_data[18], in_data[19], in_data[20], in_data[21], in_data[22], in_data[23],
                        in_data[24], in_data[25], in_data[26], in_data[27], in_data[28], in_data[29], in_data[30], in_data[31]};

assign out_data = (in_op == NONE) ? in_data :
                  (in_op == INVERT) ? inversed_data :
                  (in_op == BIT_REVERSE) ? reversed_data : 32'b0;

endmodule
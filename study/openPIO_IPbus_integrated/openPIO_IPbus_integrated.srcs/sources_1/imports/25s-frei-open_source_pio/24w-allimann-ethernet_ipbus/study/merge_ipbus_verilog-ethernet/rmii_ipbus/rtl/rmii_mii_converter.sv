`resetall
`timescale 1ns / 1ps
`default_nettype none

/*
 * physical RMII to MII converter
 */


module rmii_mii_converter # 
(
    parameter TARGET = "GENERIC"
)
(
    input  wire rst,

    /*
     * MII interface
     */
    output  reg                      mii_rx_clk,
    output  reg [3:0]                mii_rxd,
    output  reg                      mii_rx_dv,
    output  reg                      mii_rx_er,
    output  reg                      mii_tx_clk,
    input   wire [3:0]               mii_txd,
    input   wire                     mii_tx_en,
    input   wire                     mii_tx_er,

    /*
     * RMII interface
     */
    input  wire [1:0]                rmii_rxd,
    input  wire                      rmii_rx_er,  
    input  wire                      rmii_crs_dv,
    output reg [1:0]                 rmii_txd,
    output reg                       rmii_tx_en,

    input  wire                      rmii_ref_clk

);

// Create mii clk

reg mii_clk_reg = 1'b0; 

assign mii_rx_clk = mii_clk_reg;
assign mii_tx_clk = mii_clk_reg;

always_ff @(posedge rmii_ref_clk, posedge rst) begin 
    if (rst) begin
        mii_clk_reg <= 1'b0;
    end else begin
        mii_clk_reg <= !mii_clk_reg;
    end
end

//RECEIVE
//useful signals/reg
reg [3:0] mii_rxd_reg;
reg       mii_rx_dv_reg;
reg       mii_rx_er_reg;

reg [3:0] mii_rxd_next;
reg [3:0] mii_rxd_next_reg;
reg [3:0] mii_rxd_int;  //intermediate register for receive synchronous
reg [3:0] mii_rxd_int_reg;

reg       mii_rx_dv_next;
reg       mii_rx_dv_next_reg;
reg       mii_rx_er_next;

reg [1:0] rmii_rxd_reg;
reg       rmii_crs_dv_reg;

//assign to output
assign mii_rxd   = mii_rxd_reg;
assign mii_rx_dv = mii_rx_dv_reg;
assign mii_rx_er = mii_rx_er_reg;


//FSM with 5 states : idle, receive sync, receive async, receive preamble sync, receive preamble async

localparam [2:0]
    STATE_IDLE = 3'd0,
    STATE_RX_SYNC = 3'd1,
    STATE_RX_ASYNC = 3'd2,
    STATE_RX_PRE_SYNC = 3'd3,
    STATE_RX_PRE_ASYNC = 3'd4;

reg [2:0] state_reg;
reg [2:0] state_next;

always_ff @(posedge rmii_ref_clk, posedge rst) begin 
    if (rst) begin
        state_reg     <= STATE_IDLE;

        mii_rxd_next_reg   <= 4'b0;
        mii_rxd_int_reg    <= 4'b0;
        mii_rx_dv_next_reg <= 1'b0;

    end else begin
        state_reg          <= state_next;
        mii_rxd_next_reg   <= mii_rxd_next;
        mii_rxd_int_reg    <= mii_rxd_int;
        mii_rx_dv_next_reg <= mii_rx_dv_next;
        rmii_rxd_reg       <= rmii_rxd;
        rmii_crs_dv_reg    <= rmii_crs_dv;
    end
end

always_ff @(posedge mii_clk_reg, posedge rst) begin
    if (rst) begin
        mii_rxd_reg   <= 4'b0;
        mii_rx_dv_reg <= 1'b0;
        mii_rx_er_reg <= 1'b0;
    end else begin
        mii_rxd_reg   <= mii_rxd_next;
        mii_rx_dv_reg <= mii_rx_dv_next;
        mii_rx_er_reg <= mii_rx_er_next;
    end 
end

always_comb begin
    //default statements
    state_next     <= state_reg;
    mii_rx_er_next <= mii_rx_er_reg;
    mii_rx_dv_next <= mii_rx_dv_reg;
    mii_rxd_next   <= mii_rxd_reg;
    mii_rxd_int    <= mii_rxd_reg;


    //FSM Logic
    case (state_reg)
        STATE_IDLE: begin
            if (rmii_crs_dv) begin
                state_next <= mii_rx_clk == 1'b1 ? STATE_RX_PRE_SYNC : STATE_RX_PRE_ASYNC;
            end
        end

        STATE_RX_PRE_SYNC: begin 
            if (mii_rx_clk) begin  /* rising edge */ 
                mii_rxd_int      <= {rmii_rxd_reg, mii_rxd_int_reg[1:0]};
                mii_rxd_next     <= mii_rxd_next_reg;
                mii_rx_dv_next   <= rmii_crs_dv_reg;  
            end else begin         /* falling edge */ 
                mii_rxd_next     <= mii_rxd_int_reg;
                mii_rxd_int      <= {mii_rxd_int_reg[3:2], rmii_rxd_reg};
                mii_rx_er_next   <= rmii_rx_er; 
                mii_rx_dv_next   <= mii_rx_dv_next_reg;
            end

            //resynchronize at start frame delimiter
            if (rmii_crs_dv && (rmii_rxd == 2'b11)) begin
                state_next <= mii_rx_clk == 1'b1 ? STATE_RX_ASYNC : STATE_RX_SYNC;
            end

        end

        STATE_RX_PRE_ASYNC: begin
            if (mii_rx_clk) begin  /* rising edge  */  
                mii_rxd_int      <= {mii_rxd_int_reg[3:2], rmii_rxd_reg};
                mii_rxd_next     <= mii_rxd_next_reg;
            end else begin         /* falling edge */ 
                mii_rxd_int       <= {rmii_rxd_reg, mii_rxd_int_reg[1:0]};
                mii_rxd_next      <= {rmii_rxd_reg, mii_rxd_int_reg[1:0]};
                mii_rx_dv_next    <= rmii_crs_dv_reg;  
                mii_rx_er_next    <= rmii_rx_er;  
            end

            //resynchronize at start frame delimiter
            if (rmii_crs_dv && (rmii_rxd == 2'b11)) begin
                state_next <= mii_rx_clk == 1'b1 ? STATE_RX_ASYNC : STATE_RX_SYNC;
            end
        end

        STATE_RX_SYNC: begin
            if (mii_rx_clk) begin  /* rising edge*/ 
                mii_rxd_int      <= {rmii_rxd_reg, mii_rxd_int_reg[1:0]};
                mii_rxd_next     <= mii_rxd_next_reg;
                mii_rx_dv_next   <= rmii_crs_dv_reg;  
            end else begin         /* falling edge */ 
                mii_rxd_next     <= mii_rxd_int_reg;
                mii_rxd_int      <= {mii_rxd_int_reg[3:2], rmii_rxd_reg};
                mii_rx_er_next   <= rmii_rx_er; 
                mii_rx_dv_next   <= mii_rx_dv_next_reg;
            end


            if (!rmii_crs_dv && !mii_rx_dv) begin
                state_next <= STATE_IDLE;
            end
        end

        STATE_RX_ASYNC: begin
            if (mii_rx_clk) begin  /* rising edge  */  
                mii_rxd_int      <= {mii_rxd_int_reg[3:2], rmii_rxd_reg};
                mii_rxd_next     <= mii_rxd_next_reg;
            end else begin         /* falling edge */ 
                mii_rxd_int       <= {rmii_rxd_reg, mii_rxd_int_reg[1:0]};
                mii_rxd_next      <= {rmii_rxd_reg, mii_rxd_int_reg[1:0]};
                mii_rx_dv_next    <= rmii_crs_dv_reg;  
                mii_rx_er_next    <= rmii_rx_er;  
            end


            if (!rmii_crs_dv&& !mii_rx_dv) begin
                state_next <= STATE_IDLE;
            end
        end
    endcase


end

//TRANSMIT

//rmii registers
reg [1:0] rmii_txd_reg;
reg       rmii_tx_en_reg;
reg [3:0] rmii_txd_next;

//mii registers
reg       mii_tx_en_reg;

//assign to output 
assign rmii_tx_en = rmii_tx_en_reg; 
assign rmii_txd   = rmii_txd_reg;


//sync on rmii clk 
//mii clk sync with rmii clk

always_ff @(posedge rmii_ref_clk, posedge rst) begin
    if (rst) begin
        rmii_tx_en_reg <= 1'b0;
        rmii_txd_reg   <= 2'b0;
        mii_tx_en_reg  <= 1'b0;
        rmii_txd_next  <= 2'b0;
    end else begin
        if (mii_rx_clk) begin  /* rising edge */
            rmii_txd_reg  <= rmii_txd_next[3:2]; // second 2 bits
            rmii_txd_next <= mii_txd; 
            mii_tx_en_reg <= mii_tx_en;
        end else begin         /* falling edge */
            rmii_txd_reg  <= rmii_txd_next[1:0]; // first 2 bits 

        end 

        rmii_tx_en_reg <= mii_tx_en_reg;
    end
end

endmodule

`resetall
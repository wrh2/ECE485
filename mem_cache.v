// Author: Ahmed Abdulkareem
// Date: 11/07/2015
// ECE 485/585
// Memory Cache


// This module implements the memory cache
module mem_cache(data_in,
                 address,
                 data_out,
                 RW_,
                 clk);

    input [7:0] data_in;
    input [3:0] address;
    input RW_;
    output [7:0] data_out;
    
    reg [7:0] memory[0:15];
    

    assign data_out = ~RW_ ? 0 : memory[addr]; // get the word out if it's a read otherwise keep output 0

    // if it's a write
    always @ (posedge clk) begin
        if (!RW_) 
            mem[addr] = data_in;
    end


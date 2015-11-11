// Author: Ahmed Abdulkareem
// Date: 11/07/2015
// ECE 485/585
// Cache Simulator


// This module implements a 2-way set associative cache
// with 16 cache lines, an address bus of 16 bits, and
// data bus of 8 bits.
// index is the index to select a set (4 bits)
// tag is the tag address (10 bits)
// word is the byte select (1 bit)
// data is the data to be inserted (8 bits)
// RW_ is READ/WRITE# bit. Write is active low (1 bit)
// clk is clock 
// data out is output data (8 bits)
// valid is the valid bit (1 bit)
// hit is 1 when it's a hit (1 bit)
module two_way_cache(index,
                     tag,
                     word,
                     data_in,
                     RW_,
                     clk, 
                     data_out,
                     valid,
                     hit);

    input [3:0] index;
    input [9:0] tag;
    input [7:0] data_in;
    input word;
    input RW_;
    input clk;
    output [7:0] data_out;
    output valid;
    output hit;

    wire [7:0] word0, word1;



    assign write_word0 = ~RW_ & ~word;
    assign write_word1 = ~RW_ & word;

    mem_cache cache0(data_in, index, word0, write_word0, clk);
    mem_cache cache1(data_in, index, word1, write_word1, clk);


    assign data_out = ~RW_ ? 8'h00 : word ? (word1 : word0);


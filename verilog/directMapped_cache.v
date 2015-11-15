/* Author: Ahmed Abdulkareem, William Harrington
   Date: 11/07/2015
   ECE 485/585
   Cache Simulator
*/

module directMapped_cache(address,
			  data_in,
			  write,
			  clk,
			  data_out,
			  hit,
			  valid,tag);

			  /*
			    Module description

			    This module instantiates the cache module described by cache.v
			    to make up one set of the cache.

			    Designed for simplicity and easy instantiation,
			    this module controls the internal workings of the cache.
			  */


			  /* inputs */
			  input [15:0] address; /* address to read from/write to */
			  input [7:0] data_in;  /* data input to write */
			  input write, clk;     /* control signal, and clock */

			  /* outputs */
			  output [7:0] data_out; /* data output from the cache */
			  output hit, valid;     /* hit and valid outputs */
			  output [10:0] tag;     /* tag bits output */

			  wire [7:0] d_out;      /* wire that is connected to data_out */
			  wire [10:0] tag_out;   /* wire that is connected to tag */
			  wire isHit, isValid;   /* wires connected to hit and valid outputs */

			  /* instantiation of cache module described in cache.v */
			  cache cache1(address[4:1], address[15:5], address[0], data_in, write, 1, clk, d_out, tag_out, isValid, isHit);

			  /* assign outputs */
			  assign hit = isHit; /* set if we got a hit from the cache */
			  assign valid = isValid; /* set if we got valid from the cache */
			  assign data_out = d_out; /* data if we have any, 0 otherwise */
			  assign tag = tag_out; /* tag bits if we got a hit */

endmodule
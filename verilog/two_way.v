/* Author: Ahmed Abdulkareem, William Harrington
   Date: 11/07/2015
   ECE 485/585
   Cache Simulator
*/

module two_way_cache(address, 
                     data_in, 
                     write, 
                     clk,
                     data_out,
                     hit
                     );
                     
		     /*
			Module description
			
			This module takes the directMapped_cache module described by directMapped_cahce.v
			and builds upon it by instantiating it twice, creating an expandable 2-way set 
			associative cache with 16 cache lines, an address bus of 16 bits, and data bus of 8 bits.

			There is an attempt to implement a first in first out policy but it is not fully functional.
			In hindsight, a better place to do this would of been mem_cache.v since that is really the
			memory controller.
		      */

		     /* inputs */
  		     input [15:0] address; /* address to read from/write to */
  		     input [7:0] data_in;  /* data input to write */
  		     input write, clk;     /* control signal, and clock */

		     /* outputs */
		     output [7:0] data_out; /* data output if we have any, 0 otherwise */
		     output hit;  	    /* hit output */

  		     wire [10:0] tag0, tag1; /* tag bits */
  		     wire [7:0] data_out0, data_out1; /* data bits */
		     wire valid0, valid1; /* valid bits */
		     wire hit0, hit1;

		     reg [10:0] fifo_array0[0:15]; /* arrays for keeping track of cache lines to implement first in first out replacement policy */
		     reg [10:0] fifo_array1[0:15];

		     /* instantiation of direct-mapped cache described by directMapped_cache.v */
		     directMapped_cache cache0(address, data_in, write, clk, data_out0, hit0, valid0, tag0);
		     directMapped_cache cache1(address, data_in, write, clk, data_out1, hit1, valid1, tag1);

		     /* determine if cache set 0 or 1 is selected */
		     assign select_0 = (address[15:5] == tag0) & valid0;
		     assign select_1 = (address[15:5] == tag1) & valid1;

		     /* if either select signal is set, we got a hit */
		     assign hit = select_0 | select_1;

		     /* data is output if we have a hit, data out is produced based on select signals, otherwise line is high impedance */
		     assign data_out = hit ? (select_0 ? data_out0 : data_out1) : 8'bzzzzzzzz;
endmodule
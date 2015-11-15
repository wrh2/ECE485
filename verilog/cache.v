/* Author: Ahmed Abdulkareem, William Harrington
   Date: 11/07/2015
   ECE 485/585
   Cache Simulator
*/

module cache(index,
             tag_in,
             word,
             data_in,
             write,
	     valid_in,
             clk, 
             data_out,
	     tag_out,
             valid_out,
             hit);

	     /*
		Module description

		This module implements an expandable cache set with 16 cache lines,
		an address bus of 16 bits, and data bus of 8 bits.

		The implementation utilizes 4 simplistic state machines described by mem_cache.v
		The mem_cache module is parameterized such that the cache lines can be broken up into
		four separate groups: valid bit, tag bits, data bits (word0, word 1).

		Design goals for this module were expandability and simplicity.
		For these reasons, there is no state machine here as it is not needed, and the tag_out,
		data_out, and valid_out can be connected easily to other modules.
	     */

	     /* inputs */
    	     input [3:0] index;			   /* cache line to select, 4 bits wide */
    	     input [10:0] tag_in; 		   /* an identifier for a specific line of the cache, 11 bits wide */
    	     input [7:0] data_in;    		   /* data input, 8 bits wide */
	     input valid_in, write, word, clk;	   /* valid bit input, write control signal, byte select, clock */
	     
	     /* outputs */
	     output [10:0] tag_out;		   /* last tag written, 11 bits wide */
    	     output [7:0] data_out;		   /* data output, 8 bits wide */
    	     output valid_out, hit;		   /* valid bit output, hit output */

	     /* words to write */
    	     wire [7:0] word0, word1;

	     assign match = (tag_in == tag_out);   /* check for a match */

	     /* control signals for instantiations below */
	     assign write_word0 = write & ~word;   /* determine if byte selection is for word 0 */
	     assign write_word1 = write & word;	   /* determine if byte selection is for word 1 */

	     assign write_tag = write;	  	   /* for writing tag bits */
	     assign write_valid = write;	   /* for writing valid bit */

	     /* 4 instantiations of mem_cache module from mem_cache.v */
	     /* each instantiation contains data for one of the three */
	     /* columns, if you will, to take advantage of the simple */
	     /* memory for the cache  	      		       	      */
    	     mem_cache #(8)  word_block0  (data_in,  index, word0, write_word0, clk); /* Cache data for word0.
	     	       	     		  	     	    	   		      	 When write_word0 goes high on the positive edge of the clock, word0 is written to
											 the line specified by index in the cache memory.
	     	       	     		  	     	    	   		       */
    	     mem_cache #(8)  word_block1  (data_in,  index, word1, write_word1, clk); /* Cache data for word1.
	     	       	     		  	     	    	   		      	 When write_word1 goes high on the positive edge of the clock, word1 is written to
											 the line specified by index in the cache memory.
	     	       	     		  	     	    	   		      */
	     mem_cache #(11) tag_block    (tag_in,   index, tag_out, write_tag, clk); /* Tag bits for cache line.
	     	       	     		  	     	    	     		      	 When write_tag goes high on the positive edge of the clock, tag_in is written to the
											 line specified by index in the cache memory.
	     	       	     		  	     	    	     		      */
	     mem_cache       valid_block  (valid_in, index, valid_b, write_valid, clk); /* Valid bit for cache line.
	     		     		  	     	    	     		  	   When write_valid goes high on the positive edge of the clock, valid_in is written
											   to the line specified by index in the cache memory.
	     		     		  	     	    	     		  	*/

	     assign hit = match;							/* We have a hit if match is set */
    	     assign data_out = write ? 8'h00 : (word ? word1 : word0);			/* data is output if write is low, otherwise output is 0 */
	     assign valid_out = ~write & valid_b;      	       				/* valid output, only applicable to a read, otherwise 0 */
	
endmodule

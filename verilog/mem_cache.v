/* Author: Ahmed Abdulkareem, William Harrington
   Date: 11/07/2015
   ECE 485/585
   Memory Cache
*/

module mem_cache(data_in,
                 address,
                 data_out,
                 write,
                 clk);

		 /* 
		    Module description

		    This module implements the memory sets for the cache.
		    One of the main design goals behind this implementation was simplicity.
		    Because of this, there is only one control signal -- write.
		    This makes the state machine for the module only have two states -- read and write.

		    Regardless of the current state, a high write signal will cause the next state to be write.
		    And of course, a low write signal will cause the next state to be read.

		    When the module detects a low signal for write on the positive edge of the clock and a valid
		    address, which isn't really an address instead it specifies a cache line, then data output
		    is provided via the data_out signal. Otherwise, the data_out signal goes low and whatever data is
		    present on the data line gets written to memory.

		    Another main design goal behind this implementation was expandability.
		    Because of this, the Size parameter allows you to determine the bit width of the memory set
		    when instantiating the module in other files. 
		 */
                 
		 /* parameter(s) */
		 parameter Size = 1;

		 /* inputs */
    		 input [Size - 1:0] data_in; /* specifies data input, only written if write signal is high */
    		 input [3:0] address;        /* specifies a cache line */
    		 input write;		     /* main control signal, see description for more details*/
		 input clk;		     /* clock, duh. */

		 /* outputs 
		    parameterized by Size so the bit width can be adjusted
		 */
		 output [Size - 1:0] data_out; /* data from cache line */
    
		/* cache memory
		   parameterized by Size so the bit width can be adjusted
		   but always 16 lines 
		   */
		reg [Size - 1:0] memory[0:15];
		assign data_out = write ? 0 : memory[address]; // get the word out if it's a read otherwise keep output 0
		
		/* always executed on the positive edge of the clk signal */
		always @ (posedge clk) begin
		       if (write) memory[address] = data_in;
		end
endmodule

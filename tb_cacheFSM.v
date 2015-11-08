module tb_cacheFSM;

reg r;
reg w;
reg clk;
wire [1:0] state;

initial begin
    $from_myhdl(
        r,
        w,
        clk
    );
    $to_myhdl(
        state
    );
end

cacheFSM dut(
    r,
    w,
    clk,
    state
);

endmodule

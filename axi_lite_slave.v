// AXI4-Lite register slave: 4 registers, 32-bit data
// Register address = addr[3:2]  (0x0, 0x4, 0x8, 0xC)
module axi_lite_slave (
    input  wire        clk,
    input  wire        rst_n,

    // Write address channel (AW)
    input  wire [3:0]  awaddr,
    input  wire        awvalid,
    output reg         awready,

    // Write data channel (W)
    input  wire [31:0] wdata,
    input  wire [3:0]  wstrb,
    input  wire        wvalid,
    output reg         wready,

    // Write response channel (B)
    output reg  [1:0]  bresp,
    output reg         bvalid,
    input  wire        bready,

    // Read address channel (AR)
    input  wire [3:0]  araddr,
    input  wire        arvalid,
    output reg         arready,

    // Read data channel (R)
    output reg  [31:0] rdata,
    output reg  [1:0]  rresp,
    output reg         rvalid,
    input  wire        rready
);

    reg [31:0] regs [0:3];
    integer i;

    // ---------------- WRITE SIDE ----------------
    always @(posedge clk) begin
        if (!rst_n) begin
            awready <= 1'b0;
            wready  <= 1'b0;
            bvalid  <= 1'b0;
            bresp   <= 2'b00;
            for (i = 0; i < 4; i = i + 1) regs[i] <= 32'd0;
        end else begin
            awready <= 1'b0;
            wready  <= 1'b0;

            // accept address and data together
            if (awvalid && wvalid && !awready && !bvalid) begin
                awready <= 1'b1;
                wready  <= 1'b1;
                if (wstrb[0]) regs[awaddr[3:2]][7:0]   <= wdata[7:0];
                if (wstrb[1]) regs[awaddr[3:2]][15:8]  <= wdata[15:8];
                if (wstrb[2]) regs[awaddr[3:2]][23:16] <= wdata[23:16];
                if (wstrb[3]) regs[awaddr[3:2]][31:24] <= wdata[31:24];
            end

            // send the response one cycle after the handshake
            if (awready) begin
                bvalid <= 1'b1;
                bresp  <= 2'b00;   // OKAY
            end

            if (bvalid && bready) bvalid <= 1'b0;
        end
    end

    // ---------------- READ SIDE ----------------
    always @(posedge clk) begin
        if (!rst_n) begin
            arready <= 1'b0;
            rvalid  <= 1'b0;
            rdata   <= 32'd0;
            rresp   <= 2'b00;
        end else begin
            arready <= 1'b0;

            if (arvalid && !arready && !rvalid) begin
                arready <= 1'b1;
                rdata   <= regs[araddr[3:2]];
            end

            if (arready) begin
                rvalid <= 1'b1;
                rresp  <= 2'b00;   // OKAY
            end

            if (rvalid && rready) rvalid <= 1'b0;
        end
    end

endmodule
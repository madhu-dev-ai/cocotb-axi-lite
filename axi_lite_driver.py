from cocotb.triggers import RisingEdge, ClockCycles


class AxiLiteDriver:
    """Drives the AXI4-Lite slave: one write or one read at a time."""

    def __init__(self, dut):
        self.dut = dut

    async def reset(self):
        d = self.dut
        d.awaddr.value = 0
        d.awvalid.value = 0
        d.wdata.value = 0
        d.wstrb.value = 0
        d.wvalid.value = 0
        d.bready.value = 0
        d.araddr.value = 0
        d.arvalid.value = 0
        d.rready.value = 0
        d.rst_n.value = 0
        await ClockCycles(d.clk, 3)
        d.rst_n.value = 1
        await ClockCycles(d.clk, 2)

    async def write(self, addr, data, strb=0xF):
        d = self.dut
        d.awaddr.value = addr
        d.awvalid.value = 1
        d.wdata.value = data
        d.wstrb.value = strb
        d.wvalid.value = 1
        d.bready.value = 1

        while True:
            await RisingEdge(d.clk)
            if d.awready.value == 1:
                break

        d.awvalid.value = 0
        d.wvalid.value = 0

        while True:
            await RisingEdge(d.clk)
            if d.bvalid.value == 1:
                break

        resp = int(d.bresp.value)
        await ClockCycles(d.clk, 2)
        return resp

    async def read(self, addr):
        d = self.dut
        d.araddr.value = addr
        d.arvalid.value = 1
        d.rready.value = 1

        while True:
            await RisingEdge(d.clk)
            if d.arready.value == 1:
                break

        d.arvalid.value = 0

        while True:
            await RisingEdge(d.clk)
            if d.rvalid.value == 1:
                break

        data = int(d.rdata.value)
        resp = int(d.rresp.value)
        await ClockCycles(d.clk, 2)
        return data, resp
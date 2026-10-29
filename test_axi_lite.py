import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_write_then_read(dut):
    # Start a 10 ns clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    # Set all inputs to 0
    dut.awaddr.value = 0
    dut.awvalid.value = 0
    dut.wdata.value = 0
    dut.wstrb.value = 0
    dut.wvalid.value = 0
    dut.bready.value = 0
    dut.araddr.value = 0
    dut.arvalid.value = 0
    dut.rready.value = 0

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # ---- WRITE 0xDEADBEEF to address 0x4 ----
    dut.awaddr.value = 0x4
    dut.awvalid.value = 1
    dut.wdata.value = 0xDEADBEEF
    dut.wstrb.value = 0xF
    dut.wvalid.value = 1
    dut.bready.value = 1

    # Wait until the slave accepts the write
    while True:
        await RisingEdge(dut.clk)
        if dut.awready.value == 1:
            break

    # Drop the write request
    dut.awvalid.value = 0
    dut.wvalid.value = 0

    # Wait for the write response
    while True:
        await RisingEdge(dut.clk)
        if dut.bvalid.value == 1:
            break
    dut._log.info(f"Write response bresp = {dut.bresp.value}")

    await ClockCycles(dut.clk, 2)

    # ---- READ from address 0x4 ----
    dut.araddr.value = 0x4
    dut.arvalid.value = 1
    dut.rready.value = 1

    while True:
        await RisingEdge(dut.clk)
        if dut.arready.value == 1:
            break

    dut.arvalid.value = 0

    while True:
        await RisingEdge(dut.clk)
        if dut.rvalid.value == 1:
            break

    got = int(dut.rdata.value)
    dut._log.info(f"Read back 0x{got:08X}")
    assert got == 0xDEADBEEF, f"Expected 0xDEADBEEF but got 0x{got:08X}"
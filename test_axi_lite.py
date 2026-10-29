import cocotb
from cocotb.clock import Clock

from axi_lite_driver import AxiLiteDriver
from axi_lite_monitor import AxiLiteMonitor
from axi_lite_scoreboard import AxiLiteScoreboard
from axi_lite_coverage import AxiLiteCoverage


@cocotb.test()
async def test_write_then_read_all_regs(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drv = AxiLiteDriver(dut)
    scb = AxiLiteScoreboard(dut)
    cov = AxiLiteCoverage(dut)
    mon = AxiLiteMonitor(dut, scb, cov)

    await drv.reset()
    mon.start()

    values = {
        0x0: 0x11111111,
        0x4: 0xDEADBEEF,
        0x8: 0xCAFEBABE,
        0xC: 0x12345678,
    }

    # Write all 4 registers
    for addr, data in values.items():
        resp = await drv.write(addr, data)
        assert resp == 0, f"Write to 0x{addr:X} gave resp {resp}"

    # Read them all back (the scoreboard checks each one by itself)
    for addr in values:
        got, resp = await drv.read(addr)
        assert resp == 0, f"Read from 0x{addr:X} gave resp {resp}"

    assert len(mon.writes) == 4, f"Monitor saw {len(mon.writes)} writes, expected 4"
    assert len(mon.reads) == 4, f"Monitor saw {len(mon.reads)} reads, expected 4"

    scb.report()
    cov.report()
import random

import cocotb
from cocotb.clock import Clock

from axi_lite_driver import AxiLiteDriver
from axi_lite_monitor import AxiLiteMonitor
from axi_lite_scoreboard import AxiLiteScoreboard
from axi_lite_coverage import AxiLiteCoverage


def make_env(dut):
    """Builds the whole testbench: clock, driver, scoreboard, coverage, monitor."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    drv = AxiLiteDriver(dut)
    scb = AxiLiteScoreboard(dut)
    cov = AxiLiteCoverage(dut)
    mon = AxiLiteMonitor(dut, scb, cov)
    return drv, mon, scb, cov


@cocotb.test(timeout_time=200, timeout_unit="us")
async def test_basic(dut):
    drv, mon, scb, cov = make_env(dut)
    await drv.reset()
    mon.start()

    values = {
        0x0: 0x11111111,
        0x4: 0xDEADBEEF,
        0x8: 0xCAFEBABE,
        0xC: 0x12345678,
    }

    for addr, data in values.items():
        resp = await drv.write(addr, data)
        assert resp == 0, f"Write to 0x{addr:X} gave resp {resp}"

    for addr in values:
        got, resp = await drv.read(addr)
        assert resp == 0, f"Read from 0x{addr:X} gave resp {resp}"

    assert len(mon.writes) == 4, f"Monitor saw {len(mon.writes)} writes, expected 4"
    assert len(mon.reads) == 4, f"Monitor saw {len(mon.reads)} reads, expected 4"

    scb.report()


@cocotb.test(timeout_time=200, timeout_unit="us")
async def test_random(dut):
    random.seed(1)
    drv, mon, scb, cov = make_env(dut)
    await drv.reset()
    mon.start()

    # Write every register once first, so reads never see unknown values
    for addr in (0x0, 0x4, 0x8, 0xC):
        await drv.write(addr, random.getrandbits(32))

    # 200 random operations
    for _ in range(200):
        addr = random.choice([0x0, 0x4, 0x8, 0xC])
        if random.random() < 0.5:
            data = random.getrandbits(32)
            strb = random.choice([0xF, 0xF, 0x1, 0x2, 0x4, 0x8, 0x3, 0xC, 0x5])
            resp = await drv.write(addr, data, strb)
            assert resp == 0, f"Write to 0x{addr:X} gave resp {resp}"
        else:
            got, resp = await drv.read(addr)
            assert resp == 0, f"Read from 0x{addr:X} gave resp {resp}"

    # Read all 4 registers at the end so nothing is left unchecked
    for addr in (0x0, 0x4, 0x8, 0xC):
        await drv.read(addr)

    scb.report()
    percent = cov.report()
    assert percent == 100.0, f"Coverage only {percent:.0f}%, expected 100%"
import cocotb
from cocotb.clock import Clock

from axi_lite_driver import AxiLiteDriver
from axi_lite_monitor import AxiLiteMonitor


@cocotb.test()
async def test_write_then_read_all_regs(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drv = AxiLiteDriver(dut)
    mon = AxiLiteMonitor(dut)

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

    # Read them all back
    for addr, expected in values.items():
        got, resp = await drv.read(addr)
        assert resp == 0, f"Read from 0x{addr:X} gave resp {resp}"
        assert got == expected, (
            f"Addr 0x{addr:X}: expected 0x{expected:08X}, got 0x{got:08X}"
        )

    # The monitor must have seen exactly what the driver did
    assert len(mon.writes) == 4, f"Monitor saw {len(mon.writes)} writes, expected 4"
    assert len(mon.reads) == 4, f"Monitor saw {len(mon.reads)} reads, expected 4"

    for (addr, data, strb), (exp_addr, exp_data) in zip(mon.writes, values.items()):
        assert addr == exp_addr and data == exp_data, "Monitor write record is wrong"

    for (addr, data), (exp_addr, exp_data) in zip(mon.reads, values.items()):
        assert addr == exp_addr and data == exp_data, "Monitor read record is wrong"
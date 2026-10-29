import cocotb
from cocotb.clock import Clock

from axi_lite_driver import AxiLiteDriver


@cocotb.test()
async def test_write_then_read_all_regs(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drv = AxiLiteDriver(dut)
    await drv.reset()

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
        dut._log.info(f"Read 0x{addr:X} -> 0x{got:08X}")
        assert resp == 0, f"Read from 0x{addr:X} gave resp {resp}"
        assert got == expected, (
            f"Addr 0x{addr:X}: expected 0x{expected:08X}, got 0x{got:08X}"
        )
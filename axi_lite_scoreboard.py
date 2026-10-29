class AxiLiteScoreboard:
    """Reference model: keeps its own copy of the 4 registers and checks every read."""

    def __init__(self, dut):
        self.dut = dut
        self.model = [0, 0, 0, 0]
        self.checks = 0
        self.errors = []

    def on_write(self, addr, data, strb):
        idx = (addr >> 2) & 0x3
        for byte in range(4):
            if (strb >> byte) & 1:
                mask = 0xFF << (8 * byte)
                self.model[idx] = (self.model[idx] & ~mask) | (data & mask)

    def on_read(self, addr, data):
        idx = (addr >> 2) & 0x3
        expected = self.model[idx]
        self.checks += 1
        if data != expected:
            msg = f"SCB MISMATCH addr=0x{addr:X}: expected 0x{expected:08X}, got 0x{data:08X}"
            self.dut._log.error(msg)
            self.errors.append(msg)
        else:
            self.dut._log.info(f"SCB ok       addr=0x{addr:X} data=0x{data:08X}")

    def report(self):
        assert self.checks > 0, "Scoreboard checked nothing"
        assert not self.errors, f"{len(self.errors)} scoreboard mismatches"
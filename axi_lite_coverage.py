class AxiLiteCoverage:
    """Counts which situations the tests have hit (10 bins)."""

    def __init__(self, dut):
        self.dut = dut
        self.bins = {}
        for i in range(4):
            self.bins[f"write_reg{i}"] = 0
            self.bins[f"read_reg{i}"] = 0
        self.bins["write_full_strobe"] = 0
        self.bins["write_partial_strobe"] = 0

    def sample_write(self, addr, strb):
        self.bins[f"write_reg{(addr >> 2) & 0x3}"] += 1
        if strb == 0xF:
            self.bins["write_full_strobe"] += 1
        elif strb != 0:
            self.bins["write_partial_strobe"] += 1

    def sample_read(self, addr):
        self.bins[f"read_reg{(addr >> 2) & 0x3}"] += 1

    def percent(self):
        hit = sum(1 for count in self.bins.values() if count > 0)
        return 100.0 * hit / len(self.bins)

    def report(self):
        for name, count in self.bins.items():
            mark = "HIT " if count > 0 else "MISS"
            self.dut._log.info(f"COV {mark} {name}: {count}")
        self.dut._log.info(f"COV total: {self.percent():.0f}%")
        return self.percent()
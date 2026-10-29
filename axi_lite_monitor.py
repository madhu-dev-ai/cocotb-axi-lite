import cocotb
from cocotb.triggers import RisingEdge


def high(sig):
    return str(sig.value) == "1"


class AxiLiteMonitor:
    """Watches the bus and records every write and read."""

    def __init__(self, dut):
        self.dut = dut
        self.writes = []   # each item: (addr, data, strb)
        self.reads = []    # each item: (addr, data)
        self._read_addrs = []

    def start(self):
        cocotb.start_soon(self._watch_writes())
        cocotb.start_soon(self._watch_reads())

    async def _watch_writes(self):
        d = self.dut
        while True:
            await RisingEdge(d.clk)
            if high(d.awvalid) and high(d.awready) and high(d.wvalid) and high(d.wready):
                item = (int(d.awaddr.value), int(d.wdata.value), int(d.wstrb.value))
                self.writes.append(item)
                d._log.info(f"MON write addr=0x{item[0]:X} data=0x{item[1]:08X} strb=0x{item[2]:X}")

    async def _watch_reads(self):
        d = self.dut
        while True:
            await RisingEdge(d.clk)
            if high(d.arvalid) and high(d.arready):
                self._read_addrs.append(int(d.araddr.value))
            if high(d.rvalid) and high(d.rready):
                addr = self._read_addrs.pop(0)
                data = int(d.rdata.value)
                self.reads.append((addr, data))
                d._log.info(f"MON read  addr=0x{addr:X} data=0x{data:08X}")
\# cocotb-axi-lite



!\[CI](https://github.com/madhu-dev-ai/cocotb-axi-lite/actions/workflows/ci.yml/badge.svg)



Verification of an AXI4-Lite register slave (4 registers, 32-bit data, byte strobes) using cocotb and Python, with a layered testbench.



\## What is verified



The design has 5 channels (AW, W, B, AR, R) with valid/ready handshakes. Writes support byte strobes, so a write can change only some bytes of a register.



\## Testbench structure



| Component | File | Job |

|---|---|---|

| Driver | `axi\_lite\_driver.py` | Does the write and read handshakes |

| Monitor | `axi\_lite\_monitor.py` | Watches the bus and records every transaction |

| Scoreboard | `axi\_lite\_scoreboard.py` | Keeps a reference copy of the registers and checks every read |

| Coverage | `axi\_lite\_coverage.py` | Counts 10 bins (each register written and read, full and partial strobes) |

| Tests | `test\_axi\_lite.py` | `test\_basic` and `test\_random` (both have a 200 us timeout) |



`test\_random` runs 200 random writes and reads with random byte strobes and reaches 10/10 coverage bins.



\## Bug stories



\### Bug 1: byte strobe ignored



I changed the design so byte 1 was always written, even when its strobe bit was 0.



\- `test\_basic` \*\*passed\*\*. It only writes with full strobe (`0xF`), so it never exposed the bug.

\- `test\_random` \*\*failed\*\*. The scoreboard reported `SCB MISMATCH addr=0x0: expected 0x7ED4B1F5, got 0x7ED4D5F5`. Only byte 1 was wrong (`B1` became `D5`).



Lesson: a test that only does full writes can miss a strobe bug. Random strobes plus a reference model catch it.



\### Bug 2: write response never sent



I changed the design so `bvalid` was never raised after a write.



\- Both `test\_basic` and `test\_random` \*\*failed\*\* by hitting the 200 us timeout, because the driver waited forever for the response.



Lesson: a timeout turns a hang into a clear failure instead of a stuck simulation.



\## Run it



```

make

```



Requires cocotb 2.1.0 and Icarus Verilog.


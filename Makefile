SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CURDIR)/axi_lite_slave.v

COCOTB_TOPLEVEL = axi_lite_slave
COCOTB_TEST_MODULES = test_axi_lite

include $(shell cocotb-config --makefiles)/Makefile.sim
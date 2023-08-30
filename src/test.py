import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

@cocotb.coroutine
def reset_dut(dut):
    dut.rst <= 1
    yield RisingEdge(dut.clk)
    dut.rst <= 0
    yield RisingEdge(dut.clk)

@cocotb.coroutine
def uart_tx_test(dut):
    clk_period = 10  # Time unit in nanoseconds

    cocotb.fork(Clock(dut.clk, clk_period).start())
    yield reset_dut(dut)

    dut.enable <= 1
    yield Timer(clk_period * 2)
    dut.enable <= 0
    yield Timer(clk_period * 2)

    data = 1
    while data != 0xFF:
        dut.data <= data
        dut.loopback <= 1
        yield RisingEdge(dut.clk)
        dut.loopback <= 0
        yield Timer(clk_period * 2)
        yield RisingEdge(dut.rdy)
        assert dut.rxdata == data, f"FAIL: rx data {dut.rxdata.value:x} does not match tx {data:x}"
        data += 1

    cocotb.log.info("SUCCESS: all bytes verified")

@cocotb.test()
def test_uart_tx(dut):
    cocotb.regression.test(uart_tx_test, dut, "uart_tx_test").run()
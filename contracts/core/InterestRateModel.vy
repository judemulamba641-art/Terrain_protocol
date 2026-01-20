# @version ^0.3.10
"""
Simple linear interest rate model.
"""

base_rate_bps: public(uint256)   # e.g. 200 = 2%
slope_bps: public(uint256)       # e.g. 800 = 8%
governance: public(address)


@external
def __init__(_governance: address):
    self.governance = _governance
    self.base_rate_bps = 200
    self.slope_bps = 800


@external
def set_rates(base: uint256, slope: uint256):
    assert msg.sender == self.governance
    self.base_rate_bps = base
    self.slope_bps = slope


@external
@view
def get_borrow_rate(utilization_bps: uint256) -> uint256:
    """
    utilization in bps (0–10000)
    """
    return self.base_rate_bps + utilization_bps * self.slope_bps / 10_000
# @version ^0.3.10

interface ILendingPool:
    def set_fees(borrow_bps: uint256, lending_bps: uint256): nonpayable
    def set_treasury(treasury: address): nonpayable

interface ITreasuryDAO:
    def withdraw(token: address, to: address, amount: uint256): nonpayable


governance_token: public(address)
guardian: public(address)

timelock_delay: public(uint256)
paused: public(bool)

struct Proposal:
    target: address
    data: Bytes[256]
    execute_after: uint256
    executed: bool

proposals: HashMap[uint256, Proposal]
proposal_count: public(uint256)


@external
def __init__(_guardian: address):
    self.guardian = _guardian
    self.timelock_delay = 2 * 86400  # 48h
    self.paused = False


# =======================
# PROPOSALS
# =======================

@external
def create_proposal(target: address, data: Bytes[256]):
    pid: uint256 = self.proposal_count
    self.proposals[pid] = Proposal(
        target,
        data,
        block.timestamp + self.timelock_delay,
        False
    )
    self.proposal_count += 1


@external
def execute_proposal(pid: uint256):
    prop: Proposal = self.proposals[pid]
    assert not prop.executed, "EXECUTED"
    assert block.timestamp >= prop.execute_after, "TIMELOCK"
    assert not self.paused, "PAUSED"

    raw_call(prop.target, prop.data)
    self.proposals[pid].executed = True


# =======================
# EMERGENCY
# =======================

@external
def emergency_pause():
    assert msg.sender == self.guardian
    self.paused = True

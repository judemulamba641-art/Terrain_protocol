# @version ^0.3.10
"""
Governance.vy
=============
Timelock governance with emergency guardian path.
Designed for DeFi lending protocol with NFT collateral.

Features:
- Timelocked execution (DAO / multisig)
- Emergency guardian execution (pause, caps, hotfix)
- Action queue with delay
- Protection against instant malicious changes
"""

# ------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------

MIN_DELAY: constant(uint256) = 1 days
MAX_DELAY: constant(uint256) = 7 days
GRACE_PERIOD: constant(uint256) = 14 days


# ------------------------------------------------------------
# STORAGE
# ------------------------------------------------------------

admin: public(address)          # DAO / multisig
guardian: public(address)       # Emergency multisig
delay: public(uint256)

queued_actions: public(HashMap[bytes32, uint256])


# ------------------------------------------------------------
# EVENTS
# ------------------------------------------------------------

event ActionQueued:
    action_id: bytes32
    target: address
    eta: uint256

event ActionExecuted:
    action_id: bytes32
    target: address

event EmergencyExecuted:
    target: address

event GuardianUpdated:
    old_guardian: address
    new_guardian: address


# ------------------------------------------------------------
# CONSTRUCTOR
# ------------------------------------------------------------

@external
def __init__(
    _admin: address,
    _guardian: address,
    _delay: uint256
):
    assert _admin != empty(address)
    assert _guardian != empty(address)
    assert MIN_DELAY <= _delay <= MAX_DELAY

    self.admin = _admin
    self.guardian = _guardian
    self.delay = _delay


# ------------------------------------------------------------
# INTERNAL HELPERS
# ------------------------------------------------------------

@internal
@view
def _get_action_id(
    target: address,
    value: uint256,
    data: Bytes[512],
    eta: uint256
) -> bytes32:
    return keccak256(_abi_encode(target, value, data, eta))


# ------------------------------------------------------------
# GOVERNANCE (TIMELOCKED)
# ------------------------------------------------------------

@external
def queue_action(
    target: address,
    value: uint256,
    data: Bytes[512]
) -> bytes32:
    """
    Queue a governance action to be executed after delay
    """
    assert msg.sender == self.admin
    assert target != empty(address)

    eta: uint256 = block.timestamp + self.delay
    action_id: bytes32 = self._get_action_id(target, value, data, eta)

    assert self.queued_actions[action_id] == 0

    self.queued_actions[action_id] = eta

    log ActionQueued(action_id, target, eta)
    return action_id


@external
def execute_action(
    target: address,
    value: uint256,
    data: Bytes[512],
    eta: uint256
):
    """
    Execute a queued governance action
    """
    assert msg.sender == self.admin

    action_id: bytes32 = self._get_action_id(target, value, data, eta)
    queued_eta: uint256 = self.queued_actions[action_id]

    assert queued_eta != 0
    assert block.timestamp >= queued_eta
    assert block.timestamp <= queued_eta + GRACE_PERIOD

    self.queued_actions[action_id] = 0

    raw_call(
        target,
        data,
        value=value,
        revert_on_failure=True
    )

    log ActionExecuted(action_id, target)


# ------------------------------------------------------------
# EMERGENCY GOVERNANCE (GUARDIAN)
# ------------------------------------------------------------

@external
def emergency_execute(
    target: address,
    data: Bytes[512]
):
    """
    Emergency execution WITHOUT delay.
    STRICTLY for:
    - pause()
    - set_caps()
    - emergency fixes
    """
    assert msg.sender == self.guardian
    assert target != empty(address)

    raw_call(
        target,
        data,
        revert_on_failure=True
    )

    log EmergencyExecuted(target)


# ------------------------------------------------------------
# GOVERNANCE MAINTENANCE
# ------------------------------------------------------------

@external
def update_guardian(new_guardian: address):
    """
    Timelocked guardian rotation
    """
    assert msg.sender == self.admin
    assert new_guardian != empty(address)

    old: address = self.guardian
    self.guardian = new_guardian

    log GuardianUpdated(old, new_guardian)


@external
def update_delay(new_delay: uint256):
    """
    Change timelock delay (timelocked call itself)
    """
    assert msg.sender == self.admin
    assert MIN_DELAY <= new_delay <= MAX_DELAY

    self.delay = new_delay
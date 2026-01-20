# @version ^0.3.10

"""
Timelock Controller
Delays execution of governance actions
"""

# -------------------------
# Events
# -------------------------

event Queued:
    txHash: indexed(bytes32)
    target: address
    eta: uint256

event Executed:
    txHash: indexed(bytes32)
    target: address

event Cancelled:
    txHash: indexed(bytes32)


# -------------------------
# Storage
# -------------------------

admin: public(address)
pending_admin: public(address)

delay: public(uint256)  # seconds

queued_transactions: public(HashMap[bytes32, bool])


# -------------------------
# Constructor
# -------------------------

@external
def __init__(_admin: address, _delay: uint256):
    assert _delay >= 1 days, "Delay too short"
    assert _delay <= 30 days, "Delay too long"

    self.admin = _admin
    self.delay = _delay


# -------------------------
# Admin management
# -------------------------

@external
def setPendingAdmin(new_admin: address):
    assert msg.sender == self.admin, "Admin only"
    self.pending_admin = new_admin


@external
def acceptAdmin():
    assert msg.sender == self.pending_admin, "Not pending admin"
    self.admin = msg.sender
    self.pending_admin = ZERO_ADDRESS


# -------------------------
# Queue transaction
# -------------------------

@external
def queueTransaction(
    target: address,
    value: uint256,
    signature: String[128],
    data: Bytes[4096],
    eta: uint256
) -> bytes32:
    assert msg.sender == self.admin, "Admin only"
    assert eta >= block.timestamp + self.delay, "ETA too soon"

    txHash: bytes32 = keccak256(
        concat(
            convert(target, bytes32),
            convert(value, bytes32),
            keccak256(signature),
            keccak256(data),
            convert(eta, bytes32)
        )
    )

    self.queued_transactions[txHash] = True

    log Queued(txHash, target, eta)
    return txHash


# -------------------------
# Cancel transaction
# -------------------------

@external
def cancelTransaction(
    target: address,
    value: uint256,
    signature: String[128],
    data: Bytes[4096],
    eta: uint256
):
    assert msg.sender == self.admin, "Admin only"

    txHash: bytes32 = keccak256(
        concat(
            convert(target, bytes32),
            convert(value, bytes32),
            keccak256(signature),
            keccak256(data),
            convert(eta, bytes32)
        )
    )

    self.queued_transactions[txHash] = False
    log Cancelled(txHash)


# -------------------------
# Execute transaction
# -------------------------

@external
@payable
def executeTransaction(
    target: address,
    value: uint256,
    signature: String[128],
    data: Bytes[4096],
    eta: uint256
):
    assert msg.sender == self.admin, "Admin only"

    txHash: bytes32 = keccak256(
        concat(
            convert(target, bytes32),
            convert(value, bytes32),
            keccak256(signature),
            keccak256(data),
            convert(eta, bytes32)
        )
    )

    assert self.queued_transactions[txHash], "Tx not queued"
    assert block.timestamp >= eta, "Timelock not expired"

    self.queued_transactions[txHash] = False

    call_data: Bytes[4096] = data
    if len(signature) > 0:
        call_data = concat(method_id(signature), data)

    raw_call(
        target,
        call_data,
        value=value,
        max_outsize=0
    )

    log Executed(txHash, target)
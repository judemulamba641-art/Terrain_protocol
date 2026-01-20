# @version ^0.3.10

"""
SafeCast Utilities
Safe type casting helpers
Inspired by OpenZeppelin SafeCast
"""

# -------------------------
# uint256 → smaller uint
# -------------------------

@internal
@pure
def to_uint128(value: uint256) -> uint128:
    assert value <= max_value(uint128), "CAST_OVERFLOW"
    return convert(value, uint128)


@internal
@pure
def to_uint64(value: uint256) -> uint64:
    assert value <= max_value(uint64), "CAST_OVERFLOW"
    return convert(value, uint64)


@internal
@pure
def to_uint32(value: uint256) -> uint32:
    assert value <= max_value(uint32), "CAST_OVERFLOW"
    return convert(value, uint32)


# -------------------------
# int → uint
# -------------------------

@internal
@pure
def int_to_uint(value: int256) -> uint256:
    assert value >= 0, "NEGATIVE_TO_UINT"
    return convert(value, uint256)


# -------------------------
# uint → int
# -------------------------

@internal
@pure
def uint_to_int(value: uint256) -> int256:
    assert value <= max_value(int256), "CAST_OVERFLOW"
    return convert(value, int256)
# @version ^0.3.10

interface IERC20:
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def burn(amount: uint256): nonpayable

interface IUniswapRouter:
    def swapExactTokensForTokens(
        amountIn: uint256,
        amountOutMin: uint256,
        path: address[2],
        to: address,
        deadline: uint256
    ): nonpayable


governance: public(address)
guardian: public(address)

paused: public(bool)
withdraw_cap: public(uint256)

insurance_fund: public(uint256)
insurance_ratio_bps: public(uint256)

event Withdraw(token: address, to: address, amount: uint256)
event InsuranceFundIncreased(amount: uint256)


@external
def __init__(_gov: address, _guardian: address):
    self.governance = _gov
    self.guardian = _guardian
    self.withdraw_cap = 10**22
    self.insurance_ratio_bps = 2000  # 20%
    self.paused = False


# =======================
# FEES & INSURANCE
# =======================

@external
def receive_fees(token: address, amount: uint256):
    """
    LendingPool envoie ici TOUS les frais.
    """
    insurance_part: uint256 = amount * self.insurance_ratio_bps / 10_000
    self.insurance_fund += insurance_part
    log InsuranceFundIncreased(insurance_part)


# =======================
# GOVERNANCE ACTIONS
# =======================

@external
def withdraw(token: address, to: address, amount: uint256):
    assert msg.sender == self.governance, "ONLY_GOV"
    assert not self.paused, "PAUSED"
    assert amount <= self.withdraw_cap, "CAP"
    assert IERC20(token).transfer(to, amount)
    log Withdraw(token, to, amount)


@external
def buyback_and_burn(
    router: address,
    token_in: address,
    gov_token: address,
    amount: uint256
):
    assert msg.sender == self.governance, "ONLY_GOV"

    IUniswapRouter(router).swapExactTokensForTokens(
        amount,
        0,
        [token_in, gov_token],
        self,
        block.timestamp + 300
    )

    IERC20(gov_token).burn(IERC20(gov_token).balanceOf(self))


# =======================
# EMERGENCY
# =======================

@external
def emergency_pause():
    assert msg.sender == self.guardian, "ONLY_GUARDIAN"
    self.paused = True

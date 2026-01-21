# contracts/TreasuryDAO.vy
# @version ^0.3.10

interface IERC20:
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def balanceOf(account: address) -> uint256: view
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
insurance_ratio_bps: public(uint256)  # ex: 2000 = 20%

event FundsWithdrawn:
    token: address
    to: address
    amount: uint256

event FeesDeposited:
    amount: uint256
    insurance_part: uint256


@external
def __init__(_gov: address, _guardian: address):
    self.governance = _gov
    self.guardian = _guardian
    self.withdraw_cap = 10**22
    self.insurance_ratio_bps = 2000
    self.paused = False


@external
def deposit_fees(amount: uint256):
    """
    Called by LendingPool
    """
    insurance_part: uint256 = amount * self.insurance_ratio_bps / 10_000
    self.insurance_fund += insurance_part
    log FeesDeposited(amount, insurance_part)


@external
def withdraw(token: address, to: address, amount: uint256):
    assert msg.sender == self.governance, "ONLY_GOV"
    assert not self.paused, "PAUSED"
    assert amount <= self.withdraw_cap, "CAP_EXCEEDED"
    assert IERC20(token).transfer(to, amount)
    log FundsWithdrawn(token, to, amount)


@external
def buyback_and_burn(
    router: address,
    token_in: address,
    gov_token: address,
    amount: uint256
):
    assert msg.sender == self.governance, "ONLY_GOV"
    assert not self.paused, "PAUSED"

    path: address[2] = [token_in, gov_token]

    IUniswapRouter(router).swapExactTokensForTokens(
        amount,
        0,
        path,
        self,
        block.timestamp + 300
    )

    burn_amount: uint256 = IERC20(gov_token).balanceOf(self)
    IERC20(gov_token).burn(burn_amount)


@external
def emergency_pause():
    assert msg.sender == self.guardian, "ONLY_GUARDIAN"
    self.paused = True

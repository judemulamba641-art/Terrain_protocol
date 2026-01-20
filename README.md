🏦 NFT‑Backed DeFi Lending Protocol

Overview

This repository contains a DeFi lending & borrowing protocol (Aave‑like) where 3D Land NFTs are used as collateral.

The protocol is designed with audit‑readiness, modularity, and safety as first‑class goals.

It includes:

NFT‑based collateralization

Lending / borrowing with interest accrual

Liquidation engine

On‑chain governance with timelock

Off‑chain bots (keepers, liquidators, price engine)

Extensive testing (integration, simulations, invariants, fuzz, E2E)



---

Core Components

Smart Contracts (Vyper)

Contract	Responsibility

LendingPool.vy	Core lending / borrowing logic, interest accrual
NFTCollateralManager.vy	NFT deposits, withdrawals, valuation
LiquidationManager.vy	Liquidations, incentives, bad debt handling
Governance.vy	DAO governance + timelock
InterestRateModel.vy	Governed interest rate model



---

Architecture

contracts/
├── LendingPool.vy
├── NFTCollateralManager.vy
├── LiquidationManager.vy
├── Governance.vy
└── InterestRateModel.vy

tests/
├── integration/
│   ├── environment/
│   ├── flows/
│   ├── scenarios/
│   └── assertions/
├── simulations/
│   ├── engine/
│   ├── scenarios/
│   └── reports/
├── invariants/
├── fuzz/
└── e2e/


---

Governance Model

The protocol is governed by an on‑chain DAO with:

Timelocked execution

Emergency guardian (pause only)

Parameter governance (LTV, liquidation threshold, rates)


Governance Guarantees

❌ No direct admin writes

⏱ Timelock enforced

🛑 Emergency pause without state mutation



---

Risk Management & Guardrails

Built‑in Safety Mechanisms

Health Factor enforcement

Borrow caps

Global pause

Liquidation incentives

Oracle sanity checks

Debt invariants

Governance‑only setters


Protocol Invariants

Total debt consistency

No borrowing when paused

NFT cannot be withdrawn if collateralized

Only governance can change risk parameters



---

Testing Strategy

Test Categories

Category	Purpose

Integration	Full protocol flows
Invariants	Always‑true safety rules
Fuzz	Adversarial sequences
Simulations	Stress & Monte‑Carlo
E2E	Realistic user journeys


Coverage Goal

✅ ~80%+ logic coverage

✅ All critical paths tested

✅ Governance paths tested



---

Running Tests

Install dependencies

pip install -r requirements.txt

Run all tests

pytest -v --maxfail=1

or

brownie test


---

CI / Automation

All tests are executed automatically via GitHub Actions on:

Push

Pull requests


This ensures deterministic, reproducible test results.


---

Security Assumptions

Oracle prices are eventually consistent

NFTs have deterministic valuation logic

Governance token distribution is external

Liquidators are rational actors



---

Audit Readiness

✔ Modular contracts ✔ Explicit invariants ✔ Fuzz & adversarial tests ✔ Timelocked governance ✔ No privileged shortcuts

Status: 🟢 Pre‑Audit / Testnet Ready


---

License

MIT License


---

Disclaimer

This project is experimental and provided for research and testnet usage only. Do not use in production without an independent security audit.
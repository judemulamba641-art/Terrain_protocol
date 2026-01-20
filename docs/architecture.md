# 🏗️ Terrain DeFi Protocol — Architecture

## Overview

Terrain DeFi Protocol is a decentralized lending protocol that enables users to borrow fungible tokens using **3D Terrain NFTs** as collateral.

The protocol combines:
- On-chain smart contracts (Vyper)
- Off-chain bots (Python)
- DAO governance
- External liquidity via Uniswap

---

## High-Level Architecture

---

## Smart Contracts

### Core
- **LendingPool.vy**: Deposits, borrows, repayments
- **NFTCollateralManager.vy**: NFT locking & valuation
- **InterestRateStrategy.vy**: Dynamic borrow rates
- **LiquidationManager.vy**: Liquidations

### Governance
- **Governor.vy**
- **Timelock.vy**

### Utilities
- **Math.vy**
- **SafeCast.vy**
- **Interfaces (IERC20, IERC721, Oracle, Uniswap)**

---

## Off-Chain Components

- **Terrain Indexer**: NFT rarity & metadata indexing
- **Price Engine**: Token & NFT pricing
- **Keeper**: Interest updates, health checks
- **Liquidation Bot**: Executes liquidations
- **Event Listener**: Sync on-chain ↔ off-chain state

---

## Security Design

- DAO-controlled parameters
- Time-locked governance
- Keeper redundancy
- Oracle separation
- Minimal trusted off-chain logic
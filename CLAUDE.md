# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python trading bot for Polymarket with gasless transactions via Builder Program. Uses EIP-712 signing for orders, encrypted private key storage, and supports both the CLOB API and Relayer API.

## Common Commands

```bash
# Setup (first time)
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials
source .env

# Run full integration test
python scripts/full_test.py

# Run the bot
python scripts/run_bot.py              # Quick demo
python scripts/run_bot.py --interactive # Interactive mode

# Testing
pytest tests/ -v                        # Run all tests
pytest tests/test_bot.py -v             # Test bot module
pytest tests/test_crypto.py -v          # Test encryption
pytest tests/test_signer.py -v          # Test EIP-712 signing
pytest tests/test_bot.py::TestTradingBot::test_init_with_config -v  # Single test
```

## Architecture

```
src/
├── bot.py      # TradingBot - main entry point, orchestrates order flow
├── client.py   # ClobClient (order book) + RelayerClient (gasless tx)
├── signer.py   # EIP-712 order signing with OrderSigner
├── crypto.py   # KeyManager - PBKDF2/Fernet encryption for private keys
└── config.py   # Config dataclasses, YAML loading, validation
```

### Data Flow

1. `TradingBot.place_order()` creates an `Order` dataclass
2. `OrderSigner.sign_order()` produces EIP-712 signature
3. `ClobClient.post_order()` submits to CLOB with Builder HMAC auth headers
4. If gasless enabled, `RelayerClient` handles Safe deployment/approvals

### Key Patterns

- **Async methods**: All trading operations (`place_order`, `cancel_order`, `get_trades`) are async
- **Config precedence**: Environment vars > YAML file > defaults
- **Builder HMAC auth**: Timestamp + method + path + body signed with api_secret
- **Signature type 2**: Gnosis Safe signatures for Polymarket

## Configuration

Config loads from `config.yaml` with these key fields:
- `safe_address`: Your Polymarket proxy wallet address
- `builder.api_key/api_secret/api_passphrase`: For gasless trading
- `clob.chain_id`: 137 (Polygon mainnet)

## Testing Notes

- Tests use `pytest` with `pytest-asyncio` for async
- Mock external API calls; never hit real Polymarket APIs in tests
- Test private key: `"0x" + "a" * 64`
- Test safe address: `"0x" + "b" * 40`
- YAML config values starting with `0x` must be quoted to avoid integer parsing

## Dependencies

- `eth-account>=0.13.0`: Uses new `encode_typed_data` API with `domain_data`, `message_types`, `message_data` params
- `web3>=7.0.0`: Polygon RPC interactions
- `cryptography`: Fernet encryption for private keys

## Polymarket API Context

- CLOB API: `https://clob.polymarket.com` - order submission/cancellation
- Relayer API: `https://relayer-v2.polymarket.com` - gasless transactions
- Token IDs are ERC-1155 identifiers for market outcomes
- Prices are 0-1 (probability percentages)
- USDC has 6 decimal places

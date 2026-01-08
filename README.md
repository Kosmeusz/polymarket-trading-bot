# Polymarket Trading Bot Demo

A production-ready, modular trading bot for Polymarket with gasless transactions via Builder Program.

## Features

- **Gasless Transactions**: Uses Builder Program credentials to eliminate gas fees
- **Encrypted Private Key Storage**: Keys are encrypted with PBKDF2 before storage
- **Modular Architecture**: Easy to extend and customize
- **Strategy Framework**: Built-in support for custom trading strategies
- **Comprehensive Testing**: Unit tests for all core modules

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Bot

**Option A: Using Environment Variables (Recommended)**

```bash
# Copy the example env file
cp .env.example .env

# Edit with your credentials
nano .env

# Load environment variables
source .env

# Run the full test to verify setup
python scripts/full_test.py
```

**Option B: Using Setup Script**

Run the interactive setup script:

```bash
python scripts/setup.py
```

You'll need:
- Your MetaMask private key
- Your Polymarket Safe address (from polymarket.com/settings)
- Optional: Builder Program credentials (for gasless trading)

### 3. Start Trading

```bash
# Interactive mode
python scripts/run_bot.py --interactive

# Quick demo
python scripts/run_bot.py
```

## Environment Variables

All environment variables are prefixed with `POLY_`:

| Variable | Required | Description |
|----------|----------|-------------|
| `POLY_PRIVATE_KEY` | Yes | Your MetaMask private key (hex) |
| `POLY_SAFE_ADDRESS` | Yes | Your Polymarket Safe/Proxy address |
| `POLY_BUILDER_API_KEY` | For gasless | Builder Program API key |
| `POLY_BUILDER_API_SECRET` | For gasless | Builder Program secret |
| `POLY_BUILDER_API_PASSPHRASE` | For gasless | Builder Program passphrase |
| `POLY_RPC_URL` | No | Polygon RPC URL (default: polygon-rpc.com) |
| `POLY_LOG_LEVEL` | No | Logging level (default: INFO) |

## Project Structure

```
polymarket-trading-bot/
├── src/                      # Core modules
│   ├── __init__.py
│   ├── bot.py               # Trading bot
│   ├── client.py            # API clients
│   ├── config.py            # Configuration
│   ├── crypto.py            # Encryption
│   └── signer.py            # Order signing
├── scripts/                 # Executable scripts
│   ├── setup.py             # Initial setup
│   └── run_bot.py           # Run the bot
├── examples/                # Usage examples
│   ├── basic_trading.py     # Basic operations
│   └── strategy_example.py  # Custom strategies
├── tests/                   # Unit tests
│   ├── test_crypto.py
│   ├── test_signer.py
│   └── test_bot.py
├── config.yaml              # Configuration file (created by setup)
├── credentials/             # Encrypted credentials (created by setup)
│   ├── encrypted_key.json
│   └── api_creds.json
└── requirements.txt         # Python dependencies
```

## Usage Examples

### Basic Trading

```python
from src.bot import TradingBot
import asyncio

async def trade():
    bot = TradingBot(config_path="config.yaml")

    # Place a buy order
    result = await bot.place_order(
        token_id="0x1234567890...",
        price=0.65,      # 65% probability
        size=10.0,       # 10 shares
        side="BUY"
    )
    print(f"Order placed: {result.success}")

    # Check open orders
    orders = await bot.get_open_orders()
    print(f"Open orders: {len(orders)}")

    # Cancel an order
    await bot.cancel_order("order_id")

asyncio.run(trade())
```

### Custom Strategy

```python
from examples.strategy_example import MeanReversionStrategy
from src.bot import TradingBot
import asyncio

async def run_strategy():
    bot = TradingBot(config_path="config.yaml")

    strategy = MeanReversionStrategy(
        bot=bot,
        params={
            'window': 10,        # Moving average window
            'threshold': 0.05,   # 5% deviation
            'size': 1.0,         # Order size
            'check_interval': 60 # Check every 60s
        }
    )

    # Run strategy
    await strategy.run(
        tokens=[bot.config.default_token_id],
        duration=3600  # Run for 1 hour
    )

asyncio.run(run_strategy())
```

## Configuration

### config.yaml

```yaml
safe_address: "0x..."           # Your Polymarket Safe address
rpc_url: "https://polygon-rpc.com"

clob:
  host: "https://clob.polymarket.com"
  chain_id: 137
  signature_type: 2

relayer:
  host: "https://relayer-v2.polymarket.com"
  tx_type: "SAFE"

builder:
  api_key: ""                   # For gasless trading
  api_secret: ""
  api_passphrase: ""

default_token_id: "0x..."       # Default market to trade
default_size: 1.0
default_price: 0.5
data_dir: "credentials"
log_level: "INFO"
```

### Gasless Trading

To enable gasless transactions:

1. Apply for [Polymarket Builder Program](https://polymarket.com/settings?tab=builder)
2. Copy your API credentials to `config.yaml`:

```yaml
builder:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  api_passphrase: "your_passphrase"
```

## Security

### Private Key Storage

Your private key is:
1. Encrypted using **PBKDF2** (480,000 iterations)
2. Protected by a **Fernet** symmetric cipher
3. Stored only in the `credentials/encrypted_key.json` file
4. Never sent over the network

### Best Practices

- Use a strong, unique password
- Never share your encrypted key file
- Run the bot on a secure, private machine
- Regularly backup your credentials folder

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run specific tests:

```bash
pytest tests/test_crypto.py -v      # Encryption tests
pytest tests/test_signer.py -v      # Signing tests
pytest tests/test_bot.py -v          # Bot tests
```

## API Reference

### TradingBot

```python
bot.place_order(token_id, price, size, side, order_type="GTC")
    # Place a limit order

bot.cancel_order(order_id)
    # Cancel a specific order

bot.cancel_all_orders(token_id=None)
    # Cancel all open orders

bot.get_open_orders()
    # Get list of open orders

bot.get_trades(token_id=None, limit=100)
    # Get trade history

bot.get_market_price(token_id)
    # Get current market price

bot.get_order_book(token_id)
    # Get order book for a token
```

### Order Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `token_id` | str | Market token ID (from Gamma API) |
| `price` | float | Price per share (0-1, e.g., 0.65) |
| `size` | float | Number of shares |
| `side` | str | "BUY" or "SELL" |
| `order_type` | str | "GTC" (Good Till Cancelled), "GTD", "FOK" |

## Troubleshooting

### "config.yaml not found"
Run the setup script:
```bash
python scripts/setup.py
```

### "Invalid password"
You entered the wrong password for the encrypted key.

### "Safe address not found"
Make sure your Safe address is set in `config.yaml` or `credentials/`.

### Gas fees not eliminated
Ensure Builder credentials are correctly configured in `config.yaml`.

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

#!/usr/bin/env python3
"""
Quick test script to verify order placement works.
"""
import asyncio
import os
from dotenv import load_dotenv
from src.utils import create_bot_from_env

# Load environment variables
load_dotenv()

async def main():
    # Create bot from config file (which has signature_type=2)
    from src.config import Config
    from src.bot import TradingBot

    # Load config
    config = Config.load_with_env("config.yaml")

    # Get private key from environment
    private_key = os.getenv("POLY_PRIVATE_KEY")
    if not private_key:
        print("Error: POLY_PRIVATE_KEY environment variable not set")
        return

    # Create bot
    bot = TradingBot(private_key=private_key, config=config)
    
    print(f"Bot initialized successfully!")
    print(f"  EOA address: {bot.signer.address}")
    print(f"  Proxy address: {bot.config.safe_address}")
    print(f"  Signature type: {bot.config.clob.signature_type}")
    print(f"  API key: {bot._api_creds.api_key[:20]}...")
    
    # Get current BTC market
    from src.gamma_client import GammaClient
    gamma = GammaClient()
    market_info = gamma.get_market_info("BTC")

    if not market_info:
        print("No active BTC markets found")
        return

    print(f"\nMarket: {market_info['question']}")
    print(f"  Ends: {market_info['end_date']}")
    print(f"  Accepting orders: {market_info['accepting_orders']}")

    # Get token IDs
    token_ids = market_info['token_ids']
    up_token_id = token_ids.get('up')

    if not up_token_id:
        print("Could not find UP token")
        return

    print(f"  UP Token ID: {up_token_id}")
    
    # Try to place a small test order with a realistic price
    # Note: Minimum order size is $1.00, so at price 0.45, we need at least 2.23 shares
    # Note: Market requires fee_rate_bps=1000 (10%)
    # Note: Market has minimum size of 5 shares
    print(f"\nAttempting to place test order...")
    try:
        result = await bot.place_order(
            token_id=up_token_id,
            side="BUY",
            price=0.45,  # More realistic price
            size=5.00,   # 5 shares @ 0.45 = $2.25 (meets minimum size requirement)
            fee_rate_bps=1000  # Market requires 1000 basis points (10%)
        )
        print(f"✓ Order placed successfully!")
        print(f"  Order ID: {result.order_id}")
        print(f"  Success: {result.success}")
        print(f"  Error: {result.error_msg}")
        print(f"  Full result: {result}")
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            print(f"✗ Still getting 401 Unauthorized error:")
            print(f"  {error_msg}")
        else:
            print(f"✓ No 401 error! Got different error (this is progress):")
            print(f"  {error_msg}")

if __name__ == "__main__":
    asyncio.run(main())


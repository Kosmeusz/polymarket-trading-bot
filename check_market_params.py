#!/usr/bin/env python3
"""
Check market parameters to understand order requirements.
"""
import asyncio
from src.gamma_client import GammaClient
from src.client import ClobClient

async def main():
    # Get current BTC market
    gamma = GammaClient()
    market_info = gamma.get_market_info("BTC")
    
    if not market_info:
        print("No active BTC markets found")
        return
    
    print(f"Market: {market_info['question']}")
    print(f"  Accepting orders: {market_info['accepting_orders']}")
    
    # Get raw market data
    raw = market_info.get('raw', {})
    print(f"\nMarket Parameters:")
    print(f"  Minimum order size: {raw.get('minimumOrderSize', 'N/A')}")
    print(f"  Minimum tick size: {raw.get('minimumTickSize', 'N/A')}")
    print(f"  Maker base fee: {raw.get('makerBaseFee', 'N/A')}")
    print(f"  Taker base fee: {raw.get('takerBaseFee', 'N/A')}")
    print(f"  Neg risk: {raw.get('negRisk', 'N/A')}")
    
    # Get token IDs
    token_ids = market_info['token_ids']
    up_token_id = token_ids.get('up')
    
    if up_token_id:
        print(f"\nUP Token ID: {up_token_id}")
        
        # Try to get market-specific parameters from CLOB API
        clob = ClobClient()
        try:
            # Get order book to see if market is active
            book = clob.get_order_book(up_token_id)
            print(f"\nOrder Book:")
            print(f"  Market: {book.get('market', 'N/A')}")
            print(f"  Asset ID: {book.get('asset_id', 'N/A')}")
            
            bids = book.get('bids', [])
            asks = book.get('asks', [])
            print(f"  Bids: {len(bids)}")
            print(f"  Asks: {len(asks)}")
            
            if bids:
                print(f"  Best bid: {bids[0].get('price', 'N/A')}")
            if asks:
                print(f"  Best ask: {asks[0].get('price', 'N/A')}")
                
        except Exception as e:
            print(f"Error getting order book: {e}")

if __name__ == "__main__":
    asyncio.run(main())


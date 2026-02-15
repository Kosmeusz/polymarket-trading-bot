#!/usr/bin/env python3
"""Test decimal precision for order amounts."""

from src.signer import Order

print("=" * 60)
print("Testing LIMIT BUY order (GTC)")
print("=" * 60)

# Test limit order
limit_order = Order(
    token_id='17677295341284404301684190429353870897397456800894496393305525348207706127476',
    price=0.70,
    size=1.47,
    side='BUY',
    maker='0x81E16FFAED0357FCB6514F5F59B961Bbf29152a5',
    fee_rate_bps=1000,
    signature_type=1,
    order_type='GTC',
)

print(f'Price: {limit_order.price}')
print(f'Size: {limit_order.size}')
print(f'makerAmount: {limit_order.maker_amount} ({int(limit_order.maker_amount) / 1e6:.6f} USDC)')
print(f'takerAmount: {limit_order.taker_amount} ({int(limit_order.taker_amount) / 1e6:.6f} shares)')

usdc_value = int(limit_order.maker_amount) / 1e6
shares_value = int(limit_order.taker_amount) / 1e6
usdc_str = f'{usdc_value:.6f}'.rstrip('0')
shares_str = f'{shares_value:.6f}'.rstrip('0')
usdc_decimals = len(usdc_str.split('.')[1]) if '.' in usdc_str else 0
shares_decimals = len(shares_str.split('.')[1]) if '.' in shares_str else 0

print(f'USDC decimals: {usdc_decimals} (max 4 for limit BUY)')
print(f'Shares decimals: {shares_decimals} (max 2 for limit BUY)')
print(f'Valid: {usdc_decimals <= 4 and shares_decimals <= 2}')

print("\n" + "=" * 60)
print("Testing MARKET BUY order (FOK)")
print("=" * 60)

# Test market order (FOK)
market_buy = Order(
    token_id='76997023535667477195165391948542290629515300652387516563120146046953694422176',
    price=0.61,
    size=1.68,
    side='BUY',
    maker='0x81E16FFAED0357FCB6514F5F59B961Bbf29152a5',
    fee_rate_bps=1000,
    signature_type=1,
    order_type='FOK',
)

print(f'Price: {market_buy.price}')
print(f'Size: {market_buy.size}')
print(f'makerAmount: {market_buy.maker_amount} ({int(market_buy.maker_amount) / 1e6:.6f} USDC)')
print(f'takerAmount: {market_buy.taker_amount} ({int(market_buy.taker_amount) / 1e6:.6f} shares)')

usdc_value = int(market_buy.maker_amount) / 1e6
shares_value = int(market_buy.taker_amount) / 1e6
usdc_str = f'{usdc_value:.6f}'.rstrip('0')
shares_str = f'{shares_value:.6f}'.rstrip('0')
usdc_decimals = len(usdc_str.split('.')[1]) if '.' in usdc_str else 0
shares_decimals = len(shares_str.split('.')[1]) if '.' in shares_str else 0

print(f'USDC decimals: {usdc_decimals} (max 2 for market BUY)')
print(f'Shares decimals: {shares_decimals} (max 4 for market BUY)')
print(f'Valid: {usdc_decimals <= 2 and shares_decimals <= 4}')

print("\n" + "=" * 60)
print("Testing MARKET SELL order (FOK)")
print("=" * 60)

# Test market SELL order (the problematic case)
market_sell = Order(
    token_id='90278214017514619867617721590099295713109600573292137004415444312307556372916',
    price=0.11,
    size=5.5556,
    side='SELL',
    maker='0x81E16FFAED0357FCB6514F5F59B961Bbf29152a5',
    fee_rate_bps=1000,
    signature_type=1,
    order_type='FOK',
)

print(f'Price: {market_sell.price}')
print(f'Size: {market_sell.size}')
print(f'makerAmount: {market_sell.maker_amount} ({int(market_sell.maker_amount) / 1e6:.6f} shares)')
print(f'takerAmount: {market_sell.taker_amount} ({int(market_sell.taker_amount) / 1e6:.6f} USDC)')

shares_value = int(market_sell.maker_amount) / 1e6
usdc_value = int(market_sell.taker_amount) / 1e6
shares_str = f'{shares_value:.6f}'.rstrip('0')
usdc_str = f'{usdc_value:.6f}'.rstrip('0')
shares_decimals = len(shares_str.split('.')[1]) if '.' in shares_str else 0
usdc_decimals = len(usdc_str.split('.')[1]) if '.' in usdc_str else 0

print(f'Shares decimals: {shares_decimals} (max 2 for SELL)')
print(f'USDC decimals: {usdc_decimals} (max 4 for SELL)')
print(f'Valid: {shares_decimals <= 2 and usdc_decimals <= 4}')


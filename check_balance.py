#!/usr/bin/env python3
"""
Check USDC balance and allowances.
"""
import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# Polygon RPC
w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

# USDC contract on Polygon
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

# ERC-20 ABI (minimal)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Get addresses from env
proxy_address = os.getenv("POLY_SAFE_ADDRESS")

if not proxy_address:
    print("Error: POLY_SAFE_ADDRESS not set")
    exit(1)

print(f"Checking balance for: {proxy_address}")

# Create contract instance
usdc = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)

# Get balance
balance = usdc.functions.balanceOf(proxy_address).call()
balance_usdc = balance / 10**6  # USDC has 6 decimals

print(f"USDC Balance: {balance_usdc:.2f} USDC")

# Get allowance for Exchange contract
allowance = usdc.functions.allowance(proxy_address, EXCHANGE_ADDRESS).call()
allowance_usdc = allowance / 10**6

print(f"Allowance for Exchange: {allowance_usdc:.2f} USDC")

if balance_usdc < 1.0:
    print("\n⚠️  WARNING: Insufficient USDC balance to place $1 order")
if allowance_usdc < 1.0:
    print("\n⚠️  WARNING: Insufficient allowance for Exchange contract")


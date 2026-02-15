#!/usr/bin/env python3
"""
Test API Authentication

Tests if the bot can authenticate with Polymarket's API.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.client import ClobClient
from src.signer import OrderSigner
from dotenv import load_dotenv
import os

def main():
    print("=" * 70)
    print("Polymarket API Authentication Test")
    print("=" * 70)
    print()
    
    # Load environment
    load_dotenv()
    
    private_key = os.getenv("POLY_PRIVATE_KEY")
    safe_address = os.getenv("POLY_SAFE_ADDRESS")
    
    if not private_key or not safe_address:
        print("❌ Missing POLY_PRIVATE_KEY or POLY_SAFE_ADDRESS in .env")
        return
    
    print(f"Private Key: {private_key[:10]}...{private_key[-10:]}")
    print(f"Safe Address: {safe_address}")
    print()
    
    # Create signer
    print("Creating signer...")
    signer = OrderSigner(private_key)
    print(f"✅ Signer address: {signer.address}")
    print()
    
    # Check if signer address matches
    if signer.address.lower() != safe_address.lower():
        print("⚠️  WARNING: Signer address doesn't match Safe address")
        print(f"   Signer: {signer.address}")
        print(f"   Safe:   {safe_address}")
        print()
        print("This is NORMAL for Polymarket (EOA vs Proxy wallet)")
        print()
    
    # Create CLOB client
    print("Creating CLOB client...")
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137,
        signature_type=2,  # Gnosis Safe signature
        funder=safe_address,
    )
    print("✅ CLOB client created")
    print()
    
    # Derive API credentials
    print("Deriving L2 API credentials...")
    try:
        api_creds = client.create_or_derive_api_key(signer)
        print("✅ API credentials derived:")
        print(f"   API Key: {api_creds.api_key[:20]}...")
        print(f"   Secret:  {api_creds.secret[:20]}...")
        print(f"   Passphrase: {api_creds.passphrase[:20]}...")
        print()
        
        # Set credentials
        client.set_api_creds(api_creds)
        print("✅ Credentials set on client")
        print()
    except Exception as e:
        print(f"❌ Failed to derive credentials: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test: Get open orders (requires authentication)
    print("=" * 70)
    print("Testing authenticated endpoint: GET /data/orders")
    print("=" * 70)
    try:
        orders = client.get_open_orders()
        print(f"✅ SUCCESS! Got {len(orders)} open orders")
        if orders:
            print("Sample order:")
            print(f"  ID: {orders[0].get('id', 'N/A')}")
            print(f"  Market: {orders[0].get('market', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print()
        if "401" in str(e):
            print("This is a 401 Unauthorized error.")
            print()
            print("Possible causes:")
            print("1. Your Polymarket account needs to create API credentials on the website first")
            print("2. The Safe address is not properly linked to your EOA")
            print("3. Polymarket's API authentication has changed")
            print()
            print("Try this:")
            print("- Go to https://polymarket.com")
            print("- Check if there's an 'API' or 'Developer' section in Settings")
            print("- You might need to generate API credentials there first")
        return

    print("=" * 70)
    print("✅ Authentication Test PASSED!")
    print("=" * 70)
    print()
    print("Your API credentials are working correctly.")
    print("The 401 errors in the bot might be due to a different issue.")

if __name__ == "__main__":
    main()


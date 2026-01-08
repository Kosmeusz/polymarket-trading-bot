"""
Client Module - API Clients for Polymarket

Provides clients for interacting with:
- CLOB (Central Limit Order Book) API
- Builder Relayer API

Features:
- Gasless transactions via Builder Program
- HMAC authentication for Builder APIs
- Automatic retry and error handling

Example:
    from src.client import ClobClient, RelayerClient

    clob = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137,
        signature_type=2,
        funder="0x..."
    )

    relayer = RelayerClient(
        host="https://relayer-v2.polymarket.com",
        chain_id=137,
        builder_creds=builder_creds
    )
"""

import time
import hmac
import hashlib
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import requests

from .config import BuilderConfig


class ApiError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(ApiError):
    """Raised when authentication fails."""
    pass


class OrderError(ApiError):
    """Raised when order operations fail."""
    pass


@dataclass
class ApiCredentials:
    """User-level API credentials for CLOB."""
    api_key: str
    secret: str
    passphrase: str

    @classmethod
    def load(cls, filepath: str) -> "ApiCredentials":
        """Load credentials from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(
            api_key=data.get("apiKey", ""),
            secret=data.get("secret", ""),
            passphrase=data.get("passphrase", ""),
        )

    def is_valid(self) -> bool:
        """Check if credentials are valid."""
        return bool(self.api_key and self.secret and self.passphrase)


class ApiClient:
    """
    Base HTTP client with common functionality.

    Provides:
    - Automatic JSON handling
    - Request/response logging
    - Error handling
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        retry_count: int = 3
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            retry_count: Number of retries on failure
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            headers: Additional headers
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            ApiError: On request failure
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {"Content-Type": "application/json"}

        if headers:
            request_headers.update(headers)

        last_error = None
        for attempt in range(self.retry_count):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, headers=request_headers,
                        params=params, timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url, headers=request_headers,
                        json=data, params=params, timeout=self.timeout
                    )
                elif method.upper() == "DELETE":
                    response = self.session.delete(
                        url, headers=request_headers,
                        json=data, params=params, timeout=self.timeout
                    )
                else:
                    raise ApiError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json() if response.text else {}

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        raise ApiError(f"Request failed after {self.retry_count} attempts: {last_error}")


class ClobClient(ApiClient):
    """
    Client for Polymarket CLOB (Central Limit Order Book) API.

    Features:
    - Order placement and cancellation
    - Order book queries
    - Trade history
    - Builder attribution support

    Example:
        client = ClobClient(
            host="https://clob.polymarket.com",
            chain_id=137,
            signature_type=2,
            funder="0x..."
        )
    """

    def __init__(
        self,
        host: str = "https://clob.polymarket.com",
        chain_id: int = 137,
        signature_type: int = 2,
        funder: str = "",
        api_creds: Optional[ApiCredentials] = None,
        builder_creds: Optional[BuilderConfig] = None,
        timeout: int = 30
    ):
        """
        Initialize CLOB client.

        Args:
            host: CLOB API host
            chain_id: Chain ID (137 for Polygon mainnet)
            signature_type: Signature type (2 = Gnosis Safe)
            funder: Funder/Safe address
            api_creds: User API credentials (optional)
            builder_creds: Builder credentials for attribution (optional)
            timeout: Request timeout
        """
        super().__init__(base_url=host, timeout=timeout)
        self.host = host
        self.chain_id = chain_id
        self.signature_type = signature_type
        self.funder = funder
        self.api_creds = api_creds
        self.builder_creds = builder_creds

    def _build_headers(
        self,
        method: str,
        path: str,
        body: str = ""
    ) -> Dict[str, str]:
        """
        Build authentication headers.

        Supports both user API credentials and Builder credentials.

        Args:
            method: HTTP method
            path: Request path
            body: Request body

        Returns:
            Dictionary of headers
        """
        headers = {}

        # Builder HMAC authentication
        if self.builder_creds and self.builder_creds.is_configured():
            timestamp = str(int(time.time()))

            message = f"{timestamp}{method}{path}{body}"
            signature = hmac.new(
                self.builder_creds.api_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            headers.update({
                "POLY_BUILDER_API_KEY": self.builder_creds.api_key,
                "POLY_BUILDER_TIMESTAMP": timestamp,
                "POLY_BUILDER_PASSPHRASE": self.builder_creds.api_passphrase,
                "POLY_BUILDER_SIGNATURE": signature,
            })

        # User API credentials
        if self.api_creds and self.api_creds.is_valid():
            # L2 authentication would go here
            pass

        return headers

    def get_order_book(self, token_id: str) -> Dict[str, Any]:
        """
        Get order book for a token.

        Args:
            token_id: Market token ID

        Returns:
            Order book data
        """
        return self._request(
            "GET",
            f"/orderbook/{token_id}"
        )

    def get_market_price(self, token_id: str) -> Dict[str, Any]:
        """
        Get current market price for a token.

        Args:
            token_id: Market token ID

        Returns:
            Price data
        """
        return self._request(
            "GET",
            f"/price/{token_id}"
        )

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """
        Get all open orders for the funder.

        Returns:
            List of open orders
        """
        endpoint = "/orders"
        params = {"maker": self.funder}

        headers = self._build_headers("GET", endpoint)

        return self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers
        ) or []

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order details
        """
        return self._request("GET", f"/order/{order_id}")

    def get_trades(
        self,
        token_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get trade history.

        Args:
            token_id: Filter by token (optional)
            limit: Maximum number of trades

        Returns:
            List of trades
        """
        endpoint = "/trades"
        params = {"limit": str(limit)}

        if token_id:
            params["token_id"] = token_id

        headers = self._build_headers("GET", endpoint)

        return self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers
        ) or []

    def post_order(
        self,
        signed_order: Dict[str, Any],
        order_type: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Submit a signed order.

        Args:
            signed_order: Order with signature
            order_type: Order type (GTC, GTD, FOK)

        Returns:
            Response with order ID and status
        """
        endpoint = "/order"

        # Build request body
        body = {
            "order": signed_order.get("order", signed_order),
            "owner": self.funder,
            "orderType": order_type,
        }

        # Add signature
        if "signature" in signed_order:
            body["signature"] = signed_order["signature"]

        body_json = json.dumps(body, separators=(',', ':'))
        headers = self._build_headers("POST", endpoint, body_json)

        return self._request(
            "POST",
            endpoint,
            data=body,
            headers=headers
        )

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order.

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancellation response
        """
        endpoint = f"/order/{order_id}"
        headers = self._build_headers("DELETE", endpoint)

        return self._request(
            "DELETE",
            endpoint,
            headers=headers
        )

    def cancel_all_orders(self, token_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel all orders.

        Args:
            token_id: Cancel only orders for this token (optional)

        Returns:
            Cancellation response
        """
        endpoint = "/orders"
        params = {}

        if token_id:
            params["token_id"] = token_id

        body = {"maker": self.funder}
        body_json = json.dumps(body, separators=(',', ':'))
        headers = self._build_headers("DELETE", endpoint, body_json)

        return self._request(
            "DELETE",
            endpoint,
            data=body,
            params=params,
            headers=headers
        )


class RelayerClient(ApiClient):
    """
    Client for Builder Relayer API.

    Provides gasless transactions through Polymarket's
    relayer infrastructure.

    Example:
        client = RelayerClient(
            host="https://relayer-v2.polymarket.com",
            chain_id=137,
            builder_creds=builder_creds
        )
    """

    def __init__(
        self,
        host: str = "https://relayer-v2.polymarket.com",
        chain_id: int = 137,
        builder_creds: Optional[BuilderConfig] = None,
        tx_type: str = "SAFE",
        timeout: int = 60
    ):
        """
        Initialize Relayer client.

        Args:
            host: Relayer API host
            chain_id: Chain ID (137 for Polygon)
            builder_creds: Builder credentials
            tx_type: Transaction type (SAFE or PROXY)
            timeout: Request timeout
        """
        super().__init__(base_url=host, timeout=timeout)
        self.chain_id = chain_id
        self.builder_creds = builder_creds
        self.tx_type = tx_type

    def _build_headers(
        self,
        method: str,
        path: str,
        body: str = ""
    ) -> Dict[str, str]:
        """Build Builder HMAC authentication headers."""
        if not self.builder_creds or not self.builder_creds.is_configured():
            raise AuthenticationError("Builder credentials required for relayer")

        timestamp = str(int(time.time()))

        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.builder_creds.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return {
            "POLY_BUILDER_API_KEY": self.builder_creds.api_key,
            "POLY_BUILDER_TIMESTAMP": timestamp,
            "POLY_BUILDER_PASSPHRASE": self.builder_creds.api_passphrase,
            "POLY_BUILDER_SIGNATURE": signature,
        }

    def deploy_safe(self, safe_address: str) -> Dict[str, Any]:
        """
        Deploy a Safe proxy wallet.

        Args:
            safe_address: The Safe address to deploy

        Returns:
            Deployment transaction response
        """
        endpoint = "/deploy"
        body = {"safeAddress": safe_address}
        body_json = json.dumps(body, separators=(',', ':'))
        headers = self._build_headers("POST", endpoint, body_json)

        return self._request(
            "POST",
            endpoint,
            data=body,
            headers=headers
        )

    def approve_usdc(
        self,
        safe_address: str,
        spender: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        Approve USDC spending.

        Args:
            safe_address: Safe address
            spender: Spender address
            amount: Amount to approve

        Returns:
            Approval transaction response
        """
        endpoint = "/approve-usdc"
        body = {
            "safeAddress": safe_address,
            "spender": spender,
            "amount": str(amount),
        }
        body_json = json.dumps(body, separators=(',', ':'))
        headers = self._build_headers("POST", endpoint, body_json)

        return self._request(
            "POST",
            endpoint,
            data=body,
            headers=headers
        )

    def approve_token(
        self,
        safe_address: str,
        token_id: str,
        spender: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        Approve an ERC-1155 token.

        Args:
            safe_address: Safe address
            token_id: Token ID
            spender: Spender address
            amount: Amount to approve

        Returns:
            Approval transaction response
        """
        endpoint = "/approve-token"
        body = {
            "safeAddress": safe_address,
            "tokenId": token_id,
            "spender": spender,
            "amount": str(amount),
        }
        body_json = json.dumps(body, separators=(',', ':'))
        headers = self._build_headers("POST", endpoint, body_json)

        return self._request(
            "POST",
            endpoint,
            data=body,
            headers=headers
        )

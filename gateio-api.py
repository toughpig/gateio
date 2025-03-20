#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gate.io API v4 Demo Script
This script demonstrates how to use the Gate.io API v4 with the Python SDK

API Documentation: https://www.gate.io/docs/developers/apiv4/en/
"""

import time
import os
from dotenv import load_dotenv
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import pprint

# Load environment variables from .env file
load_dotenv()

# Configuration for the API client
def get_api_client(with_credentials=False):
    # Initialize configuration
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4"
    )
    
    # Add API keys for authenticated endpoints
    if with_credentials:
        # Load API keys from environment variables
        configuration.key = os.getenv("GATEIO_API_KEY")
        configuration.secret = os.getenv("GATEIO_API_SECRET")
    
    # Create API client
    api_client = gate_api.ApiClient(configuration)
    return api_client

def demo_spot_public_apis():
    """Demonstrate public spot market endpoints that don't require authentication"""
    print("\n=== Spot Public APIs ===\n")
    
    # Create API client
    api_client = get_api_client()
    
    # Initialize API instances
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # List all currency pairs supported
        print("Listing currency pairs...")
        currency_pairs = spot_api.list_currency_pairs()
        print(f"Total currency pairs: {len(currency_pairs)}")
        print(f"Sample currency pair: {currency_pairs[0]}")
        
        # Get ticker information
        print("\nGetting ticker for BTC_USDT...")
        ticker = spot_api.list_tickers(currency_pair="BTC_USDT")
        pprint.pprint(ticker)
        
        # Get order book
        print("\nGetting order book for BTC_USDT...")
        order_book = spot_api.list_order_book(currency_pair="BTC_USDT", limit=10)
        print(f"Ask orders: {len(order_book.asks)}")
        print(f"Bid orders: {len(order_book.bids)}")
        if order_book.asks:
            print(f"Lowest ask: {order_book.asks[0]}")
        if order_book.bids:
            print(f"Highest bid: {order_book.bids[0]}")
        
        # Get market trades
        print("\nGetting recent trades for BTC_USDT...")
        trades = spot_api.list_trades(currency_pair="BTC_USDT", limit=5)
        for trade in trades:
            print(f"Trade: {trade.id}, Price: {trade.price}, Amount: {trade.amount}, Side: {trade.side}")
        
        # Get candlesticks data
        print("\nGetting candlesticks for BTC_USDT...")
        candles = spot_api.list_candlesticks(currency_pair="BTC_USDT", interval="1h", limit=5)
        for candle in candles:
            print(f"Time: {candle[0]}, Open: {candle[1]}, Close: {candle[2]}, High: {candle[3]}, Low: {candle[4]}, Volume: {candle[5]}")
    
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_spot_private_apis():
    """Demonstrate private spot market endpoints that require authentication"""
    print("\n=== Spot Private APIs ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # Get account balances
        print("Getting account balances...")
        balances = spot_api.list_spot_accounts(currency="BTC,USDT")
        for balance in balances:
            print(f"Currency: {balance.currency}, Available: {balance.available}, Locked: {balance.locked}")
        
        # The following endpoints require authentication with trading permissions:
        # Uncommenting these will execute real trading operations
        
        """
        # Create a limit order
        print("\nCreating a limit buy order...")
        order = gate_api.Order(
            currency_pair="BTC_USDT",
            side="buy",
            amount="0.001",
            price="20000",
            time_in_force="gtc"  # Good till canceled
        )
        result = spot_api.create_order(order)
        print(f"Order created: {result}")
        
        # List open orders
        print("\nListing open orders...")
        open_orders = spot_api.list_orders("BTC_USDT", status="open")
        for order in open_orders:
            print(f"Order: {order.id}, Pair: {order.currency_pair}, Side: {order.side}, Amount: {order.amount}, Price: {order.price}")
        
        # Cancel an order (using the order ID from the created order)
        if result and hasattr(result, 'id'):
            print(f"\nCancelling order {result.id}...")
            cancelled = spot_api.cancel_order(result.id, currency_pair="BTC_USDT")
            print(f"Cancelled order: {cancelled}")
        """
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_futures_public_apis():
    """Demonstrate futures market endpoints that don't require authentication"""
    print("\n=== Futures Public APIs ===\n")
    
    # Create API client
    api_client = get_api_client()
    
    # Initialize API instance
    futures_api = gate_api.FuturesApi(api_client)
    
    try:
        # List all futures contracts
        print("Listing futures contracts...")
        contracts = futures_api.list_futures_contracts("usdt")
        print(f"Total USDT contracts: {len(contracts)}")
        print(f"Sample contract: {contracts[0]}")
        
        # Get futures orderbook
        print("\nGetting futures orderbook for BTC_USDT...")
        orderbook = futures_api.list_futures_order_book(settle="usdt", contract="BTC_USDT", limit=10)
        print(f"Ask orders: {len(orderbook.asks)}")
        print(f"Bid orders: {len(orderbook.bids)}")
        
        # Get futures candlesticks
        print("\nGetting futures candlesticks for BTC_USDT...")
        candles = futures_api.list_futures_candlesticks(settle="usdt", contract="BTC_USDT", interval="1h", limit=5)
        for candle in candles:
            if isinstance(candle, list) and len(candle) >= 6:
                print(f"Time: {candle[0]}, Open: {candle[1]}, Close: {candle[2]}, High: {candle[3]}, Low: {candle[4]}, Volume: {candle[5]}")
        
        # Get futures tickers
        print("\nGetting futures ticker for BTC_USDT...")
        tickers = futures_api.list_futures_tickers(settle="usdt", contract="BTC_USDT")
        for ticker in tickers:
            print(f"Contract: {ticker.contract}, Last: {ticker.last}, Volume 24h: {ticker.volume_24h}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling FuturesApi: {e}")

def demo_margin_apis():
    """Demonstrate margin related endpoints"""
    print("\n=== Margin APIs ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instances
    margin_api = gate_api.MarginApi(api_client)
    
    try:
        # Get margin accounts
        print("Getting margin accounts...")
        accounts = margin_api.list_margin_accounts()
        print(f"Total margin accounts: {len(accounts)}")
        if accounts:
            print(f"Sample account: {accounts[0]}")
        
        # Get cross margin currencies
        print("\nGetting cross margin supported currencies...")
        currencies = margin_api.list_cross_margin_currencies()
        print(f"Total cross margin currencies: {len(currencies)}")
        if currencies:
            print(f"Sample currency: {currencies[0]}")
            
        # Get funding accounts
        print("\nGetting funding accounts...")
        funding = margin_api.list_funding_accounts()
        print(f"Total funding accounts: {len(funding)}")
        if funding:
            print(f"Sample funding account: {funding[0]}")
        
        # The following endpoints require authentication with margin permissions
        # Uncommenting these will execute real margin operations
        
        """
        # Query specific margin account
        print("\nQuerying specific margin account...")
        specific_accounts = margin_api.list_margin_accounts(currency_pair="BTC_USDT")
        for acc in specific_accounts:
            print(f"Pair: {acc.currency_pair}, Risk: {acc.risk}, Base: {acc.base}, Quote: {acc.quote}")
        
        # Query funding accounts for specific currencies
        print("\nGetting specific funding accounts...")
        specific_funding = margin_api.list_funding_accounts(currency="BTC,USDT")
        for fund in specific_funding:
            print(f"Currency: {fund.currency}, Available: {fund.available}, Locked: {fund.locked}")
        """
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling MarginApi: {e}")


def main():
    print("Gate.io API v4 Demo\n")
    print("NOTE: Please install the Gate.io Python SDK first: pip install gate-api")
    print("WARNING: For authenticated endpoints, replace placeholders with your actual API keys")
    
    # Run demos for various API categories
    demo_spot_public_apis()
    # print("\nSkipping authenticated endpoints. To use them, set your API keys in the code.")
    # Comment these lines if you've added your API keys and want to test authenticated endpoints
    demo_spot_private_apis()
    demo_futures_public_apis()
    demo_margin_apis()
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main() 
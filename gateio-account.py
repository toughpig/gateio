#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gate.io Account API v4 Demo Script
This script demonstrates how to use the Gate.io Account API v4 with the Python SDK

API Documentation: https://www.gate.io/docs/developers/apiv4/en/#account
"""

import os
import pprint
from dotenv import load_dotenv
import gate_api
from gate_api.exceptions import ApiException, GateApiException

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

def demo_account_detail():
    """Demonstrate getting account details"""
    print("\n=== Account Details ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance for account
    # Note: Gate.io SDK should have AccountApi class
    account_api = gate_api.AccountApi(api_client)
    
    try:
        # Get account details
        print("Getting account details...")
        account_detail = account_api.get_account_detail()
        print(f"User ID: {account_detail.user_id}")
        print(f"VIP Tier: {account_detail.tier}")
        
        if hasattr(account_detail, 'copy_trading_role'):
            role_descriptions = {
                0: "Ordinary user",
                1: "Order leader",
                2: "Follower",
                3: "Order leader and follower"
            }
            role = account_detail.copy_trading_role
            role_desc = role_descriptions.get(role, "Unknown role")
            print(f"Copy Trading Role: {role} ({role_desc})")
        
        if hasattr(account_detail, 'key') and hasattr(account_detail.key, 'mode'):
            mode_descriptions = {
                1: "Classic account",
                2: "Portfolio margin account"
            }
            mode = account_detail.key.mode
            mode_desc = mode_descriptions.get(mode, "Unknown mode")
            print(f"Account Mode: {mode} ({mode_desc})")
        
        if hasattr(account_detail, 'ip_whitelist') and account_detail.ip_whitelist:
            print(f"IP Whitelist: {', '.join(account_detail.ip_whitelist)}")
        
        if hasattr(account_detail, 'currency_pairs') and account_detail.currency_pairs:
            print(f"Currency Pairs Whitelist: {', '.join(account_detail.currency_pairs)}")
            
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling AccountApi: {e}")

def demo_account_balances():
    """Demonstrate getting account balances across different accounts"""
    print("\n=== Account Balances ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # We'll use spot API for spot account balances
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # Get spot account balances
        print("Getting spot account balances...")
        spot_balances = spot_api.list_spot_accounts()
        
        print(f"Total spot currencies: {len(spot_balances)}")
        
        # Show non-zero balances for spot account
        print("\nNon-zero spot balances:")
        for balance in spot_balances:
            # Only show balances with available or locked amounts
            if float(balance.available) > 0 or float(balance.locked) > 0:
                print(f"Currency: {balance.currency}, Available: {balance.available}, Locked: {balance.locked}")
        
        # Get cross margin account balances if available
        try:
            margin_api = gate_api.MarginApi(api_client)
            print("\nGetting cross margin account balances...")
            cross_margin_account = margin_api.get_cross_margin_account()
            
            if hasattr(cross_margin_account, 'balances') and cross_margin_account.balances:
                print(f"Total cross margin currencies: {len(cross_margin_account.balances)}")
                
                # Show non-zero balances for cross margin account
                print("\nNon-zero cross margin balances:")
                for currency, balance in cross_margin_account.balances.items():
                    # Only show balances with non-zero amounts
                    if (hasattr(balance, 'available') and float(balance.available) > 0) or \
                       (hasattr(balance, 'borrowed') and float(balance.borrowed) > 0) or \
                       (hasattr(balance, 'interest') and float(balance.interest) > 0):
                        print(f"Currency: {currency}, Available: {balance.available}, " +
                              f"Borrowed: {balance.borrowed}, Interest: {balance.interest}")
            else:
                print("No cross margin balances found or cross margin account not enabled.")
        except GateApiException as ex:
            if ex.label == "CROSS_ACCOUNT_NOT_FOUND":
                print("Note: Cross margin account is not enabled. Transfer funds to cross margin account to activate it.")
            else:
                print(f"Note: Cross margin account error: {ex.message}")
        except ApiException as e:
            print(f"Note: Cross margin account might not be accessible: {e}")
        
        # Get futures account balances if available
        try:
            futures_api = gate_api.FuturesApi(api_client)
            print("\nGetting USDT futures account balances...")
            usdt_futures_accounts = futures_api.list_futures_accounts("usdt")
            
            if hasattr(usdt_futures_accounts, 'total') and hasattr(usdt_futures_accounts.total, 'equity'):
                print(f"USDT Futures Equity: {usdt_futures_accounts.total.equity}")
                print(f"USDT Futures Unrealized PNL: {usdt_futures_accounts.total.unrealised_pnl}")
                print(f"USDT Futures Available Balance: {usdt_futures_accounts.total.available}")
        except GateApiException as ex:
            if ex.label == "USER_NOT_FOUND":
                print("Note: Futures account is not enabled. Transfer funds to futures account to activate it.")
            else:
                print(f"Note: Futures account error: {ex.message}")
        except ApiException as e:
            print(f"Note: Futures account might not be accessible: {e}")
            
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_account_trading_fees():
    """Demonstrate getting trading fees for the account"""
    print("\n=== Account Trading Fees ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance for spot trading (which includes fee endpoints)
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # Get trading fee rates
        print("Getting trading fee rates...")
        fee_rates = spot_api.get_fee()  # Get general fee rates
        
        if hasattr(fee_rates, 'user_id'):
            print(f"User ID: {fee_rates.user_id}")
        
        if hasattr(fee_rates, 'taker_fee'):
            print(f"Taker Fee Rate: {fee_rates.taker_fee}")
        
        if hasattr(fee_rates, 'maker_fee'):
            print(f"Maker Fee Rate: {fee_rates.maker_fee}")
        
        if hasattr(fee_rates, 'gt_discount'):
            print(f"GT Discount Enabled: {fee_rates.gt_discount}")
        
        if hasattr(fee_rates, 'gt_taker_fee'):
            print(f"GT Taker Fee Rate: {fee_rates.gt_taker_fee}")
        
        if hasattr(fee_rates, 'gt_maker_fee'):
            print(f"GT Maker Fee Rate: {fee_rates.gt_maker_fee}")
        
        # Get fee rates for specific currency pairs if needed
        try:
            print("\nGetting currency-specific fee rates for BTC_USDT...")
            currency_pair_fee = spot_api.get_fee(currency_pair="BTC_USDT")  # Use keyword argument
            if currency_pair_fee:
                print(f"BTC_USDT fee details:")
                if hasattr(currency_pair_fee, 'taker_fee'):
                    print(f"  Taker Fee: {currency_pair_fee.taker_fee}")
                if hasattr(currency_pair_fee, 'maker_fee'):
                    print(f"  Maker Fee: {currency_pair_fee.maker_fee}")
        except (GateApiException, ApiException) as e:
            print(f"Note: Could not get currency pair specific fees: {e}")
            
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_account_activity():
    """Demonstrate getting account activity and logs"""
    print("\n=== Account Activity ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Create a general API instance to query different API endpoints
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # Get account activity (spot trading history)
        print("Getting recent trades...")
        # Query the most recent trades for the account
        my_trades = spot_api.list_my_trades(limit=10)
        
        print(f"Total recent trades: {len(my_trades)}")
        if my_trades:
            print("\nRecent trades:")
            for trade in my_trades:
                print(f"ID: {trade.id}, Pair: {trade.currency_pair}, Side: {trade.side}, Amount: {trade.amount}, Price: {trade.price}, Fee: {trade.fee}, Time: {trade.create_time}")
        
        # Get order history for BTC_USDT as an example
        print("\nGetting order history for BTC_USDT...")
        try:
            orders = spot_api.list_orders("BTC_USDT", status="finished", limit=10)  # Added currency_pair parameter
            
            print(f"Total orders: {len(orders)}")
            if orders:
                print("\nRecent orders:")
                for order in orders:
                    print(f"ID: {order.id}, Pair: {order.currency_pair}, Side: {order.side}, Amount: {order.amount}, Price: {order.price}, Status: {order.status}, Time: {order.create_time}")
        except GateApiException as ex:
            if "INVALID_CURRENCY_PAIR" in str(ex):
                print("Note: BTC_USDT pair might not be available for your account.")
            else:
                raise
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_account_settings():
    """Demonstrate account settings (where available)"""
    print("\n=== Account Settings ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Create an account API instance
    account_api = gate_api.AccountApi(api_client)
    
    try:
        # Get account detail which includes some settings
        print("Getting account settings from account detail...")
        account_detail = account_api.get_account_detail()
        
        # Print settings details
        if hasattr(account_detail, 'user_id'):
            print(f"User ID: {account_detail.user_id}")
        
        # IP whitelist
        if hasattr(account_detail, 'ip_whitelist'):
            if account_detail.ip_whitelist:
                print(f"IP Whitelist: {', '.join(account_detail.ip_whitelist)}")
            else:
                print("IP Whitelist: Not configured")
        
        # Currency pair whitelist
        if hasattr(account_detail, 'currency_pairs'):
            if account_detail.currency_pairs:
                print(f"Currency Pairs Whitelist: {', '.join(account_detail.currency_pairs)}")
            else:
                print("Currency Pairs Whitelist: Not configured")
        
        # Check if portfolio margin is enabled
        if hasattr(account_detail, 'key') and hasattr(account_detail.key, 'mode'):
            if account_detail.key.mode == 2:
                print("Portfolio Margin Account: Enabled")
            else:
                print("Portfolio Margin Account: Not enabled")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling AccountApi: {e}")

def demo_account_history():
    """Demonstrate account history and ledger entries"""
    print("\n=== Account History ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize spot API for account book entries
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # Get account book entries
        print("Getting account book entries...")
        account_book = spot_api.list_spot_account_book(limit=10)
        
        print(f"Total account book entries: {len(account_book)}")
        if account_book:
            print("\nRecent account book entries:")
            for entry in account_book:
                print(f"Time: {entry.time}, Currency: {entry.currency}, Change: {entry.change}, Balance: {entry.balance}, Type: {entry.type}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_sub_accounts():
    """Demonstrate sub-account management"""
    print("\n=== Sub-Account Management ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Create sub-account API
    sub_account_api = gate_api.SubAccountApi(api_client)
    
    try:
        # List all sub-accounts
        print("Getting sub-accounts...")
        sub_accounts = sub_account_api.list_sub_accounts()
        
        print(f"Total sub-accounts: {len(sub_accounts)}")
        if sub_accounts:
            print("\nSub-accounts:")
            for sub in sub_accounts:
                status = "Enabled" if sub.status == 1 else "Disabled"
                print(f"User ID: {sub.user_id}, Name: {sub.name}, Email: {sub.email}, Status: {status}")
        
        # Note: Creating, modifying, or deleting sub-accounts requires additional permissions
        # and involves POST/PUT/DELETE requests that are not shown here to avoid making changes
        
        # Get sub-account balances if there are sub-accounts
        if sub_accounts:
            print("\nGetting sub-account balances...")
            wallet_api = gate_api.WalletApi(api_client)
            sub_balances = wallet_api.list_sub_account_balances()
            
            if sub_balances:
                for sub_balance in sub_balances:
                    print(f"\nSub-account: {sub_balance.user_id}")
                    if hasattr(sub_balance, 'total'):
                        for currency, amount in sub_balance.total.items():
                            if float(amount) > 0:
                                print(f"  {currency}: {amount}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SubAccountApi/WalletApi: {e}")

def demo_unified_account():
    """Demonstrate unified account features (if available)"""
    print("\n=== Unified Account ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Try to check if unified account is available
    # Since unified account API might be under a different class
    try:
        # Attempt to get the unified account status
        # This is just a check - in practice, you'd need to refer to the exact API class
        # that Gate.io provides for unified accounts
        
        # First, check using account detail if account mode indicates unified
        account_api = gate_api.AccountApi(api_client)
        account_detail = account_api.get_account_detail()
        
        print("Checking if unified account is enabled...")
        
        # Check account mode
        if hasattr(account_detail, 'key') and hasattr(account_detail.key, 'mode'):
            if account_detail.key.mode == 1:
                print("Account Type: Classic Account")
                print("Note: Unified Account features are not available with this account type.")
            elif account_detail.key.mode == 2:
                print("Account Type: Portfolio Margin Account")
                print("Note: This is a portfolio margin account, which has some unified features.")
            else:
                print(f"Account Type: Unknown Mode ({account_detail.key.mode})")
        
        # Try to access unified-specific API endpoints if they exist
        # This is placeholder code and would need adjusting based on the actual SDK
        try:
            # This is a placeholder - the actual implementation would depend on the SDK
            print("\nAttempting to check unified account details (if available)...")
            # unified_api = gate_api.UnifiedApi(api_client)  # Example - might not exist
            # unified_info = unified_api.get_unified_account_info()  # Example - might not exist
            print("Note: Unified account API endpoints may require specific SDK support.")
        except (GateApiException, ApiException, AttributeError) as e:
            print(f"Unified account endpoints not available or accessible: {e}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when checking unified account: {e}")

def main():
    """Main function to run the demo"""
    print("=== Gate.io Account API v4 Demo ===\n")
    
    # Verify API credentials are set
    if not os.getenv("GATEIO_API_KEY") or not os.getenv("GATEIO_API_SECRET"):
        print("Error: API credentials not set. Please configure GATEIO_API_KEY and GATEIO_API_SECRET in .env file.")
        return
    
    # Run the demos
    demo_account_detail()
    demo_account_balances()
    demo_account_trading_fees()
    demo_account_activity()
    demo_account_settings()
    demo_account_history()
    demo_sub_accounts()
    demo_unified_account()
    
    print("\n=== Demo Completed ===")

if __name__ == "__main__":
    main() 
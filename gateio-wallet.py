#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gate.io Wallet API v4 Demo Script
This script demonstrates how to use the Gate.io Wallet API v4 with the Python SDK

API Documentation: https://www.gate.io/docs/developers/apiv4/en/#wallet
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

def demo_wallet_currencies():
    """Demonstrate getting currency information"""
    print("\n=== Wallet Currencies ===\n")
    
    # Create API client 
    api_client = get_api_client()
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # Get currency details (public endpoint)
        print("Getting currency details...")
        currencies = spot_api.list_currencies()
        print(f"Total currencies: {len(currencies)}")
        if currencies:
            print(f"Sample currency: {currencies[0]}")
        
        # Get specific currency details
        print("\nGetting BTC currency details...")
        btc_currency = spot_api.get_currency("BTC")
        print(f"BTC details: {btc_currency}")
            
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling SpotApi: {e}")

def demo_wallet_deposit_address():
    """Demonstrate getting deposit address"""
    print("\n=== Wallet Deposit Address ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # Get deposit address
        print("Getting deposit address for BTC...")
        address = wallet_api.get_deposit_address("BTC")
        print(f"Currency: {address.currency}, Address: {address.address}")
        
        # Get deposit address for USDT
        print("\nGetting deposit address for USDT...")
        # The get_deposit_address method doesn't accept a chain parameter in current SDK version
        usdt_address = wallet_api.get_deposit_address("USDT")
        print(f"Currency: {usdt_address.currency}, Address: {usdt_address.address}")
        if hasattr(usdt_address, 'chain'):
            print(f"Chain: {usdt_address.chain}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_wallet_withdrawals():
    """Demonstrate withdrawal related endpoints"""
    print("\n=== Wallet Withdrawals ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instances
    wallet_api = gate_api.WalletApi(api_client)
    withdrawal_api = gate_api.WithdrawalApi(api_client)
    
    try:
        # Get withdrawal records
        print("Getting withdrawal records...")
        withdrawals = wallet_api.list_withdrawals(limit=5)
        for withdrawal in withdrawals:
            print(f"ID: {withdrawal.id}, Currency: {withdrawal.currency}, Amount: {withdrawal.amount}, Status: {withdrawal.status}")
        
        # Get withdrawal records for specific currency
        print("\nGetting BTC withdrawal records...")
        btc_withdrawals = wallet_api.list_withdrawals(currency="BTC", limit=5)
        print(f"Total records: {len(btc_withdrawals)}")
        if btc_withdrawals:
            print(f"Sample BTC withdrawal: {btc_withdrawals[0]}")
        
        # The following code demonstrates creating a withdrawal - commented out to avoid real withdrawals
        """
        # Create a withdrawal request
        print("\nCreating a withdrawal request...")
        withdrawal_request = gate_api.LedgerRecord(
            currency="USDT",
            address="TRC20AddressHere", 
            amount="10",
            chain="trc20"  # For tokens like USDT, specify the chain
        )
        result = withdrawal_api.withdraw(withdrawal_request)
        print(f"Withdrawal created: {result}")
        """
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi/WithdrawalApi: {e}")

def demo_wallet_deposits():
    """Demonstrate deposit related endpoints"""
    print("\n=== Wallet Deposits ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # Get deposit records
        print("Getting deposit records...")
        deposits = wallet_api.list_deposits(limit=5)
        for deposit in deposits:
            print(f"ID: {deposit.id}, Currency: {deposit.currency}, Amount: {deposit.amount}, Status: {deposit.status}")
        
        # Get deposit records for specific currency
        print("\nGetting USDT deposit records...")
        usdt_deposits = wallet_api.list_deposits(currency="USDT", limit=5)
        print(f"Total USDT deposits: {len(usdt_deposits)}")
        if usdt_deposits:
            print(f"Sample USDT deposit: {usdt_deposits[0]}")
            
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_wallet_transfers():
    """Demonstrate transfer related endpoints"""
    print("\n=== Wallet Transfers ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # List transfers between trading accounts
        print("Getting transfers between trading accounts...")
        transfers = wallet_api.list_sub_account_transfers(limit=5)
        print(f"Total transfers: {len(transfers)}")
        if transfers:
            print(f"Sample transfer: {transfers[0]}")
        
        # The following code demonstrates creating a transfer - commented out to avoid real transfers
        """
        # Transfer between main and sub accounts
        print("\nTransferring from main to sub account...")
        transfer_request = gate_api.Transfer(
            currency="USDT",
            sub_account="SubAccountUID",
            direction="to",  # 'to' or 'from'
            amount="10",
            type="spot"  # 'spot' or 'futures'
        )
        result = wallet_api.transfer_with_sub_account(transfer_request)
        print(f"Transfer created: {result}")
        
        # Transfer between trading accounts (e.g., spot to margin)
        print("\nTransferring from spot to margin account...")
        transfer_request = gate_api.TransferRequest(
            currency="USDT",
            from_account="spot",
            to_account="margin",
            amount="10"
        )
        result = wallet_api.transfer(transfer_request)
        print(f"Transfer created: {result}")
        """
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_wallet_account_balances():
    """Demonstrate getting account balances"""
    print("\n=== Wallet Account Balances ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # Get total balance
        print("Getting total balance...")
        total_balance = wallet_api.get_total_balance()
        print(f"Total balance: {total_balance}")
        
        # The structure of total_balance may have changed in recent API versions
        # Check if specific attributes are available before accessing them
        if hasattr(total_balance, 'total'):
            if hasattr(total_balance.total, 'btc'):
                print(f"Total balance in BTC: {total_balance.total.btc}")
            if hasattr(total_balance.total, 'usd'):
                print(f"Total balance in USD: {total_balance.total.usd}")
        
        # Get sub-account balances
        print("\nGetting sub-account balances...")
        sub_balances = wallet_api.list_sub_account_balances()
        print(f"Total sub-accounts: {len(sub_balances)}")
        if sub_balances:
            print(f"Sample sub-account balance: {sub_balances[0]}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_wallet_small_balances():
    """Demonstrate small balance related endpoints"""
    print("\n=== Wallet Small Balances ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # List small balances
        print("Listing small balances...")
        small_balances = wallet_api.list_small_balance()
        print(f"Total small balances: {len(small_balances)}")
        if small_balances:
            print(f"Sample small balance: {small_balances[0]}")
        
        # List small balance history
        print("\nListing small balance conversion history...")
        balance_history = wallet_api.list_small_balance_history()
        print(f"Total conversion history: {len(balance_history)}")
        if balance_history:
            print(f"Sample conversion: {balance_history[0]}")
        
        # The following code demonstrates converting small balances - commented out to avoid real conversion
        """
        # Convert small balances to BTC
        print("\nConverting small balances to BTC...")
        result = wallet_api.convert_small_balance()
        print(f"Conversion result: {result}")
        """
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_wallet_saved_addresses():
    """Demonstrate saved address related endpoints"""
    print("\n=== Wallet Saved Addresses ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # List saved addresses
        print("Listing saved addresses for BTC...")
        saved_addresses = wallet_api.list_saved_address(currency="BTC")
        print(f"Total saved BTC addresses: {len(saved_addresses)}")
        if saved_addresses:
            print(f"Sample saved address: {saved_addresses[0]}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_wallet_trading_fees():
    """Demonstrate trading fee related endpoints"""
    print("\n=== Wallet Trading Fees ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # Get personal trading fee rate
        print("Getting personal trading fee rate...")
        trading_fee = wallet_api.get_trade_fee()
        print(f"Trading fee: {trading_fee}")
        
        # Get trading fee for a specific currency pair
        print("\nGetting trading fee for BTC_USDT...")
        btc_trading_fee = wallet_api.get_trade_fee(currency_pair="BTC_USDT")
        print(f"BTC_USDT trading fee: {btc_trading_fee}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_withdrawal_cancel():
    """Demonstrate canceling a withdrawal"""
    print("\n=== Cancel Withdrawal ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instance
    withdrawal_api = gate_api.WithdrawalApi(api_client)
    
    try:
        # The following code demonstrates canceling a withdrawal - commented out to avoid real cancellations
        """
        # Cancel a withdrawal
        print("Canceling withdrawal with ID 123456...")
        result = withdrawal_api.cancel_withdrawal("123456")
        print(f"Cancellation result: {result}")
        """
        print("Warning: Cancellation example is commented out to prevent actual cancellations.")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WithdrawalApi: {e}")

def demo_wallet_chains():
    """Demonstrate getting chains for a currency"""
    print("\n=== Wallet Currency Chains ===\n")
    
    # Create API client
    api_client = get_api_client()
    
    # Initialize API instance
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # List chains supported for USDT
        print("Listing chains supported for USDT...")
        chains = wallet_api.list_currency_chains("USDT")
        print(f"Total chains for USDT: {len(chains)}")
        for chain in chains:
            print(f"Chain: {chain.chain}, Name: {chain.name_cn}/{chain.name_en}, Is_deposit: {chain.is_deposit_disabled}, Is_withdraw: {chain.is_withdraw_disabled}")
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WalletApi: {e}")

def demo_uid_transfers():
    """Demonstrate UID transfer related endpoints"""
    print("\n=== UID Transfers ===\n")
    
    # Create API client with authentication
    api_client = get_api_client(with_credentials=True)
    
    # Initialize API instances
    withdrawal_api = gate_api.WithdrawalApi(api_client)
    wallet_api = gate_api.WalletApi(api_client)
    
    try:
        # Get UID transfer history
        print("Getting UID transfer history...")
        transfers = wallet_api.list_push_orders(limit=5)
        print(f"Total transfers: {len(transfers)}")
        if transfers:
            print(f"Sample transfer: {transfers[0]}")
        
        # The following code demonstrates creating a UID transfer - commented out to avoid real transfers
        """
        # Create a UID transfer
        print("\nCreating a UID transfer...")
        transfer_request = gate_api.PushOrder(
            currency="USDT",
            amount="10",
            uid="12345",  # Recipient UID
            memo="Gift"   # Optional memo
        )
        result = withdrawal_api.withdraw_push_order(transfer_request)
        print(f"Transfer created: {result}")
        """
        
    except GateApiException as ex:
        print(f"Gate API exception, label: {ex.label}, message: {ex.message}")
    except ApiException as e:
        print(f"Exception when calling WithdrawalApi/WalletApi: {e}")

def main():
    print("Gate.io Wallet API v4 Demo\n")
    print("NOTE: Please install the Gate.io Python SDK first: pip install gate-api")
    print("WARNING: For authenticated endpoints, you need API keys with appropriate permissions")
    
    # Run demos for public API endpoints (no authentication required)
    demo_wallet_currencies()
    demo_wallet_chains()
    
    # Check if API credentials are available
    if os.getenv("GATEIO_API_KEY") and os.getenv("GATEIO_API_SECRET"):
        print("\nAPI credentials found. Running authenticated endpoints...")
        # Run demos for authenticated API endpoints
        try:
            demo_wallet_deposit_address()
            demo_wallet_withdrawals()
            demo_wallet_deposits()
            demo_wallet_transfers()
            demo_wallet_account_balances()
            demo_wallet_small_balances()
            demo_wallet_saved_addresses()
            demo_wallet_trading_fees()
            demo_withdrawal_cancel()
            demo_uid_transfers()
        except Exception as e:
            print(f"\nError occurred while running authenticated endpoints: {e}")
            print("Please check your API key permissions and try again.")
    else:
        print("\nAPI credentials not found in .env file. Skipping authenticated endpoints.")
        print("To run authenticated endpoints, create a .env file with GATEIO_API_KEY and GATEIO_API_SECRET.")
    
    print("\nWallet API Demo completed!")

if __name__ == "__main__":
    main() 
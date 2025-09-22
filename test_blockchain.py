from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Test connection
if w3.is_connected():
    print("✅ Connected to Ganache!")
    print(f"Latest block number: {w3.eth.block_number}")
    
    # Get accounts
    accounts = w3.eth.accounts
    print(f"Available accounts: {len(accounts)}")
    print(f"First account: {accounts[0]}")
    print(f"Balance: {w3.eth.get_balance(accounts[0])} Wei")
else:
    print("❌ Not connected to Ganache")
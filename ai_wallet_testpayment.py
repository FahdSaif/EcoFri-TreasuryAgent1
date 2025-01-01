from web3 import Web3
import requests
import time
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Connect to Sepolia testnet via Infura
infura_url = "https://sepolia.infura.io/v3/e0148fcea0d64bee8747c0717bab039e"  # Infura Project ID
web3 = Web3(Web3.HTTPProvider(infura_url))

# Ensure connection is established
if not web3.is_connected():
    raise ConnectionError("Failed to connect to the Sepolia network. Check your Infura URL or internet connection.")

# Contract and wallet things
contract_address = "0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066"  # Deployed smart contract address on sepolia - watch video to load it
backup_wallet_address = "0x79438A85548Cd4f1E6FFd0A190274060B533fd01"  # Fahd's:Backup wallet address
backup_wallet_private_key = "7992894d806fce60a0b7bc8b57bd2bfa88ea0101d01f5b281a771652d89641d7"  # Backup wallet private key: nEED TO PUT THIS IN AN Envirn=onment variable - later
api_owner_wallet = "0x222464B2c06d7be1644b8c8Ec04086233ef0663D"  # API owner's wallet : for now this is just one of my wallets - will be another user and his respective wallet
postman_api_url = "https://f495ae9c-29fc-461f-8b53-1a12962c34cd.mock.pstmn.io/getdata"  # Postman mock server URL - not sure how long this is valid. :) 

token_address = "0xF469A33cd0B806AFDDCFA5CEA1d8Fe408ec43B9c"  # Test DAI contract address

#my abo - take this out later as a good practive in a seprate file - mitigate spegetti below
abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "address", "name": "recipient", "type": "address"}
        ],
        "name": "executeTransfer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "refillFromBackup",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_backupWallet", "type": "address"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "backupWallet",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"}
        ],
        "name": "getBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Connect to the smart contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Machine Learning model setup
model = RandomForestRegressor(n_estimators=100)  # Random forest for gas price prediction
historical_gas_prices = []  # Store historical gas prices for training of my model

def get_gas_price():
    """Fetch the current gas price."""
    try:
        return web3.eth.gas_price
    except Exception as e:
        print(f"Error fetching gas price: {e}")
        return None

def get_dai_price():
    """Fetch the current DAI price in USD from CoinGecko."""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=dai&vs_currencies=usd")
        data = response.json()
        return data["dai"]["usd"]
    except Exception as e:
        print(f"Error fetching DAI price: {e}")
        return None

def get_wallet_balance():
    """Fetch the current balance of the AI smart contract wallet."""
    try:
        balance = contract.functions.getBalance(token_address).call()
        print(f"Current wallet balance: {balance / (10 ** 18)} DAI")
        return balance
    except Exception as e:
        print(f"Error fetching wallet balance: {e}")
        return 0

def transfer_from_backup(token_address, amount):
    """Transfer tokens from the backup wallet to the smart contract."""
    try:
        transaction = contract.functions.refillFromBackup(
            token_address,
            amount * (10 ** 18)
        ).build_transaction({
            'from': backup_wallet_address,
            'nonce': web3.eth.get_transaction_count(backup_wallet_address),
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })

        signed_tx = web3.eth.account.sign_transaction(transaction, backup_wallet_private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Refill transaction sent. Hash: {web3.to_hex(tx_hash)}")
    except Exception as e:
        print(f"Error transferring from backup: {e}")

def call_api_and_pay(api_url, amount_dai):
    """Call an API and pay the API owner."""
    try:
        print("Calling API...")
        response = requests.get(api_url)
        if response.status_code == 200:
            print("API call successful. Processing payment...")

            current_balance = get_wallet_balance()
            if current_balance < amount_dai * (10 ** 18):
                print("Insufficient funds in AI Wallet. Replenish before proceeding.")
                return

            web3.eth.default_account = backup_wallet_address  # Ensure default account is set
            transaction = contract.functions.executeTransfer(
                token_address,
                amount_dai * (10 ** 18),
                api_owner_wallet
            ).build_transaction({
                'from': backup_wallet_address,
                'nonce': web3.eth.get_transaction_count(backup_wallet_address),
                'gas': 200000,
                'gasPrice': web3.eth.gas_price
            })

            signed_tx = web3.eth.account.sign_transaction(transaction, backup_wallet_private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"Payment sent. Transaction hash: {web3.to_hex(tx_hash)}")
        else:
            print(f"API call failed. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def monitor_and_act():
    """Monitor wallet balance, DAI price, and interact with the API."""
    payment_amount_dai = 1  # Amount of DAI to pay per API call
    while True:
        print("Monitoring API and wallet...")
        call_api_and_pay(postman_api_url, payment_amount_dai)
        time.sleep(500)  # Run every 2 minutes

if __name__ == "__main__":
    print("Starting API interaction and payment monitoring...")
    monitor_and_act()

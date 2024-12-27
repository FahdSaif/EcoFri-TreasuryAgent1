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

# Contract and wallet details
contract_address = "0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066"  # deployed smart contract address
backup_wallet_address = "0x79438A85548Cd4f1E6FFd0A190274060B533fd01"  # backup wallet address
backup_wallet_private_key = "7992894d806fce60a0b7bc8b57bd2bfa88ea0101d01f5b281a771652d89641d7"  # backup wallet private key
abi =  [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "token",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "recipient",
				"type": "address"
			}
		],
		"name": "executeTransfer",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "token",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "refillFromBackup",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_backupWallet",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "backupWallet",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "token",
				"type": "address"
			}
		],
		"name": "getBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
  # AI SMART CONTRACT WALLET contract ABI
token_address = "0xF469A33cd0B806AFDDCFA5CEA1d8Fe408ec43B9c"  # Test DAI contract address

# Connect to the smart contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Machine Learning model setup
model = RandomForestRegressor(n_estimators=100)  # Random forest for gas price prediction
historical_gas_prices = []  # Store historical gas prices for training

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

def train_model():
    """Train the ML model on historical gas price data."""
    if len(historical_gas_prices) > 10:
        X = np.arange(len(historical_gas_prices)).reshape(-1, 1)
        y = historical_gas_prices
        model.fit(X, y)
        print("Model trained on historical gas price data.")

def predict_gas_price():
    """Predict future gas prices based on the trained model."""
    if len(historical_gas_prices) > 10:
        next_time_step = np.array([[len(historical_gas_prices)]])
        return model.predict(next_time_step)[0]
    return None

def transfer_from_backup(token_address, amount):
    """Transfer tokens from the backup wallet to the smart contract."""
    try:
        transaction = contract.functions.refillFromBackup(
            token_address,
            amount * (10 ** 18)  # Convert amount to token decimals
        ).build_transaction({
            'from': backup_wallet_address,
            'nonce': web3.eth.get_transaction_count(backup_wallet_address),
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })

        signed_tx = web3.eth.account.sign_transaction(transaction, backup_wallet_private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Refill transaction sent. Hash: {web3.to_hex(tx_hash)}")
    except Exception as e:
        print(f"Error transferring from backup: {e}")

def monitor_and_act():
    """Monitor wallet balance, DAI price, gas price, and act intelligently."""
    while True:
        # Fetch current balance of the wallet
        token_balance = contract.functions.getBalance(token_address).call()
        print(f"Current wallet balance: {token_balance / (10 ** 18)} tokens")

        # Fetch gas price and predict future gas prices
        current_gas_price = get_gas_price()
        predicted_gas_price = predict_gas_price()

        # Fetch the current DAI price
        dai_price = get_dai_price()
        if dai_price:
            print(f"Current DAI Price: ${dai_price} USD")

        if current_gas_price:
            historical_gas_prices.append(current_gas_price)
            if len(historical_gas_prices) % 10 == 0:  # Train the model every 10 data points
                train_model()

        # Decision-making logic
        if token_balance < 100 * (10 ** 18):  # Low balance condition
            print("Primary wallet balance low. Replenishing from backup wallet.")
            transfer_from_backup(token_address, 50)  # Transfer 50 tokens
        elif dai_price and dai_price < 1.01:  # DAI price condition
            print("DAI price is low. Consider buying or taking action.")
        elif current_gas_price and predicted_gas_price and current_gas_price < predicted_gas_price:  # Gas price condition
            print("Favorable conditions detected. Replenishing from backup wallet.")
            transfer_from_backup(token_address, 50)
        else:
            print("No action required.") 

        # Wait before the next monitoring cycle
        time.sleep(60)

if __name__ == "__main__":
    print("Starting AI wallet monitoring...")
    monitor_and_act()

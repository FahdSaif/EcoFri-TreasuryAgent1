from web3 import Web3
import openai
import requests
import time
import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Set up logging
logging.basicConfig(filename="ai_wallet_logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# OpenAI API Key
openai.api_key = "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"  # Replace with your OpenAI API key

# MY ConnectION to Sepolia testnet via Infura
infura_url = "https://sepolia.infura.io/v3/e0148fcea0d64bee8747c0717bab039e"  # Replace with your Infura URL
web3 = Web3(Web3.HTTPProvider(infura_url))

# Ensurng connection is established
if not web3.is_connected():
    raise ConnectionError("Failed to connect to the Sepolia network. Check your Infura URL or internet connection.")

# Contract and wallet details
contract_address = "0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066"  # Replace with your smart contract address
backup_wallet_address = "0x79438A85548Cd4f1E6FFd0A190274060B533fd01"  # Replace with your backup wallet address
backup_wallet_private_key = "7992894d806fce60a0b7bc8b57bd2bfa88ea0101d01f5b281a771652d89641d7"  # Replace with private key for backup wallet
token_address = "0xF469A33cd0B806AFDDCFA5CEA1d8Fe408ec43B9c"  # Replace with Test DAI contract address

# ABI
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

# ML model setup
model = RandomForestRegressor(n_estimators=100)
historical_gas_prices = []


def get_gas_price():
    try:
        return web3.eth.gas_price
    except Exception as e:
        logging.error(f"Error fetching gas price: {e}")
        return None


def get_dai_price():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=dai&vs_currencies=usd")
        return response.json()["dai"]["usd"]
    except Exception as e:
        logging.error(f"Error fetching DAI price: {e}")
        return None


def train_model():
    if len(historical_gas_prices) > 10:
        X = np.arange(len(historical_gas_prices)).reshape(-1, 1)
        y = historical_gas_prices
        model.fit(X, y)
        logging.info("Model trained on historical gas price data.")


def predict_gas_price():
    if len(historical_gas_prices) > 10:
        next_time_step = np.array([[len(historical_gas_prices)]])
        return model.predict(next_time_step)[0]
    return None


def transfer_from_backup(token_address, amount):
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
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logging.info(f"Refill transaction sent. Hash: {web3.to_hex(tx_hash)}")
    except Exception as e:
        logging.error(f"Error transferring from backup: {e}")


def decide_action(wallet_balance, dai_price, gas_price):
    prompt = f"""
    Current wallet balance: {wallet_balance} DAI
    Current DAI price: {dai_price} USD
    Current gas price: {gas_price} GWEI

    Options:
    1. Replenish the DAI balance from the backup wallet.
    2. Stake the DAI balance to earn rewards.
    3. Swap DAI for ETH.
    4. Do nothing.

    Based on the data, what action should we take? Provide reasoning and the recommended action.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Error querying OpenAI: {e}")
        return "Error in decision-making."


def monitor_and_act():
    while True:
        token_balance = contract.functions.getBalance(token_address).call() / (10 ** 18)
        gas_price = get_gas_price() / (10 ** 9)
        dai_price = get_dai_price()

        logging.info(f"Wallet balance: {token_balance} DAI, Gas price: {gas_price} GWEI, DAI price: {dai_price} USD")

        if gas_price:
            historical_gas_prices.append(gas_price)
            if len(historical_gas_prices) % 10 == 0:
                train_model()

        decision = decide_action(token_balance, dai_price, gas_price)
        logging.info(f"AI Decision: {decision}")

        if "Replenish" in decision:
            transfer_from_backup(token_address, 50)
        elif "Stake" in decision:
            logging.info("Staking DAI is not yet implemented.")
        elif "Swap" in decision:
            logging.info("Swapping DAI for ETH is not yet implemented.")
        else:
            logging.info("No action taken.")

        time.sleep(60)


if __name__ == "__main__":
    print("Starting AI wallet monitoring...")
    monitor_and_act()

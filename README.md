# Agentic Wallet - README

## Overview
The **Agentic Wallet** is a smart contract deployed on the Sepolia testnet. This wallet includes features such as:
- Token transfer execution.
- Backup wallet refilling.
- Real-time balance retrieval.


[![Watch this non Technical video as a first step](https://img.youtube.com/vi/XuIQLOs-gp8/0.jpg)](https://www.youtube.com/watch?v=XuIQLOs-gp8)



This document contains all the necessary information, including deployed addresses and instructions, to interact with the wallet.

---

## Deployed Addresses

### Contract Addresses
| Contract               | Address                                    |
|------------------------|--------------------------------------------|
| **AIEnhancedWallet**  | `0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066` |
| **TestDai.sol**        | `0xF469A33cd0B806AFDDCFA5CEA1d8Fe408ec43B9c` |

### Backup Wallet Address
- `0x79438A85548Cd4f1E6FFd0A190274060B533fd01`

---

## How to Interact with the Agentic Wallet

### 1. Prerequisites
- Connect Metamask with sEPOLIA Test net and simply load the above 2 addresses on Remix IDE. You will have access to some functions to do basic interactions. 
- Set up a Sepolia testnet account and acquire test ETH from a faucet.

### 2. ABI
Use the following ABI to interact with the **AIEnhancedWallet**:

```json
[
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
```

### 3. Steps to Interact

#### a. Set Up Environment
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

#### b. Deploy Your Own Instance (Optional)
1. Edit `hardhat.config.js` to include your private key and Sepolia RPC URL.
2. Deploy the contract:
   ```bash
   npx hardhat run scripts/deploy.js --network sepolia
   ```

#### c. Execute Functions

##### **Execute a Token Transfer**
Transfer tokens from the wallet to a recipient.

```javascript
const { ethers } = require("ethers");

async function executeTransfer() {
  const wallet = new ethers.Wallet("<PRIVATE_KEY>", ethers.getDefaultProvider("https://sepolia.infura.io/v3/<INFURA_PROJECT_ID>"));
  const contract = new ethers.Contract("0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066", ABI, wallet);

  const tokenAddress = "<TOKEN_CONTRACT_ADDRESS>";
  const recipient = "<RECIPIENT_ADDRESS>";
  const amount = ethers.utils.parseUnits("10", 18);

  const tx = await contract.executeTransfer(tokenAddress, amount, recipient);
  await tx.wait();
  console.log("Transfer executed.");
}

executeTransfer();
```

##### **Refill From Backup Wallet**
Refill the wallet from the backup wallet.

```javascript
async function refillFromBackup() {
  const contract = new ethers.Contract("0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066", ABI, wallet);

  const tokenAddress = "<TOKEN_CONTRACT_ADDRESS>";
  const amount = ethers.utils.parseUnits("5", 18);

  const tx = await contract.refillFromBackup(tokenAddress, amount);
  await tx.wait();
  console.log("Wallet refilled.");
}

refillFromBackup();
```

---

## Additional Notes
- Use the Sepolia testnet for development and testing.
- Ensure you have enough Sepolia ETH for gas fees.
- Double-check all addresses before executing transactions.

For further questions, feel free to contact [Your Email/Handle].



**TestDAI**
https://sepolia.etherscan.io/tx/0xfaa87220d3d4bbb3d59506ccd2b641e18a38a0e0492cf23d6222551b726aa25c
deployed contract address
0xF469A33cd0B806AFDDCFA5CEA1d8Fe408ec43B9c

**Backup Test wallet address:** 0x79438A85548Cd4f1E6FFd0A190274060B533fd01
configure yours e.g in Metamask or any other wallet provider


**AIEnhancedWallet contract**
https://sepolia.etherscan.io/tx/0xac173c9e73885e970a68713ffc066ea9e626a398f6b277a078ebd54112821993
and 
deployed contract address on Sepolia is 
0xd6f6df67Ba778a49BEa462b53bf8A473d7BD0066

## Wallet of the API Service Provider
![Screen Shot 2024-12-30 at 11 51 22 am](https://github.com/user-attachments/assets/0bcd6652-571d-4909-a814-fc40a51e02b0)

## Sample Backup Wallet which feeds into the Paying Wallet
![Screen Shot 2024-12-30 at 11 51 32 am](https://github.com/user-attachments/assets/d64595b3-e4c9-4983-a10e-ba2f118e8b5e)


## Videos - Phase 1- Python ML Agents doing the Test Dai Transactions
[![Watch the video](https://img.youtube.com/vi/dXe0ewu7QGs/0.jpg)](https://www.youtube.com/watch?v=dXe0ewu7QGs)

## Videos - Phase 1- Mock Server for Testing APIs
[![Watch the video](https://img.youtube.com/vi/_uZLIaKm8AM/0.jpg)](https://www.youtube.com/watch?v=_uZLIaKm8AM)

## Videos - Phase 1- Loading the Sepolia Deployed Smart Contracts in REMIX
[![Watch the video](https://img.youtube.com/vi/9Tzh0AxiAjY/0.jpg)](https://www.youtube.com/watch?v=9Tzh0AxiAjY)




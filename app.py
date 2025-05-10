import streamlit as st
from web3 import Web3
from web3.exceptions import ContractLogicError

# ------------------------------
# 🔗 Blockchain & Contract Setup
# ------------------------------

# Connect to Sepolia Testnet via Infura
INFURA_URL = "https://sepolia.infura.io/v3/fe337c3c7ea047bdbf304ead0a2217d9"  
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Smart contract address (your deployed contract on Sepolia)
CONTRACT_ADDRESS = "0x85F7e48E87A2Cb8a0ef213e98561ceeA0E6faCE8"

# Smart contract ABI 
CONTRACT_ABI = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "age",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "gender",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "condition",
				"type": "string"
			}
		],
		"name": "addPatientRecord",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "provider",
				"type": "address"
			}
		],
		"name": "authorizeProvider",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "recordId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferRecord",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "admin",
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
				"name": "",
				"type": "address"
			}
		],
		"name": "authorizedProviders",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "recordId",
				"type": "uint256"
			}
		],
		"name": "getRecord",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
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
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "records",
		"outputs": [
			{
				"internalType": "string",
				"name": "patientName",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "age",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "gender",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "condition",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalRecords",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# Load contract
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# ------------------------------
# 🧑‍⚕️ Doctor Login
# ------------------------------

st.title("🏥 Blockchain-Based Patient Record System")

with st.sidebar:
    st.header("Doctor Login")
    doctor_id = st.text_input("Doctor ID (e.g., DOC782A)")
    doctor_wallet = st.text_input("Doctor Ethereum Wallet Address")
    private_key = st.text_input("Private Key (Sepolia testnet only)", type="password")

# ------------------------------
# ➕ Add New Record Section
# ------------------------------

st.subheader("➕ Add Patient Record (Authorized Doctors Only)")

with st.form("add_form"):
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    condition = st.text_input("Medical Condition")

    submitted = st.form_submit_button("Add Record")

    if submitted:
        if not all([doctor_wallet, private_key]):
            st.error("❌ Please login as a doctor first.")
        else:
            try:
                # Build transaction
                txn = contract.functions.addPatientRecord(name, age, gender, condition).build_transaction({
                    "from": doctor_wallet,
                    "nonce": web3.eth.get_transaction_count(doctor_wallet),
                    "gas": 300000,
                    "gasPrice": web3.to_wei("20", "gwei")
                })

                # Sign and send
                signed_txn = web3.eth.account.sign_transaction(txn, private_key)
                tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                st.success("✅ Record submitted successfully!")
                st.markdown(f"🔗 [View on Sepolia Etherscan](https://sepolia.etherscan.io/tx/{tx_hash.hex()})")
            except ContractLogicError as e:
                st.error(f"❌ Smart contract error: {e}")
            except Exception as ex:
                st.error(f"❌ Transaction failed: {ex}")

# ------------------------------
# 🔍 View Record Section
# ------------------------------

st.subheader("🔍 View Patient Record")

record_id = st.number_input("Enter Record ID", min_value=0, step=1)
if st.button("View Record"):
    try:
        result = contract.functions.getRecord(record_id).call()
        st.info("📄 Record Details:")
        st.write(f"👤 Name: {result[0]}")
        st.write(f"🎂 Age: {result[1]}")
        st.write(f"⚧️ Gender: {result[2]}")
        st.write(f"🩺 Condition: {result[3]}")
        st.write(f"🔐 Owner Address: {result[4]}")
    except Exception:
        st.error("❌ Record not found or error occurred.")


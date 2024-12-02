import os
import json
import logging
from web3 import Web3
from dotenv import load_dotenv
from typing import Dict, Any

class BlockchainVerifier:
    def __init__(self):
        """
        Initialize Blockchain Verification System
        """
        load_dotenv()
        
        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Web3 Connection
        self.provider_url = os.getenv('BLOCKCHAIN_PROVIDER_URL', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Smart Contract Configuration
        self.contract_address = os.getenv('TRADE_VERIFICATION_CONTRACT')
        self.contract_abi = self.load_contract_abi()
    
    def load_contract_abi(self) -> list:
        """
        Load contract ABI from file
        
        Returns:
            Contract ABI as list
        """
        try:
            with open('blockchain/smart_contracts/TradeVerification_abi.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"ABI loading failed: {e}")
            return []
    
    def record_trade(self, trade_details: Dict[str, Any]) -> bool:
        """
        Record trade details on blockchain
        
        Args:
            trade_details (dict): Trade information to record
        
        Returns:
            bool: Success status
        """
        try:
            # Initialize contract
            contract = self.w3.eth.contract(
                address=self.contract_address, 
                abi=self.contract_abi
            )
            
            # Prepare transaction
            transaction = contract.functions.recordTrade(
                trade_details['symbol'],
                trade_details['amount'],
                trade_details['price'],
                trade_details['timestamp']
            ).build_transaction({
                'from': self.w3.eth.default_account,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=os.getenv('BLOCKCHAIN_PRIVATE_KEY')
            )
            
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            self.logger.info(f"Trade recorded on blockchain: {tx_hash.hex()}")
            return tx_receipt['status'] == 1
        
        except Exception as e:
            self.logger.error(f"Blockchain recording failed: {e}")
            return False
    
    def verify_trade(self, trade_hash: str) -> Dict[str, Any]:
        """
        Verify trade details from blockchain
        
        Args:
            trade_hash (str): Transaction hash to verify
        
        Returns:
            Trade verification details
        """
        try:
            contract = self.w3.eth.contract(
                address=self.contract_address, 
                abi=self.contract_abi
            )
            
            trade_details = contract.functions.getTrade(trade_hash).call()
            return {
                'symbol': trade_details[0],
                'amount': trade_details[1],
                'price': trade_details[2],
                'timestamp': trade_details[3]
            }
        except Exception as e:
            self.logger.error(f"Trade verification failed: {e}")
            return {}

# Usage example
def main():
    verifier = BlockchainVerifier()
    trade_details = {
        'symbol': 'BTC/USDT',
        'amount': 0.1,
        'price': 50000,
        'timestamp': int(time.time())
    }
    verifier.record_trade(trade_details)

if __name__ == "__main__":
    main()
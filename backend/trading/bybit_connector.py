import os
import ccxt
import logging
from typing import Dict, Any
from dotenv import load_dotenv

class BybitTrader:
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Initialize Bybit trading connector
        
        Args:
            api_key (str): Bybit API Key
            api_secret (str): Bybit API Secret
        """
        load_dotenv()
        
        # Logging configuration
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # API Credentials
        self.api_key = api_key or os.getenv('BYBIT_API_KEY')
        self.api_secret = api_secret or os.getenv('BYBIT_API_SECRET')
        
        # Initialize Bybit exchange
        self.exchange = ccxt.bybit({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'  # Futures trading
            }
        })
    
    def get_account_balance(self) -> Dict[str, float]:
        """
        Retrieve account balance
        
        Returns:
            Dict containing balance information
        """
        try:
            balance = self.exchange.fetch_balance()
            return {
                'total': balance['total']['USDT'],
                'free': balance['free']['USDT'],
                'used': balance['used']['USDT']
            }
        except Exception as e:
            self.logger.error(f"Balance retrieval failed: {e}")
            return {}
    
    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """
        Create a market order
        
        Args:
            symbol (str): Trading pair (e.g., 'BTC/USDT')
            side (str): 'buy' or 'sell'
            amount (float): Order quantity
        
        Returns:
            Dict containing order details
        """
        try:
            order = self.exchange.create_market_order(symbol, side, amount)
            self.logger.info(f"Order created: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Order creation failed: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price
        
        Args:
            symbol (str): Trading pair
        
        Returns:
            Current market price
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            self.logger.error(f"Price retrieval failed: {e}")
            return 0.0

# Usage example
def main():
    trader = BybitTrader()
    balance = trader.get_account_balance()
    print(f"Account Balance: {balance}")
    
    btc_price = trader.get_current_price('BTC/USDT')
    print(f"Current BTC Price: ${btc_price}")

if __name__ == "__main__":
    main()
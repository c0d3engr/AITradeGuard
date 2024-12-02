# backend/config/app_config.py
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any

class AppConfig:
    """
    Centralized configuration management for AITradeGuard
    """
    _instance = None

    def __new__(cls):
        """
        Singleton pattern to ensure only one configuration instance
        """
        if not cls._instance:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize application configuration
        """
        # Prevent re-initialization
        if not hasattr(self, 'initialized'):
            # Load environment variables
            load_dotenv()
            
            # Configure logging
            self._setup_logging()
            
            # Load configuration
            self.config = self._load_config()
            
            # Mark as initialized
            self.initialized = True
    
    def _setup_logging(self):
        """
        Configure application logging
        """
        log_level = logging.INFO if self.get_config('ENVIRONMENT') != 'production' else logging.ERROR
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/aitradeguard.log',
            filemode='a'
        )
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console_handler)
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables
        
        Returns:
            Dictionary of configuration settings
        """
        return {
            # Application Settings
            'ENVIRONMENT': os.getenv('APP_ENV', 'development'),
            'DEBUG_MODE': os.getenv('DEBUG', 'False').lower() == 'true',
            
            # Trading Configuration
            'TRADING_SYMBOLS': os.getenv('TRADING_SYMBOLS', 'BTC/USDT,ETH/USDT').split(','),
            'MAX_TRADE_AMOUNT': float(os.getenv('MAX_TRADE_AMOUNT', 100)),
            
            # API Credentials
            'BYBIT_API_KEY': os.getenv('BYBIT_API_KEY'),
            'BYBIT_API_SECRET': os.getenv('BYBIT_API_SECRET'),
            
            # Blockchain Configuration
            'BLOCKCHAIN_PROVIDER': os.getenv('BLOCKCHAIN_PROVIDER_URL'),
            'TRADE_CONTRACT_ADDRESS': os.getenv('TRADE_VERIFICATION_CONTRACT'),
            
            # AI Model Configuration
            'MODEL_TRAINING_FREQUENCY': int(os.getenv('MODEL_TRAIN_FREQ', 7)),
            'SENTIMENT_SYMBOLS': os.getenv('SENTIMENT_SYMBOLS', 'BTC,ETH').split(','),
            
            # Security Settings
            'MAX_CONSECUTIVE_TRADES': int(os.getenv('MAX_CONSECUTIVE_TRADES', 5)),
            'RISK_THRESHOLD': float(os.getenv('RISK_THRESHOLD', 0.5))
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a specific configuration value
        
        Args:
            key (str): Configuration key
            default (Any, optional): Default value if key not found
        
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def is_production(self) -> bool:
        """
        Check if application is running in production environment
        
        Returns:
            Boolean indicating production status
        """
        return self.get_config('ENVIRONMENT') == 'production'
    
    def validate_config(self) -> bool:
        """
        Validate critical configuration settings
        
        Returns:
            Boolean indicating configuration validity
        """
        critical_keys = [
            'BYBIT_API_KEY', 
            'BYBIT_API_SECRET', 
            'BLOCKCHAIN_PROVIDER'
        ]
        
        for key in critical_keys:
            if not self.get_config(key):
                logging.error(f"Missing critical configuration: {key}")
                return False
        
        return True

# Create global configuration instance
config = AppConfig()

# Example usage
def main():
    # Validate configuration
    if config.validate_config():
        print("Configuration is valid!")
        
        # Access configuration values
        trading_symbols = config.get_config('TRADING_SYMBOLS')
        print(f"Trading Symbols: {trading_symbols}")
    else:
        print("Invalid configuration. Please check your .env file.")

if __name__ == "__main__":
    main()
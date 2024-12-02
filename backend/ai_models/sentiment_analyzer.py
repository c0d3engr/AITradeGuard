import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import logging
from typing import Dict, Any

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize Sentiment Analysis Model
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Model configuration
        self.model = self.build_sentiment_model()
        self.scaler = StandardScaler()
    
    def fetch_market_data(self, symbol: str, period: str = '1mo') -> pd.DataFrame:
        """
        Fetch market data for sentiment analysis
        
        Args:
            symbol (str): Stock/Crypto symbol
            period (str): Data retrieval period
        
        Returns:
            Market data DataFrame
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            # Feature engineering
            data['price_change'] = data['Close'].pct_change()
            data['volume_change'] = data['Volume'].pct_change()
            
            return data
        except Exception as e:
            self.logger.error(f"Data fetching failed: {e}")
            return pd.DataFrame()
    
    def build_sentiment_model(self) -> tf.keras.Model:
        """
        Build neural network for sentiment prediction
        
        Returns:
            Compiled TensorFlow model
        """
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_model(self, symbol: str = 'BTC-USD'):
        """
        Train sentiment prediction model
        
        Args:
            symbol (str): Symbol to analyze
        """
        data = self.fetch_market_data(symbol)
        
        # Prepare features and labels
        features = data[['price_change', 'volume_change', 'Open', 'High', 'Low']].values
        labels = (data['Close'] > data['Open']).astype(int).values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_scaled, labels, test_size=0.2
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_split=0.2,
            epochs=50,
            batch_size=32
        )
        
        # Evaluate model
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test)
        self.logger.info(f"Model Accuracy: {test_accuracy}")
    
    def analyze_sentiment(self, symbol: str) -> float:
        """
        Analyze market sentiment
        
        Args:
            symbol (str): Trading symbol
        
        Returns:
            Sentiment score (0-1)
        """
        data = self.fetch_market_data(symbol)
        
        if data.empty:
            return 0.5
        
        features = data[['price_change', 'volume_change', 'Open', 'High', 'Low']].values[-1:]
        features_scaled = self.scaler.transform(features)
        
        sentiment_score = self.model.predict(features_scaled)[0][0]
        return float(sentiment_score)

# Usage example
def main():
    analyzer = SentimentAnalyzer()
    analyzer.train_model()
    sentiment = analyzer.analyze_sentiment('BTC-USD')
    print(f"Sentiment Score: {sentiment}")

if __name__ == "__main__":
    main()
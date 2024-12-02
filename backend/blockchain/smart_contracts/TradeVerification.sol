// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TradeVerification {
    struct Trade {
        string symbol;
        uint256 amount;
        uint256 price;
        uint256 timestamp;
        address trader;
    }
    
    mapping(bytes32 => Trade) public trades;
    mapping(address => Trade[]) public traderTrades;
    
    event TradeRecorded(
        bytes32 indexed tradeHash, 
        string symbol, 
        uint256 amount, 
        uint256 price
    );
    
    function recordTrade(
        string memory _symbol, 
        uint256 _amount, 
        uint256 _price,
        uint256 _timestamp
    ) public returns (bytes32) {
        // Validate trade parameters
        require(_amount > 0, "Invalid trade amount");
        require(_price > 0, "Invalid trade price");
        
        // Generate unique trade hash
        bytes32 tradeHash = keccak256(abi.encodePacked(
            msg.sender, 
            _symbol, 
            _amount, 
            _price, 
            _timestamp
        ));
        
        // Record trade
        trades[tradeHash] = Trade({
            symbol: _symbol,
            amount: _amount,
            price: _price,
            timestamp: _timestamp,
            trader: msg.sender
        });
        
        // Record trade for specific trader
        traderTrades[msg.sender].push(trades[tradeHash]);
        
        // Emit event
        emit TradeRecorded(tradeHash, _symbol, _amount, _price);
        
        return tradeHash;
    }
    
    function getTrade(bytes32 _tradeHash) public view returns (
        string memory symbol, 
        uint256 amount, 
        uint256 price, 
        uint256 timestamp
    ) {
        Trade memory trade = trades[_tradeHash];
        return (
            trade.symbol, 
            trade.amount, 
            trade.price, 
            trade.timestamp
        );
    }
    
    function getTraderTrades(address _trader) public view returns (Trade[] memory) {
        return traderTrades[_trader];
    }
}
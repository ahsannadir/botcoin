import json
from src.utils.helpers import hash_data, current_timestamp

class Transaction:
    def __init__(self, sender, recipient, amount, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or current_timestamp()
        self.tx_id = self._calculate_hash()
    
    def _calculate_hash(self):
        tx_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        return hash_data(tx_data)
    
    def is_valid(self, check_balance=False, blockchain=None):
        if self.amount <= 0:
            return False
        if self.sender == self.recipient:
            return False
        if not self.sender or not self.recipient:
            return False
        
        if check_balance and blockchain:
            balance = blockchain.get_balance(self.sender)
            if balance < self.amount:
                return False
        
        return True
    
    def to_dict(self):
        return {
            'tx_id': self.tx_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return f"TX({self.sender[:8]}→{self.recipient[:8]}: {self.amount})"
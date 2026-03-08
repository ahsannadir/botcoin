from src.utils.helpers import hash_data, current_timestamp
from src.utils.config import Config

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, miner=None):
        self.index = index
        self.timestamp = timestamp or current_timestamp()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.miner = miner
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }
        return hash_data(block_data)
    
    def mine_block(self, difficulty):
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash
    
    def is_valid(self):
        if self.hash != self.calculate_hash():
            return False
        if not self.hash.startswith('0' * Config.DIFFICULTY):
            return False
        for tx in self.transactions:
            if not tx.is_valid():
                return False
        return True
    
    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'miner': self.miner,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def __repr__(self):
        return f"Block#{self.index}({self.hash[:8]}...)"
from src.core.block import Block
from src.core.transaction import Transaction
from src.utils.config import Config

class Blockchain:
    def __init__(self):
        self.chain = [self._create_genesis_block()]
        self.pending_transactions = []
    
    def _create_genesis_block(self):
        genesis_tx = Transaction("GENESIS", "GENESIS", 0)
        return Block(0, [genesis_tx], "0", miner="GENESIS")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, block):
        if not self.is_valid_new_block(block):
            return False
        self.chain.append(block)
        tx_ids = {tx.tx_id for tx in block.transactions}
        self.pending_transactions = [
            tx for tx in self.pending_transactions 
            if tx.tx_id not in tx_ids
        ]
        return True
    
    def is_valid_new_block(self, block):
        latest_block = self.get_latest_block()
        
        if block.index != latest_block.index + 1:
            return False
        if block.previous_hash != latest_block.hash:
            return False
        if not block.is_valid():
            return False
        return True
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if not current_block.is_valid():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
    
    def add_transaction(self, transaction):
        if transaction.is_valid(check_balance=True, blockchain=self):
            self.pending_transactions.append(transaction)
            return True
        return False
    
    def get_balance(self, address):
        balance = Config.INITIAL_BALANCE
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        return balance
    
    def get_transaction_history(self, address):
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    history.append({
                        'block': block.index,
                        'tx': tx,
                        'type': 'sent' if tx.sender == address else 'received'
                    })
        return history
    
    def replace_chain(self, new_chain):
        if len(new_chain) <= len(self.chain):
            return False
        
        for i in range(1, len(new_chain)):
            if not new_chain[i].is_valid():
                return False
            if new_chain[i].previous_hash != new_chain[i-1].hash:
                return False
        
        self.chain = new_chain
        return True
    
    def __len__(self):
        return len(self.chain)
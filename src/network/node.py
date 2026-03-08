import random
import time
from threading import Thread, Lock
from src.core.blockchain import Blockchain
from src.core.transaction import Transaction
from src.core.block import Block
from src.network.message import Message, MessageType
from src.utils.config import Config

class Node:
    def __init__(self, node_id, network, is_miner=False, is_ai=False):
        self.node_id = node_id
        self.network = network
        self.blockchain = Blockchain()
        self.peers = set()
        self.is_miner = is_miner
        self.is_ai = is_ai
        self.mining = False
        self.mining_active = False
        self.lock = Lock()
        
        network.register_node(self)
    
    def connect_to_peer(self, peer_node):
        self.peers.add(peer_node.node_id)
        peer_node.peers.add(self.node_id)
    
    def create_transaction(self, recipient, amount):
        balance = self.blockchain.get_balance(self.node_id)
        if balance < amount:
            return None, "Insufficient balance"
        
        tx = Transaction(self.node_id, recipient, amount)
        
        if not self.blockchain.add_transaction(tx):
            return None, "Invalid transaction"
        
        message = Message(MessageType.NEW_TRANSACTION, tx, self.node_id)
        for peer_id in self.peers:
            self.network.send_message(self.node_id, peer_id, message)
        
        return tx, "Transaction created successfully"
    
    def receive_message(self, message):
        if message.type == MessageType.NEW_TRANSACTION:
            self._handle_new_transaction(message)
        elif message.type == MessageType.NEW_BLOCK:
            self._handle_new_block(message)
        elif message.type == MessageType.REQUEST_CHAIN:
            self._handle_chain_request(message)
        elif message.type == MessageType.CHAIN_RESPONSE:
            self._handle_chain_response(message)
    
    def _handle_new_transaction(self, message):
        tx = message.data
        with self.lock:
            tx_ids = {t.tx_id for t in self.blockchain.pending_transactions}
            if tx.tx_id not in tx_ids and tx.is_valid(check_balance=True, blockchain=self.blockchain):
                self.blockchain.add_transaction(tx)
                
                for peer_id in self.peers:
                    if peer_id != message.sender_id:
                        self.network.send_message(self.node_id, peer_id, message)
    
    def _handle_new_block(self, message):
        block = message.data
        with self.lock:
            if self.blockchain.add_block(block):
                for peer_id in self.peers:
                    if peer_id != message.sender_id:
                        self.network.send_message(self.node_id, peer_id, message)
                
                if self.is_miner and self.mining:
                    self.mining = False
    
    def _handle_chain_request(self, message):
        response = Message(
            MessageType.CHAIN_RESPONSE,
            self.blockchain.chain,
            self.node_id
        )
        self.network.send_message(self.node_id, message.sender_id, response)
    
    def _handle_chain_response(self, message):
        new_chain = message.data
        with self.lock:
            self.blockchain.replace_chain(new_chain)
    
    def mine_block(self):
        if not self.is_miner:
            return None
        
        with self.lock:
            if not self.blockchain.pending_transactions:
                return None
            
            transactions = self.blockchain.pending_transactions[:Config.MAX_BLOCK_SIZE]
            
            reward_tx = Transaction("COINBASE", self.node_id, Config.BLOCK_REWARD)
            transactions.insert(0, reward_tx)
            
            previous_block = self.blockchain.get_latest_block()
            new_block = Block(
                index=previous_block.index + 1,
                transactions=transactions,
                previous_hash=previous_block.hash,
                miner=self.node_id
            )
        
        self.mining = True
        new_block.mine_block(Config.DIFFICULTY)
        
        with self.lock:
            if not self.mining:
                return None
            
            if self.blockchain.add_block(new_block):
                message = Message(MessageType.NEW_BLOCK, new_block, self.node_id)
                for peer_id in self.peers:
                    self.network.send_message(self.node_id, peer_id, message)
                
                self.mining = False
                return new_block
        
        return None
    
    def start_mining(self):
        self.mining_active = True
        
        def mine_loop():
            while self.mining_active:
                if self.is_miner:
                    self.mine_block()
                time.sleep(1)
        
        Thread(target=mine_loop, daemon=True).start()
    
    def stop_mining(self):
        self.mining_active = False
        self.mining = False
    
    def get_balance(self):
        return self.blockchain.get_balance(self.node_id)
    
    def ai_behavior(self):
        if not self.is_ai:
            return
        
        def ai_loop():
            while True:
                time.sleep(random.uniform(*Config.AI_TRANSACTION_INTERVAL))
                
                with self.lock:
                    available_nodes = [
                        n for n in self.network.nodes.values() 
                        if n.node_id != self.node_id
                    ]
                
                if available_nodes and self.get_balance() > 10:
                    recipient = random.choice(available_nodes)
                    amount = random.uniform(1, min(50, self.get_balance() * 0.1))
                    self.create_transaction(recipient.node_id, amount)
        
        Thread(target=ai_loop, daemon=True).start()
    
    def __repr__(self):
        return f"Node({self.node_id}, miner={self.is_miner}, ai={self.is_ai})"
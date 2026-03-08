import time
import random
from src.network.network import Network
from src.network.node import Node
from src.network.topology import create_random_topology

class Simulator:
    def __init__(self, num_nodes=10, num_miners=3):
        self.network = Network()
        self.nodes = []
        self.miners = []
        
        for i in range(num_nodes):
            is_miner = i < num_miners
            node = Node(f"node_{i}", self.network, is_miner=is_miner)
            self.nodes.append(node)
            if is_miner:
                self.miners.append(node)
        
        create_random_topology(self.nodes, avg_connections=4)
        
        print(f"Created {num_nodes} nodes ({num_miners} miners)")
        print(f"Network topology established")
    
    def run(self, duration=60):
        print(f"\nStarting simulation for {duration} seconds...")
        
        self.network.start()
        
        for miner in self.miners:
            miner.start_mining()
        
        start_time = time.time()
        
        tx_count = 0
        while time.time() - start_time < duration:
            time.sleep(random.uniform(2, 5))
            
            sender = random.choice(self.nodes)
            recipient = random.choice([n for n in self.nodes if n != sender])
            amount = random.uniform(1, 50)
            
            tx = sender.create_transaction(recipient.node_id, amount)
            tx_count += 1
            print(f"Transaction {tx_count}: {sender.node_id} -> {recipient.node_id}: {amount:.2f}")
        
        self.network.stop()
        
        print(f"\nSimulation completed!")
        self.show_results()
    
    def show_results(self):
        """Display simulation results"""
        print("\n" + "="*60)
        print("SIMULATION RESULTS")
        print("="*60)
        
        longest_chain = max(len(node.blockchain) for node in self.nodes)
        print(f"\nBlockchain Length: {longest_chain} blocks")
        
        chain_lengths = [len(node.blockchain) for node in self.nodes]
        consensus = len(set(chain_lengths)) == 1
        print(f"Network Consensus: {'✓ Achieved' if consensus else '✗ Not achieved'}")
        
        print("\nNode Balances:")
        for node in self.nodes:
            balance = node.get_balance()
            role = "MINER" if node.is_miner else "NODE"
            print(f"  {node.node_id} ({role}): {balance:.2f}")
        
        sample_node = self.nodes[0]
        total_transactions = sum(
            len(block.transactions) 
            for block in sample_node.blockchain.chain
        )
        print(f"\nTotal Transactions: {total_transactions}")
        print(f"Pending Transactions: {len(sample_node.blockchain.pending_transactions)}")

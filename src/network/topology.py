import random

def create_random_topology(nodes, avg_connections=4):
    for node in nodes:
        num_connections = random.randint(
            max(2, avg_connections - 2),
            avg_connections + 2
        )
        
        available_peers = [
            n for n in nodes 
            if n != node and n.node_id not in node.peers
        ]
        peers_to_connect = random.sample(
            available_peers,
            min(num_connections, len(available_peers))
        )
        
        for peer in peers_to_connect:
            node.connect_to_peer(peer)
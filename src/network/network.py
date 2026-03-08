import random
import time
from threading import Thread, Lock
from queue import Queue
from src.utils.config import Config

class Network:
    def __init__(self):
        self.nodes = {}
        self.message_queue = Queue()
        self.lock = Lock()
        self.running = False
        self.message_log = []
    
    def register_node(self, node):
        with self.lock:
            self.nodes[node.node_id] = node
    
    def unregister_node(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
    
    def send_message(self, sender_id, recipient_id, message):
        if random.random() < Config.PACKET_LOSS_RATE:
            return
        
        latency = random.uniform(Config.MIN_LATENCY, Config.MAX_LATENCY)
        self.message_queue.put((time.time() + latency, recipient_id, message))
        
        self.message_log.append({
            'time': time.time(),
            'from': sender_id,
            'to': recipient_id,
            'type': message.type.value
        })
    
    def broadcast(self, sender_id, message, exclude=None):
        exclude = exclude or set()
        exclude.add(sender_id)
        
        with self.lock:
            for node_id in self.nodes:
                if node_id not in exclude:
                    self.send_message(sender_id, node_id, message)
    
    def process_messages(self):
        while self.running:
            if not self.message_queue.empty():
                delivery_time, recipient_id, message = self.message_queue.get()
                
                if time.time() >= delivery_time:
                    with self.lock:
                        if recipient_id in self.nodes:
                            self.nodes[recipient_id].receive_message(message)
                else:
                    self.message_queue.put((delivery_time, recipient_id, message))
            
            time.sleep(0.01)
    
    def start(self):
        self.running = True
        Thread(target=self.process_messages, daemon=True).start()
    
    def stop(self):
        self.running = False
    
    def get_recent_messages(self, limit=10):
        return self.message_log[-limit:]
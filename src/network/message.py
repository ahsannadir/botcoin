from enum import Enum

class MessageType(Enum):
    NEW_TRANSACTION = "NEW_TRANSACTION"
    NEW_BLOCK = "NEW_BLOCK"
    REQUEST_CHAIN = "REQUEST_CHAIN"
    CHAIN_RESPONSE = "CHAIN_RESPONSE"
    PEER_DISCOVERY = "PEER_DISCOVERY"

class Message:
    def __init__(self, msg_type, data, sender_id):
        self.type = msg_type
        self.data = data
        self.sender_id = sender_id
    
    def __repr__(self):
        return f"Message({self.type.value}, from={self.sender_id})"

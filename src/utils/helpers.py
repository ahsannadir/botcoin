import hashlib
import json
import time

def hash_data(data):
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()

def current_timestamp():
    return int(time.time())

def verify_proof_of_work(block_hash, difficulty):
    return block_hash.startswith('0' * difficulty)
import os
import random
import hashlib
import json
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

class WalletAuth:
    def __init__(self, wordlist_path="wordlist.txt", wallet_db_path="data/wallets.txt"):
        self.wordlist_path = wordlist_path
        self.wallet_db_path = wallet_db_path
        self.keys_path = "data/rsa_keys"
        self.wordlist = self._load_wordlist()
        self._ensure_db_exists()
        self._ensure_keys_exist()
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()
    
    def _load_wordlist(self):
        if not os.path.exists(self.wordlist_path):
            raise FileNotFoundError(f"Wordlist not found at {self.wordlist_path}")
        
        with open(self.wordlist_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        
        if len(words) < 12:
            raise ValueError("Wordlist must contain at least 12 words")
        
        return words
    
    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.wallet_db_path), exist_ok=True)
        if not os.path.exists(self.wallet_db_path):
            with open(self.wallet_db_path, 'w') as f:
                f.write("")

    def _ensure_keys_exist(self):
        os.makedirs(self.keys_path, exist_ok=True)
        private_key_path = os.path.join(self.keys_path, "private_key.pem")
        public_key_path = os.path.join(self.keys_path, "public_key.pem")

        if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
            self._generate_rsa_keys()

    def _generate_rsa_keys(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        private_key_path = os.path.join(self.keys_path, "private_key.pem")
        public_key_path = os.path.join(self.keys_path, "public_key.pem")

        with open(private_key_path, 'wb') as f:
            f.write(private_pem)
        with open(public_key_path, 'wb') as f:
            f.write(public_pem)

    def _load_private_key(self):
        private_key_path = os.path.join(self.keys_path, "private_key.pem")
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        return private_key

    def _load_public_key(self):
        public_key_path = os.path.join(self.keys_path, "public_key.pem")
        with open(public_key_path, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        return public_key

    def _encrypt_phrase(self, phrase):
        phrase_str = " ".join(phrase)
        phrase_bytes = phrase_str.encode('utf-8')
        encrypted = self.public_key.encrypt(
            phrase_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted.hex()

    def _decrypt_phrase(self, encrypted_hex):
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        decrypted = self.private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        phrase_str = decrypted.decode('utf-8')
        return phrase_str.split()
    
    def generate_recovery_phrase(self):
        return random.sample(self.wordlist, 12)
    
    def phrase_to_wallet_id(self, phrase):
        phrase_str = " ".join(phrase)
        return hashlib.sha256(phrase_str.encode()).hexdigest()[:16]
    
    def create_wallet(self, phrase):
        wallet_id = self.phrase_to_wallet_id(phrase)
        
        if self.wallet_exists(wallet_id):
            return None, "Wallet with this phrase already exists"
        
        encrypted_phrase = self._encrypt_phrase(phrase)
        
        wallet_data = {
            'wallet_id': wallet_id,
            'encrypted_phrase': encrypted_phrase,
            'created_at': int(time.time())
        }
        
        with open(self.wallet_db_path, 'a') as f:
            f.write(json.dumps(wallet_data) + '\n')
        
        return wallet_id, "Wallet created successfully"
    
    def wallet_exists(self, wallet_id):
        if not os.path.exists(self.wallet_db_path):
            return False
        
        with open(self.wallet_db_path, 'r') as f:
            for line in f:
                if line.strip():
                    wallet_data = json.loads(line)
                    if wallet_data['wallet_id'] == wallet_id:
                        return True
        return False
    
    def verify_phrase(self, phrase):
        wallet_id = self.phrase_to_wallet_id(phrase)
        
        if not os.path.exists(self.wallet_db_path):
            return None, "No wallets found"
        
        with open(self.wallet_db_path, 'r') as f:
            for line in f:
                if line.strip():
                    wallet_data = json.loads(line)
                    if wallet_data['wallet_id'] == wallet_id:
                        if 'encrypted_phrase' in wallet_data:
                            decrypted_phrase = self._decrypt_phrase(wallet_data['encrypted_phrase'])
                            if decrypted_phrase == phrase:
                                return wallet_id, "Login successful"
                        elif 'phrase' in wallet_data:
                            if wallet_data['phrase'] == phrase:
                                return wallet_id, "Login successful"
        
        return None, "Invalid recovery phrase"
    
    def get_all_wallets(self):
        wallets = []
        if os.path.exists(self.wallet_db_path):
            with open(self.wallet_db_path, 'r') as f:
                for line in f:
                    if line.strip():
                        wallet_data = json.loads(line)
                        if 'encrypted_phrase' in wallet_data:
                            wallet_data['phrase'] = self._decrypt_phrase(wallet_data['encrypted_phrase'])
                            del wallet_data['encrypted_phrase']
                        wallets.append(wallet_data)
        return wallets
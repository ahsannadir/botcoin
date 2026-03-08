class Config:
    BLOCK_TIME = 10  # Target time between blocks in seconds
    DIFFICULTY = 4  # Number of leading zeros required in block hash
    BLOCK_REWARD = 50  # Mining reward
    MAX_BLOCK_SIZE = 100  # Maximum transactions per block
    
    MIN_LATENCY = 0.1  # Minimum network delay in seconds
    MAX_LATENCY = 2.0  # Maximum network delay in seconds
    PACKET_LOSS_RATE = 0.01  # 1% packet loss
    
    CONFIRMATIONS_REQUIRED = 6  # Blocks needed for transaction confirmation
    
    INITIAL_BALANCE = 1000  # Starting balance for nodes
    AI_TRANSACTION_INTERVAL = (5, 15)  # AI nodes create transactions every 5-15 seconds
# Botcoin

A simulated blockchain cryptocurrency implementation with P2P networking, wallet authentication, and mining capabilities.

## Features

- **Blockchain Core**: Implements proof-of-work consensus with transaction validation
- **P2P Network**: Decentralized network simulation with configurable topology
- **Wallet System**: Secure wallet creation and authentication using 12-word recovery phrases
- **Mining**: Proof-of-work mining with adjustable difficulty
- **Web Interface**: Streamlit-based wallet interface for managing transactions
- **Simulation**: Command-line simulation tool for testing network behavior

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ahsannadir/botcoin.git
   cd botcoin
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `wordlist.txt` is in the root directory (for wallet recovery phrases)

## Usage

### Web Wallet Interface

Run the Streamlit web application:

```bash
streamlit run app.py
```

This launches a web interface where you can:
- Create new wallets with 12-word recovery phrases
- Login to existing wallets
- View transaction history
- Send transactions

### Network Simulation

Run the command-line simulation:

```bash
python main.py
```

This simulates a P2P network with 10 nodes (3 miners) for 60 seconds, demonstrating transaction creation and mining.

## Project Structure

```
botcoin/
├── app.py                 # Streamlit web application
├── main.py                # Simulation entry point
├── requirements.txt       # Python dependencies
├── wordlist.txt          # BIP39 wordlist for wallet recovery
├── data/                 # Data storage
│   ├── rsa_keys/         # RSA key pairs
│   └── wallets.txt       # Wallet database
├── simulation/           # Simulation components
│   └── simulator.py      # Network simulator
└── src/                  # Core implementation
    ├── core/             # Blockchain core
    │   ├── block.py
    │   ├── blockchain.py
    │   └── transaction.py
    ├── network/          # P2P networking
    │   ├── message.py
    │   ├── network.py
    │   ├── node.py
    │   └── topology.py
    ├── utils/            # Utilities
    │   ├── config.py
    │   └── helpers.py
    └── wallet/           # Wallet management
        └── auth.py
```

## Configuration

Adjust simulation parameters in `src/utils/config.py`:
- Network latency and packet loss
- Mining difficulty
- Block size limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Use at your own risk.

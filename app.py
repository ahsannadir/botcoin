import streamlit as st
import time
import pandas as pd
from src.network.network import Network
from src.network.node import Node
from src.network.topology import create_random_topology
from src.utils.config import Config
from src.wallet.auth import WalletAuth

st.set_page_config(
    page_title="Botcoin",
    page_icon="₿",
    layout="wide"
)

if 'wallet_auth' not in st.session_state:
    try:
        st.session_state.wallet_auth = WalletAuth()
    except FileNotFoundError:
        st.error("❌ Wordlist file not found! Please add 'wordlist.txt' in the root directory.")
        st.stop()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.wallet_id = None
    st.session_state.recovery_phrase = None

if not st.session_state.logged_in:
    st.title("₿ Botcoin Wallet")
    st.markdown("### Secure Your Digital Assets")
    
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Create New Wallet"])
    
    with tab1:
        st.subheader("Login to Your Wallet")
        st.write("Enter your 12-word recovery phrase to access your wallet.")
        
        cols = st.columns(3)
        phrase_inputs = []
        
        for i in range(12):
            col_idx = i % 3
            with cols[col_idx]:
                word = st.text_input(
                    f"Word {i+1}", 
                    key=f"login_word_{i}",
                    placeholder=f"word {i+1}"
                )
                phrase_inputs.append(word.strip().lower())
        
        if st.button("🔓 Unlock Wallet", type="primary", use_container_width=True):
            if all(phrase_inputs):
                wallet_id, message = st.session_state.wallet_auth.verify_phrase(phrase_inputs)
                if wallet_id:
                    st.session_state.logged_in = True
                    st.session_state.wallet_id = wallet_id
                    st.session_state.recovery_phrase = phrase_inputs
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Please enter all 12 words")
    
    with tab2:
        st.subheader("Create New Wallet")
        st.write("Generate a new wallet with a secure 12-word recovery phrase.")
        
        if st.button("🎲 Generate Recovery Phrase", use_container_width=True):
            phrase = st.session_state.wallet_auth.generate_recovery_phrase()
            st.session_state.new_phrase = phrase
        
        if 'new_phrase' in st.session_state:
            st.success("✅ Your Recovery Phrase (Write it down and keep it safe!):")
            
            cols = st.columns(3)
            for i, word in enumerate(st.session_state.new_phrase):
                col_idx = i % 3
                with cols[col_idx]:
                    st.code(f"{i+1}. {word}", language=None)
            
            st.error("⚠️ WARNING: Save these words in order! You'll need them to access your wallet.")
            
            confirm1 = st.checkbox("✅ I have written down my recovery phrase")
            confirm2 = st.checkbox("✅ I understand I cannot recover my wallet without these words")
            
            if confirm1 and confirm2:
                if st.button("Create Wallet", type="primary", use_container_width=True):
                    wallet_id, message = st.session_state.wallet_auth.create_wallet(
                        st.session_state.new_phrase
                    )
                    if wallet_id:
                        st.session_state.logged_in = True
                        st.session_state.wallet_id = wallet_id
                        st.session_state.recovery_phrase = st.session_state.new_phrase
                        st.success(f"✅ {message}")
                        del st.session_state.new_phrase
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    st.stop()

if 'network' not in st.session_state:
    st.session_state.network = Network()
    st.session_state.network.start()

if 'main_node' not in st.session_state:
    st.session_state.main_node = Node(
        st.session_state.wallet_id,
        st.session_state.network,
        is_miner=True,
        is_ai=False
    )

if 'ai_nodes' not in st.session_state:
    ai_nodes = []
    for i in range(9):
        is_miner = i < 2
        node = Node(
            f"AI_Node_{i+1}",
            st.session_state.network,
            is_miner=is_miner,
            is_ai=True
        )
        ai_nodes.append(node)
    
    st.session_state.ai_nodes = ai_nodes
    
    all_nodes = [st.session_state.main_node] + ai_nodes
    create_random_topology(all_nodes, avg_connections=4)
    
    for node in ai_nodes:
        node.ai_behavior()
        if node.is_miner:
            node.start_mining()

if 'mining_active' not in st.session_state:
    st.session_state.mining_active = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

st.title("₿ Botcoin")
st.markdown("---")

with st.sidebar:
    st.header("🧑 Your Wallet")
    st.subheader(f"ID: {st.session_state.wallet_id[:8]}...")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.wallet_id = None
        st.session_state.recovery_phrase = None
        if 'main_node' in st.session_state:
            del st.session_state.main_node
        if 'ai_nodes' in st.session_state:
            del st.session_state.ai_nodes
        st.rerun()
    
    st.markdown("---")
    
    balance = st.session_state.main_node.get_balance()
    st.metric("Balance", f"₿{balance:.2f}")
    
    chain_length = len(st.session_state.main_node.blockchain)
    st.metric("Blockchain Length", f"{chain_length} blocks")
    
    pending = len(st.session_state.main_node.blockchain.pending_transactions)
    st.metric("Pending Transactions", pending)
    
    st.markdown("---")
    
    st.subheader("⛏️ Mining")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Mining", disabled=st.session_state.mining_active):
            st.session_state.main_node.start_mining()
            st.session_state.mining_active = True
            st.success("Mining started!")
    
    with col2:
        if st.button("Stop Mining", disabled=not st.session_state.mining_active):
            st.session_state.main_node.stop_mining()
            st.session_state.mining_active = False
            st.info("Mining stopped!")
    
    if st.button("Mine One Block"):
        with st.spinner("Mining block..."):
            block = st.session_state.main_node.mine_block()
            if block:
                st.success(f"Block #{block.index} mined!")
            else:
                st.warning("No transactions to mine")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💸 Send Transaction", 
    "📊 Network Status", 
    "⛓️ Blockchain Explorer",
    "📜 Transaction History",
    "🌐 Network Graph"
])

with tab1:
    st.header("Send Transaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        all_nodes = [st.session_state.main_node] + st.session_state.ai_nodes
        recipient_options = [
            node.node_id for node in all_nodes 
            if node.node_id != st.session_state.main_node.node_id
        ]
        recipient = st.selectbox("Recipient", recipient_options)
    
    with col2:
        max_amount = max(0, balance - 1)
        amount = st.number_input(
            "Amount (₿)", 
            min_value=0.01, 
            max_value=float(max_amount),
            value=10.0,
            step=0.01
        )
    
    if st.button("Send Transaction", type="primary"):
        tx, message = st.session_state.main_node.create_transaction(recipient, amount)
        if tx:
            st.success(f"✅ {message}")
            st.info(f"Transaction ID: {tx.tx_id[:16]}...")
        else:
            st.error(f"❌ {message}")

with tab2:
    st.header("Network Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    all_nodes = [st.session_state.main_node] + st.session_state.ai_nodes
    total_nodes = len(all_nodes)
    miner_nodes = sum(1 for n in all_nodes if n.is_miner)
    
    col1.metric("Total Nodes", total_nodes)
    col2.metric("Miner Nodes", miner_nodes)
    col3.metric("Your Connections", len(st.session_state.main_node.peers))
    
    chain_lengths = [len(node.blockchain) for node in all_nodes]
    consensus = len(set(chain_lengths)) == 1
    col4.metric("Consensus", "✅ Yes" if consensus else "❌ No")
    
    st.markdown("---")
    
    st.subheader("Node Balances")
    
    node_data = []
    for node in all_nodes:
        node_data.append({
            'Node ID': node.node_id,
            'Type': 'You' if node.node_id == 'YOU' else ('Miner' if node.is_miner else 'Node'),
            'Balance (₿)': f"{node.get_balance():.2f}",
            'Chain Length': len(node.blockchain),
            'Pending TXs': len(node.blockchain.pending_transactions)
        })
    
    df = pd.DataFrame(node_data)
    st.dataframe(df, use_container_width=True)

with tab3:
    st.header("Blockchain Explorer")
    
    blockchain = st.session_state.main_node.blockchain
    recent_blocks = list(reversed(blockchain.chain[-10:]))
    
    for block in recent_blocks:
        with st.expander(f"Block #{block.index} - {block.hash[:16]}..."):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Miner:** {block.miner}")
            col2.write(f"**Transactions:** {len(block.transactions)}")
            col3.write(f"**Nonce:** {block.nonce}")
            
            st.write("**Transactions:**")
            for tx in block.transactions:
                if tx.sender == "COINBASE":
                    st.write(f"  🎁 Mining Reward → {tx.recipient}: ₿{tx.amount}")
                else:
                    st.write(f"  💸 {tx.sender} → {tx.recipient}: ₿{tx.amount}")

with tab4:
    st.header("Your Transaction History")
    
    history = st.session_state.main_node.blockchain.get_transaction_history(
        st.session_state.wallet_id
    )
    
    if history:
        for item in reversed(history[-20:]):
            tx = item['tx']
            tx_type = item['type']
            block_num = item['block']
            
            if tx.sender == "COINBASE":
                st.success(f"⛏️ Block #{block_num}: Mining Reward ₿{tx.amount}")
            elif tx_type == 'sent':
                st.error(f"📤 Block #{block_num}: Sent ₿{tx.amount} to {tx.recipient[:8]}...")
            else:
                st.success(f"📥 Block #{block_num}: Received ₿{tx.amount} from {tx.sender[:8]}...")
    else:
        st.info("No transactions yet")

with tab5:
    st.header("Network Topology")
    
    st.write("**Your Peers:**")
    for peer_id in st.session_state.main_node.peers:
        peer = st.session_state.network.nodes[peer_id]
        peer_type = "⛏️ Miner" if peer.is_miner else "📡 Node"
        st.write(f"- {peer_id} {peer_type}")
    
    st.markdown("---")
    
    st.subheader("Recent Network Messages")
    recent_msgs = st.session_state.network.get_recent_messages(10)
    
    for msg in reversed(recent_msgs):
        msg_type = msg['type'].replace('_', ' ').title()
        st.write(f"🔄 {msg['from']} → {msg['to']}: {msg_type}")

if st.button("🔄 Refresh"):
    st.rerun()

st.markdown("---")
st.caption("Botcoin - A Bitcoin Network Prototype")
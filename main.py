"""Entry point for Bitcoin simulation"""
from simulation.simulator import Simulator

def main():
    print("=" * 60)
    print("BITCOIN P2P NETWORK SIMULATION")
    print("=" * 60)
    
    sim = Simulator(num_nodes=10, num_miners=3)
    
    sim.run(duration=60)

if __name__ == "__main__":
    main()
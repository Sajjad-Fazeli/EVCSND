"""
Script to run EV charging station network simulations

This script runs both basic and sensitivity analysis simulations for EV charging stations.
"""

import os
import sys
import time
from simulation import EVCSSimulation


def setup_directories():
    """
    Create necessary directories for the simulation
    """
    required_dirs = ['data', 'results']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}")


def check_data_files():
    """
    Check if required data files exist
    """
    required_files = [
        'Weekday.csv',
        'Weekend.csv',
        'BEV.csv',
        'PHEV.csv',
        'Building.csv',
        'Parking.csv',
        'BuildingCount.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join('data', file)):
            missing_files.append(file)
    
    if missing_files:
        print("Error: Missing required data files:")
        for file in missing_files:
            print(f"- {file}")
        sys.exit(1)


def main():
    """Main function to run simulations"""
    start_time = time.time()
    
    # Setup directories
    setup_directories()
    
    # Check data files
    check_data_files()
    
    # Run simulations
    print("\nStarting EV Charging Station Network Simulations...")
    
    # Run basic simulation
    print("\nRunning basic simulation...")
    basic_sim = EVCSSimulation()
    basic_results = basic_sim.run_basic_simulation()
    print(f"Basic simulation completed in {basic_results['runtime']:.2f} seconds")
    
    # Run sensitivity analysis
    print("\nRunning sensitivity analysis...")
    sensitivity_sim = EVCSSimulation()
    
    # Analyze BEV share sensitivity
    print("\nAnalyzing BEV share sensitivity...")
    bev_values = [0.01, 0.02, 0.03, 0.04, 0.05]
    bev_results = sensitivity_sim.run_sensitivity_analysis('bev_share', bev_values)
    
    # Analyze demand range sensitivity
    print("\nAnalyzing demand range sensitivity...")
    demand_values = [(5000, 15000), (10000, 20000), (15000, 25000)]
    demand_results = sensitivity_sim.run_sensitivity_analysis('min_demand', 
                                                           [v[0] for v in demand_values])
    
    # Print summary
    print("\nSimulation Summary:")
    print(f"Total runtime: {time.time() - start_time:.2f} seconds")
    print(f"Results saved in: {os.path.abspath('results')} directory")
    print("\nSimulation completed successfully!")


if __name__ == "__main__":
    main()

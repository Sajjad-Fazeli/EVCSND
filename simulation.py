"""
Simulation module for Electric Vehicle Charging Station Network Design

This module handles both basic and sensitivity analysis simulations for EV charging stations.
"""

import pandas as pd
import numpy as np
import time
from config import CONFIG
from demand_generation import DemandGenerator
import matplotlib.pyplot as plt
import json
from collections import Counter


class EVCSSimulation:
    """
    Class for running EV Charging Station Network simulations
    """
    
    def __init__(self, 
                 num_scenarios: int = CONFIG['SIMULATION']['SCENARIOS'],
                 min_demand: int = CONFIG['SIMULATION']['MIN_DEMAND'],
                 max_demand: int = CONFIG['SIMULATION']['MAX_DEMAND'],
                 bev_share: float = CONFIG['SIMULATION']['BEV_SHARE'],
                 phev_share: float = CONFIG['SIMULATION']['PHEV_SHARE']):
        """
        Initialize the simulation
        
        Args:
            num_scenarios: Number of scenarios to simulate
            min_demand: Minimum demand per scenario
            max_demand: Maximum demand per scenario
            bev_share: Share of BEV vehicles
            phev_share: Share of PHEV vehicles
        """
        self.num_scenarios = num_scenarios
        self.min_demand = min_demand
        self.max_demand = max_demand
        self.bev_share = bev_share
        self.phev_share = phev_share
        self.demand_generator = DemandGenerator(min_demand, max_demand, bev_share, phev_share)
        
    def run_basic_simulation(self) -> dict:
        """
        Run the basic simulation
        
        Returns:
            Dictionary containing simulation results
        """
        start_time = time.time()
        
        # Generate demand
        demand = self.demand_generator.generate_demand(self.num_scenarios)
        
        # Calculate utilities
        utilities = self.demand_generator.calculate_utilities(demand)
        
        # Process results
        results = {
            'total_demand': len(demand),
            'num_scenarios': self.num_scenarios,
            'avg_demand_per_scenario': len(demand) / self.num_scenarios,
            'runtime': time.time() - start_time,
            'utilities': utilities
        }
        
        # Save results
        self.save_results('basic_simulation', results)
        
        return results
    
    def run_sensitivity_analysis(self, 
                               parameter: str, 
                               values: list,
                               num_samples: int = 10) -> dict:
        """
        Run sensitivity analysis for a specific parameter
        
        Args:
            parameter: Parameter to analyze (e.g., 'bev_share', 'min_demand')
            values: List of values to test
            num_samples: Number of samples per value
            
        Returns:
            Dictionary containing sensitivity analysis results
        """
        results = {}
        
        for value in values:
            # Update parameter value
            if parameter == 'bev_share':
                self.demand_generator.bev_share = value
            elif parameter == 'min_demand':
                self.demand_generator.min_demand = value
            elif parameter == 'max_demand':
                self.demand_generator.max_demand = value
            
            # Run multiple samples
            sample_results = []
            for _ in range(num_samples):
                sample = self.run_basic_simulation()
                sample_results.append(sample)
            
            # Calculate statistics
            avg_demand = np.mean([r['avg_demand_per_scenario'] for r in sample_results])
            std_demand = np.std([r['avg_demand_per_scenario'] for r in sample_results])
            
            results[value] = {
                'avg_demand': avg_demand,
                'std_demand': std_demand,
                'runtime': np.mean([r['runtime'] for r in sample_results])
            }
        
        # Save results
        self.save_results(f'sensitivity_{parameter}', results)
        
        # Generate plots
        self.generate_sensitivity_plots(parameter, results)
        
        return results
    
    def save_results(self, simulation_type: str, results: dict):
        """
        Save simulation results to files
        
        Args:
            simulation_type: Type of simulation (basic or sensitivity)
            results: Dictionary containing results
        """
        # Save results as JSON
        with open(f'results/{simulation_type}_results.json', 'w') as f:
            json.dump(results, f, indent=4)
            
        # Save summary statistics
        summary = {
            'total_demand': results.get('total_demand', 0),
            'num_scenarios': results.get('num_scenarios', 0),
            'runtime': results.get('runtime', 0)
        }
        with open(f'results/{simulation_type}_summary.json', 'w') as f:
            json.dump(summary, f, indent=4)
    
    def generate_sensitivity_plots(self, parameter: str, results: dict):
        """
        Generate plots for sensitivity analysis
        
        Args:
            parameter: Parameter being analyzed
            results: Dictionary containing results
        """
        values = list(results.keys())
        avg_demands = [results[v]['avg_demand'] for v in values]
        std_demands = [results[v]['std_demand'] for v in values]
        
        plt.figure(figsize=(10, 6))
        plt.errorbar(values, avg_demands, yerr=std_demands, fmt='-o')
        plt.title(f'Sensitivity Analysis - {parameter}')
        plt.xlabel(parameter)
        plt.ylabel('Average Demand per Scenario')
        plt.grid(True)
        plt.savefig(f'results/sensitivity_{parameter}.png')
        plt.close()


def main():
    """Main function to run simulations"""
    # Run basic simulation
    print("Running basic simulation...")
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
    
    print("\nAll simulations completed!")


if __name__ == "__main__":
    main()

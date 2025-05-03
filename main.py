"""
Main application for Electric Vehicle Charging Station Network Design

This module orchestrates the entire process from data processing to optimization
and result analysis.
"""

import pandas as pd
import numpy as np
from config import CONFIG
from data_processing import calculate_distances, generate_demand, process_demand_data
from optimization import optimize_station_locations


def load_data():
    """Load all necessary data files"""
    # Load transportation distributions
    weekday = pd.read_csv("data/Weekday.csv")
    weekend = pd.read_csv("data/Weekend.csv")
    bev = pd.read_csv("data/BEV.csv")
    phev = pd.read_csv("data/PHEV.csv")
    
    # Load building and parking data
    building = pd.read_csv("data/Building.csv")
    parking = pd.read_csv("data/Parking.csv")
    building_count = pd.read_csv("data/BuildingCount.csv")
    
    return {
        'weekday': weekday,
        'weekend': weekend,
        'bev': bev,
        'phev': phev,
        'building': building,
        'parking': parking,
        'building_count': building_count
    }


def main():
    """Main function to run the optimization process"""
    # Load data
    data = load_data()
    
    # Calculate distances
    distances = calculate_distances(data['building'], data['parking'])
    
    # Generate demand
    total_demand = pd.DataFrame()
    for _ in range(CONFIG['SIMULATION']['SCENARIOS']):
        demand = generate_demand()
        demand['scenario'] = len(total_demand) + 1
        total_demand = pd.concat([total_demand, demand])
    
    # Process demand data
    demand_data = process_demand_data(total_demand)
    
    # Run optimization
    results = optimize_station_locations(
        num_stations=CONFIG['OPTIMIZATION']['STATIONS'],
        num_scenarios=CONFIG['OPTIMIZATION']['SCENARIOS_SAMPLE']
    )
    
    # Save results
    results[2].to_csv('results/station_locations.csv', index=False)
    
    print(f"Optimization completed. Objective value: {results[0]}")
    print(f"Runtime: {results[1]} seconds")


if __name__ == "__main__":
    main()

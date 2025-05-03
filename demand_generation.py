"""
Demand generation module for Electric Vehicle Charging Station Network Design

This module handles the generation of demand scenarios for EV charging stations.
"""

import pandas as pd
import numpy as np
from config import CONFIG, DESTINATION_TYPES, PURPOSE_TYPES
import time
from collections import Counter
import json


class DemandGenerator:
    """
    Class for generating demand scenarios for EV charging stations
    """
    
    def __init__(self, min_demand: int = CONFIG['SIMULATION']['MIN_DEMAND'],
                 max_demand: int = CONFIG['SIMULATION']['MAX_DEMAND'],
                 bev_share: float = CONFIG['SIMULATION']['BEV_SHARE'],
                 phev_share: float = CONFIG['SIMULATION']['PHEV_SHARE']):
        """
        Initialize the demand generator
        
        Args:
            min_demand: Minimum demand to generate
            max_demand: Maximum demand to generate
            bev_share: Share of BEV vehicles
            phev_share: Share of PHEV vehicles
        """
        self.min_demand = min_demand
        self.max_demand = max_demand
        self.bev_share = bev_share
        self.phev_share = phev_share
        self.data_loaded = False
        
    def load_data(self):
        """
        Load all necessary data files
        """
        # Load transportation distributions
        self.weekday = pd.read_csv("data/Weekday.csv")
        self.weekend = pd.read_csv("data/Weekend.csv")
        self.bev = pd.read_csv("data/BEV.csv")
        self.phev = pd.read_csv("data/PHEV.csv")
        
        # Load building and parking data
        self.building = pd.read_csv("data/Building.csv")
        self.parking = pd.read_csv("data/Parking.csv")
        self.building_count = pd.read_csv("data/BuildingCount.csv")
        
        self.data_loaded = True
        
    def generate_demand(self, num_scenarios: int = CONFIG['SIMULATION']['SCENARIOS']) -> pd.DataFrame:
        """
        Generate demand scenarios
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            DataFrame containing generated demand data
        """
        if not self.data_loaded:
            self.load_data()
            
        total_demand = pd.DataFrame()
        
        for scenario in range(num_scenarios):
            # Generate random demand
            rand_demand = np.random.randint(self.min_demand, self.max_demand + 1)
            demand = pd.DataFrame({'rand': np.random.random(rand_demand)})
            
            # Assign vehicle types
            demand['vehicle_type'] = np.where(
                demand['rand'] <= self.bev_share,
                'BEV',
                np.where(
                    demand['rand'] <= self.bev_share + self.phev_share,
                    'PHEV',
                    'Gas'
                )
            )
            
            # Filter out gas vehicles
            demand = demand[demand.vehicle_type != 'Gas'].reset_index(drop=True)
            
            # Generate arrival times
            weekday_arrival = np.ceil(
                np.random.weibull(8 / 0.66 ** 0.33, len(demand))
            )
            weekend_arrival = np.ceil(
                np.random.weibull(13 / 0.75 ** 0.25, len(demand))
            )
            
            # Assign day type
            demand['day'] = np.where(
                np.random.random() <= 5/7,
                'Weekday',
                'Weekend'
            )
            
            # Assign arrival times based on day
            demand['arrival'] = np.where(
                demand['day'] == 'Weekday',
                weekday_arrival,
                weekend_arrival
            )
            
            # Adjust arrival times that exceed 24 hours
            demand['arrival'] = demand['arrival'].apply(
                lambda x: x - 24 if x > 24 else x
            )
            
            # Add scenario identifier
            demand['scenario'] = scenario + 1
            
            total_demand = pd.concat([total_demand, demand])
            
        return total_demand
    
    def calculate_utilities(self, demand_df: pd.DataFrame) -> dict:
        """
        Calculate utilities for each scenario
        
        Args:
            demand_df: DataFrame containing demand data
            
        Returns:
            Dictionary of utilities for each scenario
        """
        utilities = {}
        for scenario in demand_df['scenario'].unique():
            scenario_data = demand_df[demand_df['scenario'] == scenario]
            utilities[scenario] = {
                'total_demand': len(scenario_data),
                'bev_count': len(scenario_data[scenario_data.vehicle_type == 'BEV']),
                'phev_count': len(scenario_data[scenario_data.vehicle_type == 'PHEV']),
                'weekday_count': len(scenario_data[scenario_data.day == 'Weekday']),
                'weekend_count': len(scenario_data[scenario_data.day == 'Weekend'])
            }
        
        return utilities
    
    def save_results(self, demand_df: pd.DataFrame, utilities: dict):
        """
        Save results to files
        
        Args:
            demand_df: DataFrame containing demand data
            utilities: Dictionary of utilities
        """
        # Save demand data
        demand_df.to_csv('results/demand_scenarios.csv', index=False)
        
        # Save utilities
        with open('results/utilities.json', 'w') as f:
            json.dump(utilities, f, indent=4)


def main():
    """Main function to run demand generation"""
    start_time = time.time()
    
    # Initialize demand generator
    generator = DemandGenerator()
    
    # Generate demand
    demand = generator.generate_demand()
    
    # Calculate utilities
    utilities = generator.calculate_utilities(demand)
    
    # Save results
    generator.save_results(demand, utilities)
    
    # Print summary
    print(f"Total demand generated: {len(demand)}")
    print(f"Number of scenarios: {len(demand['scenario'].unique())}")
    print(f"Total runtime: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()

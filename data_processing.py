"""
Data processing module for Electric Vehicle Charging Station Network Design

This module handles all data processing tasks including:
- Demand generation
- Distance calculations
- Data aggregation
"""

import pandas as pd
import numpy as np
from config import CONFIG, DESTINATION_TYPES, PURPOSE_TYPES


def calculate_distances(building_df: pd.DataFrame, parking_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate distances between buildings and parking lots
    
    Args:
        building_df: DataFrame containing building information
        parking_df: DataFrame containing parking lot information
        
    Returns:
        DataFrame containing distances between all building-parking pairs
    """
    distance_df = pd.DataFrame([
        {
            'building_type': building_df.Destype[t],
            'building_number': building_df.NumberB[t],
            'building_x': building_df.FirstB[t],
            'building_y': building_df.SecondB[t],
            'parking_x': parking_df.FirstP[s],
            'parking_y': parking_df.SecondP[s],
            'parking_number': s + 1
        }
        for t in range(len(building_df))
        for s in range(len(parking_df))
    ])
    
    # Calculate Euclidean distance
    distance_df['distance'] = np.sqrt(
        (distance_df.building_x - distance_df.parking_x) ** 2 +
        (distance_df.building_y - distance_df.parking_y) ** 2
    )
    
    return distance_df


def generate_demand(
    min_demand: int = CONFIG['SIMULATION']['MIN_DEMAND'],
    max_demand: int = CONFIG['SIMULATION']['MAX_DEMAND'],
    bev_share: float = CONFIG['SIMULATION']['BEV_SHARE'],
    phev_share: float = CONFIG['SIMULATION']['PHEV_SHARE']
) -> pd.DataFrame:
    """
    Generate demand data for charging stations
    
    Args:
        min_demand: Minimum demand to generate
        max_demand: Maximum demand to generate
        bev_share: Share of BEV vehicles
        phev_share: Share of PHEV vehicles
        
    Returns:
        DataFrame containing generated demand data
    """
    demand = pd.DataFrame()
    
    # Generate random demand
    rand_demand = np.random.randint(min_demand, max_demand + 1)
    demand['rand'] = np.random.random(rand_demand)
    
    # Assign vehicle types
    demand['vehicle_type'] = np.where(
        demand['rand'] <= bev_share,
        'BEV',
        np.where(
            demand['rand'] <= bev_share + phev_share,
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
        WEEKDAY,
        WEEKEND
    )
    
    # Assign arrival times based on day
    demand['arrival'] = np.where(
        demand['day'] == WEEKDAY,
        weekday_arrival,
        weekend_arrival
    )
    
    # Adjust arrival times that exceed 24 hours
    demand['arrival'] = demand['arrival'].apply(
        lambda x: x - 24 if x > 24 else x
    )
    
    return demand


def process_demand_data(demand_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process demand data to calculate key metrics
    
    Args:
        demand_df: DataFrame containing demand data
        
    Returns:
        Processed DataFrame with calculated metrics
    """
    # Calculate access rate
    access_rate = len(demand_df[(demand_df.Station != 0) & 
                              (demand_df.Station != 1000)]) / len(demand_df)
    
    # Calculate lost demand rate
    lost_rate = len(demand_df[demand_df.Station == 1000]) / len(demand_df)
    
    # Calculate utilization
    utilization = demand_df['Duration'][(demand_df.Station != 0) & 
                                      (demand_df.Station != 1000)].sum() / \
                 (demand_df.Capacity.sum() * 12)
    
    # Calculate average walk distances
    walk_before = demand_df['WalkBefore'].mean()
    walk_after = demand_df['WalkAfter'].mean()
    
    return {
        'access_rate': access_rate,
        'lost_rate': lost_rate,
        'utilization': utilization,
        'walk_before': walk_before,
        'walk_after': walk_after
    }

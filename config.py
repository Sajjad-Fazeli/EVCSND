"""
Configuration file for Electric Vehicle Charging Station Network Design

This module contains all configuration settings and constants used throughout the application.
"""

# Configuration settings
CONFIG = {
    # Simulation parameters
    'SIMULATION': {
        'MIN_DEMAND': 10000,
        'MAX_DEMAND': 20000,
        'BEV_SHARE': 0.01,
        'PHEV_SHARE': 0.02,
        'SCENARIOS': 2500
    },
    
    # Optimization parameters
    'OPTIMIZATION': {
        'STATIONS': 8,
        'SCENARIOS_SAMPLE': 50,
        'TOTAL_SCENARIOS': 2500,
        'MIP_GAP': 0.01
    },
    
    # Cost parameters
    'COSTS': {
        'LEVEL2_COST': 900,
        'LEVEL3_COST': 25000
    }
}

# Constants
WEEKDAY = 'Weekday'
WEEKEND = 'Weekend'

# Destination types
DESTINATION_TYPES = {
    1: 'Residential',
    2: 'Commercial',
    3: 'Office',
    4: 'Retail',
    5: 'Industrial',
    6: 'Other'
}

# Purpose types
PURPOSE_TYPES = {
    2: 'Level2 Charging',
    3: 'Level3 Charging'
}

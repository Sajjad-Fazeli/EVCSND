"""
Optimization module for Electric Vehicle Charging Station Network Design

This module contains the optimization models using Gurobi for:
- Station location optimization
- Capacity optimization
- Demand assignment
"""

from gurobipy import Model, GRB, LinExpr, tuplelist
import pandas as pd
import numpy as np
from config import CONFIG


def optimize_station_locations(
    num_stations: int = CONFIG['OPTIMIZATION']['STATIONS'],
    num_scenarios: int = CONFIG['OPTIMIZATION']['SCENARIOS_SAMPLE'],
    budget: float = None
) -> tuple:
    """
    Optimize charging station locations and capacities
    
    Args:
        num_stations: Number of stations to locate
        num_scenarios: Number of demand scenarios
        budget: Optional budget constraint
        
    Returns:
        Tuple containing:
        - Objective value
        - Solution runtime
        - Station locations and capacities
    """
    # Create model
    model = Model("ChargingStationOptimization")
    
    # Get station list and capacity options
    station_list = [s + 1 for s in range(len(parking))]
    capacity_options = tuplelist([
        (s + 1, 2 * (l + 1)) 
        for s in range(len(parking)) 
        for l in range(parking.Max[s])
    ])
    
    # Add variables
    # x[s] = 1 if station s is selected
    x = {
        s: model.addVar(vtype=GRB.BINARY, name=f'x_{s}')
        for s in station_list
    }
    
    # z[l,s] = 1 if we install l pack of charging stations at location s
    z = {
        (s, l): model.addVar(vtype=GRB.BINARY, name=f'z_{s}_{l}')
        for s, l in capacity_options
    }
    
    # y defines the percentage of demand assigned to each station
    y = {}
    for i in range(len(demand_data)):
        for j in range(len(demand_data[i][3])):
            y[demand_data[i][0],
              demand_data[i][1][j],
              demand_data[i][2],
              demand_data[i][3][j],
              demand_data[i][4]] = model.addVar(
                ub=1, vtype=GRB.BINARY,
                name=f'y_{demand_data[i][0]}_{demand_data[i][1][j]}_{demand_data[i][2]}_{demand_data[i][3][j]}_{demand_data[i][4]}'
            )
    
    model.update()
    
    # Set objective: Maximize accessibility
    model.setObjective(
        LinExpr([
            (demand_data[k] * (1/num_scenarios), y[k])
            for k in demand_data
        ]),
        GRB.MAXIMIZE
    )
    
    # Add constraints
    # Constraint 1: Number of stations
    model.addConstr(
        LinExpr([(1.0, x[s]) for s in station_list]),
        GRB.EQUAL,
        num_stations
    )
    
    # Constraint 2: Budget constraint (if provided)
    if budget is not None:
        capacity_costs = {
            (s, l): 2 * (l + 1) * station_costs[station_costs.Parking == s + 1].Cost.iloc[0]
            for s, l in capacity_options
        }
        model.addConstr(
            LinExpr([
                (capacity_costs[k], z[k])
                for k in capacity_costs
            ]),
            GRB.LESS_EQUAL,
            budget
        )
    
    # Constraint 3: Capacity constraints
    for s, l in capacity_options:
        model.addConstr(
            LinExpr([(1.0, z[s, l]), (-1.0, x[s])]),
            GRB.LESS_EQUAL,
            0
        )
    
    for s in station_list:
        model.addConstr(
            LinExpr([(1.0, z[s, l]) for s, l in capacity_options.select(s, '*')]),
            GRB.LESS_EQUAL,
            1
        )
    
    # Constraint 4: Demand assignment
    for i in range(len(demand_data)):
        model.addConstr(
            LinExpr([
                (1.0, y[demand_data[i][0],
                       demand_data[i][1][j],
                       demand_data[i][2],
                       demand_data[i][3][j],
                       demand_data[i][4]])
                for j in range(len(demand_data[i][3]))
            ]),
            GRB.LESS_EQUAL,
            1
        )
    
    # Constraint 5: Supply-demand balance
    for w in scenario_list:
        scenario_demand = {
            k: v for k, v in demand_data.items() if k[4] == w
        }
        
        for t in range(int(demand.Arrival.min()), int(demand.Departure.max())):
            time_demand = {
                k: v for k, v in scenario_demand.items() 
                if k[0] <= t and k[1] > t
            }
            
            if len(time_demand) > 0:
                for s in station_list:
                    station_demand = {
                        k: v for k, v in time_demand.items() 
                        if s in k[3]
                    }
                    
                    if len(station_demand) > 0:
                        model.addConstr(
                            LinExpr([
                                (station_demand[k],
                                 y[k[0], k[1], k[2], s, w])
                                for k in station_demand
                            ]),
                            GRB.LESS_EQUAL,
                            LinExpr([
                                (l, z[s, l])
                                for s, l in capacity_options.select(s, '*')
                            ])
                        )
    
    # Set solver parameters
    model.Params.MIPGap = CONFIG['OPTIMIZATION']['MIP_GAP']
    
    # Solve
    model.optimize()
    
    # Extract solution
    solution = pd.DataFrame([
        [s + 1, 2 * (l + 1) * z[s + 1, 2 * (l + 1)].x]
        for s in range(len(parking))
        for l in range(parking.Max[s])
    ])
    
    solution.columns = ['Station', 'Capacity']
    
    return (
        model.objVal * num_scenarios / sum(demand.Count),
        model.Runtime,
        solution
    )

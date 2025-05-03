"""
Benders Decomposition module for Electric Vehicle Charging Station Network Design

This module implements the Benders Decomposition algorithm for optimizing EV charging station network design.
"""

import pandas as pd
import numpy as np
from gurobipy import *
from config import CONFIG
import time
from collections import Counter


class BendersDecomposition:
    """
    Class implementing Benders Decomposition for EV charging station network design
    """
    
    def __init__(self,
                 num_stations: int = CONFIG['OPTIMIZATION']['STATIONS'],
                 num_scenarios: int = CONFIG['OPTIMIZATION']['SCENARIOS_SAMPLE'],
                 max_iterations: int = 100,
                 tolerance: float = 0.001):
        """
        Initialize the Benders Decomposition solver
        
        Args:
            num_stations: Number of stations to locate
            num_scenarios: Number of demand scenarios
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
        """
        self.num_stations = num_stations
        self.num_scenarios = num_scenarios
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.master_problem = None
        self.sub_problem = None
        self.iteration = 0
        self.upper_bound = float('inf')
        self.lower_bound = -float('inf')
        
    def build_master_problem(self):
        """
        Build the master problem
        """
        m = Model("Master_Problem")
        
        # Add variables
        x = m.addVars(self.N, self.J, vtype=GRB.BINARY, name="x")
        theta = m.addVars(self.S, self.T, vtype=GRB.CONTINUOUS, name="theta")
        
        # Set objective
        m.setObjective(quicksum(theta[s, t] for s in self.S for t in self.T), GRB.MINIMIZE)
        
        # Add constraints
        # Station count constraint
        m.addConstr(quicksum(x[n, j] for n in self.N for j in self.J) == self.num_stations)
        
        # Station capacity constraints
        for n in self.N:
            for j in self.J:
                m.addConstr(x[n, j] <= 1)
                m.addConstr(quicksum(x[n, j] for j in self.J) <= 1)
        
        self.master_problem = m
        
    def build_sub_problem(self, x_values):
        """
        Build the sub-problem for a given x solution
        
        Args:
            x_values: Values of x variables from master problem
            
        Returns:
            Sub-problem model
        """
        m = Model("Sub_Problem")
        
        # Add variables
        y = m.addVars(self.T, self.N, self.J, self.B, self.W, vtype=GRB.BINARY, name="y")
        o = m.addVars(self.T, self.N, self.N, self.J, self.B, self.W, vtype=GRB.BINARY, name="o")
        
        # Set objective
        m.setObjective(quicksum(
            self.Demand_p[t, s, b] * y[t, n, j, s, b, w]
            for s in self.S
            for t in self.T
            for n in self.N
            for j in self.J
            for b in self.B
            for w in self.W
        ), GRB.MAXIMIZE)
        
        # Add constraints
        # Linearization constraints
        for s in self.S:
            for t in self.T:
                for n in self.N:
                    for q in self.N:
                        for j in self.J:
                            for b in self.B:
                                for w in self.W:
                                    m.addConstr(o[t, n, q, j, s, b, w] <= y[t, n, j, s, b, w])
                                    m.addConstr(o[t, n, q, j, s, b, w] <= x_values[n, j])
                                    m.addConstr(o[t, n, q, j, s, b, w] >= y[t, n, j, s, b, w] + x_values[n, j] - 1)
        
        # Choice constraints
        for s in self.S:
            for t in self.T:
                for b in self.B:
                    m.addConstr(quicksum(
                        y[t, n, j, s, b, w]
                        for n in self.N
                        for j in self.J
                        for w in self.W
                    ) <= 1)
        
        # Capacity constraints
        for s in self.S:
            for t in self.T:
                for b in self.B:
                    for w in self.W:
                        m.addConstr(quicksum(
                            self.Demand_p[t, s, b] * y[t, n, j, s, b, w]
                            for n in self.N
                            for j in self.J
                        ) <= self.Walking_p[t, s, b][w])
        
        return m
    
    def add_benders_cut(self, x_values, sub_problem_obj):
        """
        Add Benders cut to master problem
        
        Args:
            x_values: Values of x variables
            sub_problem_obj: Objective value from sub-problem
        """
        cut = LinExpr()
        for n in self.N:
            for j in self.J:
                cut += x_values[n, j] * sub_problem_obj
        
        self.master_problem.addConstr(
            quicksum(self.theta[s, t] for s in self.S for t in self.T) >= cut,
            name=f"Benders_Cut_{self.iteration}"
        )
    
    def solve(self):
        """
        Solve the Benders Decomposition problem
        
        Returns:
            Tuple containing:
            - Optimal solution
            - Objective value
            - Runtime
        """
        start_time = time.time()
        
        # Initialize master problem
        self.build_master_problem()
        
        while self.iteration < self.max_iterations and \
              abs(self.upper_bound - self.lower_bound) > self.tolerance:
            
            # Solve master problem
            self.master_problem.optimize()
            
            # Get x values
            x_values = {}
            for n in self.N:
                for j in self.J:
                    x_values[n, j] = self.master_problem.getVarByName(f"x[{n},{j}").x
            
            # Build and solve sub-problem
            sub_problem = self.build_sub_problem(x_values)
            sub_problem.optimize()
            
            # Update bounds
            self.upper_bound = min(self.upper_bound, sub_problem.objVal)
            self.lower_bound = max(self.lower_bound, self.master_problem.objVal)
            
            # Add Benders cut
            self.add_benders_cut(x_values, sub_problem.objVal)
            
            self.iteration += 1
            
            print(f"Iteration {self.iteration}:")
            print(f"  Upper bound: {self.upper_bound:.2f}")
            print(f"  Lower bound: {self.lower_bound:.2f}")
            print(f"  Gap: {abs(self.upper_bound - self.lower_bound):.2f}")
        
        runtime = time.time() - start_time
        
        # Extract solution
        solution = {}
        for n in self.N:
            for j in self.J:
                solution[n, j] = self.master_problem.getVarByName(f"x[{n},{j}").x
        
        return solution, self.lower_bound, runtime


def main():
    """Main function to run Benders Decomposition"""
    # Initialize solver
    solver = BendersDecomposition()
    
    # Solve problem
    solution, obj_val, runtime = solver.solve()
    
    # Print results
    print("\nSolution:")
    for (n, j), value in solution.items():
        if value > 0.5:
            print(f"Station {n} in location {j}: {value:.2f}")
    
    print(f"\nObjective value: {obj_val:.2f}")
    print(f"Runtime: {runtime:.2f} seconds")
    print(f"Number of iterations: {solver.iteration}")


if __name__ == "__main__":
    main()

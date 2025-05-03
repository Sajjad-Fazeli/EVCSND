# Electric Vehicle Charging Station Network Design

This project implements an optimization model for designing an electric vehicle charging station network.

## Features

- Demand generation and processing
- Station location optimization
- Capacity optimization
- Demand assignment
- Performance metrics calculation

## Requirements

- Python 3.8+
- pandas>=1.5.0
- numpy>=1.21.0
- gurobipy>=9.5.0
- python-dateutil>=2.8.2
- pytz>=2021.3

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Structure

The project expects the following data files in the `data` directory:
- `Weekday.csv`: Weekday transportation distributions
- `Weekend.csv`: Weekend transportation distributions
- `BEV.csv`: Battery Electric Vehicle data
- `PHEV.csv`: Plug-in Hybrid Electric Vehicle data
- `Building.csv`: Building information
- `Parking.csv`: Parking lot information
- `BuildingCount.csv`: Building count data

## Usage

1. Run the main application:
```bash
python main.py
```

2. The results will be saved in the `results` directory:
- `station_locations.csv`: Optimized station locations and capacities

## Configuration

The configuration parameters can be modified in `config.py`:
- Simulation parameters (demand generation)
- Optimization parameters (number of stations, scenarios)
- Cost parameters (charging station costs)

## Results

The optimization process will output:
- Objective value (accessibility measure)
- Runtime
- Station locations and capacities
- Performance metrics (access rate, lost rate, utilization)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

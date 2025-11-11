# Santa Route Planner

A sophisticated route optimization application for Santa's Christmas delivery service, featuring capacity-constrained vehicle routing and real-time delivery visualization.

## Overview

This application solves the classic **Vehicle Routing Problem (VRP)** with capacity constraints for Santa's sleigh deliveries. It optimizes Santa's route to deliver presents to all good children while respecting the sleigh's weight and volume limitations.

### Features

- **Route Optimization**: Greedy clustering algorithm with nearest-neighbor heuristic
- **Capacity Management**: Respects weight (1000kg) and volume (100 units) constraints
- **Naughty/Nice Filter**: Automatically excludes naughty children from delivery route
- **CSV Export**: Semicolon-separated CSV with comma as decimal separator (European format)
- **Interactive Dashboard**: Real-time delivery simulation with map visualization
- **Statistics Tracking**: Distance, time, and delivery metrics

## Requirements

### Data Structure (from Excel file)

The application expects an Excel file with the following sheets:

1. **Overview**: Task description and criteria
2. **Sample Input**: Children data with columns:
   - `child`: Child ID number
   - `latitude`: Geographic latitude
   - `longitude`: Geographic longitude
   - `wish`: Article ID they want
   - `naughty`: 0 for good, 1 for naughty

3. **Articles**: Product catalog with:
   - `article`: Article ID
   - `weight`: Weight in kg
   - `volume`: Volume units

4. **Slay Meta Data**: Sleigh specifications:
   - `maximum weight`: 1000 kg
   - `maximum volume`: 100 units
   - `speed (km/h)`: 500 km/h
   - `time per stop (min)`: 1 minute

### Dependencies

```bash
pip install pandas openpyxl numpy
```

## Installation

1. Clone or download the repository
2. Ensure the Excel file `Kopie von Santa Planner.xlsx` is in the same directory
3. Install Python dependencies:

```bash
pip install pandas openpyxl numpy
```

## Usage

### Step 1: Generate Route Plan

Run the route planner algorithm:

```bash
python3 santa_planner.py
```

This will generate:
- `santa_route.csv` - The delivery route in CSV format (semicolon-separated)
- `route_plan.json` - Route plan in JSON format for the dashboard
- `children_data.json` - Children data for visualization
- `statistics.json` - Route statistics and metrics

### Step 2: View the Dashboard

Open the dashboard in a web browser:

```bash
# If you have Python's http.server
python3 -m http.server 8000
```

Then navigate to: `http://localhost:8000/dashboard.html`

Or simply open `dashboard.html` directly in your browser.

## Output Format

### CSV Output (`santa_route.csv`)

The CSV file contains the delivery sequence with these columns:

- **stop**: Child number to deliver to, or 0 for North Pole refill
- **article**: Article ID to load (only when stop=0)
- **pieces**: Number of pieces to load (only when stop=0)

Example:
```csv
stop;article;pieces
0;1,0;10,0
0;2,0;20,0
2;;
12;;
0;3,0;10,0
```

**Interpretation:**
- Row 1-2: At North Pole (stop=0), load 10 pieces of article 1 and 20 pieces of article 2
- Row 3: Deliver to child #2
- Row 4: Deliver to child #12
- Row 5: Return to North Pole and load 10 pieces of article 3

## Algorithm Details

### Route Optimization Strategy

1. **Filtering**: Exclude naughty children from deliveries
2. **Clustering**: Greedy capacity-based clustering
   - Start from North Pole
   - Use nearest-neighbor to add children to current trip
   - Check capacity constraints (weight & volume) before adding
   - Start new trip when capacity reached
3. **Route Ordering**: Nearest-neighbor TSP heuristic within each trip
4. **Refill Planning**: Calculate required articles per trip

### Distance Calculation

Uses the **Haversine formula** to calculate great-circle distances between geographic coordinates on Earth's surface.

### Key Optimizations

- Greedy clustering minimizes the number of trips
- Nearest-neighbor reduces travel distance within trips
- Capacity checking prevents overloading

## Dashboard Features

### Statistics Display
- Total children (good and naughty)
- Number of delivery stops
- Number of refill stops
- Total distance in kilometers
- Total time in hours

### Interactive Map
- **Red marker**: North Pole (start/refill point)
- **Green markers**: Good children (to visit)
- **Black markers**: Naughty children (no delivery)
- **Orange marker**: Current Santa location
- **Gray markers**: Already visited
- **Blue lines**: Route paths

### Simulation Controls
- **Start**: Begin delivery simulation
- **Pause**: Pause the simulation
- **Reset**: Reset to beginning

### Real-time Progress
- Progress bar showing completion percentage
- Current stop information
- Trip statistics
- Distance covered

## Performance Metrics

Based on sample data with 1000 children:
- **Good children**: 953
- **Naughty children**: 47 (excluded)
- **Total trips**: 9
- **Delivery stops**: 953
- **Refill stops**: 181
- **Total distance**: ~730,703 km
- **Total time**: ~1,477 hours (~61.5 days)

## Technical Stack

- **Backend**: Python 3
  - pandas: Data processing
  - openpyxl: Excel file reading
  - numpy: Numerical computations

- **Frontend**:
  - HTML5/CSS3: Layout and styling
  - JavaScript: Interactive functionality
  - Leaflet.js: Map visualization
  - OpenStreetMap: Map tiles

## File Structure

```
.
├── Kopie von Santa Planner.xlsx   # Input Excel file
├── santa_planner.py                # Route optimization algorithm
├── dashboard.html                  # Interactive visualization dashboard
├── README.md                       # This file
├── santa_route.csv                 # Generated route plan (CSV)
├── route_plan.json                 # Route plan (JSON)
├── children_data.json              # Children data (JSON)
└── statistics.json                 # Route statistics (JSON)
```

## Scoring Criteria

According to the overview sheet:

### Route Speed
- Fastest route: 10 points
- Second fastest: 5 points
- Third fastest: 1 point

### Dashboard Quality
- Nicest dashboard: 5 points
- Second nicest: 2 points
- Third nicest: 1 point

## Future Improvements

Potential enhancements for better optimization:

1. **Advanced Algorithms**:
   - Genetic algorithms for global optimization
   - Simulated annealing
   - Ant colony optimization
   - 2-opt or 3-opt local search improvements

2. **Better Clustering**:
   - K-means geographic clustering
   - Density-based clustering (DBSCAN)
   - Sweep algorithm for polar coordinates

3. **Multi-objective Optimization**:
   - Balance between distance and time
   - Minimize number of refills
   - Consider priority children

4. **Real-time Features**:
   - Weather conditions
   - Dynamic rerouting
   - Real-time capacity updates

## License

This project is created for the Santa Planner challenge.

## Author

Built with care for Christmas deliveries! 🎅🎄

---

**Merry Christmas and Happy Coding!** 🎁

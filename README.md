# Grid Criticality Analysis - IEEE-738 Thermal Rating System

A comprehensive web application for analyzing electrical grid criticality using IEEE-738 thermal rating calculations. This system provides real-time analysis of power line capacity under various environmental conditions.

## 🌟 Features

### Backend (FastAPI)

- **IEEE-738 Implementation**: Complete thermal rating calculations with all environmental parameters
- **RESTful API**: Clean API endpoints for ratings and stress analysis
- **Real-time Calculations**: Dynamic thermal ratings based on weather and environmental conditions
- **Data Validation**: Robust error handling and data validation
- **Comprehensive Parameters**: Support for all IEEE-738 parameters including:
  - Weather conditions (temperature, wind speed, wind angle)
  - Environmental factors (elevation, latitude, sun time)
  - Material properties (emissivity, absorptivity)
  - Configuration options (conductor direction, atmosphere type)

### Frontend (React)

- **Interactive Parameter Controls**: Intuitive sliders and dropdowns for all IEEE-738 parameters
- **Real-time Map Visualization**: Interactive map showing grid line status with color-coded markers
- **Comprehensive Data Tables**: Sortable tables with detailed ratings and stress analysis
- **Status Summary Dashboard**: System health overview with key metrics
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend │ ◄─────────────► │  FastAPI Backend │
│   (Port 3000)    │                 │   (Port 8000)    │
└─────────────────┘                 └─────────────────┘
         │                                    │
         │                                    │
    ┌─────────┐                         ┌─────────────┐
    │ Leaflet │                         │ IEEE-738    │
    │   Map   │                         │ Calculator  │
    └─────────┘                         └─────────────┘
                                               │
                                         ┌─────────────┐
                                         │ CSV Data    │
                                         │ (Grid Info) │
                                         └─────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
# Make script executable and run
chmod +x start.sh
./start.sh
```

### Option 2: Manual Startup

#### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

## 📊 Data Structure

### Input Files

- **buses.csv**: Bus information with voltage levels
- **lines.csv**: Transmission line data with conductor specifications
- **conductor_library.csv**: Conductor properties for IEEE-738 calculations
- **flows.csv**: Power flow data for stress analysis

### API Endpoints

- `GET /ratings`: Thermal ratings for all lines
- `GET /stress_summary`: Stress analysis with utilization percentages
- `GET /ratings_geojson`: GeoJSON format for map visualization
- `GET /health`: System health check

## 🎛️ IEEE-738 Parameters

The system supports all IEEE-738 thermal rating parameters:

| Parameter           | Range                  | Description                          |
| ------------------- | ---------------------- | ------------------------------------ |
| Ambient Temperature | -60°C to 80°C          | Air temperature                      |
| Wind Speed          | 0 to 60 m/s            | Wind velocity                        |
| Wind Angle          | 0° to 90°              | Wind direction relative to conductor |
| Elevation           | 0 to 50,000 ft         | Height above sea level               |
| Latitude            | -90° to 90°            | Geographic latitude                  |
| Sun Time            | 0 to 24 hours          | Hour of day                          |
| Emissivity          | 0 to 1                 | Surface emissivity                   |
| Absorptivity        | 0 to 1                 | Solar absorptivity                   |
| Direction           | East-West, North-South | Conductor orientation                |
| Atmosphere          | Clear, Industrial      | Atmospheric conditions               |

## 🗺️ Map Visualization

The interactive map displays the Hawaiian power grid using real geographic data:

### Real Data Integration

- **Actual Bus Coordinates**: Uses real coordinates from `oneline_buses.geojson` with proper latitude/longitude positioning
- **Real Transmission Lines**: Displays actual transmission line geometries from `oneline_lines.geojson`
- **Accurate Spacing**: Buses are positioned at their real geographic locations across Hawaii
- **Professional Grid Layout**: Shows the actual Hawaiian power grid topology
- **Real Bus Names**: Displays actual bus names like ALOHA138, HONOLULU69, WAIPAHU138, etc.

### Transmission Lines

- **Geographic Accuracy**: Lines follow real transmission line paths from the GeoJSON data
- **Consistent Styling**: All transmission lines use uniform 6px thickness for clear visibility
- **Dynamic Thresholds**: Line colors update based on configurable warning and overload thresholds
- **Three-Color System**: Lines use distinct colors - Green (Good <warn%), Orange (Warning warn%-bad%), Red (Overloaded ≥bad%)
- **Interactive Popups**: Click on lines to see detailed information including voltage, status, and utilization

### Bus Markers

- **Voltage-Based Sizing**: Larger markers for higher voltage buses (138kV: 12px, 69kV: 10px, others: 8px)
- **Uniform Color**: All buses use the same blue color for consistent appearance
- **Real Bus Names**: Displays actual bus names from the Hawaiian grid (e.g., ALOHA138, HONOLULU69)
- **Interactive Popups**: Click on buses to see bus name, voltage, and thermal rating

### Map Features

- **Dynamic Bounds**: Map bounds automatically calculated from actual bus coordinates
- **Optimal Zoom**: Initial zoom level of 9 for comprehensive view of the Hawaiian grid
- **Responsive Design**: Map height of 600px for optimal visibility
- **Professional Layout**: Clean legend and proper spacing for electrical engineering use

### Color Coding

**Transmission Lines:**

- 🟢 **Green**: Utilization < 80% (Good)
- 🟠 **Orange**: Utilization 80-100% (Warning)
- 🔴 **Red**: Utilization ≥ 100% (Overloaded)

**Bus/Substations:**

- 🔴 **Red circles**: 138kV and above (high voltage)
- 🔵 **Blue circles**: 69kV (medium voltage)
- 🟢 **Green circles**: Lower voltages

## 📈 Dashboard Features

### Status Summary

- Overall system health indicator
- Line status breakdown (Good/Warning/Overloaded)
- Utilization statistics (average, min, max)
- Power summary (total rating, flow, margins)

### Data Tables

- **Stress Analysis**: Current utilization and margins
- **Ratings Data**: Thermal ratings and conductor information
- **Sortable columns**: Click headers to sort data
- **Real-time updates**: Automatic refresh when parameters change

## 🔧 Technical Details

### Backend Technologies

- **FastAPI**: Modern Python web framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Pydantic**: Data validation and serialization
- **IEEE-738**: Custom thermal rating implementation

### Frontend Technologies

- **React 18**: Modern React with hooks
- **Material-UI**: Component library
- **Leaflet**: Interactive map visualization
- **Axios**: HTTP client
- **CSS3**: Responsive design

## 📁 Project Structure

```
HackOHIO_2025/
├── app/                    # FastAPI backend
│   ├── main.py            # Main application
│   ├── stress.py          # Stress analysis logic
│   ├── physics_ieee.py    # IEEE-738 calculations
│   ├── io.py              # Data loading
│   └── config.py          # Configuration
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.js         # Main app component
│   │   └── components/    # React components
│   └── package.json       # Node.js dependencies
├── data/                  # CSV data files
├── ieee738.py            # IEEE-738 implementation
├── requirements.txt      # Python dependencies
└── start.sh             # Startup script
```

## 🌐 Access Points

- **Frontend Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🔍 Usage Examples

### Adjusting Environmental Conditions

1. Use the **Ambient Temperature** slider to simulate different weather conditions
2. Modify **Wind Speed** and **Wind Angle** to see how wind affects thermal ratings
3. Change **Elevation** to simulate different altitudes
4. Adjust **Sun Time** to see daily variations in solar heating

### Analyzing Grid Stress

1. View the **Status Summary** for overall system health
2. Check the **Map Visualization** for geographic distribution of stress
3. Use **Data Tables** to examine specific line details
4. Sort by utilization to identify critical lines

## 🛠️ Development

### Adding New Parameters

1. Update the IEEE-738 implementation in `ieee738.py`
2. Modify the API endpoints in `app/main.py`
3. Add controls to the React frontend
4. Update the data flow in `app/stress.py`

### Customizing the Map

1. Modify `MapVisualization.js` for different marker styles
2. Update color schemes in the component
3. Add new popup information as needed

## 📝 License

This project is developed for HackOHIO 2025.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues, please refer to the API documentation at http://localhost:8000/docs or check the console logs for detailed error messages.

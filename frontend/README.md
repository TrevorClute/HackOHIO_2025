# Grid Criticality Analysis Frontend

A React-based frontend application for visualizing grid criticality analysis using IEEE-738 thermal rating calculations.

## Features

- **Interactive Parameter Controls**: Sliders and dropdowns for all IEEE-738 parameters
- **Real-time Map Visualization**: Interactive map showing grid line status with color-coded markers
- **Comprehensive Data Tables**: Sortable tables showing detailed ratings and stress analysis
- **Status Summary Dashboard**: Overview of system health and utilization statistics
- **Responsive Design**: Works on desktop and mobile devices

## IEEE-738 Parameters

The application provides controls for all IEEE-738 thermal rating parameters:

### Weather Conditions

- Ambient Temperature (-60°C to 80°C)
- Wind Speed (0 to 60 m/s)
- Wind Angle (0° to 90°)

### Environmental

- Elevation (0 to 50,000 ft)
- Latitude (-90° to 90°)
- Sun Time (0 to 24 hours)

### Material Properties

- Emissivity (0 to 1)
- Absorptivity (0 to 1)

### Configuration

- Conductor Direction (East-West, North-South)
- Atmosphere Type (Clear, Industrial)
- Warning Threshold (0 to 100%)
- Bad Threshold (0 to 100%)

## Installation

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000` and will proxy API requests to the backend at `http://localhost:8000`.

## Usage

1. **Adjust Parameters**: Use the sliders and dropdowns in the left panel to modify IEEE-738 parameters
2. **View Map**: The map shows grid lines with color-coded markers indicating utilization levels
3. **Check Status**: The summary panel provides an overview of system health
4. **Analyze Data**: Use the data tables to examine detailed ratings and stress information

## Map Visualization

- **Green markers**: Lines with utilization < 80% (Good)
- **Orange markers**: Lines with utilization 80-100% (Warning)
- **Red markers**: Lines with utilization ≥ 100% (Overloaded)
- **Marker size**: Indicates utilization level (larger = higher utilization)

## Data Tables

- **Stress Analysis**: Shows current utilization, status, and margins for each line
- **Ratings Data**: Displays thermal ratings calculated using IEEE-738 parameters
- **Sortable columns**: Click column headers to sort data
- **Real-time updates**: Data refreshes automatically when parameters change

## Technology Stack

- **React 18**: Modern React with hooks
- **Material-UI**: Component library for consistent design
- **Leaflet**: Interactive map visualization
- **Axios**: HTTP client for API communication
- **CSS3**: Custom styling and responsive design

## API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- `GET /ratings`: Fetch thermal ratings data
- `GET /stress_summary`: Fetch stress analysis data
- `GET /health`: Check backend health status

All API requests are automatically proxied from the development server to the backend.

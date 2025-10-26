#!/bin/bash

# Grid Criticality Analysis - Demo Script
# This script demonstrates key features of the application

echo "🔬 Grid Criticality Analysis - Demo"
echo "==================================="
echo ""

echo "📋 This demo will show you how to use the Grid Criticality Analysis system."
echo ""

echo "🎯 Key Features to Explore:"
echo "1. Interactive Parameter Controls"
echo "2. Real-time Map Visualization"
echo "3. Comprehensive Data Analysis"
echo "4. System Status Monitoring"
echo ""

echo "🚀 Getting Started:"
echo "1. Start the application using: ./start.sh"
echo "2. Open your browser to: http://localhost:3000"
echo "3. The backend API will be available at: http://localhost:8000"
echo ""

echo "🎛️ Parameter Controls Demo:"
echo "• Adjust Ambient Temperature slider (-60°C to 80°C)"
echo "• Modify Wind Speed (0 to 60 m/s)"
echo "• Change Wind Angle (0° to 90°)"
echo "• Set Elevation (0 to 50,000 ft)"
echo "• Configure Material Properties (Emissivity, Absorptivity)"
echo ""

echo "🗺️ Map Visualization Demo:"
echo "• Green markers: Lines with utilization < 80% (Good)"
echo "• Orange markers: Lines with utilization 80-100% (Warning)"
echo "• Red markers: Lines with utilization ≥ 100% (Overloaded)"
echo "• Click markers for detailed line information"
echo "• Marker size indicates utilization level"
echo ""

echo "📊 Data Analysis Demo:"
echo "• View Status Summary for system health overview"
echo "• Check Stress Analysis table for detailed utilization data"
echo "• Examine Ratings Data table for thermal ratings"
echo "• Sort columns by clicking headers"
echo "• Monitor real-time updates as you change parameters"
echo ""

echo "🔬 IEEE-738 Parameter Scenarios:"
echo ""
echo "Scenario 1: Hot Summer Day"
echo "• Ambient Temperature: 40°C"
echo "• Wind Speed: 2 m/s"
echo "• Sun Time: 14:00 (2 PM)"
echo "• Expected: Higher utilization due to heat"
echo ""

echo "Scenario 2: Windy Winter Day"
echo "• Ambient Temperature: 10°C"
echo "• Wind Speed: 15 m/s"
echo "• Sun Time: 10:00 (10 AM)"
echo "• Expected: Lower utilization due to cooling"
echo ""

echo "Scenario 3: High Altitude Location"
echo "• Elevation: 10,000 ft"
echo "• Ambient Temperature: 25°C"
echo "• Wind Speed: 5 m/s"
echo "• Expected: Different thermal characteristics"
echo ""

echo "🎯 Try These Exercises:"
echo "1. Increase ambient temperature and watch utilization rise"
echo "2. Add wind speed and observe cooling effects"
echo "3. Change sun time to see daily variations"
echo "4. Adjust warning thresholds to see status changes"
echo "5. Sort data tables by utilization to find critical lines"
echo ""

echo "📈 Understanding the Results:"
echo "• Utilization % = (Current Flow / Thermal Rating) × 100"
echo "• Good: < 80% utilization"
echo "• Warning: 80-100% utilization"
echo "• Overloaded: ≥ 100% utilization"
echo "• Margin = Rating - Current Flow"
echo ""

echo "🔧 Troubleshooting:"
echo "• If map doesn't load: Check browser console for errors"
echo "• If data doesn't update: Verify backend is running on port 8000"
echo "• If sliders don't work: Check browser JavaScript is enabled"
echo "• For API issues: Visit http://localhost:8000/docs"
echo ""

echo "📚 Additional Resources:"
echo "• API Documentation: http://localhost:8000/docs"
echo "• IEEE-738 Standard: IEEE Std 738-2012"
echo "• Project README: ./README.md"
echo ""

echo "✅ Ready to explore! Start the application and begin your analysis."
echo ""

# Check if the application is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "🎉 Backend is already running!"
    echo "🌐 Frontend should be available at: http://localhost:3000"
else
    echo "🚀 To start the application, run: ./start.sh"
fi

echo ""

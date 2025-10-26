import React, { useState, useEffect } from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { ParameterPanel } from "./components/ParameterPanel";
import { MapVisualization } from "./components/MapVisualization";
import { DataTable } from "./components/DataTable";
import { StatusSummary } from "./components/StatusSummary";
import axios from "axios";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
    background: {
      default: "#f5f5f5",
    },
  },
});

// API base URL - will proxy to backend
const API_BASE_URL = "";

function App() {
  const [parameters, setParameters] = useState({
    ambient_c: 35.0,
    wind_ms: 1.0,
    wind_angle_deg: 90.0,
    elevation_ft: 0.0,
    latitude_deg: 21.3,
    sun_time_hr: 12.0,
    emissivity: 0.5,
    absorptivity: 0.5,
    direction: "EastWest",
    atmosphere: "Clear",
    date_str: "12 Jun",
    warn_threshold: 80.0,
    bad_threshold: 100.0,
  });

  const [ratingsData, setRatingsData] = useState([]);
  const [stressData, setStressData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [ratingsResponse, stressResponse] = await Promise.all([axios.get(`${API_BASE_URL}/ratings`, { params: parameters }), axios.get(`${API_BASE_URL}/stress_summary`, { params: parameters })]);

      setRatingsData(ratingsResponse.data);
      setStressData(stressResponse.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch data");
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [parameters]);

  const handleParameterChange = (paramName, value) => {
    setParameters((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ mt: 2, mb: 2 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mb: 3 }}>
          Grid Criticality Analysis (IEEE-738)
        </Typography>

        <Grid container spacing={3}>
          {/* Parameter Panel */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, height: "fit-content" }}>
              <ParameterPanel parameters={parameters} onParameterChange={handleParameterChange} onRefresh={fetchData} loading={loading} />
            </Paper>
          </Grid>

          {/* Main Content */}
          <Grid item xs={12} md={9}>
            <Grid container spacing={3}>
              {/* Status Summary */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <StatusSummary stressData={stressData} loading={loading} error={error} />
                </Paper>
              </Grid>

              {/* Map Visualization */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <MapVisualization stressData={stressData} ratingsData={ratingsData} loading={loading} warnThreshold={parameters.warn_threshold} badThreshold={parameters.bad_threshold} />
                </Paper>
              </Grid>

              {/* Data Tables */}
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <DataTable stressData={stressData} ratingsData={ratingsData} loading={loading} />
                </Paper>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App;

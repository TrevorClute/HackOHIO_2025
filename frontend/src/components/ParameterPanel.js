import React from "react";
import { Box, Typography, Slider, FormControl, InputLabel, Select, MenuItem, Button, Divider, Card, CardContent, Grid } from "@mui/material";
import { Refresh } from "@mui/icons-material";

const ParameterPanel = ({ parameters, onParameterChange, onRefresh, loading }) => {
  const handleSliderChange = (paramName) => (event, newValue) => {
    onParameterChange(paramName, newValue);
  };

  const handleSelectChange = (paramName) => (event) => {
    onParameterChange(paramName, event.target.value);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" component="h2">
          IEEE-738 Parameters
        </Typography>
        <Button variant="outlined" startIcon={<Refresh />} onClick={onRefresh} disabled={loading} size="small">
          Refresh
        </Button>
      </Box>

      <Grid container spacing={2}>
        {/* Weather Parameters */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Weather Conditions
              </Typography>

              <Box mb={2}>
                <Typography gutterBottom>Ambient Temperature: {parameters.ambient_c}°C</Typography>
                <Slider
                  value={parameters.ambient_c}
                  onChange={handleSliderChange("ambient_c")}
                  min={-60}
                  max={80}
                  step={0.1}
                  marks={[
                    { value: -60, label: "-60°C" },
                    { value: 0, label: "0°C" },
                    { value: 35, label: "35°C" },
                    { value: 80, label: "80°C" },
                  ]}
                />
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Wind Speed: {parameters.wind_ms} m/s</Typography>
                <Slider
                  value={parameters.wind_ms}
                  onChange={handleSliderChange("wind_ms")}
                  min={0}
                  max={60}
                  step={0.1}
                  marks={[
                    { value: 0, label: "0 m/s" },
                    { value: 10, label: "10 m/s" },
                    { value: 30, label: "30 m/s" },
                    { value: 60, label: "60 m/s" },
                  ]}
                />
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Wind Angle: {parameters.wind_angle_deg}°</Typography>
                <Slider
                  value={parameters.wind_angle_deg}
                  onChange={handleSliderChange("wind_angle_deg")}
                  min={0}
                  max={90}
                  step={1}
                  marks={[
                    { value: 0, label: "0°" },
                    { value: 45, label: "45°" },
                    { value: 90, label: "90°" },
                  ]}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Environmental Parameters */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Environmental
              </Typography>

              <Box mb={2}>
                <Typography gutterBottom>Elevation: {parameters.elevation_ft} ft</Typography>
                <Slider
                  value={parameters.elevation_ft}
                  onChange={handleSliderChange("elevation_ft")}
                  min={0}
                  max={50000}
                  step={100}
                  marks={[
                    { value: 0, label: "0 ft" },
                    { value: 10000, label: "10k ft" },
                    { value: 25000, label: "25k ft" },
                    { value: 50000, label: "50k ft" },
                  ]}
                />
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Latitude: {parameters.latitude_deg}°</Typography>
                <Slider
                  value={parameters.latitude_deg}
                  onChange={handleSliderChange("latitude_deg")}
                  min={-90}
                  max={90}
                  step={0.1}
                  marks={[
                    { value: -90, label: "-90°" },
                    { value: 0, label: "0°" },
                    { value: 21.3, label: "21.3°" },
                    { value: 90, label: "90°" },
                  ]}
                />
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Sun Time: {parameters.sun_time_hr} hr</Typography>
                <Slider
                  value={parameters.sun_time_hr}
                  onChange={handleSliderChange("sun_time_hr")}
                  min={0}
                  max={24}
                  step={0.1}
                  marks={[
                    { value: 0, label: "0h" },
                    { value: 6, label: "6h" },
                    { value: 12, label: "12h" },
                    { value: 18, label: "18h" },
                    { value: 24, label: "24h" },
                  ]}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Material Properties */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Material Properties
              </Typography>

              <Box mb={2}>
                <Typography gutterBottom>Emissivity: {parameters.emissivity}</Typography>
                <Slider
                  value={parameters.emissivity}
                  onChange={handleSliderChange("emissivity")}
                  min={0}
                  max={1}
                  step={0.01}
                  marks={[
                    { value: 0, label: "0" },
                    { value: 0.5, label: "0.5" },
                    { value: 1, label: "1" },
                  ]}
                />
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Absorptivity: {parameters.absorptivity}</Typography>
                <Slider
                  value={parameters.absorptivity}
                  onChange={handleSliderChange("absorptivity")}
                  min={0}
                  max={1}
                  step={0.01}
                  marks={[
                    { value: 0, label: "0" },
                    { value: 0.5, label: "0.5" },
                    { value: 1, label: "1" },
                  ]}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Configuration */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Configuration
              </Typography>

              <Box mb={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Direction</InputLabel>
                  <Select value={parameters.direction} onChange={handleSelectChange("direction")} label="Direction">
                    <MenuItem value="EastWest">East-West</MenuItem>
                    <MenuItem value="NorthSouth">North-South</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box mb={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Atmosphere</InputLabel>
                  <Select value={parameters.atmosphere} onChange={handleSelectChange("atmosphere")} label="Atmosphere">
                    <MenuItem value="Clear">Clear</MenuItem>
                    <MenuItem value="Industrial">Industrial</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Warning Threshold: {parameters.warn_threshold}%</Typography>
                <Slider
                  value={parameters.warn_threshold}
                  onChange={handleSliderChange("warn_threshold")}
                  min={0}
                  max={100}
                  step={1}
                  marks={[
                    { value: 0, label: "0%" },
                    { value: 50, label: "50%" },
                    { value: 80, label: "80%" },
                    { value: 100, label: "100%" },
                  ]}
                />
              </Box>

              <Box mb={2}>
                <Typography gutterBottom>Bad Threshold: {parameters.bad_threshold}%</Typography>
                <Slider
                  value={parameters.bad_threshold}
                  onChange={handleSliderChange("bad_threshold")}
                  min={0}
                  max={100}
                  step={1}
                  marks={[
                    { value: 0, label: "0%" },
                    { value: 50, label: "50%" },
                    { value: 100, label: "100%" },
                  ]}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export { ParameterPanel };

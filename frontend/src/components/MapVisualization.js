import React, { useEffect, useRef, useState, useCallback } from "react";
import { MapContainer, TileLayer, Popup, CircleMarker, Polyline } from "react-leaflet";
import L from "leaflet";
import { Box, Typography, Chip, CircularProgress, Paper, Divider } from "@mui/material";
import "leaflet/dist/leaflet.css";

// Fix marker icons (works in CRA/Vite; adjust if using Next/ESM-only)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

const MapVisualization = ({ stressData = [], ratingsData, loading, warnThreshold = 80, badThreshold = 100 }) => {
  const mapRef = useRef(null);
  const [busData, setBusData] = useState(null);
  const [renderKey, setRenderKey] = useState(0);

  // Load bus data from GeoJSON
  useEffect(() => {
    const loadBusData = async () => {
      try {
        const response = await fetch("/data/oneline_buses.geojson");
        const geojson = await response.json();
        setBusData(geojson);
      } catch (error) {
        console.error("Error loading bus data:", error);
      }
    };
    loadBusData();
  }, []);

  // Force re-render when thresholds change
  useEffect(() => {
    setRenderKey((prev) => prev + 1);
  }, [warnThreshold, badThreshold]);

  const defaultCenter = [21.35, -157.82];

  const getBusCoordinates = (busId) => {
    if (!busData) return [21.33 + (busId % 10) * 0.003, -157.9 + (busId % 8) * 0.003];

    const busFeature = busData.features.find((feature) => feature?.properties?.BusNum === busId);
    if (busFeature) {
      const [lng, lat] = busFeature.geometry.coordinates;
      return [lat, lng]; // Leaflet expects [lat, lng]
    }
    // Fallback (kept on Oahu-ish area)
    return [21.33 + (busId % 10) * 0.003, -157.9 + (busId % 8) * 0.003];
  };

  const getBusInfo = (busId) => {
    if (!busData) return { name: `Bus ${busId}`, voltage: "Unknown" };
    const busFeature = busData.features.find((feature) => feature?.properties?.BusNum === busId);
    if (busFeature) {
      return {
        name: busFeature.properties.BusName,
        voltage: busFeature.properties.kV,
      };
    }
    return { name: `Bus ${busId}`, voltage: "Unknown" };
  };

  const getUtilizationColor = useCallback(
    (u) => {
      const utilization = Number.isFinite(u) ? Math.max(0, Math.min(100, u)) : 0;
      if (utilization >= badThreshold) return "#f44336"; // red
      if (utilization >= warnThreshold) return "#ff9800"; // orange
      return "#4caf50"; // green
    },
    [warnThreshold, badThreshold]
  );

  const getLineWeight = useCallback(() => 6, []);

  const createTransmissionLines = () =>
    (stressData || []).map((line) => {
      const bus0Coords = getBusCoordinates(line.bus0);
      const bus1Coords = getBusCoordinates(line.bus1);
      const utilization = line?.utilization_pct ?? 0;
      const color = getUtilizationColor(utilization);
      const weight = getLineWeight(utilization);
      const uniqueKey = `${line.line_id}-${utilization.toFixed(1)}-${warnThreshold}-${badThreshold}`;

      return (
        <Polyline key={uniqueKey} positions={[bus0Coords, bus1Coords]} color={color} weight={weight} opacity={0.9} pane="overlayPane" bubblingMouseEvents={false}>
          <Popup>
            <Box sx={{ minWidth: 200 }}>
              <Typography variant="h6" gutterBottom>
                Line: {line.line_id}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>From:</strong> {line.bus0_name} (Bus {line.bus0})
                <br />
                <strong>To:</strong> {line.bus1_name} (Bus {line.bus1})
                <br />
                <strong>Conductor:</strong> {line.conductor}
                <br />
                <strong>Voltage:</strong> {line.voltage_kv} kV
                <br />
                <strong>MOT:</strong> {line.mot_c}°C
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Chip
                  label={`${(line.utilization_pct ?? 0).toFixed(1)}% Utilization`}
                  color={(line.utilization_pct ?? 0) >= badThreshold ? "error" : (line.utilization_pct ?? 0) >= warnThreshold ? "warning" : "success"}
                  size="small"
                />
              </Box>
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Rating:</strong> {(line.rating_amps ?? 0).toFixed(0)} A ({(line.rating_mva ?? 0).toFixed(1)} MVA)
                <br />
                <strong>Flow:</strong> {(line.flow_amps ?? 0).toFixed(0)} A ({(line.flow_mva ?? 0).toFixed(1)} MVA)
                <br />
                <strong>Margin:</strong> {((line.rating_amps ?? 0) - (line.flow_amps ?? 0)).toFixed(0)} A
              </Typography>
            </Box>
          </Popup>
        </Polyline>
      );
    });

  const createBusMarkers = () => {
    const uniqueBuses = new Set();
    (stressData || []).forEach((l) => {
      uniqueBuses.add(l.bus0);
      uniqueBuses.add(l.bus1);
    });

    return Array.from(uniqueBuses).map((busId) => {
      const coords = getBusCoordinates(busId);
      const busInfo = getBusInfo(busId);
      const voltage = busInfo.voltage;
      const size = voltage >= 138 ? 12 : voltage >= 69 ? 10 : 8;
      const color = "#1976d2"; // single color for all buses

      return (
        <CircleMarker key={`bus-${busId}`} center={coords} radius={size} color={color} fillColor={color} fillOpacity={0.85} weight={2}>
          <Popup>
            <Box sx={{ minWidth: 150 }}>
              <Typography variant="h6" gutterBottom>
                {busInfo.name}
              </Typography>
              <Typography variant="body2">
                <strong>Bus ID:</strong> {busId}
                <br />
                <strong>Voltage:</strong> {voltage} kV
                <br />
                <strong>Coordinates:</strong> {coords[0].toFixed(4)}, {coords[1].toFixed(4)}
              </Typography>
            </Box>
          </Popup>
        </CircleMarker>
      );
    });
  };

  // Fit/bounds on data change
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !stressData?.length) return;

    const allCoords = [];
    stressData.forEach((line) => {
      allCoords.push(getBusCoordinates(line.bus0));
      allCoords.push(getBusCoordinates(line.bus1));
    });
    if (allCoords.length) {
      const bounds = L.latLngBounds(allCoords).pad(0.1);
      map.fitBounds(bounds, { padding: [30, 30] });
    }
    map.invalidateSize();
  }, [stressData, warnThreshold, badThreshold]);

  // Force redraw on threshold/data change (Huawei/WebView quirk)
  useEffect(() => {
    const map = mapRef.current;
    if (map && stressData?.length) {
      setTimeout(() => {
        map.invalidateSize();
        map.redraw?.();
        map.eachLayer((layer) => {
          if (layer?.redraw) layer.redraw();
        });
      }, 50);
    }
  }, [stressData, warnThreshold, badThreshold]);

  return (
    <Box>
      {/* MAP AREA */}
      <Box sx={{ height: 500, position: "relative", mb: 2 }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            position: "absolute",
            zIndex: 500,
            top: 8,
            left: 8,
          }}
        >
          <Typography variant="h6" sx={{ bgcolor: "background.paper", px: 1, borderRadius: 1 }}>
            Grid Line Status Map
          </Typography>
          {stressData?.length > 0 && <Chip label={`${stressData.length} lines`} size="small" color="primary" variant="outlined" />}
        </Box>

        {loading && (
          <Box
            sx={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              zIndex: 1000,
              backgroundColor: "rgba(255, 255, 255, 0.8)",
              borderRadius: 1,
              p: 2,
            }}
          >
            <CircularProgress />
            <Typography variant="body2" sx={{ mt: 1 }}>
              Loading data...
            </Typography>
          </Box>
        )}

        <MapContainer
          key={renderKey} // refresh when thresholds change
          whenCreated={(map) => {
            mapRef.current = map;
            setTimeout(() => map.invalidateSize(), 50);
          }}
          preferCanvas={true}
          center={defaultCenter}
          zoom={10}
          style={{ height: "100%", width: "100%" }}
          updateWhenIdle={false}
        >
          <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {createTransmissionLines()}
          {createBusMarkers()}
        </MapContainer>
      </Box>

      {/* LEGEND AREA (separate dedicated space) */}
      <Paper variant="outlined" sx={{ p: 2 }} role="region" aria-label="Map legend">
        <Typography variant="body2" gutterBottom>
          <strong>Legend:</strong>
        </Typography>

        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", alignItems: "center", mb: 1 }}>
          <Typography variant="body2" sx={{ mr: 1 }}>
            <strong>Transmission Lines:</strong>
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <div style={{ width: 20, height: 4, backgroundColor: "#4caf50", borderRadius: 2 }} />
            <Typography variant="body2">Good (&lt;{warnThreshold}%)</Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <div style={{ width: 20, height: 4, backgroundColor: "#ff9800", borderRadius: 2 }} />
            <Typography variant="body2">
              Warning ({warnThreshold}-{badThreshold - 1}%)
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <div style={{ width: 20, height: 4, backgroundColor: "#f44336", borderRadius: 2 }} />
            <Typography variant="body2">Overloaded (≥{badThreshold}%)</Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 1 }} />

        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", alignItems: "center" }}>
          <Typography variant="body2" sx={{ mr: 1 }}>
            <strong>Bus/Substations:</strong>
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#1976d2" }} />
            <Typography variant="body2">All buses (size varies by voltage)</Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export { MapVisualization };

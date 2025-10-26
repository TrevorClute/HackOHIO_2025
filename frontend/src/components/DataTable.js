import React, { useState } from "react";
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, Tabs, Tab, TableSortLabel, CircularProgress, Alert } from "@mui/material";
import { TrendingUp, TrendingDown } from "@mui/icons-material";

const DataTable = ({ stressData, ratingsData, loading }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [sortField, setSortField] = useState("utilization_pct");
  const [sortDirection, setSortDirection] = useState("desc");

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const getSortedData = (data) => {
    if (!data || data.length === 0) return [];

    return [...data].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      if (sortDirection === "asc") {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });
  };

  const getStatusChip = (status) => {
    const colorMap = {
      GOOD: "success",
      WARN: "warning",
      BAD: "error",
    };
    return <Chip label={status} color={colorMap[status] || "default"} size="small" />;
  };

  const getUtilizationTrend = (utilization) => {
    if (utilization >= 100) return <TrendingUp color="error" />;
    if (utilization >= 80) return <TrendingUp color="warning" />;
    return <TrendingDown color="success" />;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Loading data...
        </Typography>
      </Box>
    );
  }

  const sortedStressData = getSortedData(stressData);
  const sortedRatingsData = getSortedData(ratingsData);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Detailed Data Tables
      </Typography>

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
        <Tab label={`Stress Analysis (${stressData?.length || 0})`} />
        <Tab label={`Ratings Data (${ratingsData?.length || 0})`} />
      </Tabs>

      {activeTab === 0 && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel active={sortField === "line_id"} direction={sortField === "line_id" ? sortDirection : "asc"} onClick={() => handleSort("line_id")}>
                    Line ID
                  </TableSortLabel>
                </TableCell>
                <TableCell>From → To</TableCell>
                <TableCell>Conductor</TableCell>
                <TableCell>Voltage (kV)</TableCell>
                <TableCell>
                  <TableSortLabel active={sortField === "utilization_pct"} direction={sortField === "utilization_pct" ? sortDirection : "asc"} onClick={() => handleSort("utilization_pct")}>
                    Utilization %
                  </TableSortLabel>
                </TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Rating (A)</TableCell>
                <TableCell>Flow (A)</TableCell>
                <TableCell>Margin (A)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedStressData.map((line) => (
                <TableRow key={line.line_id} hover>
                  <TableCell>{line.line_id}</TableCell>
                  <TableCell>
                    {line.bus0_name} → {line.bus1_name}
                  </TableCell>
                  <TableCell>{line.conductor}</TableCell>
                  <TableCell>{line.voltage_kv}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {line.utilization_pct.toFixed(1)}%{getUtilizationTrend(line.utilization_pct)}
                    </Box>
                  </TableCell>
                  <TableCell>{getStatusChip(line.status)}</TableCell>
                  <TableCell>{line.rating_amps.toFixed(0)}</TableCell>
                  <TableCell>{line.flow_amps.toFixed(0)}</TableCell>
                  <TableCell>
                    <Typography color={line.ampacity_margin_a < 0 ? "error.main" : "text.primary"} variant="body2">
                      {line.ampacity_margin_a.toFixed(0)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel active={sortField === "line_id"} direction={sortField === "line_id" ? sortDirection : "asc"} onClick={() => handleSort("line_id")}>
                    Line ID
                  </TableSortLabel>
                </TableCell>
                <TableCell>From → To</TableCell>
                <TableCell>Conductor</TableCell>
                <TableCell>Voltage (kV)</TableCell>
                <TableCell>MOT (°C)</TableCell>
                <TableCell>
                  <TableSortLabel active={sortField === "rating_amps"} direction={sortField === "rating_amps" ? sortDirection : "asc"} onClick={() => handleSort("rating_amps")}>
                    Rating (A)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel active={sortField === "rating_mva"} direction={sortField === "rating_mva" ? sortDirection : "asc"} onClick={() => handleSort("rating_mva")}>
                    Rating (MVA)
                  </TableSortLabel>
                </TableCell>
                <TableCell>Static Rating (MVA)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedRatingsData.map((line) => (
                <TableRow key={line.line_id} hover>
                  <TableCell>{line.line_id}</TableCell>
                  <TableCell>
                    {line.bus0_name} → {line.bus1_name}
                  </TableCell>
                  <TableCell>{line.conductor}</TableCell>
                  <TableCell>{line.voltage_kv}</TableCell>
                  <TableCell>{line.mot_c}</TableCell>
                  <TableCell>{line.rating_amps.toFixed(0)}</TableCell>
                  <TableCell>{line.rating_mva.toFixed(1)}</TableCell>
                  <TableCell>{line.static_s_nom_mva ? line.static_s_nom_mva.toFixed(1) : "N/A"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {(!stressData || stressData.length === 0) && (!ratingsData || ratingsData.length === 0) && <Alert severity="info">No data available. Please check your parameters and try again.</Alert>}
    </Box>
  );
};

export { DataTable };

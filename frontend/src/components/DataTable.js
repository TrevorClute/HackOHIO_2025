import React, { useState, useMemo } from "react";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Tabs,
  Tab,
  TableSortLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import { TrendingUp, TrendingDown } from "@mui/icons-material";

const DataTable = ({ stressData = [], ratingsData = [], loading }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [sortField, setSortField] = useState("utilization_pct");
  const [sortDirection, setSortDirection] = useState("desc");

  // Natural sort for strings like "L1", "L12", "L3"
  const collator = useMemo(
    () => new Intl.Collator(undefined, { numeric: true, sensitivity: "base" }),
    []
  );

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const safeNum = (v) => (Number.isFinite(v) ? v : NaN);
  const fmt = (v, digits = 0) => (Number.isFinite(v) ? v.toFixed(digits) : "—");

  const compareValues = (aVal, bVal) => {
    // Both strings: use natural sort (handles L1, L12, L3)
    if (typeof aVal === "string" && typeof bVal === "string") {
      return collator.compare(aVal, bVal);
    }

    // Try numeric compare
    const an = Number(aVal);
    const bn = Number(bVal);
    const aIsNum = Number.isFinite(an);
    const bIsNum = Number.isFinite(bn);

    if (aIsNum && bIsNum) return an - bn;

    // Fallback: compare as strings
    return collator.compare(String(aVal ?? ""), String(bVal ?? ""));
  };

  const getSortedData = (data) => {
    if (!data || data.length === 0) return [];
    const sorted = [...data].sort((a, b) => {
      const aVal = a?.[sortField];
      const bVal = b?.[sortField];
      const cmp = compareValues(aVal, bVal);
      return sortDirection === "asc" ? cmp : -cmp;
    });
    return sorted;
  };

  const getStatusChip = (status) => {
    const colorMap = {
      GOOD: "success",
      WARN: "warning",
      BAD: "error",
    };
    return <Chip label={status ?? "—"} color={colorMap[status] || "default"} size="small" />;
  };

  const getUtilizationTrend = (utilization) => {
    const u = safeNum(utilization);
    if (!Number.isFinite(u)) return <TrendingDown color="success" />;
    if (u >= 100) return <TrendingUp color="error" />;
    if (u >= 80) return <TrendingUp color="warning" />;
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
                  <TableSortLabel
                    active={sortField === "line_id"}
                    direction={sortField === "line_id" ? sortDirection : "asc"}
                    onClick={() => handleSort("line_id")}
                  >
                    Line ID
                  </TableSortLabel>
                </TableCell>
                <TableCell>From → To</TableCell>
                <TableCell>Conductor</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "voltage_kv"}
                    direction={sortField === "voltage_kv" ? sortDirection : "asc"}
                    onClick={() => handleSort("voltage_kv")}
                  >
                    Voltage (kV)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "utilization_pct"}
                    direction={sortField === "utilization_pct" ? sortDirection : "asc"}
                    onClick={() => handleSort("utilization_pct")}
                  >
                    Utilization %
                  </TableSortLabel>
                </TableCell>
                <TableCell>Status</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "rating_amps"}
                    direction={sortField === "rating_amps" ? sortDirection : "asc"}
                    onClick={() => handleSort("rating_amps")}
                  >
                    Rating (A)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "flow_amps"}
                    direction={sortField === "flow_amps" ? sortDirection : "asc"}
                    onClick={() => handleSort("flow_amps")}
                  >
                    Flow (A)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "ampacity_margin_a"}
                    direction={sortField === "ampacity_margin_a" ? sortDirection : "asc"}
                    onClick={() => handleSort("ampacity_margin_a")}
                  >
                    Margin (A)
                  </TableSortLabel>
                </TableCell>
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
                  <TableCell>{fmt(line.voltage_kv, 0)}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {fmt(line.utilization_pct, 1)}%{getUtilizationTrend(line.utilization_pct)}
                    </Box>
                  </TableCell>
                  <TableCell>{getStatusChip(line.status)}</TableCell>
                  <TableCell>{fmt(line.rating_amps, 0)}</TableCell>
                  <TableCell>{fmt(line.flow_amps, 0)}</TableCell>
                  <TableCell>
                    <Typography color={safeNum(line.ampacity_margin_a) < 0 ? "error.main" : "text.primary"} variant="body2">
                      {fmt(line.ampacity_margin_a, 0)}
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
                  <TableSortLabel
                    active={sortField === "line_id"}
                    direction={sortField === "line_id" ? sortDirection : "asc"}
                    onClick={() => handleSort("line_id")}
                  >
                    Line ID
                  </TableSortLabel>
                </TableCell>
                <TableCell>From → To</TableCell>
                <TableCell>Conductor</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "voltage_kv"}
                    direction={sortField === "voltage_kv" ? sortDirection : "asc"}
                    onClick={() => handleSort("voltage_kv")}
                  >
                    Voltage (kV)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "mot_c"}
                    direction={sortField === "mot_c" ? sortDirection : "asc"}
                    onClick={() => handleSort("mot_c")}
                  >
                    MOT (°C)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "rating_amps"}
                    direction={sortField === "rating_amps" ? sortDirection : "asc"}
                    onClick={() => handleSort("rating_amps")}
                  >
                    Rating (A)
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === "rating_mva"}
                    direction={sortField === "rating_mva" ? sortDirection : "asc"}
                    onClick={() => handleSort("rating_mva")}
                  >
                    Rating (MVA)
                  </TableSortLabel>
                </TableCell>
                <TableCell>Static Rating (MVA)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {getSortedData(ratingsData).map((line) => (
                <TableRow key={line.line_id} hover>
                  <TableCell>{line.line_id}</TableCell>
                  <TableCell>
                    {line.bus0_name} → {line.bus1_name}
                  </TableCell>
                  <TableCell>{line.conductor}</TableCell>
                  <TableCell>{fmt(line.voltage_kv, 0)}</TableCell>
                  <TableCell>{fmt(line.mot_c, 1)}</TableCell>
                  <TableCell>{fmt(line.rating_amps, 0)}</TableCell>
                  <TableCell>{fmt(line.rating_mva, 1)}</TableCell>
                  <TableCell>{Number.isFinite(line.static_s_nom_mva) ? fmt(line.static_s_nom_mva, 1) : "N/A"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {(!stressData || stressData.length === 0) &&
        (!ratingsData || ratingsData.length === 0) && (
          <Alert severity="info">No data available. Please check your parameters and try again.</Alert>
        )}
    </Box>
  );
};

export { DataTable };


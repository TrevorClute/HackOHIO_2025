import React from "react";
import { Box, Typography, Grid, Card, CardContent, Chip, LinearProgress, Alert } from "@mui/material";
import { CheckCircle, Warning, Error, TrendingUp, Power } from "@mui/icons-material";

const StatusSummary = ({ stressData, loading, error }) => {
  if (loading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          System Status Summary
        </Typography>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 1 }}>
          Loading status data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          System Status Summary
        </Typography>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!stressData || stressData.length === 0) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          System Status Summary
        </Typography>
        <Alert severity="info">No data available. Please check your parameters and try again.</Alert>
      </Box>
    );
  }

  // Calculate statistics
  const totalLines = stressData.length;
  const goodLines = stressData.filter((line) => line.status === "GOOD").length;
  const warnLines = stressData.filter((line) => line.status === "WARN").length;
  const badLines = stressData.filter((line) => line.status === "BAD").length;

  const avgUtilization = stressData.reduce((sum, line) => sum + line.utilization_pct, 0) / totalLines;
  const maxUtilization = Math.max(...stressData.map((line) => line.utilization_pct));
  const minUtilization = Math.min(...stressData.map((line) => line.utilization_pct));

  const totalRatingMVA = stressData.reduce((sum, line) => sum + line.rating_mva, 0);
  const totalFlowMVA = stressData.reduce((sum, line) => sum + line.flow_mva, 0);
  const systemUtilization = (totalFlowMVA / totalRatingMVA) * 100;

  const getOverallStatus = () => {
    if (badLines > 0) return { status: "CRITICAL", color: "error", icon: <Error /> };
    if (warnLines > 0) return { status: "WARNING", color: "warning", icon: <Warning /> };
    return { status: "HEALTHY", color: "success", icon: <CheckCircle /> };
  };

  const overallStatus = getOverallStatus();

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        System Status Summary
      </Typography>

      <Grid container spacing={2}>
        {/* Overall Status */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                {overallStatus.icon}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  {overallStatus.status}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Overall System Health
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Line Status Breakdown */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Line Status
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Chip label="Good" color="success" size="small" />
                  <Typography variant="body2">{goodLines}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Chip label="Warning" color="warning" size="small" />
                  <Typography variant="body2">{warnLines}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Chip label="Overloaded" color="error" size="small" />
                  <Typography variant="body2">{badLines}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">
                    <strong>Total:</strong>
                  </Typography>
                  <Typography variant="body2">
                    <strong>{totalLines}</strong>
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Utilization Statistics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Utilization Stats
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Average:</Typography>
                  <Typography variant="body2">{avgUtilization.toFixed(1)}%</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Maximum:</Typography>
                  <Typography variant="body2">{maxUtilization.toFixed(1)}%</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Minimum:</Typography>
                  <Typography variant="body2">{minUtilization.toFixed(1)}%</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">System:</Typography>
                  <Typography variant="body2">{systemUtilization.toFixed(1)}%</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Power Summary */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Power Summary
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Total Rating:</Typography>
                  <Typography variant="body2">{totalRatingMVA.toFixed(1)} MVA</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Total Flow:</Typography>
                  <Typography variant="body2">{totalFlowMVA.toFixed(1)} MVA</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Available:</Typography>
                  <Typography variant="body2">{(totalRatingMVA - totalFlowMVA).toFixed(1)} MVA</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Margin:</Typography>
                  <Typography variant="body2">{(((totalRatingMVA - totalFlowMVA) / totalRatingMVA) * 100).toFixed(1)}%</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export { StatusSummary };

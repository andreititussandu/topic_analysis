import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  CircularProgress, 
  Alert, 
  Card, 
  CardContent,
  Grid,
  Box
} from '@mui/material';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { getAnalytics } from '../../services/api';
import './Analytics.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

const Analytics = ({ userId }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, [userId]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getAnalytics(userId);
      setAnalytics(data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load analytics. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Format data for charts
  const formatTopicDistribution = () => {
    if (!analytics || !analytics.topic_distribution) return [];
    
    return analytics.topic_distribution.map(item => ({
      name: item._id,
      value: item.count
    }));
  };

  const formatDailyActivity = () => {
    if (!analytics || !analytics.daily_activity) return [];
    
    return analytics.daily_activity.map(item => ({
      date: item._id,
      predictions: item.count
    }));
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
      >
        {`${name} (${(percent * 100).toFixed(0)}%)`}
      </text>
    );
  };

  return (
    <Container maxWidth="md" className="analytics-container">
      <Card>
        <CardContent>
          <Typography variant="h4" component="h2" gutterBottom>
            Analytics Dashboard
          </Typography>
          
          {loading ? (
            <Grid container justifyContent="center" sx={{ py: 4 }}>
              <CircularProgress />
            </Grid>
          ) : error ? (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          ) : !analytics ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              No analytics data available yet. Try predicting some topics first!
            </Alert>
          ) : (
            <Grid container spacing={4}>
              {/* Topic Distribution */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Topic Distribution
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={formatTopicDistribution()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={renderCustomizedLabel}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {formatTopicDistribution().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </Grid>
              
              {/* Daily Activity */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Daily Activity (Last 7 Days)
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={formatDailyActivity()}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="predictions" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default Analytics;

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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getAnalytics(userId);
      setAnalytics(data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Nu s-a putut încărca analiza. Vă rugăm să încercați mai târziu.');
    } finally {
      setLoading(false);
    }
  };

  // Format data for charts
  const formatTopicDistribution = () => {
    if (!analytics || !analytics.topic_distribution) return [];

    const total = analytics.topic_distribution.reduce((sum, item) => sum + item.count, 0);
    
    return analytics.topic_distribution.map(item => ({
      name: item._id,
      value: item.count,
      percentage: ((item.count / total) * 100).toFixed(0)
    }));
  };

  const formatDailyActivity = () => {
    if (!analytics || !analytics.daily_activity) return [];
    
    return analytics.daily_activity.map(item => ({
      date: item._id,
      predictions: item.count
    }));
  };

  const renderCustomizedLabel = () => {
    return null;
  };

  return (
    <Container maxWidth="md" className="analytics-container">
      <Card>
        <CardContent>
          <Typography variant="h4" component="h2" gutterBottom>
            Tablou de Bord Analitic
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
              Nu există încă date analitice disponibile. Încercați mai întâi să preziceți câteva topicuri!
            </Alert>
          ) : (
            <Grid container spacing={4}>
              {/* Topic Distribution */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Distribuția Topicurilor
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={formatTopicDistribution()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={null}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {formatTopicDistribution().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend 
                        formatter={(value, entry, index) => {
                          const items = formatTopicDistribution();
                          return items[index] ? `${value} (${items[index].percentage}%)` : value;
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </Grid>
              
              {/* Daily Activity */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Activitate Zilnică (Ultimele 7 Zile)
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

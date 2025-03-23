import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Paper, 
  Tabs, 
  Tab, 
  ThemeProvider, 
  CssBaseline,
  AppBar,
  useMediaQuery
} from '@mui/material';
import { v4 as uuidv4 } from 'uuid';
import './assets/styles/App.css';
import theme from './theme';
import Header from './components/Header/Header';
import PredictTopic from './components/PredictTopic/PredictTopic';
import BatchPredict from './components/BatchPredict/BatchPredict';
import History from './components/History/History';
import Analytics from './components/Analytics/Analytics';

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [userId, setUserId] = useState('');
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    // Get or create user ID
    let storedUserId = localStorage.getItem('userId');
    if (!storedUserId) {
      storedUserId = uuidv4();
      localStorage.setItem('userId', storedUserId);
    }
    setUserId(storedUserId);
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <Header />
        
        <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
          <AppBar 
            position="static" 
            color="default" 
            elevation={0}
            sx={{ 
              borderRadius: 3,
              overflow: 'hidden',
              mb: 4,
              backgroundColor: 'background.paper'
            }}
          >
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              variant={isMobile ? "scrollable" : "fullWidth"}
              scrollButtons={isMobile ? "auto" : false}
              indicatorColor="primary"
              textColor="primary"
              aria-label="navigation tabs"
              sx={{ 
                '& .MuiTab-root': { 
                  py: 2,
                  fontSize: isMobile ? '0.8rem' : '0.9rem'
                }
              }}
            >
              <Tab label="Predict Topic" />
              <Tab label="Batch Predict" />
              <Tab label="History" />
              <Tab label="Analytics" />
            </Tabs>
          </AppBar>

          <Box sx={{ 
            p: { xs: 0, sm: 2 },
            borderRadius: 3,
            backgroundColor: 'transparent'
          }}>
            {tabValue === 0 && <PredictTopic userId={userId} />}
            {tabValue === 1 && <BatchPredict userId={userId} />}
            {tabValue === 2 && <History userId={userId} />}
            {tabValue === 3 && <Analytics userId={userId} />}
          </Box>
        </Container>
      </div>
    </ThemeProvider>
  );
}

export default App;

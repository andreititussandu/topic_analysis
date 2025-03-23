import React, { useState } from 'react';
import { 
  Container, 
  TextField,
  Button, 
  Typography, 
  CircularProgress, 
  Alert, 
  Card, 
  CardContent,
  Grid,
  Box,
  Snackbar,
  Paper,
  Chip,
  Fade,
  InputAdornment,
  IconButton,
  ButtonGroup
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import DownloadIcon from '@mui/icons-material/Download';
import ReactWordcloud from 'react-wordcloud';
import { predictTopic, saveContent } from '../../services/api';
import './PredictTopic.css';

const PredictTopic = ({ userId }) => {
  const [url, setUrl] = useState('');
  const [predictedTopic, setPredictedTopic] = useState('');
  const [wordFrequencies, setWordFrequencies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [error, setError] = useState('');
  const [fromCache, setFromCache] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const handleInputChange = (e) => {
    setUrl(e.target.value);
  };

  const handleClearInput = () => {
    setUrl('');
    setPredictedTopic('');
    setWordFrequencies([]);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPredictedTopic('');
    setWordFrequencies([]);
    console.log('Submitting URL:', url);

    try {
      const data = await predictTopic(url, userId);
      console.log('Response received:', data);
      setPredictedTopic(data.predicted_topic);
      setFromCache(data.from_cache || false);
      
      // Transform word frequencies for the word cloud
      if (data.word_frequencies) {
        const words = Object.entries(data.word_frequencies).map(([text, value]) => ({
          text,
          value
        }));
        setWordFrequencies(words);
      }
    } catch (err) {
      console.error('Error in prediction:', err);
      if (err.response) {
        if (err.response.status === 400) {
          setError('Invalid URL provided. Please check the URL and try again.');
        } else if (err.response.status === 500) {
          setError('Server error occurred while processing the URL. Please try again later.');
        } else {
          setError(`Unexpected error: ${err.response.data}`);
        }
      } else if (err.request) {
        setError('No response received from the server. Please check your network connection and try again.');
      } else {
        setError(`Error in request: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadContent = async () => {
    if (!url) {
      showSnackbar('Please enter a URL first', 'warning');
      return;
    }

    setDownloadLoading(true);
    try {
      await saveContent(url);
      showSnackbar('Content downloaded successfully', 'success');
    } catch (err) {
      console.error('Error downloading content:', err);
      showSnackbar('Failed to download content. Please try again.', 'error');
    } finally {
      setDownloadLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  // Word cloud options
  const options = {
    colors: ['#3f51b5', '#757de8', '#002984', '#f50057', '#ff4081', '#c51162'],
    enableTooltip: true,
    deterministic: false,
    fontFamily: 'Poppins, sans-serif',
    fontSizes: [15, 60],
    fontStyle: 'normal',
    fontWeight: 'normal',
    padding: 2,
    rotations: 3,
    rotationAngles: [0, 90],
    scale: 'sqrt',
    spiral: 'archimedean',
    transitionDuration: 1000
  };

  return (
    <Container maxWidth="md" className="predict-topic-container">
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card 
            elevation={0}
            sx={{ 
              borderRadius: 3,
              overflow: 'hidden',
              border: '1px solid rgba(0, 0, 0, 0.08)'
            }}
          >
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography 
                variant="h4" 
                component="h2" 
                gutterBottom
                sx={{ 
                  fontWeight: 600,
                  mb: 3,
                  color: 'primary.main'
                }}
              >
                Predict Topic from URL
              </Typography>
              
              <Paper
                elevation={0}
                sx={{
                  p: 1,
                  mb: 3,
                  backgroundColor: 'rgba(63, 81, 181, 0.05)',
                  borderRadius: 2,
                  border: '1px solid rgba(63, 81, 181, 0.1)'
                }}
              >
                <Typography variant="body2" color="textSecondary">
                  Enter any webpage URL to analyze its content and predict the topic. 
                  Our AI model will process the text and determine the most likely subject matter.
                </Typography>
              </Paper>
              
              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Enter URL"
                  variant="outlined"
                  value={url}
                  onChange={handleInputChange}
                  required
                  margin="normal"
                  placeholder="https://example.com/article"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon color="primary" />
                      </InputAdornment>
                    ),
                    endAdornment: url && (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="clear input"
                          onClick={handleClearInput}
                          edge="end"
                        >
                          <ClearIcon />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  sx={{ mb: 2 }}
                />
                <ButtonGroup fullWidth variant="contained" size="large" sx={{ py: 0 }}>
                  <Button 
                    type="submit" 
                    color="primary" 
                    disabled={loading} 
                    sx={{ 
                      py: 1.5,
                      fontWeight: 600,
                      flex: 3
                    }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Predict Topic'}
                  </Button>
                  <Button
                    color="secondary"
                    onClick={handleDownloadContent}
                    disabled={downloadLoading}
                    sx={{
                      py: 1.5,
                      fontWeight: 600,
                      flex: 1
                    }}
                    startIcon={downloadLoading ? <CircularProgress size={20} /> : <DownloadIcon />}
                  >
                    {downloadLoading ? '' : 'Download'}
                  </Button>
                </ButtonGroup>
              </form>
              
              {predictedTopic && (
                <Fade in={!!predictedTopic}>
                  <Box mt={3}>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 3,
                        borderRadius: 2,
                        backgroundColor: 'rgba(63, 81, 181, 0.08)',
                        border: '1px solid rgba(63, 81, 181, 0.2)'
                      }}
                    >
                      <Typography variant="h6" gutterBottom>
                        Predicted Topic:
                      </Typography>
                      <Box 
                        sx={{ 
                          display: 'flex',
                          alignItems: 'center',
                          flexWrap: 'wrap'
                        }}
                      >
                        <Chip
                          label={predictedTopic}
                          color="primary"
                          sx={{ 
                            fontWeight: 600,
                            fontSize: '1.1rem',
                            py: 2.5,
                            mr: 1
                          }}
                        />
                        {fromCache && (
                          <Chip
                            label="Cached Result"
                            color="secondary"
                            size="small"
                            variant="outlined"
                            sx={{ mt: { xs: 1, sm: 0 } }}
                          />
                        )}
                      </Box>
                    </Paper>
                  </Box>
                </Fade>
              )}
              
              {error && (
                <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {wordFrequencies.length > 0 && (
          <Grid item xs={12}>
            <Card 
              elevation={0}
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                border: '1px solid rgba(0, 0, 0, 0.08)',
                mt: 2
              }}
            >
              <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                <Typography 
                  variant="h5" 
                  component="h3" 
                  gutterBottom
                  sx={{ fontWeight: 600 }}
                >
                  Word Cloud
                </Typography>
                <Typography 
                  variant="body2" 
                  color="textSecondary"
                  sx={{ mb: 2 }}
                >
                  Visual representation of the most frequent words in the content
                </Typography>
                <Box 
                  sx={{ 
                    height: 400, 
                    width: '100%',
                    border: '1px solid rgba(0, 0, 0, 0.05)',
                    borderRadius: 2,
                    p: 2
                  }}
                >
                  <ReactWordcloud words={wordFrequencies} options={options} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbarSeverity} 
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PredictTopic;

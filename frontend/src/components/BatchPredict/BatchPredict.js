import React, { useState } from 'react';
import { 
  Container, 
  Button, 
  Typography, 
  CircularProgress, 
  Alert, 
  Card, 
  CardContent,
  Grid,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Tooltip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import InfoIcon from '@mui/icons-material/Info';
import { batchPredictTopics } from '../../services/api';
import './BatchPredict.css';

const BatchPredict = ({ userId }) => {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);
  const [groupedResults, setGroupedResults] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/plain') {
        setError('Please upload a text file (.txt)');
        setFile(null);
        setFileName('');
        return;
      }
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);
    setGroupedResults(null);

    try {
      const data = await batchPredictTopics(file, userId);
      console.log('Batch prediction results:', data);
      setResults(data.results);
      setGroupedResults(data.grouped_results);
    } catch (err) {
      console.error('Error in batch prediction:', err);
      if (err.response) {
        setError(`Server error: ${err.response.data}`);
      } else if (err.request) {
        setError('No response received from the server. Please check your network connection and try again.');
      } else {
        setError(`Error in request: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" className="batch-predict-container">
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h4" component="h2" gutterBottom>
                Batch Predict Topics
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="body1" sx={{ mr: 1 }}>
                  Process multiple URLs at once by uploading a text file
                </Typography>
                <Tooltip title="Create a simple text file with one URL per line" arrow>
                  <InfoIcon color="primary" fontSize="small" />
                </Tooltip>
              </Box>
              
              <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'rgba(0, 0, 0, 0.02)' }}>
                <Typography variant="body2" color="textSecondary">
                  <strong>How it works:</strong>
                  <ol style={{ marginTop: '8px', paddingLeft: '20px' }}>
                    <li>Create a text file (.txt) with one URL per line</li>
                    <li>Upload the file using the button below</li>
                    <li>The system will process each URL and group them by topic</li>
                    <li>Results are automatically saved to your history</li>
                  </ol>
                </Typography>
              </Paper>
              
              <form onSubmit={handleSubmit}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                  <input
                    accept=".txt"
                    style={{ display: 'none' }}
                    id="file-upload"
                    type="file"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="file-upload">
                    <Button 
                      variant="contained" 
                      component="span"
                      startIcon={<UploadFileIcon />}
                      sx={{ mb: 1 }}
                    >
                      Select File
                    </Button>
                  </label>
                  {fileName && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Selected file: <strong>{fileName}</strong>
                    </Typography>
                  )}
                </Box>
                
                <Button 
                  type="submit" 
                  variant="contained" 
                  color="primary" 
                  disabled={loading || !file}
                  fullWidth
                >
                  {loading ? <CircularProgress size={24} /> : 'Process URLs'}
                </Button>
              </form>
              
              {error && (
                <Alert severity="error" className="error" style={{ marginTop: '20px' }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {groupedResults && Object.keys(groupedResults).length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h3" gutterBottom>
                  Results Grouped by Topic
                </Typography>
                
                {Object.entries(groupedResults).map(([topic, urls]) => (
                  <Accordion key={topic}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="h6">
                        {topic} <Chip label={urls.length} size="small" color="primary" />
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <List dense>
                        {urls.map((url, index) => (
                          <React.Fragment key={index}>
                            <ListItem>
                              <ListItemText 
                                primary={url} 
                                primaryTypographyProps={{ 
                                  style: { 
                                    wordBreak: 'break-all',
                                    fontSize: '0.9rem' 
                                  } 
                                }}
                              />
                            </ListItem>
                            {index < urls.length - 1 && <Divider />}
                          </React.Fragment>
                        ))}
                      </List>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </CardContent>
            </Card>
          </Grid>
        )}
        
        {results && results.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="h3" gutterBottom>
                  All Results
                </Typography>
                <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <List dense>
                    {results.map((result, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemText
                            primary={result.url}
                            secondary={
                              result.error 
                                ? `Error: ${result.error}` 
                                : `Topic: ${result.predicted_topic} ${result.from_cache ? '(cached)' : ''}`
                            }
                            primaryTypographyProps={{ 
                              style: { 
                                wordBreak: 'break-all',
                                fontSize: '0.9rem' 
                              } 
                            }}
                            secondaryTypographyProps={{ 
                              color: result.error ? 'error' : 'textSecondary' 
                            }}
                          />
                        </ListItem>
                        {index < results.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default BatchPredict;

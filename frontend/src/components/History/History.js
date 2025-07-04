import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  CircularProgress, 
  Alert, 
  Card, 
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Chip,
  IconButton,
  Tooltip,
  TablePagination,
  TextField,
  InputAdornment,
  Checkbox,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteIcon from '@mui/icons-material/Delete';
import { getHistory, retrainModel, deleteHistoryEntry } from '../../services/api';
import './History.css';

const History = ({ userId }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUrls, setSelectedUrls] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [retrainingLoading, setRetrainingLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [entryToDelete, setEntryToDelete] = useState(null);

  useEffect(() => {
    fetchHistory();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getHistory(userId);
      setHistory(data);
    } catch (err) {
      console.error('Error fetching history:', err);
      setError('Nu s-a putut încărca istoricul. Vă rugăm să încercați mai târziu.');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  const formatDate = (dateString) => {
    const options = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const handleCheckboxChange = (url) => {
    setSelectedUrls(prevSelected => {
      if (prevSelected.includes(url)) {
        return prevSelected.filter(item => item !== url);
      } else {
        return [...prevSelected, url];
      }
    });
  };

  const handleOpenRetrainDialog = () => {
    if (selectedUrls.length === 0) {
      showSnackbar('Vă rugăm să selectați cel puțin un URL pentru reantrenare', 'warning');
      return;
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const handleRetrainModel = async () => {
    setRetrainingLoading(true);
    try {
      const result = await retrainModel(selectedUrls, userId);
      if (result.success) {
        showSnackbar(result.message, 'success');
        setSelectedUrls([]);
      } else {
        showSnackbar(result.message || 'Eroare la reantrenarea modelului', 'error');
      }
    } catch (err) {
      console.error('Error retraining model:', err);
      showSnackbar('Nu s-a putut reantrena modelul. Vă rugăm să încercați mai târziu.', 'error');
    } finally {
      setRetrainingLoading(false);
      setDialogOpen(false);
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

  const handleOpenDeleteDialog = (entry) => {
    setEntryToDelete(entry);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setEntryToDelete(null);
  };

  const handleDeleteEntry = async () => {
    if (!entryToDelete) return;
    
    try {
      const result = await deleteHistoryEntry(entryToDelete._id, userId);
      if (result.success) {
        showSnackbar('Intrarea a fost ștearsă cu succes', 'success');
        // Actualizează lista de istoric după ștergere
        fetchHistory();
      } else {
        showSnackbar(result.message || 'Eroare la ștergerea intrării', 'error');
      }
    } catch (err) {
      console.error('Error deleting history entry:', err);
      showSnackbar('Nu s-a putut șterge intrarea. Vă rugăm să încercați mai târziu.', 'error');
    } finally {
      handleCloseDeleteDialog();
    }
  };

  const filteredHistory = history.filter(item => 
    item.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.prediction.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container maxWidth="md" className="history-container">
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
            Istoric Predicții
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
              Vizualizați predicțiile și rezultatele URL-urilor anterioare. Selectați URL-uri pentru a reantrena modelul și a îmbunătăți acuratețea predicțiilor.
            </Typography>
          </Paper>
          
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 2,
              mb: 3
            }}
          >
            <TextField
              variant="outlined"
              placeholder="Caută după URL sau topic..."
              value={searchTerm}
              onChange={handleSearchChange}
              sx={{ flexGrow: 1 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="primary" />
                  </InputAdornment>
                ),
              }}
            />
            <Button
              variant="contained"
              color="secondary"
              startIcon={<RefreshIcon />}
              onClick={handleOpenRetrainDialog}
              disabled={selectedUrls.length === 0}
            >
              Reantrenează Model
            </Button>
          </Box>
          
          {loading ? (
            <Box display="flex" justifyContent="center" my={4}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          ) : history.length === 0 ? (
            <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
              Nu există încă istoric de predicții. Încercați mai întâi să preziceți câteva topicuri!
            </Alert>
          ) : (
            <>
              <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 2, border: '1px solid rgba(0, 0, 0, 0.05)' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Tooltip title="Selectați pentru reantrenare">
                          <span>
                            <Checkbox 
                              indeterminate={selectedUrls.length > 0 && selectedUrls.length < filteredHistory.length}
                              checked={filteredHistory.length > 0 && selectedUrls.length === filteredHistory.length}
                              onChange={() => {
                                if (selectedUrls.length === filteredHistory.length) {
                                  setSelectedUrls([]);
                                } else {
                                  setSelectedUrls(filteredHistory.map(item => item.url));
                                }
                              }}
                            />
                          </span>
                        </Tooltip>
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>URL</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Topic</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Dată</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Acțiune</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredHistory
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((item, index) => (
                        <TableRow key={index} hover>
                          <TableCell padding="checkbox">
                            <Checkbox
                              checked={selectedUrls.includes(item.url)}
                              onChange={() => handleCheckboxChange(item.url)}
                            />
                          </TableCell>
                          <TableCell 
                            sx={{ 
                              maxWidth: '250px',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {item.url}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={item.prediction} 
                              color="primary" 
                              variant="outlined"
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{formatDate(item.timestamp)}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="Deschide URL">
                                <IconButton 
                                  size="small" 
                                  color="primary"
                                  onClick={() => window.open(item.url, '_blank')}
                                >
                                  <OpenInNewIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Șterge intrare">
                                <IconButton 
                                  size="small" 
                                  color="error"
                                  onClick={() => handleOpenDeleteDialog(item)}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <TablePagination
                rowsPerPageOptions={[5, 10, 25]}
                component="div"
                count={filteredHistory.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* Reantrenare model */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>Reantrenare Model</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Sunteți sigur că doriți să reantrenați modelul cu {selectedUrls.length} URL-uri selectate? Acest proces poate dura câteva minute.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Anulează
          </Button>
          <Button 
            onClick={handleRetrainModel} 
            color="primary" 
            variant="contained"
            disabled={retrainingLoading}
            startIcon={retrainingLoading && <CircularProgress size={20} />}
          >
            {retrainingLoading ? 'Se procesează...' : 'Reantrenează'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirmare ștergere</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Sunteți sigur că doriți să ștergeți această intrare din istoric? Această acțiune nu poate fi anulată.
            {entryToDelete && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid rgba(0, 0, 0, 0.12)' }}>
                <Typography variant="subtitle2" gutterBottom>URL:</Typography>
                <Typography variant="body2" sx={{ wordBreak: 'break-all', mb: 1 }}>
                  {entryToDelete.url}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>Topic:</Typography>
                <Chip 
                  label={entryToDelete.prediction} 
                  color="primary" 
                  variant="outlined"
                  size="small"
                  sx={{ mb: 1 }}
                />
              </Box>
            )}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Anulează
          </Button>
          <Button 
            onClick={handleDeleteEntry} 
            color="error" 
            variant="contained"
          >
            Șterge
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notificari */}
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

export default History;

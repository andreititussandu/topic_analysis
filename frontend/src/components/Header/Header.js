import React from 'react';
import { AppBar, Toolbar, Typography, Box, Container, useTheme } from '@mui/material';
import LanguageIcon from '@mui/icons-material/Language';

const Header = () => {
  const theme = useTheme();
  
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.primary.light} 90%)`,
        mb: 4
      }}
    >
      <Container>
        <Toolbar sx={{ py: 1 }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              color: 'white'
            }}
          >
            <LanguageIcon sx={{ fontSize: 36, mr: 2 }} />
            <Typography 
              variant="h5" 
              component="h1" 
              sx={{ 
                fontWeight: 700,
                letterSpacing: 0.5,
                flexGrow: 1
              }}
            >
              Topic Analyzer
            </Typography>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;

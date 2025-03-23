import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box mt={5} py={3} textAlign="center" bgcolor="#f5f5f5">
      <Typography variant="body2" color="textSecondary">
        © 2024 Web Topic Modeling. All rights reserved.
      </Typography>
      <Typography variant="body2">
        <Link href="#" color="inherit">
          Privacy Policy
        </Link>
        {' | '}
        <Link href="#" color="inherit">
          Terms of Service
        </Link>
      </Typography>
    </Box>
  );
};

export default Footer;

import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#ec489a',
      light: '#f472b6',
      dark: '#db2777',
    },
    background: {
      default: '#0a0a0a',
      paper: '#141414',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a3a3a3',
    },
    error: {
      main: '#ef4444',
    },
    success: {
      main: '#22c55e',
    },
    warning: {
      main: '#f59e0b',
    },
  },
  typography: {
    fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: '4rem',
      fontWeight: 700,
      background: 'linear-gradient(135deg, #6366f1 0%, #ec489a 100%)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      color: 'transparent',
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          padding: '10px 24px',
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

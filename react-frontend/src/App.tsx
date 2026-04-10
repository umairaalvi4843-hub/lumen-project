import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  CssBaseline, Container, Box, Typography, AppBar, Toolbar, 
  Chip, LinearProgress, Alert, Paper, Card, CardContent, 
  Button, CircularProgress, Grid 
} from '@mui/material';
import { Analytics, Timeline, Psychology, VolumeUp, Warning, CloudUpload } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import axios from 'axios';

const darkTheme = createTheme({
  palette: { mode: 'dark', primary: { main: '#6366f1' }, secondary: { main: '#ec489a' }, background: { default: '#0a0a0a', paper: '#141414' } },
});

const API_BASE = 'http://localhost:8081/api/analysis';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const pollStatus = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE}/status/${id}`);
        const currentStatus = response.data.status;
        setStatus(currentStatus);

        if (currentStatus === 'COMPLETED') {
          const res = await axios.get(`${API_BASE}/results/${id}`);
          if (res.data && !res.data.error) {
             clearInterval(interval);
             setResults(res.data);
             toast.success('Analysis Complete');
             setUploading(false);
          } else {
             setStatus("SYNCING_DISK...");
          }
        } else if (currentStatus === 'FAILED') {
          clearInterval(interval);
          setError("Analysis pipeline failed.");
          setUploading(false);
        }
      } catch (err: any) {
         if (err.response?.status !== 404) {
            clearInterval(interval);
            setError("Polling error.");
            setUploading(false);
         }
      }
    }, 2000);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true); setError(null); setResults(null); setStatus('UPLOADING');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_BASE}/upload`, formData);
      pollStatus(response.data.jobId);
    } catch (err) {
      setError('Upload failed.'); setUploading(false);
    }
  };

  const StatCard = ({ title, value, icon, color, delay }: any) => (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }} style={{ height: '100%' }}>
      <Card sx={{ bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 3, border: '1px solid rgba(99,102,241,0.2)', height: '100%' }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>{title}</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color }}>{value ?? 0}</Typography>
            </Box>
            <Box sx={{ p: 1, bgcolor: `${color}15`, borderRadius: 2 }}>{icon}</Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline /><Toaster position="bottom-center" />
      <AppBar position="static" elevation={0} sx={{ borderBottom: '1px solid #333', bgcolor: '#141414' }}>
        <Toolbar><Analytics sx={{ mr: 1, color: '#6366f1' }} /><Typography variant="h6" sx={{ fontWeight: 800 }}>LUMEN AI</Typography></Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 6 }}>
        <AnimatePresence mode="wait">
          {!uploading && !results ? (
            <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Paper sx={{ p: 8, textAlign: 'center', border: '2px dashed #333', borderRadius: 4 }}>
                <input type="file" id="u" hidden onChange={(e) => setFile(e.target.files?.[0] || null)} accept="audio/*" />
                <label htmlFor="u"><Button component="span" startIcon={<CloudUpload />}>{file ? 'Change File' : 'Select Audio'}</Button></label>
                {file && <Typography sx={{ mt: 2 }}>{file.name}</Typography>}
                <Box mt={2}><Button variant="contained" onClick={handleUpload} disabled={!file}>Analyze</Button></Box>
                {error && <Alert severity="error" sx={{ mt: 3 }}>{error}</Alert>}
              </Paper>
            </motion.div>
          ) : uploading ? (
            <motion.div key="progress" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Box sx={{ textAlign: 'center', py: 10 }}>
                <CircularProgress sx={{ mb: 4 }} />
                <Typography variant="h5">Status: {status}</Typography>
              </Box>
            </motion.div>
          ) : (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Box display="flex" justifyContent="space-between" mb={4}>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>Results</Typography>
                <Button onClick={() => setResults(null)}>New Scan</Button>
              </Box>
              <Grid container spacing={3}>
                <Grid item {...({ xs: 12, sm: 6, md: 3 } as any)}><StatCard title="Words" value={results.metadata?.total_words} color="#6366f1" icon={<VolumeUp />} delay={0.1} /></Grid>
                <Grid item {...({ xs: 12, sm: 6, md: 3 } as any)}><StatCard title="Anomalies" value={results.metadata?.anomalies} color="#ef4444" icon={<Warning />} delay={0.2} /></Grid>
                <Grid item {...({ xs: 12, sm: 6, md: 3 } as any)}><StatCard title="Speakers" value={results.metadata?.speakers?.length} color="#ec489a" icon={<Psychology />} delay={0.3} /></Grid>
                <Grid item {...({ xs: 12, sm: 6, md: 3 } as any)}><StatCard title="Stress Avg" value={results.metadata?.avg_stress?.toFixed(2)} color="#f59e0b" icon={<Timeline />} delay={0.4} /></Grid>
              </Grid>
              {results.words && (
                <Paper sx={{ mt: 4, p: 3, borderRadius: 3, bgcolor: '#141414' }}>
                  <Typography variant="h6" gutterBottom>Transcription</Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {results.words.slice(0, 30).map((w: any, i: number) => (
                      <Chip key={i} label={w.word} variant="outlined" size="small" />
                    ))}
                  </Box>
                </Paper>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </Container>
    </ThemeProvider>
  );
};

export default App;
import React, { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Container, Box, Typography, AppBar, Toolbar, Chip, LinearProgress, Alert, Paper, Card, CardContent } from '@mui/material';
import { Analytics, Timeline, Psychology, VolumeUp, CheckCircle, Error, Warning } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { theme } from './theme';
import FileUpload from './components/FileUpload';
import StressTimeline from './components/StressTimeline';
import { uploadAudio, getAnalysisStatus, getAnalysisResults } from './services/api';
import { AlignedData, AlignedWord } from './types';

const AnimatedCard = motion(Card);

function App() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [results, setResults] = useState<AlignedData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setLoading(true);
    setError(null);

    const uploadToast = toast.loading('Uploading audio file...');

    try {
      const response = await uploadAudio(file);
      setJobId(response.jobId);
      setStatus('PROCESSING');
      toast.success('File uploaded! Processing started.', { id: uploadToast });
      
      pollStatus(response.jobId);
    } catch (err) {
      setError('Upload failed. Please try again.');
      toast.error('Upload failed', { id: uploadToast });
      setLoading(false);
    }
  };

  const pollStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const statusResponse = await getAnalysisStatus(id);
        setStatus(statusResponse.status);
        
        if (statusResponse.status === 'COMPLETED') {
          clearInterval(interval);
          const resultsResponse = await getAnalysisResults(id);
          if (resultsResponse.result) {
            const parsedResults = JSON.parse(resultsResponse.result);
            setResults(parsedResults);
            toast.success('Analysis complete!');
          }
          setLoading(false);
        } else if (statusResponse.status === 'FAILED') {
          clearInterval(interval);
          setError(statusResponse.errorMessage || 'Analysis failed');
          toast.error('Analysis failed');
          setLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setError('Failed to get status');
        setLoading(false);
      }
    }, 3000);
  };

  const handleReset = () => {
    setJobId(null);
    setResults(null);
    setStatus('');
    setError(null);
  };

  const StatCard = ({ title, value, icon, color, delay }: any) => (
    <AnimatedCard
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      sx={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        borderRadius: 3,
        height: '100%',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 'bold', color }}>
              {value}
            </Typography>
          </Box>
          <Box sx={{ p: 1, borderRadius: 2, bgcolor: `${color}20` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </AnimatedCard>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Toaster position="top-right" />
      
      <AppBar position="sticky" sx={{ bgcolor: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(99,102,241,0.3)' }}>
        <Toolbar>
          <Analytics sx={{ mr: 2, color: '#6366f1' }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Lumen
          </Typography>
          <Chip 
            label="Forensic Audio Intelligence" 
            size="small" 
            sx={{ bgcolor: 'rgba(99,102,241,0.2)', color: '#6366f1' }} 
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box textAlign="center" mb={6}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h1" gutterBottom>
              Lumen
            </Typography>
            <Typography variant="h5" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
              Detect sentiment anomalies in earnings calls through multimodal AI analysis
            </Typography>
          </motion.div>
        </Box>

        <AnimatePresence mode="wait">
          {!jobId ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <FileUpload onUpload={handleUpload} loading={loading} />
              
              {error && (
                <Alert severity="error" sx={{ mt: 3 }} onClose={() => setError(null)}>
                  {error}
                </Alert>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Box mb={3}>
                <Paper sx={{ p: 3, bgcolor: 'rgba(99,102,241,0.1)', borderRadius: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="h6">Job ID: <Typography component="span" variant="body1" sx={{ fontFamily: 'monospace' }}>{jobId.slice(0, 8)}...</Typography></Typography>
                      <Chip 
                        label={status === 'PROCESSING' ? 'Processing' : status === 'COMPLETED' ? 'Complete' : 'Failed'}
                        icon={status === 'PROCESSING' ? <Timeline /> : status === 'COMPLETED' ? <CheckCircle /> : <Error />}
                        sx={{ 
                          bgcolor: status === 'PROCESSING' ? 'rgba(245,158,11,0.2)' : status === 'COMPLETED' ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)',
                          color: status === 'PROCESSING' ? '#f59e0b' : status === 'COMPLETED' ? '#22c55e' : '#ef4444'
                        }}
                      />
                    </Box>
                    <button
                      onClick={handleReset}
                      style={{
                        padding: '8px 16px',
                        background: 'rgba(99,102,241,0.2)',
                        border: '1px solid rgba(99,102,241,0.5)',
                        borderRadius: '8px',
                        color: '#fff',
                        cursor: 'pointer',
                        fontFamily: 'inherit'
                      }}
                    >
                      New Analysis
                    </button>
                  </Box>
                  {status === 'PROCESSING' && (
                    <Box mt={2}>
                      <LinearProgress sx={{ bgcolor: 'rgba(99,102,241,0.2)', '& .MuiLinearProgress-bar': { bgcolor: '#6366f1' } }} />
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        Processing audio through 4 AI layers... (2-5 minutes)
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Box>

              {results && (
                <>
                  <Box 
                    display="grid" 
                    gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }} 
                    gap={3} 
                    sx={{ mb: 4 }}
                  >
                    <StatCard 
                      title="Total Words" 
                      value={results.metadata.total_words.toLocaleString()} 
                      icon={<VolumeUp sx={{ fontSize: 32, color: '#6366f1' }} />}
                      color="#6366f1"
                      delay={0.1}
                    />
                    <StatCard 
                      title="Anomalies Detected" 
                      value={results.metadata.anomalies} 
                      icon={results.metadata.anomalies > 0 ? <Warning sx={{ fontSize: 32, color: '#ef4444' }} /> : <CheckCircle sx={{ fontSize: 32, color: '#22c55e' }} />}
                      color={results.metadata.anomalies > 0 ? '#ef4444' : '#22c55e'}
                      delay={0.2}
                    />
                    <StatCard 
                      title="Speakers" 
                      value={results.metadata.speakers.join(', ')} 
                      icon={<Psychology sx={{ fontSize: 32, color: '#ec489a' }} />}
                      color="#ec489a"
                      delay={0.3}
                    />
                    <StatCard 
                      title="Average Stress" 
                      value={results.metadata.avg_stress.toFixed(3)} 
                      icon={<Timeline sx={{ fontSize: 32, color: '#f59e0b' }} />}
                      color="#f59e0b"
                      delay={0.4}
                    />
                  </Box>

                  <Box mb={4}>
                    <StressTimeline words={results.words} />
                  </Box>

                  <Paper sx={{ p: 3, borderRadius: 3, overflowX: 'auto' }}>
                    <Typography variant="h6" gutterBottom>
                      Word-Level Analysis
                    </Typography>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                          <th style={{ textAlign: 'left', padding: '12px' }}>Time (s)</th>
                          <th style={{ textAlign: 'left', padding: '12px' }}>Word</th>
                          <th style={{ textAlign: 'left', padding: '12px' }}>Speaker</th>
                          <th style={{ textAlign: 'left', padding: '12px' }}>Stress</th>
                          <th style={{ textAlign: 'left', padding: '12px' }}>Sentiment</th>
                          <th style={{ textAlign: 'left', padding: '12px' }}>Anomaly</th>
                         </tr>
                      </thead>
                      <tbody>
                        {results.words.slice(0, 20).map((word: AlignedWord, idx: number) => (
                          <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', backgroundColor: word.anomaly ? 'rgba(239,68,68,0.1)' : 'transparent' }}>
                            <td style={{ padding: '12px' }}>{word.start.toFixed(2)}</td>
                            <td style={{ padding: '12px', fontWeight: 500 }}>{word.word}</td>
                            <td style={{ padding: '12px' }}>{word.speaker}</td>
                            <td style={{ padding: '12px' }}>
                              <span style={{ color: word.stress_score > 0.7 ? '#ef4444' : word.stress_score > 0.4 ? '#f59e0b' : '#22c55e' }}>
                                {word.stress_score.toFixed(3)}
                              </span>
                            </td>
                            <td style={{ padding: '12px' }}>
                              <span style={{
                                color: word.sentiment === 'positive' ? '#22c55e' : word.sentiment === 'negative' ? '#ef4444' : '#a3a3a3'
                              }}>
                                {word.sentiment}
                              </span>
                            </td>
                            <td style={{ padding: '12px' }}>
                              {word.anomaly ? <Warning sx={{ fontSize: 20, color: '#ef4444' }} /> : <CheckCircle sx={{ fontSize: 20, color: '#22c55e' }} />}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {results.words.length > 20 && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block', textAlign: 'center' }}>
                        Showing first 20 of {results.words.length} words
                      </Typography>
                    )}
                  </Paper>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </Container>
    </ThemeProvider>
  );
}

export default App;

import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  CssBaseline, Container, Box, Typography, AppBar, Toolbar, 
  Chip, LinearProgress, Alert, Paper, Card, CardContent, 
  Button, CircularProgress, Tab, Tabs, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  TableSortLabel, Tooltip, IconButton, Fade
} from '@mui/material';
import { 
  Analytics, Timeline, Psychology, VolumeUp, Warning, CloudUpload, 
  BarChart, ShowChart, Refresh, Equalizer, GraphicEq, People, Assessment, Info
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import {
  AreaChart, Area, BarChart as ReBarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip, ResponsiveContainer,
  Legend, ReferenceLine, Cell
} from 'recharts';
import axios from 'axios';

const darkTheme = createTheme({
  palette: { 
    mode: 'dark', 
    primary: { main: '#6366f1' }, 
    secondary: { main: '#ec489a' }, 
    background: { default: '#0a0a0a', paper: '#141414' }
  },
  shape: { borderRadius: 12 }
});

const API_BASE = 'http://localhost:8081/api/analysis';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [orderBy, setOrderBy] = useState('start');
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');

  const handleSort = (property: string) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

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
             toast.success(`Analysis Complete! Found ${res.data.metadata?.anomalies || 0} anomalies`);
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

  const StatCard = ({ title, value, icon, color, subtitle }: any) => (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} style={{ height: '100%' }}>
      <Card sx={{ 
        bgcolor: 'rgba(255,255,255,0.03)', 
        borderRadius: 3, 
        border: `1px solid ${color}30`,
        transition: 'transform 0.2s',
        '&:hover': { transform: 'translateY(-4px)', borderColor: color }
      }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 1 }}>{title}</Typography>
              <Typography variant="h4" sx={{ fontWeight: 800, color, fontSize: '2rem', mt: 1 }}>{value ?? 0}</Typography>
              {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
            </Box>
            <Box sx={{ p: 1.5, bgcolor: `${color}15`, borderRadius: 2 }}>
              {React.cloneElement(icon, { sx: { fontSize: 32, color } })}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const timelineData = (results?.words || []).map((word: any, idx: number) => ({
    index: idx,
    stress: word.stress_score,
    word: word.word,
    sentiment: word.sentiment,
    anomaly: word.anomaly,
    time: word.start
  }));

  const sentimentData = (() => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    (results?.words || []).forEach((w: any) => {
      if (w.sentiment === 'positive') counts.positive++;
      else if (w.sentiment === 'negative') counts.negative++;
      else counts.neutral++;
    });
    return [
      { name: 'Positive', value: counts.positive, color: '#22c55e' },
      { name: 'Negative', value: counts.negative, color: '#ef4444' },
      { name: 'Neutral', value: counts.neutral, color: '#6366f1' }
    ];
  })();

  const speakerData = (() => {
    const speakerMap = new Map();
    (results?.words || []).forEach((word: any) => {
      if (!speakerMap.has(word.speaker)) {
        speakerMap.set(word.speaker, { count: 0, totalStress: 0, anomalies: 0 });
      }
      const data = speakerMap.get(word.speaker);
      data.count++;
      data.totalStress += word.stress_score;
      if (word.anomaly) data.anomalies++;
    });
    return Array.from(speakerMap.entries()).map(([speaker, data]: any) => ({
      speaker,
      wordCount: data.count,
      avgStress: data.totalStress / data.count,
      anomalies: data.anomalies,
      anomalyRate: (data.anomalies / data.count) * 100
    }));
  })();

  const sortedWords = [...(results?.words || [])].sort((a, b) => {
    const aVal = a[orderBy];
    const bVal = b[orderBy];
    if (order === 'asc') return aVal > bVal ? 1 : -1;
    return aVal < bVal ? 1 : -1;
  });

  const anomalyWords = (results?.words || []).filter((w: any) => w.anomaly);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Toaster position="top-right" />
      
      <AppBar position="sticky" elevation={0} sx={{ borderBottom: '1px solid rgba(99,102,241,0.2)', bgcolor: 'rgba(20,20,20,0.9)', backdropFilter: 'blur(10px)' }}>
        <Toolbar>
          <Analytics sx={{ mr: 1.5, color: '#6366f1' }} />
          <Typography variant="h6" sx={{ fontWeight: 800, flexGrow: 1 }}>LUMEN</Typography>
          <Chip label="Forensic Audio Intelligence" size="small" sx={{ bgcolor: 'rgba(99,102,241,0.15)', color: '#6366f1' }} />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <AnimatePresence mode="wait">
          {!uploading && !results ? (
            <motion.div key="upload" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
              <Paper sx={{ p: 8, textAlign: 'center', border: '2px dashed rgba(99,102,241,0.3)', borderRadius: 4, bgcolor: 'rgba(255,255,255,0.02)' }}>
                <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
                  <CloudUpload sx={{ fontSize: 80, color: '#6366f1', mb: 2, opacity: 0.7 }} />
                </motion.div>
                <Typography variant="h5" gutterBottom>Upload Earnings Call Audio</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>Supports MP3, WAV, M4A — Up to 100MB</Typography>
                <input type="file" id="audio-upload" hidden onChange={(e) => setFile(e.target.files?.[0] || null)} accept="audio/*" />
                <label htmlFor="audio-upload">
                  <Button component="span" variant="outlined" startIcon={<CloudUpload />} sx={{ mr: 2 }}>
                    {file ? 'Change File' : 'Select File'}
                  </Button>
                </label>
                {file && <Chip label={file.name} sx={{ ml: 2 }} />}
                <Box mt={3}>
                  <Button 
                    variant="contained" 
                    onClick={handleUpload} 
                    disabled={!file}
                    sx={{ 
                      background: 'linear-gradient(135deg, #6366f1, #ec489a)',
                      '&:hover': { background: 'linear-gradient(135deg, #4f46e5, #db2777)' }
                    }}
                  >
                    Analyze Earnings Call
                  </Button>
                </Box>
                {error && <Alert severity="error" sx={{ mt: 3 }}>{error}</Alert>}
              </Paper>
            </motion.div>
          ) : uploading ? (
            <motion.div key="progress" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Paper sx={{ p: 8, textAlign: 'center', borderRadius: 4 }}>
                <CircularProgress size={60} sx={{ color: '#6366f1', mb: 3 }} />
                <Typography variant="h5">Processing Audio</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>Status: {status}</Typography>
                <LinearProgress sx={{ mt: 4, maxWidth: 400, mx: 'auto', width: '100%', bgcolor: 'rgba(99,102,241,0.2)' }} />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                  Running Whisper → Diarizer → Stress Analysis → FinBERT → Alignment
                </Typography>
              </Paper>
            </motion.div>
          ) : (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(135deg, #6366f1, #ec489a)', backgroundClip: 'text', WebkitBackgroundClip: 'text', color: 'transparent' }}>
                  Analysis Results
                </Typography>
                <Button variant="outlined" startIcon={<Refresh />} onClick={() => setResults(null)}>
                  New Analysis
                </Button>
              </Box>

              {results?.metadata?.anomalies > 0 && (
                <Alert severity="warning" icon={<Warning />} sx={{ mb: 3, borderRadius: 2 }}>
                  <Typography variant="body2">
                    <strong>{results.metadata.anomalies} anomalies detected!</strong> These segments show positive sentiment with high vocal stress.
                  </Typography>
                </Alert>
              )}

              <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }} gap={3} sx={{ mb: 4 }}>
                <StatCard title="Total Words" value={results?.metadata?.total_words} icon={<VolumeUp />} color="#6366f1" subtitle="words analyzed" />
                <StatCard 
                  title="Anomalies" 
                  value={results?.metadata?.anomalies} 
                  icon={<Warning />} 
                  color={results?.metadata?.anomalies > 0 ? "#ef4444" : "#22c55e"} 
                  subtitle={results?.metadata?.anomalies > 0 ? "⚠️ INVESTIGATE" : "no red flags"} 
                />
                <StatCard title="Speakers" value={results?.metadata?.speakers?.length} icon={<People />} color="#ec489a" subtitle="voices detected" />
                <StatCard title="Avg Stress" value={results?.metadata?.avg_stress?.toFixed(3)} icon={<GraphicEq />} color="#f59e0b" subtitle="vocal tension (0-1 scale)" />
              </Box>

              <Paper sx={{ borderRadius: 3, overflow: 'hidden', mb: 3 }}>
                <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: '1px solid #333', px: 2 }}>
                  <Tab label="Stress Timeline" icon={<ShowChart />} iconPosition="start" />
                  <Tab label="Anomalies" icon={<Warning />} iconPosition="start" />
                  <Tab label="Speaker Analysis" icon={<People />} iconPosition="start" />
                  <Tab label="Word Details" icon={<Assessment />} iconPosition="start" />
                </Tabs>
                
                <Box sx={{ p: 3 }}>
                  {tabValue === 0 && (
                    <Box>
                      <ResponsiveContainer width="100%" height={350}>
                        <AreaChart data={timelineData}>
                          <defs>
                            <linearGradient id="stressGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                          <XAxis dataKey="index" label={{ value: 'Word Index', position: 'insideBottom', offset: -5 }} />
                          <YAxis label={{ value: 'Stress Score', angle: -90, position: 'insideLeft' }} domain={[0, 1]} />
                          <ReTooltip 
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                const data = payload[0].payload;
                                return (
                                  <Paper sx={{ p: 2, bgcolor: '#1a1a1a', border: `1px solid ${data.anomaly ? '#ef4444' : '#6366f1'}` }}>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>"{data.word}"</Typography>
                                    <Typography variant="caption" display="block">Time: {data.time}s</Typography>
                                    <Typography variant="caption" display="block" sx={{ color: data.stress > 0.7 ? '#ef4444' : '#f59e0b' }}>
                                      Stress: {data.stress}
                                    </Typography>
                                    <Typography variant="caption" display="block">Sentiment: {data.sentiment}</Typography>
                                    {data.anomaly && <Typography variant="caption" sx={{ color: '#ef4444', fontWeight: 'bold' }}>⚠️ ANOMALY DETECTED</Typography>}
                                  </Paper>
                                );
                              }
                              return null;
                            }}
                          />
                          <Legend />
                          <Area type="monotone" dataKey="stress" stroke="#6366f1" fill="url(#stressGradient)" name="Stress Score" />
                          <ReferenceLine y={0.55} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Anomaly Threshold (0.55)', fill: '#f59e0b', fontSize: 12 }} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Box>
                  )}

                  {tabValue === 1 && (
                    <Box>
                      {anomalyWords.length === 0 ? (
                        <Alert severity="success" sx={{ borderRadius: 2 }}>
                          No anomalies detected. The speaker's sentiment matches their vocal stress.
                        </Alert>
                      ) : (
                        <>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {anomalyWords.length} anomalies found. These segments show positive sentiment with high vocal stress (&gt;0.55):
                          </Typography>
                          <TableContainer component={Paper} sx={{ bgcolor: 'transparent' }}>
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Time (s)</TableCell>
                                  <TableCell>Text</TableCell>
                                  <TableCell>Stress</TableCell>
                                  <TableCell>Sentiment</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {anomalyWords.map((word: any, idx: number) => (
                                  <TableRow key={idx} sx={{ bgcolor: 'rgba(239,68,68,0.1)' }}>
                                    <TableCell>{word.start?.toFixed(2)}</TableCell>
                                    <TableCell sx={{ fontWeight: 500 }}>"{word.word}"</TableCell>
                                    <TableCell sx={{ color: '#ef4444', fontWeight: 'bold' }}>{word.stress_score?.toFixed(3)}</TableCell>
                                    <TableCell>
                                      <Chip label={word.sentiment} size="small" sx={{ bgcolor: 'rgba(34,197,94,0.2)', color: '#22c55e' }} />
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </>
                      )}
                    </Box>
                  )}

                  {tabValue === 2 && (
                    <Box>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Speaker</TableCell>
                              <TableCell align="right">Word Count</TableCell>
                              <TableCell align="right">Avg Stress</TableCell>
                              <TableCell align="right">Anomalies</TableCell>
                              <TableCell align="right">Anomaly Rate</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {speakerData.map((speaker) => (
                              <TableRow key={speaker.speaker}>
                                <TableCell>{speaker.speaker}</TableCell>
                                <TableCell align="right">{speaker.wordCount}</TableCell>
                                <TableCell align="right" sx={{ color: speaker.avgStress > 0.55 ? '#ef4444' : '#f59e0b' }}>
                                  {speaker.avgStress.toFixed(3)}
                                </TableCell>
                                <TableCell align="right" sx={{ color: speaker.anomalies > 0 ? '#ef4444' : '#22c55e' }}>
                                  {speaker.anomalies}
                                </TableCell>
                                <TableCell align="right">
                                  <Chip 
                                    label={`${speaker.anomalyRate.toFixed(1)}%`} 
                                    size="small" 
                                    sx={{ 
                                      bgcolor: speaker.anomalyRate > 10 ? 'rgba(239,68,68,0.2)' : 'rgba(34,197,94,0.2)',
                                      color: speaker.anomalyRate > 10 ? '#ef4444' : '#22c55e'
                                    }} 
                                  />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                  )}

                  {tabValue === 3 && (
                    <TableContainer>
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell><TableSortLabel active={orderBy === 'start'} direction={order} onClick={() => handleSort('start')}>Time (s)</TableSortLabel></TableCell>
                            <TableCell><TableSortLabel active={orderBy === 'word'} direction={order} onClick={() => handleSort('word')}>Word</TableSortLabel></TableCell>
                            <TableCell><TableSortLabel active={orderBy === 'speaker'} direction={order} onClick={() => handleSort('speaker')}>Speaker</TableSortLabel></TableCell>
                            <TableCell><TableSortLabel active={orderBy === 'stress_score'} direction={order} onClick={() => handleSort('stress_score')}>Stress</TableSortLabel></TableCell>
                            <TableCell><TableSortLabel active={orderBy === 'sentiment'} direction={order} onClick={() => handleSort('sentiment')}>Sentiment</TableSortLabel></TableCell>
                            <TableCell>Anomaly</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {sortedWords.slice(0, 100).map((word: any, idx: number) => (
                            <TableRow key={idx} sx={{ backgroundColor: word.anomaly ? 'rgba(239,68,68,0.15)' : 'transparent' }}>
                              <TableCell>{word.start?.toFixed(2)}</TableCell>
                              <TableCell sx={{ fontWeight: 500 }}>{word.word}</TableCell>
                              <TableCell>{word.speaker}</TableCell>
                              <TableCell sx={{ color: word.stress_score > 0.7 ? '#ef4444' : word.stress_score > 0.55 ? '#f59e0b' : '#22c55e', fontWeight: word.stress_score > 0.55 ? 'bold' : 'normal' }}>
                                {word.stress_score?.toFixed(3)}
                              </TableCell>
                              <TableCell>
                                <Chip 
                                  label={word.sentiment} 
                                  size="small" 
                                  sx={{ 
                                    bgcolor: word.sentiment === 'positive' ? 'rgba(34,197,94,0.2)' : 
                                             word.sentiment === 'negative' ? 'rgba(239,68,68,0.2)' : 'rgba(99,102,241,0.2)',
                                    color: word.sentiment === 'positive' ? '#22c55e' : 
                                           word.sentiment === 'negative' ? '#ef4444' : '#6366f1'
                                  }}
                                />
                              </TableCell>
                              <TableCell>{word.anomaly ? <Warning sx={{ color: '#ef4444', fontSize: 20 }} /> : '✅'}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </Box>
              </Paper>
            </motion.div>
          )}
        </AnimatePresence>
      </Container>
    </ThemeProvider>
  );
};

export default App;

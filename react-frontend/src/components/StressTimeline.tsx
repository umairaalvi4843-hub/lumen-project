import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Box, Typography, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { AlignedWord } from '../types';

interface StressTimelineProps {
  words: AlignedWord[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <Paper sx={{ p: 2, bgcolor: 'rgba(20,20,20,0.95)', border: '1px solid #6366f1', borderRadius: 2 }}>
        <Typography variant="body2" sx={{ color: '#fff', fontWeight: 500 }}>
          "{data.word}"
        </Typography>
        <Typography variant="caption" display="block" sx={{ color: '#a3a3a3', mt: 0.5 }}>
          Time: {data.time.toFixed(2)}s
        </Typography>
        <Typography variant="caption" display="block" sx={{ color: data.stress > 0.7 ? '#ef4444' : '#f59e0b' }}>
          Stress: {data.stress.toFixed(3)}
        </Typography>
        {data.anomaly && (
          <Typography variant="caption" display="block" sx={{ color: '#ef4444', mt: 1, fontWeight: 500 }}>
            ⚠️ ANOMALY DETECTED
          </Typography>
        )}
      </Paper>
    );
  }
  return null;
};

const StressTimeline: React.FC<StressTimelineProps> = ({ words }) => {
  const data = words.map(word => ({
    time: word.start,
    stress: word.stress_score,
    word: word.word,
    anomaly: word.anomaly
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom>
          Vocal Stress Timeline
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
          Red dots indicate anomalies (positive sentiment with high stress)
        </Typography>
        <Box sx={{ height: 350, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="time" 
                stroke="#a3a3a3"
                label={{ value: 'Time (seconds)', position: 'insideBottom', offset: -5, fill: '#a3a3a3' }}
              />
              <YAxis 
                stroke="#a3a3a3"
                domain={[0, 1]}
                label={{ value: 'Stress Score', angle: -90, position: 'insideLeft', fill: '#a3a3a3' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={0.7} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Anomaly Threshold', fill: '#f59e0b', fontSize: 12 }} />
              <Line 
                type="monotone" 
                dataKey="stress" 
                stroke="#6366f1" 
                strokeWidth={2}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.anomaly) {
                    return <circle cx={cx} cy={cy} r={6} fill="#ef4444" stroke="none" />;
                  }
                  return <circle cx={cx} cy={cy} r={3} fill="#6366f1" stroke="none" />;
                }}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
    </motion.div>
  );
};

export default StressTimeline;

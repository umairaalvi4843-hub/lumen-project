import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button, CircularProgress, Paper } from '@mui/material';
import { CloudUpload, AudioFile } from '@mui/icons-material';
import { motion } from 'framer-motion';

interface FileUploadProps {
  onUpload: (file: File) => void;
  loading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload, loading }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.m4a', '.flac']
    },
    maxFiles: 1,
    disabled: loading
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Paper
        {...getRootProps()}
        sx={{
          p: 6,
          textAlign: 'center',
          cursor: loading ? 'not-allowed' : 'pointer',
          background: isDragActive 
            ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)'
            : 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
          border: isDragActive ? '2px solid #6366f1' : '2px dashed rgba(99, 102, 241, 0.5)',
          transition: 'all 0.3s ease',
        }}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ scale: isDragActive ? 1.1 : 1 }}
          transition={{ duration: 0.2 }}
        >
          {loading ? (
            <CircularProgress size={60} sx={{ color: '#6366f1', mb: 2 }} />
          ) : (
            <CloudUpload sx={{ fontSize: 80, color: '#6366f1', mb: 2 }} />
          )}
        </motion.div>
        
        <Typography variant="h5" gutterBottom>
          {isDragActive ? 'Drop your audio file here' : 'Upload Earnings Call'}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Support .wav, .mp3, .m4a files up to 100MB
        </Typography>
        
        <Button
          variant="contained"
          disabled={loading}
          startIcon={<AudioFile />}
          sx={{
            background: 'linear-gradient(135deg, #6366f1 0%, #ec489a 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #4f46e5 0%, #db2777 100%)',
            },
          }}
        >
          Select File
        </Button>
      </Paper>
    </motion.div>
  );
};

export default FileUpload;

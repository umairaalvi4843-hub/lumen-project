import axios from 'axios';

const API_BASE_URL = 'http://localhost:8081/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/analysis/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalysisStatus = async (jobId: string) => {
  const response = await api.get(`/analysis/status/${jobId}`);
  return response.data;
};

export const getAnalysisResults = async (jobId: string) => {
  const response = await api.get(`/analysis/results/${jobId}`);
  return response.data;
};

export default api;

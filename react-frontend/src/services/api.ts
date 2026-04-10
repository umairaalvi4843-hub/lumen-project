import axios from 'axios';

const API_BASE_URL = 'http://localhost:8081/api';

export const uploadAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE_URL}/analysis/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  });
  return response.data;
};

export const getAnalysisStatus = async (jobId: string) => {
  const response = await axios.get(`${API_BASE_URL}/analysis/status/${jobId}`);
  return response.data;
};

export const getAnalysisResults = async (jobId: string) => {
  const response = await axios.get(`${API_BASE_URL}/analysis/results/${jobId}`);
  return response.data;
};

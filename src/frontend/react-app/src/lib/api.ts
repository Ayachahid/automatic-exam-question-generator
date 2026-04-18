import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const generateQuestions = async (payload: any) => {
  const response = await api.post('/generate/', payload);
  return response.data;
};

export const indexDocuments = async (filePaths: string[]) => {
  const response = await api.post('/kb/index', { file_paths: filePaths });
  return response.data;
};

export const generateRAGQuestions = async (payload: any) => {
  const response = await api.post('/kb/generate', payload);
  return response.data;
};

export const listKBFiles = async () => {
  const response = await api.get('/kb/files');
  return response.data;
};

export const resetKB = async () => {
  const response = await api.post('/kb/reset');
  return response.data;
};

export default api;

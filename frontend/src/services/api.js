import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080';

export const predictTopic = async (url, userId) => {
  try {
    const response = await axios.post(`${API_URL}/predict`, { url, user_id: userId });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const batchPredictTopics = async (file, userId) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (userId) {
      formData.append('user_id', userId);
    }
    
    const response = await axios.post(`${API_URL}/batch_predict`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const saveContent = async (url, userId) => {
  try {
    // First save the content on the server
    const response = await axios.post(`${API_URL}/save_content`, { url, user_id: userId });
    
    // Then trigger the download
    if (response.data && response.data.filename) {
      // Create a temporary link element to trigger the download
      window.location.href = `${API_URL}/download_content/${response.data.filename}`;
    }
    
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Retrain the model using selected URLs from history
 * @param {Array} urls - Array of URLs to use for retraining
 * @param {string} userId - User ID
 * @returns {Promise} - Promise with the retraining result
 */
export const retrainModel = async (urls, userId) => {
  try {
    const response = await axios.post(`${API_URL}/retrain_model`, { 
      urls, 
      user_id: userId 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getHistory = async (userId, limit = 50) => {
  try {
    const params = new URLSearchParams();
    if (userId) {
      params.append('user_id', userId);
    }
    params.append('limit', limit);
    
    const response = await axios.get(`${API_URL}/history?${params.toString()}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getAnalytics = async (userId) => {
  try {
    const params = new URLSearchParams();
    if (userId) {
      params.append('user_id', userId);
    }
    
    const response = await axios.get(`${API_URL}/analytics?${params.toString()}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

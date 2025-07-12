// API Configuration
const API_BASE_URL = 'http://localhost:3006/api';

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: `${API_BASE_URL}/login`,
  REGISTER: `${API_BASE_URL}/register`,
  LOGOUT: `${API_BASE_URL}/logout`,
  REFRESH: `${API_BASE_URL}/refresh`,
  ME: `${API_BASE_URL}/me`,
  
  // Password Reset
  PASSWORD_RESET_REQUEST: `${API_BASE_URL}/password-reset/request`,
  PASSWORD_RESET_CONFIRM: `${API_BASE_URL}/password-reset/confirm`,
  
  // Profile
  PROFILE: `${API_BASE_URL}/profile`,
  PROFILE_PASSWORD: `${API_BASE_URL}/profile/password`,
  
  // Read History
  READ_HISTORY: `${API_BASE_URL}/read-history`,
  
  // Cache Management
  CACHE_STATS: `${API_BASE_URL}/cache/stats`,
  CACHE_CLEAR: `${API_BASE_URL}/cache/clear`,
  CACHE_CLEANUP: `${API_BASE_URL}/cache/cleanup`,
  ADMIN_CACHE_STATS: `${API_BASE_URL}/admin/cache/stats`,
  ADMIN_CACHE_CLEAR: `${API_BASE_URL}/admin/cache/clear`,
  ADMIN_CACHE_CLEANUP: `${API_BASE_URL}/admin/cache/cleanup`,
  
  // Search and Manga
  SEARCH: `${API_BASE_URL}/search`,
  MANGA_DETAILS: `${API_BASE_URL}/manga`,
  CHAPTER_IMAGES: `${API_BASE_URL}/chapter-images`,
  
  // Health
  HEALTH: `${API_BASE_URL}/health`,
};

export default API_ENDPOINTS; 
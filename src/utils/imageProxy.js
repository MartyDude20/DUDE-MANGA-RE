/**
 * Utility function to proxy images through our backend to avoid CORS issues
 * @param {string} imageUrl - The original image URL
 * @returns {string} - The proxied image URL or the original URL if proxying fails
 */
export const getProxiedImageUrl = (imageUrl) => {
  if (!imageUrl) {
    return null;
  }
  
  // If it's already a data URL or relative URL, return as is
  if (imageUrl.startsWith('data:') || imageUrl.startsWith('/')) {
    return imageUrl;
  }
  
  // If it's a localhost URL, return as is
  if (imageUrl.includes('localhost') || imageUrl.includes('127.0.0.1')) {
    return imageUrl;
  }
  
  // Proxy external images through our backend
  try {
    const encodedUrl = encodeURIComponent(imageUrl);
    return `/api/proxy-image?url=${encodedUrl}`;
  } catch (error) {
    console.error('Error creating proxied image URL:', error);
    return imageUrl; // Fallback to original URL
  }
};

/**
 * Check if an image URL is accessible
 * @param {string} imageUrl - The image URL to check
 * @returns {Promise<boolean>} - True if accessible, false otherwise
 */
export const isImageAccessible = async (imageUrl) => {
  if (!imageUrl) return false;
  
  try {
    const response = await fetch(imageUrl, { method: 'HEAD' });
    return response.ok;
  } catch (error) {
    console.error('Image accessibility check failed:', error);
    return false;
  }
}; 